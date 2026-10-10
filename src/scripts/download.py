from sentence_transformers import SentenceTransformer
import argparse
import os
from pathlib import Path
def main():
    models_dir = Path.cwd().joinpath('models')
    parser = argparse.ArgumentParser(description="Download and save model from HuggingFace")
    parser.add_argument(
        "--model", type=str,
    )
    args = parser.parse_args()
    path = models_dir.joinpath(args.model)
    model = SentenceTransformer(args.model)
    model.save(path)

if __name__ == "__main__":
    main()