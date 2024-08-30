import os
from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper
from langchain.agents import initialize_agent, AgentType
from langchain_groq import ChatGroq
from langchain_community.tools.tavily_search.tool import TavilySearchResults
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

# set up API key
api_key=os.getenv("API_KEY_TAVILY") or ""
def tavily_agent_search(query:str):
    
    llm = ChatGroq(api_key= os.getenv("API_KEY_GROQ"), model_name="llama-3.1-70b-versatile", temperature=0)
    search = TavilySearchAPIWrapper(tavily_api_key=api_key)
    tavily_tool = TavilySearchResults(api_wrapper=search)
    agent_chain = initialize_agent(
        [tavily_tool],
        llm,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
    )
    agent_chain.invoke(query)

def tavily_search(query:str):
    tavily_client = TavilyClient(api_key=api_key)
    response = tavily_client.search(query)
    return response
