from dotenv import load_dotenv
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