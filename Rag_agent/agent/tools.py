from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma, FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from .rag_utils import Utils, db_operations, retrieve_response, get_youtube_transcript
from langchain_core.tools import tool
from .models import User


utils = Utils()
embeddings = OpenAIEmbeddings()
crud = db_operations()

@tool
def pdf_ans(pdf_path: str, user_query: str, user_id: int) -> str:
  '''Provides answer by referencing the pdf for which the user has provided the path'''

  url_exists = crud.url_exists(pdf_path)
  
  if url_exists:
    try:
        vector = utils.load_database()
    except Exception as e:
        print(e)
  else:
    
    loader = PyPDFLoader(pdf_path)
    pages = loader.load_and_split()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    documents = text_splitter.split_documents(pages)
    vector = utils.store_embeddings(documents=documents)
    crud.store_url(pdf_path, user_id)
  
  response = retrieve_response(user_query, vector)

  return response


@tool
def web_ans(url: str, user_query: str, user_id:int) -> str:
  '''Provides answer by referenced url by extracting the content'''
  url_exists = crud.url_exists(url)
  
  if url_exists:
      try:
        vector = utils.load_database()
        response = retrieve_response(user_query, vector)
        return response
      except Exception as e:
        print(e)
  else:
    try:
      loader = WebBaseLoader(url)
      data = loader.load()
      text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=200)
      documents = text_splitter.split_documents(data)
      vector = utils.store_embeddings(documents=documents)
      print("user_id",user_id)
      user = User.objects.get(id=int(user_id))
      crud.store_url(url, user)
      print(f"vector: {vector} \n")
      response = retrieve_response(user_query, vector)
      return response
    except Exception as e:
       print(e)
         




    
    
# tool to provide responses based on the youtube url or video_id provided by the user
@tool
def yt_ans(video_id: str, user_query: str) -> str:
  """"Provides response based on the transcript of youtube video_id provided. video_id is usually an alphanumeric sequence"""
  
  url_exists = crud.url_exists(video_id)
  
  if url_exists:
      try:
        vector = utils.load_database()
      except Exception as e:
        print(e)
  else:
    transcript_text = get_youtube_transcript(video_id)

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_text(transcript_text)
    documents = text_splitter.create_documents(chunks)
    vector = utils.store_embeddings(documents=documents)

    response = retrieve_response(user_query, vector)

  return response


tools = [pdf_ans, web_ans, yt_ans]

  