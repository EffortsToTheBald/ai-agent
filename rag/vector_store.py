
from utils.logger_handler import logger
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from utils.config_handler import chroma_config 
from model.factory import embeddings_model
from utils.path_tool import get_absolute_path
import os
from utils.file_handler import get_file_md5_hex, listdir_with_allowed_type, pdf_loader,txt_loader

class VectorStoreService:
    def __init__(self):
        self.vector_store = Chroma(
                collection_name= chroma_config["collection_name"],
                embedding_function= embeddings_model,
                persist_directory= chroma_config["persist_directory"],
        )

        self.spliter = RecursiveCharacterTextSplitter(
            chunk_size=chroma_config["chunk_size"],
            chunk_overlap=chroma_config["chunk_overlap"],
            separators=chroma_config["separator"],
            length_function=len
        )

    def get_retriever(self):
        return self.vector_store.as_retriever(search_kwargs={"k": chroma_config["k"]})
    
    def load_documents(self):
        '''
        load documents to vector store
        '''

        def check_md5_hex(md5_for_check: str):
             if not os.path.exists(chroma_config["md5_hex_store"]):
                # create md5_hex_store file if it does not exist
                open(chroma_config["md5_hex_store"], 'w', encoding='utf-8').close()
                return False
             
             with open(chroma_config["md5_hex_store"], 'r', encoding='utf-8') as f:
                for line in f.readlines():
                    if line.strip() == md5_for_check:
                        return True
             return False
        
        def save_md5_hex(md5_hex: str):
            with open(chroma_config["md5_hex_store"], 'a', encoding='utf-8') as f:
                f.write(md5_hex + '\n')

        def get_file_docs(read_path: str):
            if read_path.endswith('.txt'):
                return txt_loader(read_path)
            elif read_path.endswith('.pdf'):
                return pdf_loader(read_path)
            else:
                # raise ValueError("Unsupported file type")
                return []
        
        allowed_files_path: list[str] = listdir_with_allowed_type(get_absolute_path(chroma_config["data_path"]), tuple(chroma_config["allow_knowledge_file_type"]))

        for file_path in allowed_files_path:
            md5_hex = get_file_md5_hex(file_path)
            if not md5_hex:
                continue
            
            if check_md5_hex(md5_hex):
                logger.info(f"file {file_path} has been loaded before, skip it")
                continue
            
            try:
                docs = get_file_docs(file_path)
                if not docs:
                    logger.warning(f"file {file_path} is empty or unsupported, skip it")
                    continue
                
                splitt_document: list[Document]= self.spliter.split_documents(docs)

                self.vector_store.add_documents(splitt_document)
                save_md5_hex(md5_hex)
                logger.info(f"file {file_path} loaded successfully")
            except Exception as e:
                logger.error(f"failed to load file {file_path}, error: {e}")

