from transformers import AutoModel, AutoProcessor
import pandas as pd
from pathlib import Path
import faiss
import numpy as np
from PIL import Image
import json
import torch
def main():
    batch_size = 32
    print_every = 10
    limit = 100

    data_dir = Path.cwd().joinpath("data")
    csv_dir = data_dir.joinpath("csv")
    photos_csv_path = csv_dir.joinpath("photos.csv")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    models_dir = Path.cwd().joinpath('models')
    model_name = "google/medsiglip-448"
    path = models_dir.joinpath(model_name)
    
    processor = AutoProcessor.from_pretrained(str(path))
    model = AutoModel.from_pretrained(str(path)).to(device)
    model.eval()

    index_dir = data_dir.joinpath('index')
    index_output = index_dir.joinpath('images.index')
    ids_output = index_dir.joinpath('dicom_ids.json')

    index = None

    kept_records = []

    df = pd.read_csv(photos_csv_path)
    images_paths = df["path"].tolist()
    records = df[
        ["dicom_id", "subject_id", "study_id"]
    ].to_dict("records")

    for i in range(0, len(images_paths), batch_size):

        batch_image_paths = images_paths[i:i+batch_size]
        images = []
        batch_records = records[i:i+batch_size]
        valid_records = []

        for p, record in zip(batch_image_paths, batch_records):
            try:
                images.append(Image.open(p).convert("RGB"))
                valid_records.append(record)
            except Exception:
                continue

        if not images:
            continue

        inputs = processor(
            images=images,
            return_tensors="pt",
        )

        inputs = {
            key: value.to(device)
            for key, value in inputs.items()
        }

        with torch.inference_mode():
            outputs = model(**inputs)
            embeddings = outputs.image_embeds
            embeddings = torch.nn.functional.normalize(
                embeddings,
                p=2,
                dim=-1,
            )

        embeddings = embeddings.cpu().numpy().astype("float32")

        if index is None:
            index = faiss.IndexFlatIP(embeddings.shape[1])

        index.add(embeddings)
        kept_records.extend(valid_records)

        for img in images:
            img.close()



        if True:
            print(f"Processed {i + len(batch_image_paths)} / {len(images_paths)}")

        if i>=limit:
            break
    
    
    index_dir.mkdir(parents=True, exist_ok=True)
    if index is None:
        raise RuntimeError("No valid images were processed.")
    faiss.write_index(index, str(index_output))
    with open(ids_output, "w") as f:
        json.dump(kept_records, f, ensure_ascii=True, indent=2)

    print("Total vectors:", index.ntotal)
    print("Index saved to:", index_output)
    print("IDs saved to:", ids_output)


if __name__ == "__main__":
    main()

