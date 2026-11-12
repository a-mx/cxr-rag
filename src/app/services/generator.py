from transformers import AutoProcessor, AutoModelForImageTextToText
from PIL import Image
import torch
from pathlib import Path
from flask import current_app
from dataclasses import dataclass
import json
import re
import math
@dataclass
class GenerationResult:
    report: str
    bounding_boxes: list[dict]

class Generator:
    def __init__(self, model_path):
        self.model_path = str(model_path)
        self.processor = AutoProcessor.from_pretrained(self.model_path)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = AutoModelForImageTextToText.from_pretrained(
            self.model_path,
            dtype=torch.bfloat16,
            device_map="auto"
        )
    
    @torch.inference_mode()
    def generate(
        self,
        image,
        lateral_image=None,
        retrieved_context="",
        max_new_tokens=2000,
    ):
        image = Image.open(image).convert("RGB")

        path = current_app.config["PROMPT_PATH"]

        try:
            with open(path, "r", encoding="utf-8") as file:
                prompt = file.read()
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Prompt file does not exist: {path}") from e
        
        if not prompt.strip():
            raise ValueError(f"Prompt file is empty: {path}")
        
        prompt = prompt.replace("{retrieved_context}",retrieved_context or "",)

        content = [
            {
                "type": "text",
                "text": "Frontal chest X-ray:",
            },
            {
                "type": "image",
                "image": image,
            },
        ]

        if lateral_image is not None:
            content.extend([
                {
                    "type": "text",
                    "text": "Lateral chest X-ray:",
                },
                {
                    "type": "image",
                    "image": Image.open(lateral_image).convert("RGB"),
                },
            ])

        content.append({"type": "text", "text": prompt})

        messages = [
            {
                "role": "user",
                "content": content,
            },
        ]

        inputs = self.processor.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt",
        ).to(self.device, dtype=torch.bfloat16)

        input_len = inputs["input_ids"].shape[-1]

        inputs = {
            key: value.to(self.device)
            for key, value in inputs.items()
        }

        with torch.inference_mode():
            generation = self.model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=False)
            generation = generation[0][input_len:]

        decoded = self.processor.decode(generation, skip_special_tokens=True)
        decoded = decoded.strip()

        if not decoded:
            raise ValueError("Model returned an empty response.")
        
        parsed = self._parse_response(decoded)
        return parsed
    
    @staticmethod
    def _parse_response(decoded: str) -> GenerationResult:
        match = re.search(
            r"```json\s*(.*?)\s*```",
            decoded,
            flags=re.DOTALL | re.IGNORECASE,
        )
        json_text = match.group(1) if match else decoded.strip()
        data = json.loads(json_text)

        findings = str(data.get("findings", "")).strip()
        impression = str(data.get("impression", "")).strip()

        if not findings and not impression:
            raise ValueError("Model returned an empty radiology report.")

        bounding_boxes = []

        for item in data.get("bounding_boxes", []):
            coordinates = item.get("box_2d")
            label = str(item.get("label", "")).strip()

            if not isinstance(coordinates, list) or len(coordinates) != 4:
                raise ValueError("Invalid bounding box coordinates.")

            y0, x0, y1, x1 = map(float, coordinates)

            values = (x0, y0, x1, y1)

            if (
                not all(math.isfinite(value) for value in values)
                or not 0 <= x0 < x1 <= 1000
                or not 0 <= y0 < y1 <= 1000
                or not label
            ):
                raise ValueError("Invalid bounding box returned by model.")

            bounding_boxes.append(
                {
                    "label": label,
                    "view": item.get("view", "frontal")
                    if item.get("view", "frontal") in {"frontal", "lateral"}
                    else "frontal",
                    "x0": x0 / 1000,
                    "y0": y0 / 1000,
                    "x1": x1 / 1000,
                    "y1": y1 / 1000,
                }
            )

        report = (
            f"Findings:\n{findings}\n\n"
            f"Impression:\n{impression}"
        )

        return GenerationResult(
            report=report,
            bounding_boxes=bounding_boxes,
        )

