from langchain.schema.output_parser import StrOutputParser
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema.runnable import RunnablePassthrough
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOllama
from langchain_community.vectorstores.utils import filter_complex_metadata
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader, PyPDFDirectoryLoader
from pathlib import Path
import os
from dotenv import load_dotenv
import logging
import sys

class ChatPDF:
    vector_store = None
    retriever = None
    chain = None

    def __init__(self):
        load_dotenv()
        OLLAMA_URL = os.getenv('OLLAMA_URL', 'http://localhost:11434')
        OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'mistral:latest')
        logging.info(f'OLLAM URL and MODEL {OLLAMA_URL} {OLLAMA_MODEL}')
        self.model = ChatOllama(model=OLLAMA_MODEL, base_url=OLLAMA_URL)
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=100)
        self.prompt = PromptTemplate.from_template(
            """
            <s> [INST] You are an assistant for question-answering tasks. Use the following pieces of retrieved context 
            to answer the question. If you don't know the answer, just say that you don't know. Use three sentences
             maximum and keep the answer concise. [/INST] </s> 
            [INST] Question: {question} 
            Context: {context} 
            Answer: [/INST]
            """
        )
        self.build_chain()

    def build_chain(self):
        # absolute path of ./chromadb_data
        database_path = os.path.join(Path(__file__).resolve().parent, "chromadb_data")
        self.vector_store = Chroma(
            "ollama-rag",
            embedding_function=FastEmbedEmbeddings(),
            persist_directory=database_path
        )

        self.retriever = self.vector_store.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={
                "k": 3,
                "score_threshold": 0.5,
            },
        )

        self.chain = ({"context": self.retriever, "question": RunnablePassthrough()}
                      | self.prompt
                      | self.model
                      | StrOutputParser())
        
        return self

    def ingest(self, pdf_file_path: str):
        logging.info(f'Ingesting file {pdf_file_path}')
        docs = PyPDFLoader(file_path=pdf_file_path).load()
        chunks = self.text_splitter.split_documents(docs)
        chunks = filter_complex_metadata(chunks)

        self.vector_store.add_documents(chunks)
        return self

    def ingest_directory(self, pdf_dir_path: str):
        logging.info(f'Ingesting directory {pdf_dir_path}')
        docs = PyPDFDirectoryLoader(path=pdf_dir_path).load()
        chunks = self.text_splitter.split_documents(docs)
        chunks = filter_complex_metadata(chunks)

        self.vector_store.add_documents(chunks)
        return self

    def ask(self, query: str, format = "none"):
        if not self.chain:
            return "Please, add a PDF document first."
        logging.info(f'Querying "{query}" with format {format}')
        if format != "none":
            query= self._set_format(query, format)
        return self.chain.invoke(query)

    def empty_database(self):
        logging.info(f'Emptying database')
        self.vector_store.delete_collection()
        return self.build_chain()

    def _set_format(self, question: str, format: str) -> str:
        # add a sentence to the provided prompt so that it returns data formatted the right way 
        logging.info(f'Setting format {format}')
        if format == "none":
            return question
        elif format == "json":
            return f"{question} [INST] Output Format: json [/INST]"
        elif format == "csv":
            return f"{question} [INST] Output Format: csv with each field protected by double quotes [/INST]"
        else:
            sys.exit(f"Format {format} is not supported. Please use json or csv")