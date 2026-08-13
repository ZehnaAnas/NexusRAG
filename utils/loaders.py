import os
from dotenv import load_dotenv
load_dotenv()
from langchain_unstructured import UnstructuredLoader
from utils.config import UPLOAD_DIR

UNSTRUCTURED_API_KEY = os.getenv("UNSTRUCTURED_API_KEY")

def file_loader(file_name:str,file):
    file_directory = f"{UPLOAD_DIR}/{file_name}"
    with open (file_directory,"wb") as myfile:
        myfile.write(file)
    loader = UnstructuredLoader(file_directory)
    docs = loader.load()
    return docs

