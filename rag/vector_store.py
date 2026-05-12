
from utils.logger_handler import logger
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from utils.config_handler import chroma_config
from model.factory import embeddings_model
from utils.path_tool import get_absolute_path
import os
from utils.file_handler import get_file_md5_hex, listdir_with_allowed_type, pdf_loader, txt_loader


class VectorStoreService:
    """
    向量存储服务

    Phase 2.2: 支持领域隔离 — 每个领域拥有独立的 ChromaDB collection
    - 默认使用 chroma.yaml 中的 collection_name
    - 可通过 collection_name 参数指定不同领域的集合
    """

    def __init__(self, collection_name: str = None, data_path: str = None):
        self.collection_name = collection_name or chroma_config["collection_name"]
        self.data_path = data_path or chroma_config["data_path"]

        self.vector_store = Chroma(
            collection_name=self.collection_name,
            embedding_function=embeddings_model,
            persist_directory=chroma_config["persist_directory"],
        )

        self.spliter = RecursiveCharacterTextSplitter(
            chunk_size=chroma_config["chunk_size"],
            chunk_overlap=chroma_config["chunk_overlap"],
            separators=chroma_config["separator"],
            length_function=len
        )

    def get_retriever(self):
        return self.vector_store.as_retriever(search_kwargs={"k": chroma_config["k"]})

    def load_documents(self, md5_store_path: str = None, indexed_md5_set: set = None):
        """
        加载文档到向量存储

        Phase 2.3: 支持增量更新
        - md5_store_path: MD5 记录文件路径（兼容旧逻辑）
        - indexed_md5_set: 已索引的 MD5 集合（来自 knowledge_manager）
        """

        def check_md5_hex(md5_for_check: str):
            if indexed_md5_set is not None:
                return md5_for_check in indexed_md5_set

            store_path = md5_store_path or chroma_config["md5_hex_store"]
            if not os.path.exists(store_path):
                open(store_path, 'w', encoding='utf-8').close()
                return False

            with open(store_path, 'r', encoding='utf-8') as f:
                for line in f.readlines():
                    if line.strip() == md5_for_check:
                        return True
            return False

        def save_md5_hex(md5_hex: str):
            if indexed_md5_set is not None:
                indexed_md5_set.add(md5_hex)
                return
            store_path = md5_store_path or chroma_config["md5_hex_store"]
            with open(store_path, 'a', encoding='utf-8') as f:
                f.write(md5_hex + '\n')

        def get_file_docs(read_path: str):
            if read_path.endswith('.txt'):
                return txt_loader(read_path)
            elif read_path.endswith('.pdf'):
                return pdf_loader(read_path)
            else:
                return []

        abs_data_path = get_absolute_path(self.data_path)
        allowed_files_path = listdir_with_allowed_type(
            abs_data_path,
            tuple(chroma_config["allow_knowledge_file_type"])
        )

        loaded_count = 0
        skipped_count = 0

        for file_path in allowed_files_path:
            md5_hex = get_file_md5_hex(file_path)
            if not md5_hex:
                continue

            if check_md5_hex(md5_hex):
                skipped_count += 1
                continue

            try:
                docs = get_file_docs(file_path)
                if not docs:
                    logger.warning(f"file {file_path} is empty or unsupported, skip it")
                    continue

                splitt_document = self.spliter.split_documents(docs)
                self.vector_store.add_documents(splitt_document)
                save_md5_hex(md5_hex)
                loaded_count += 1
                logger.info(f"file {file_path} loaded successfully")
            except Exception as e:
                logger.error(f"failed to load file {file_path}, error: {e}")

        if loaded_count > 0:
            logger.info(f"[VectorStore] 加载完成: 新增 {loaded_count} 个文件, 跳过 {skipped_count} 个")

        return loaded_count

    def add_texts(self, texts: list[str], metadatas: list[dict] = None) -> list[str]:
        """直接添加文本到向量存储"""
        return self.vector_store.add_texts(texts, metadatas)

    def delete_collection(self):
        """删除整个向量集合"""
        try:
            self.vector_store._client.delete_collection(self.collection_name)
            logger.info(f"[VectorStore] 已删除集合: {self.collection_name}")
        except Exception as e:
            logger.warning(f"[VectorStore] 删除集合失败: {e}")

    def get_collection_stats(self) -> dict:
        """获取集合统计信息"""
        try:
            count = self.vector_store._collection.count()
            return {"collection": self.collection_name, "document_count": count}
        except Exception:
            return {"collection": self.collection_name, "document_count": 0}
