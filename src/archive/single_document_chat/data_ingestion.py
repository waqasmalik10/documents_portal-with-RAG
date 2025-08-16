import uuid
from pathlib import Path
import sys

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException
from utils.model_loader import ModelLoader


class SingleDocumentIngestor:
    def __init__(self, data_dir: str = "data/single_document_chat", faiss_dir = "faiss_index"):
        try: 
            self.log = CustomLogger().get_logger(__name__)

            self.data_dir = data_dir
            self.data_dir.mkdir(parents=True, exist_ok=True)

            self.faiss_dir=faiss_dir
            self.faiss_dir.mkdir(parents=True, exist_ok=True)

            self.model_loader = ModelLoader()
            self.log.info("SingleDocumentChat model initialized.")


        except Exception as e:
            self.log.error("Failed to instantiate SingleDocumentIngestor", error=str(e))
            raise DocumentPortalException("Failed to instantiate SingleDocumentIngestor")
        
    def ingest_files(self, uploaded_files):
        try: 
            self.log = CustomLogger().get_logger(__name__)
            documents = []

            for uploaded_file in uploaded_files:
                unique_filename = f"session_{datetime.now(timezone.utc)}_{uuid.uuid4().hex[:8].pdf}"
                temp_path = self.data_dir / unique_filename

                with open(temp_path, "wb") as f_out:
                    f_out.write(uploaded_file.read())
                
                self.log.info("PDF saved")

                loader = PyPDFLoader(str(temp_path))
                docs = loader.load()
                documents.extend(docs)

            return self._create_retriever(documents)

        except Exception as e:
            self.log.error("Failed to ingest files", error=str(e))
            raise DocumentPortalException("Failed to ingest files")

    def _create_retriever(self, documents):
        try: 
            self.log = CustomLogger().get_logger(__name__)
            splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            chunks = splitter.split_documents(documents)

            embeddings = self.model_loader.load_embeddings()
            vectorstore = FAISS.from_documents(documents=documents)

            vectorstore.save_local(self.faiss_dir)

            retriever = vectorstore.as_retriever(search_type="similarity", top_k=5)

        except Exception as e:
            self.log.error("Failed to create retriever", error=str(e))
            raise DocumentPortalException("Failed to create retriever")