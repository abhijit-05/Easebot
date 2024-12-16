import os
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from meta import add_page_data, page_wise_retrieval
from utils import vectorstore
from config import settings


input_folder_path = settings.md_path+"/in"
processed_folder_path = settings.md_path+"/out"

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=settings.chunk_size,
    chunk_overlap=settings.chunk_overlap
)


def process_document(input_file: str) -> None:
    pdf_path = f'{settings.pdf_input_path}/{os.path.splitext(os.path.basename(input_file))[0]}.pdf'
    try:
        _, ext = os.path.splitext(input_file)
        if ext != '.md':
            raise Exception(format=ext)
    except Exception as e:
        print(f'Encountered Exception : {str(e)}')
    try:
        loader = UnstructuredMarkdownLoader(input_file)
        pdf_page_split = page_wise_retrieval(pdf_path)
        splits = loader.load_and_split(text_splitter=text_splitter)
        # add_page_data(splits, pdf_page_split)
        # vectorstore.add_documents(splits)
    except Exception as e:
        print(f'Encountered Exception while processing PDF: {str(e)}')


def data_ingestion() -> None:
    print('*** Initiated Data Ingestion')
    print("input_folder_path ",input_folder_path)
    folder_contents = os.listdir(input_folder_path)
    try:
        for file in folder_contents:
            input_file = os.path.join(input_folder_path, file)
            print(f'*** Processing Document : {input_file}')
            process_document(input_file)
    except Exception as e:
        print('!!! ', str(e))
    print('*** Data Ingestion Complete')

if __name__ == '__main__':
    data_ingestion()
