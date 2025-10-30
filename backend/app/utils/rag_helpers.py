from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import InMemoryVectorStore
from langchain_core.documents import Document
from langchain.agents import create_agent
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import ChatOllama
from langchain.agents.middleware import dynamic_prompt, ModelRequest

llm = ChatOllama(model="phi4-mini:latest")
embeddings = OllamaEmbeddings(model="nomic-embed-text:latest")
vector_store= InMemoryVectorStore(embeddings)

def load_nested_news_json(json_obj):
    docs = []
    all_stories=json_obj

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
                    "related_symbols": story.get("related_symbols", []),
                    "link": link,
                    "type": story.get("type"),
                    "publisher": publisher,
                    "report_date": date,
                    "title": title
                }
            )
        )
    return docs

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


def add_news_to_vector_store(news):
    docs=load_nested_news_json(news)
    print("loaded nested news")
    splitter=RecursiveCharacterTextSplitter(chunk_size=500,chunk_overlap=150)
    split_docs=splitter.split_documents(docs)
    print("Split Docs")
    vector_store.add_documents(split_docs)
    print("Documents Added to Vector Store")

def initialize_rag_system():
    prompt = (
        "You have access to a tool that retreives context for a stock news"
        "Use the tool and only the tool to help answer user queries"
        "answer in 3 sentences or less and give SHORT answers"
    )

    agent=create_agent(llm,tools=[],system_prompt=prompt, middleware=[prompt_with_context])
    return agent




@dynamic_prompt
def prompt_with_context(request:ModelRequest)->str:
    last_query=request.state["messages"][-1].text 
    retrieved_docs=vector_store.similarity_search(last_query)
    docs_content= "\n\n".join(doc.page_content for doc in retrieved_docs)
    system_message=(
        "You are a helpful assistant who gives information about a stock. Use the following context in your response:"
        f"\n\n{docs_content}"
    )
    return system_message


async def ask_agent(agent,query:str):
    result=agent.invoke(
        {
            "messages":[{"role":"user", "content":query}]
        }
    ) 
    return result
    


    
