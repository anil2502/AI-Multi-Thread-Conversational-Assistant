
from dotenv import load_dotenv
load_dotenv()

from langchain_core.tools import tool

from langchain_pinecone import PineconeVectorStore
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

embedding_model = OpenAIEmbeddings(model= "text-embedding-3-small")

llm = ChatOpenAI()

index_name = "dummyindex"


@tool
async def rag_tool(user_query: str) -> dict :
    """
    This tool answers questions about the financial education concepts, philosophies, and lessons presented in Rich Dad Poor Dad by Robert T. Kiyosaki.

    Extract the user's complete, verbatim question or intent as a clean string. Preserve all relevant keywords, names, and context from the message. Remove filler words (e.g. "can you", "please", "hey") but keep the full meaning intact. Pass the result as the user_query parameter to the tool.

    Do NOT use this tool for:-
        — General financial advice not grounded in the book's content
        — Questions about other books by Kiyosaki not covered in Rich Dad Poor Dad (e.g., Cashflow Quadrant as a standalone book, Rich Dad's Guide to Investing)
        — Legal, tax, or investment advice specific to the user's personal situation
        — Real-time market data or current financial news


    """
    # NOTE:- I have already stored my data into the pinecone that's why here i am Just Retriving the Data.

    # first connect to the Pinecone Index
    vectorStore = PineconeVectorStore(
        index_name = index_name,
        embedding = embedding_model
    )

    results = vectorStore.similarity_search(user_query)
    context = [document.page_content for document in results]
    metadata = [document.metadata for document in results]

    return {
        "user_query": user_query,
        "context": context,
        "tool_name": "rag_tool"
    }