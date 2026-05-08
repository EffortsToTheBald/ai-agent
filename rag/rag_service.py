"""
rag service summary class: base on user query, retrieve relevant documents from vector store,
then generate summary based on retrieved documents and user query.

Phase 1.4 优化：向量检索调优
  - 添加 similarity_score_threshold 过滤低质量检索结果
  - 检索结果去重（基于内容相似度）

Phase 1.5 优化：Agent 输出质量增强
  - 检索结果为空时返回明确提示，避免幻觉
  - 输出格式规范化（去除原始元数据泄露）
"""

from rag.vector_store import VectorStoreService
from utils.prompt_loader import load_rag_prompt
from model.factory import chat_model
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document

# Phase 1.4: 检索相似度阈值，低于此分数的结果将被过滤
SIMILARITY_SCORE_THRESHOLD = 0.6

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

    def retriever_docs(self, query: str) -> list[Document]:
        """
        Phase 1.4: 检索增强
        - 使用 similarity_search_with_relevance_scores 获取带分数的结果
        - 过滤低于阈值的低质量结果
        - 对结果去重（基于内容前100字符）
        """
        try:
            # 带分数的检索，便于过滤低质量结果
            docs_with_scores = self.vector_store_service.vector_store.similarity_search_with_relevance_scores(
                query, k=self.vector_store_service.vector_store._collection.count()
                if hasattr(self.vector_store_service.vector_store, '_collection') else 10
            )

            # 过滤低分数结果
            filtered_docs = []
            seen_contents = set()
            for doc, score in docs_with_scores:
                # Phase 1.4: 过滤低于阈值的结果
                if score < SIMILARITY_SCORE_THRESHOLD:
                    continue
                # Phase 1.4: 基于内容前100字符去重
                content_key = doc.page_content[:100]
                if content_key in seen_contents:
                    continue
                seen_contents.add(content_key)
                filtered_docs.append(doc)
                # 限制返回数量
                if len(filtered_docs) >= 5:
                    break

            return filtered_docs
        except Exception:
            # 降级到普通检索
            return self.retriever.invoke(query)

    def rag_summarize(self, query: str) -> str:
        """
        Phase 1.5: 输出质量增强
        - 检索结果为空时返回空字符串，让 Agent 自行基于常识回答
        - 不返回"未找到"等提示，避免 Agent 把这段话原样输出给用户
        - 规范化参考资料格式，避免元数据泄露
        """
        context_docs = self.retriever_docs(query)

        # 检索结果为空时返回空字符串，Agent 会基于自身知识回答
        # 不能返回"未找到"之类的话，否则 Agent 会原样转述给用户
        if not context_docs:
            return ""

        context = ""
        for counter, doc in enumerate(context_docs, 1):
            source = doc.metadata.get("source", "未知来源")
            if "/" in source:
                source = source.split("/")[-1]
            context += f"【参考资料{counter}】来源：{source}\n{doc.page_content}\n\n"

        prompt_input = {
            "input": query,
            "context": context
        }
        return self.chain.invoke(prompt_input)


def print_prompt(prompt):
    print("=" * 20)
    print(prompt.to_string())
    print("=" * 20)
    return prompt