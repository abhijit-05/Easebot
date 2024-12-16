from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load environment variables from a `.env` file
load_dotenv()

class Settings(BaseSettings):
    embedding_model: str
    chunk_size: int
    chunk_overlap: int
    chroma_collection: str
    chroma_persist_dir: str
    mongo_url: str
    mongo_port: int
    md_path: str
    pdf_input_path: str
    image_path: str

    class Config:
        # Specify the environment file explicitly if needed
        env_file = ".env"
        env_file_encoding = "utf-8"

# Initialize the settings
settings = Settings()

# Access settings fields
print(settings.model_dump())
