from dotenv import load_dotenv
from pathlib import Path
import yaml
import os
load_dotenv()
class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")

    ARGON2_TYPE="ID"
    ARGON2_ROUNDS=4
    ARGON2_MEMORY_COST=65536
    ARGON2_PARALLELISM=4
    ARGON2_HASH_LEN=32
    ARGON2_SALT_LEN=16

    EXAMPLE_PASSWORD_HASH = os.getenv("EXAMPLE_PASSWORD_HASH")

    ROOT_DIR = Path(__file__).resolve().parents[2]
    DATA_DIR = ROOT_DIR.joinpath("data")
    UPLOAD_DIR = DATA_DIR.joinpath("uploads")

    MODEL_DIR = ROOT_DIR.joinpath("models")

    INDEX_DIR = DATA_DIR.joinpath('index')

    IMAGES_INDEX_PATH = INDEX_DIR.joinpath('images.index')
    DICOM_IDS_PATH = INDEX_DIR.joinpath("dicom_idx.json")

    CONFIG_PATH = ROOT_DIR.joinpath("config.yaml")
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        try:
            cfg = yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(e)

    TOP_K = cfg["top_k"]

    ENCODER_MODEL_PATH = MODEL_DIR.joinpath(cfg["encoder_model"])
    GENERATOR_MODEL_PATH = MODEL_DIR.joinpath(cfg["generator_model"])

if __name__ == "__main__":
    pass