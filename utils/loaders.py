import os
from dotenv import load_dotenv
load_dotenv()
from langchain_unstructured import UnstructuredLoader
from utils.config import UPLOAD_DIR
import os
UNSTRUCTURED_API_KEY = os.getenv("UNSTRUCTURED_API_KEY")

def file_loader(file_name:str,file):
    file_directory = os.path.join(UPLOAD_DIR,file_name)
    with open (file_directory,"wb") as myfile:
        myfile.write(file)
    loader = UnstructuredLoader(file_path=file_directory,strategy="auto",api_key=UNSTRUCTURED_API_KEY)
    docs = loader.load()
    return docs

