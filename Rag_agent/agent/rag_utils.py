from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma, FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv
from .models import UploadedUrl, User
import os
import sqlite3

load_dotenv()
llm = ChatOpenAI()
embeddings = OpenAIEmbeddings()

class Utils:
    '''Contains utilities for creating, storing and retrieving embeddings'''

    prompt = ChatPromptTemplate.from_template("""Answer the following question based only on the provided context, also provide the citations:

        <context>
        {context}
        </context>

        Question: {input}""")
    def create_embeddings(self, documents, embeddings):
        vectors = Chroma.from_documents(documents, embeddings,persist_directory=r"C:\Users\coditas\Desktop\GenAI_Projects\RAG_Agent\Rag_agent\db")
        return vectors

    def store_embeddings(self,documents, db_name = r"C:\Users\coditas\Desktop\GenAI_Projects\RAG_Agent\Rag_agent\db"):
        vectors = Chroma.from_documents(documents, embeddings, persist_directory=db_name)
        return vectors
        # vectors.save_local(db_name)
        
    def load_database(self, db_name=r"C:\Users\coditas\Desktop\GenAI_Projects\RAG_Agent\Rag_agent\db"):
        try:
            # db = FAISS.load_local(db_name, embeddings, allow_dangerous_deserialization=True)
            db = None
            if os.path.exists(db_name):
                db = Chroma(persist_directory=r"C:\Users\coditas\Desktop\GenAI_Projects\RAG_Agent\Rag_agent\db", embedding_function=embeddings)
        except Exception as e:
            print(e)
            db = None
        return db
    
class db_operations:
    """Contains operations for vector database"""
    def store_url(self, url:str, user_id:int):
        """stores the url in the database, takes url resource provided by the user and user_id from the request"""
        try:
            UploadedUrl.objects.get_or_create(user = user_id, url = url)
        except Exception as e:
            print(e)
            
        
    
    def url_exists(self, url:str): 
        try:
            if UploadedUrl.objects.filter(url=url).exists():
                return True
            else: 
                return False
        except Exception as e:
            print(e)
       


def retrieve_response(user_query, vector):
  """Can be used to get context from database, that can be used to answer user queries"""
  try:
    prompt = ChatPromptTemplate.from_template("""Answer the following question based only on the provided context:

    <context>
    {context}
    </context>

    Question: {input}""")

    document_chain = create_stuff_documents_chain(llm, prompt)
    retriever = vector.as_retriever(search_kwargs={"k":3})
    retrieval_chain = create_retrieval_chain(retriever, document_chain)
  
    response = retrieval_chain.invoke({"input": f"{user_query}"})

    return response['answer']
  except Exception as e:
     print(e)
     
def get_youtube_transcript(video_id:str)->str:
    '''Function to extract transcript from youtube video'''
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en','ja','hi',])
        text = ' '.join([t['text'] for t in transcript])
        return text
    except Exception as e:
        print(f"An error occurred: {e}")
        return None