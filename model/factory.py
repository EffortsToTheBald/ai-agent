from abc import ABC, abstractmethod
from typing import Optional

from langchain.embeddings.base import Embeddings
from langchain.chat_models.base import BaseChatModel
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_community.embeddings import DashScopeEmbeddings

from utils.config_handler import rag_config 

class BaseModelFactory(ABC):
    @abstractmethod
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        pass

class ChatModelFactory(BaseModelFactory):
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        return ChatTongyi(model=rag_config["chat_model_name"])
    
class EmbeddingsModelFactory(BaseModelFactory):
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        return DashScopeEmbeddings(model=rag_config["embeddings_model_name"])
    
    
chat_model = ChatModelFactory().generator()
embeddings_model = EmbeddingsModelFactory().generator()