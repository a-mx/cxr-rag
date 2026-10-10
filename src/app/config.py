from dotenv import load_dotenv
from pathlib import Path
import yaml
import os
load_dotenv()
class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")

    ARGON2_TYPE=os.getenv("ARGON2_TYPE")
    ARGON2_ROUNDS=os.getenv("ARGON2_ROUNDS")
    ARGON2_MEMORY_COST=os.getenv("ARGON2_MEMORY_COST")
    ARGON2_PARALLELISM=os.getenv("ARGON2_PARALLELISM")
    ARGON2_HASH_LEN=os.getenv("ARGON2_HASH_LEN")
    ARGON2_SALT_LEN=os.getenv("ARGON2_SALT_LEN")

    EXAMPLE_PASSWORD_HASH = os.getenv("EXAMPLE_PASSWORD_HASH")

    ROOT_DIR = Path(__file__).resolve().parent.parent.parent
    DATA_DIR = ROOT_DIR.joinpath("data")
    UPLOAD_DIR = DATA_DIR.joinpath("uploads")

    CONFIG_PATH = ROOT_DIR.joinpath("config.yaml")
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        try:
            cfg = yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(e)
    TOP_K = cfg["top_k"]

if __name__ == "__main__":
    pass