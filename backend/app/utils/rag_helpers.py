from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import InMemoryVectorStore
from ..core.config import settings
from langchain_google_genai import ChatGoogleGenerativeAI

#langchain init
llm=ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
)
embeddings=GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001", google_api_key=settings.GOOGLE_API_KEY)
vector_store= InMemoryVectorStore(embeddings)



#build a rag chain

#invoke based on the rag chain

# def build_rag_chain(articles):
#     docs=[]

#     for article in articles:
#         for p in article["news"]:
#             text=p["paragraph"]
#             metadata={
#                 "uuid":article["uuid"],

#             }


#plan is 
#1) build rag chain 
#2) ask question (endpoint) maybe takes ticker 
#3) use the rag chain to invoke question that user asks and give answer
#4) return the answer to the user 