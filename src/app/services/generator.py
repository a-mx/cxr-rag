from transformers import AutoProcessor, AutoModelForImageTextToText
from PIL import Image
import torch
from pathlib import Path

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
    def generate(self, image, retrieved_context="", max_new_tokens=2000):
        image = Image.open(image).convert("RGB")

        prompt = f"""
        Generate a radiology report based only on the chest X-ray.

        Retrieved reference cases:
        {retrieved_context}

        Requirements:
        - Describe only findings supported by the image.
        - Do not invent measurements or diagnoses.
        - Use the following structure if not stated otherwise:
        Findings:
        Impression:
        - If the image is insufficient for a finding, say so.
        """

        messages = [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "You are an assistant supporting radiology "
                            "report drafting. Your output requires review "
                            "by a qualified radiologist."
                        ),
                    }
                ],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "image": image,
                    },
                    {
                        "type": "text",
                        "text": prompt,
                    },
                ],
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
        return decoded

