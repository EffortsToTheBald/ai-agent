"""
rag service summary class: base on user query, retrieve relevant documents from vector store, then generate summary based on retrieved documents and user query.
"""

from rag.vector_store import VectorStoreService
from utils.prompt_loader import load_rag_prompt
from model.factory import chat_model
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document

class RagSummaryService(object):
    def __init__(self):
        self.vector_store_service = VectorStoreService()
        self.retriever = self.vector_store_service.get_retriever()
        self.prompt_text = load_rag_prompt()
        self.prompt_template = PromptTemplate.from_template(self.prompt_text)
        self.model = chat_model
        self.chain = self._init_chain()
    
    def _init_chain(self):
        chain = self.prompt_template | print_prompt | self.model | StrOutputParser()
        return chain
    
    def retriever_docs(self,query: str) -> list[Document]:
        return self.retriever.invoke(query)
    
    def rag_summarize(self, query: str) -> str:
        context_docs = self.retriever_docs(query)
        context = ""
        counter = 0 
        for doc in context_docs:
            counter += 1
            context += f"【参考资料{counter}】参考资料：{doc.page_content} | 参考元数据：{doc.metadata}\n"
        prompt_input = {
            "input": query,
            "context": context
        }
        return self.chain.invoke(prompt_input)
    
def print_prompt(prompt):
    print("="*20 )
    print(prompt.to_string())
    print("="*20)
    return prompt