import base64
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from config import settings

emebddings = OpenAIEmbeddings(
      base_url="http://192.168.4.31:1234/v1",
      api_key="not-needed",
      check_embedding_ctx_length=False
)

vectorstore = Chroma(
    'Chroma-DB',
    embedding_function=emebddings,
    persist_directory='./Chroma-DB-03'
)

def img_to_base64(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
        
