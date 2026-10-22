from huggingface_hub import snapshot_download
import argparse
import os
from pathlib import Path
from dotenv import load_dotenv

def main():
    parser = argparse.ArgumentParser(description="Download and save model from HuggingFace")
    parser.add_argument(
        "--model", type=str, required=True
    )
    args = parser.parse_args()
    root_dir = Path(__file__).resolve().parents[2]
    models_dir = root_dir.joinpath("models")
    output_dir = models_dir.joinpath(args.model)
    snapshot_download(
        repo_id=args.model,
        local_dir=str(output_dir),
        token=os.getenv("HF_TOKEN"),
    )
    print(f"Model saved to: {output_dir}")

if __name__ == "__main__":
    load_dotenv()
    main()