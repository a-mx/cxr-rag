from transformers import AutoProcessor, AutoModel
from PIL import Image
import torch
from pathlib import Path

class Encoder:
    def __init__(self, model_path):
        self.model_path = str(model_path)
        self.processor = AutoProcessor.from_pretrained(self.model_path)

        self.model = AutoModel.from_pretrained(
            self.model_path,
            torch_dtype=torch.bfloat16,
            device_map="auto",
        )
        
    @torch.inference_mode()
    def encode_image(self, image):
        if isinstance(image, (str, Path)):
            image = Image.open(image).convert("RGB")

        inputs = self.processor(
            images=image,
            return_tensors="pt",
        )

        inputs = {
            key: value.to(self.device)
            for key, value in inputs.items()
        }

        outputs = self.model(**inputs)
        embedding = outputs.image_embeds

        return torch.nn.functional.normalize(
            embedding,
            p=2,
            dim=-1,
        ).cpu().numpy()

    @torch.inference_mode()
    def encode_images(self, images):
        converted_images = []

        for image in images:
            if isinstance(image, (str, Path)):
                image = Image.open(image).convert("RGB")
            converted_images.append(image)

        inputs = self.processor(
            images=converted_images,
            return_tensors="pt",
        )

        inputs = {
            key: value.to(self.device)
            for key, value in inputs.items()
        }

        outputs = self.model(**inputs)
        embeddings = outputs.image_embeds

        return torch.nn.functional.normalize(
            embeddings,
            p=2,
            dim=-1,
        ).cpu().numpy()

    @torch.inference_mode()
    def encode_text(self, texts):
        if isinstance(texts, str):
            texts = [texts]

        inputs = self.processor(
            text=texts,
            padding="max_length",
            return_tensors="pt",
        )

        inputs = {
            key: value.to(self.device)
            for key, value in inputs.items()
        }

        outputs = self.model(**inputs)
        embeddings = outputs.text_embeds

        return torch.nn.functional.normalize(
            embeddings,
            p=2,
            dim=-1,
        ).cpu().numpy()