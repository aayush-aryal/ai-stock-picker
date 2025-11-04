from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import InMemoryVectorStore
from langchain_core.documents import Document
from langchain.agents import create_agent
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import ChatOllama
from langchain.agents.middleware import dynamic_prompt, ModelRequest
from langchain_classic.tools.retriever import create_retriever_tool
from langchain_chroma import Chroma
from dataclasses import dataclass
from typing import Optional


llm = ChatOllama(model="gemma3:latest")
embeddings = OllamaEmbeddings(model="nomic-embed-text:latest")

#initialize two vector stores 
#one for news and one for call statement
news_vector_store= Chroma(
    collection_name="news_vector_store",
    embedding_function=embeddings,
    persist_directory="../chroma_db"
)
earning_call_statement_vector_store= Chroma(
    collection_name="earnings_call_vector_store",
    embedding_function=embeddings,
    persist_directory="../chroma_db"
)


@dataclass
class Context:
    source:str
    ticker:str
    quarter:Optional[str]=None 
    year:Optional[str]=None



#meta datafiltering soon

def load_nested_news_json(json_obj,ticker):
    docs = []
    all_stories=json_obj
    print("ticker", ticker)
    for story in all_stories:
        title = story.get("title", "")
        publisher = story.get("publisher", "")
        date = story.get("report_date", "")
        paragraphs = story.get("news", [])
        link = story.get("link", "")
        uuid = story.get("uuid", "")

        # Combine all paragraph text + highlights into one document
        content = f"Title: {title}\nPublisher: {publisher}\nDate: {date}\nLink: {link}\n\n"

        for section in paragraphs:
            highlight = section.get("highlight", "")
            paragraph = section.get("paragraph", "")
            if highlight:
                content += f"Summary: {highlight}\n"
            content += paragraph + "\n\n"

        # Create Document
        docs.append(
            Document(
                page_content=content.strip(),
                metadata={
                    "uuid": uuid,
                    "link": link,
                    "type": story.get("type"),
                    "publisher": publisher,
                    "report_date": date,
                    "title": title,
                    "ticker":ticker
                }
            )
        )
    return docs

def load_financial_call_statement(statement,year,quarter,ticker):
    content=""
    for paragraph in statement:
        print(paragraph)
        content+=f"Speaker: {paragraph['speaker']} Content{paragraph['content']} \n\n"
    doc=Document(
        page_content=content.strip(),
        metadata={
            "ticker":ticker,
            "year":str(year),
            "quarter":str(quarter)
        }
    )
    print(doc.metadata)
    return doc

# Construct a tool for retrieving context
# @tool(response_format="content_and_artifact")
# def retrieve_context(query: str):
#     """Retrieve information to help answer a query."""
#     retrieved_docs = vector_store.similarity_search(query, k=2)
#     serialized = "\n\n".join(
#         (f"Source: {doc.metadata}\nContent: {doc.page_content}")
#         for doc in retrieved_docs
#     )
#     return serialized, retrieved_docs



#instead of model calling and using tool whenever it feels like it 
#change the flow to retreive data first and then the model use it
#faster for simpler flows 



def add_news_to_vector_store(news:str,ticker_name:str):
    docs=load_nested_news_json(news,ticker_name)
    print("loaded nested news")
    splitter=RecursiveCharacterTextSplitter(chunk_size=500,chunk_overlap=150)
    split_docs=splitter.split_documents(docs)
    print("Split Docs")
    news_vector_store.add_documents(split_docs)
    print("Documents Added to Vector Store")

def add_earning_call_to_vector_store(earning_call,year,quarter,ticker):
    doc=load_financial_call_statement(earning_call,year,quarter,ticker)
    splitter=RecursiveCharacterTextSplitter(chunk_size=750,chunk_overlap=250)
    split_docs=splitter.split_documents([doc])
    print("Split Docs")
    earning_call_statement_vector_store.add_documents(split_docs)
    print("Documents Added to Vector Store")

def initialize_rag_system():
    prompt = (
        "You have access to a tool that retreives context for a stock news"
        "You have access to another tool that retreives context for financial earning call statements"
        "Use the right tool based on the user query"
        "Use the tools and only the tools to help answer user queries"
        "answer in 3 sentences or less with all accurate information with full context but in short"
        "only answer what is asked ONLY based on provided context"
        "quote the section or part of the context used to answer the question"
    )

    agent=create_agent(llm,tools=[],system_prompt=prompt, middleware=[prompt_with_context],context_schema=Context) # type: ignore
    return agent


@dynamic_prompt
def prompt_with_context(request:ModelRequest)->str:
    last_query=request.state["messages"][-1].text 

    source=request.runtime.context.source # type: ignore
    ticker=request.runtime.context.ticker # type: ignore
    if source=="news":
        retrieved_docs=news_vector_store.similarity_search(last_query,k=3, filter={"ticker":ticker}) 
        print("Esto",retrieved_docs)
    elif source=="earnings_call":
        year=request.runtime.context.year  # type: ignore
        quarter=request.runtime.context.quarter # type: ignore
        print(type(year),type(quarter))
        retrieved_docs=earning_call_statement_vector_store.similarity_search(last_query,k=3,filter={"$and":[
            {"ticker":ticker},{"year":year},{"quarter":quarter}
        ]}) # type: ignore
        print(retrieved_docs)
    else:
        retrieved_docs=[]
    docs_content= "\n\n".join(doc.page_content for doc in retrieved_docs)
    system_message=(
        "You are a helpful assistant who gives information about a stock. Use the following context and ONLY THE CONTEXT in your response:"
        f"\n\n{docs_content}"
    )
    return system_message


async def ask_agent(agent,query:str,context:Context):
    result = agent.invoke(
    {"messages": [{"role": "user", "content": query}]},
    context=context)
    return result
    
