from sentence_transformers import SentenceTransformer
import pandas as pd
from pathlib import Path
import faiss

def main():
    models_dir = Path.cwd().joinpath('models')
    model_name = "google/embeddinggemma-2"
    path = models_dir.joinpath(model_name)
    model = SentenceTransformer(str(path))



if __name__ == "__main__":
    main()

