import json
from pathlib import Path

import faiss
import numpy as np

class Retriever:
    def __init__(self, index_path, k=5, ids_path=None):
        self.index_path = Path(index_path)
        self.k = k
        self.index = faiss.read_index(str(self.index_path))

        if ids_path is None:
            ids_path = self.index_path.parent / "dicom_ids.json"

        with open(ids_path, "r", encoding="utf-8") as file:
            self.dicom_ids = json.load(file)

        if self.index.ntotal != len(self.dicom_ids):
            raise ValueError(
                "The number of vectors in the index does not match the number of IDs."
            )

        self.k = min(self.k, self.index.ntotal)

    def retrieve(self, embedding):
        vector = np.asarray(embedding, dtype=np.float32)

        if vector.ndim == 1:
            vector = vector.reshape(1, -1)

        if vector.ndim != 2 or vector.shape[0] != 1:
            raise ValueError(
                "Embedding must have shape (dimension,) or (1, dimension)."
            )

        if vector.shape[1] != self.index.d:
            raise ValueError(
                f"Invalid embedding dimension: {vector.shape[1]}. "
                f"Expected: {self.index.d}."
            )

        faiss.normalize_L2(vector)

        scores, positions = self.index.search(vector, self.k)

        results = []

        for score, position in zip(scores[0], positions[0]):
            if position == -1:
                continue

            results.append(
                {
                    **self.records[int(position)],
                    "score": float(score),
                }
            )

        return results