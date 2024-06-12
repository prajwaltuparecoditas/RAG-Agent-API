from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_groq import ChatGroq
from langchain_community.vectorstores import Chroma, FAISS
from langchain_postgres import PGVector
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.chat_message_histories import SQLChatMessageHistory
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv
from .models import UploadedUrl, User
import os


load_dotenv()
llm = ChatOpenAI()
# llm = ChatGroq(model="llama3-70b-8192")
embeddings = OpenAIEmbeddings()
CONNECTION_STRING = "postgresql+psycopg://postgres:root@localhost:5432/rag_agent"
COLLECTION_NAME = "state_of_union_vectors"
db = PGVector(collection_name=COLLECTION_NAME,  connection=CONNECTION_STRING, embeddings=embeddings)
class Utils:
    '''Contains utilities for creating, storing and retrieving embeddings'''

    prompt = ChatPromptTemplate.from_template("""Answer the following question based only on the provided context, also provide the citations:

        <context>
        {context}
        </context>

        Question: {input}""")
    def create_embeddings(self, documents, embeddings):
        # vectors = Chroma.from_documents(documents, embeddings,persist_directory=r"C:\Users\coditas\Desktop\GenAI_Projects\RAG_Agent\Rag_agent\db")
        # vectors = PGVector.from_documents(embedding=embeddings, documents=documents, collection_name=COLLECTION_NAME, connection=CONNECTION_STRING)
        vectors = db.add_documents(documents)
        return db

    def store_embeddings(self,documents, db_name = r"C:\Users\coditas\Desktop\GenAI_Projects\RAG_Agent\Rag_agent\db"):
        # vectors = Chroma.from_documents(documents, embeddings, persist_directory=db_name)
        vectors = db.add_documents(documents)
        # vectors = PGVector.from_documents(embedding=embeddings, documents=documents, collection_name=COLLECTION_NAME, connection=CONNECTION_STRING)
        return db
        # vectors.save_local(db_name)
    # db_name=r"C:\Users\coditas\Desktop\GenAI_Projects\RAG_Agent\Rag_agent\db"
    def load_database(self, db_name=r"C:\Users\coditas\Desktop\GenAI_Projects\RAG_Agent\Rag_agent\db"):
        try:
            # db = None
            db = PGVector(collection_name=COLLECTION_NAME,  connection=CONNECTION_STRING, embeddings=embeddings)
            # if os.path.exists(db_name):
                # db = Chroma(persist_directory=r"C:\Users\coditas\Desktop\GenAI_Projects\RAG_Agent\Rag_agent\db", embedding_function=embeddings)
                # db = PGVector(collection_name=COLLECTION_NAME,  connection=CONNECTION_STRING, embeddings=embeddings)
        except Exception as e:
            print(e)
            db = None
        return db
    
class db_operations:
    """Contains operations for vector database"""
    def store_url(self, url:str, user_id:int):
        """stores the url in the database, takes url resource provided by the user and user_id from the request"""
        try:
            user = User.objects.get(id=int(user_id))
            UploadedUrl.objects.get_or_create(user =user, url = url)
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
    
def get_session_history(session_id:str):
    return SQLChatMessageHistory(session_id=session_id, connection_string="postgresql+psycopg2://postgres:root@localhost:5432/rag_agent")