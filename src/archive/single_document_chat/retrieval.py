import os
import sys
from dotenv import load_dotenv

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory

from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException
from prompt.prompt_library import PROMPT_REGISTRY
from model.models import PrompTypes


class ConversationalRAG:
    def __init(self, session_id: str, retriever):
        try:
            self.log = CustomLogger().get_logger(__name__)
            self.session_id = session_id
            self.retriever = retriever
            self.llm = self._load_llm()
            self.contextualize_prompt = PROMPT_REGISTRY[PrompTypes.CONTEXTUALIZE_QUESTION.value]
            self.qa_prompt = PROMPT_REGISTRY[PrompTypes.CONTEXTUALIZE_QA.value]
            self.history_aware_retriever = create_history_aware_retriever(
                self.llm, self.retriever, self.contextualize_prompt
            )
            self.qa_chain = create_stuff_documents_chain(self.llm, self.qa_prompt)
            self.rag_chain = create_retrieval_chain(self.history_aware_retriever, self.qa_chain)

            self.chain = RunnableWithMessageHistory(

            )
        except Exception as e:
            raise DocumentPortalException("Initialization failed in conversationalRAG")

    def _load_llm(self):
        try:
            llm = ModelLoader().load_llm()
            return llm
        except Exception as e:
            self.log.error("Error in _load_llm", error=str(e))
            raise DocumentPortalException("_load_llm failed in conversationalRAG")

    def _get_session_history(self):
        try:
            pass
        except Exception as e:
            self.log.error("Error in get_session_history", error=str(e))
            raise DocumentPortalException("_get_session_history failed in conversationalRAG")
        
    def load_retriever_from_faiss(self, index_path):
        try:
            embeddings = ModelLoader().load_embeddings()
            if not os.path.isdir(index_path):
                raise FileNotFoundError("Faiss index path not found")
            
            vectorstore = FAISS.load_local(index_path)

            return vectorstore.as_retriever(search_type="similarity", top_p=5)
        
        except Exception as e:
            self.log.error("Error in load_retriever_from_faiss", error=str(e))
            raise DocumentPortalException("load_retriever_from_faiss failed in conversationalRAG")

    def invoke(self, user_input):
        try:
            response = self.chain.invoke(
                {"input": user_input},
                "config": {
                    "configurable": {
                        "session_id": self.session_id
                    }
                }
            )
            answer = response.get("answer", "No answer")

            return answer
        except Exception as e:
            self.log.error("Error in invoke", error=str(e))
            raise DocumentPortalException("invoke failed in conversationalRAG")