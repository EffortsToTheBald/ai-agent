import hashlib
import os
from utils.logger_handler import logger
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader, TextLoader

def get_file_md5_hex(file_path):
    '''
    get file md5 hex string
    '''
    if not os.path.exists(file_path):
        logger.error(f'file {file_path} does not exist')
        return
    
    if not os.path.isfile(file_path):
        logger.error(f'{file_path} is not a file')
        return
    
    hash_md5 = hashlib.md5()
    chunk_size = 4096
    try:
        with open(file_path, 'rb') as f:
            while chunk := f.read(chunk_size):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception as e:
        logger.error(f'failed to get md5 hex string for file {file_path}, error: {e}')
        return None
    


def listdir_with_allowed_type(path: str, allowed_types: tuple[list]):
    '''
    list files in directory with allowed type
    '''
    files = []
    if not os.path.isdir(path):
        logger.error(f'{path} is not a directory')
        return allowed_types
    
    for f in os.listdir(path):
        if f.endswith(allowed_types):
            files.append(os.path.join(path,f))

    return tuple(files)

def pdf_loader(filepath: str, passwd=None) -> list[Document]:
    '''
    load pdf file
    '''
    return PyPDFLoader(filepath, password=passwd).load()

def txt_loader(filepath:str) -> list[Document]:
    '''
    load txt file
    '''
    return TextLoader(filepath).load()