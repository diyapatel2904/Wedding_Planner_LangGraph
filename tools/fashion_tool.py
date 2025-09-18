import os
import json
from dotenv import load_dotenv
from tavily import TavilyClient
from loguru import logger
from typing import TypedDict


# Setup

logger.add("agents.log", rotation="10 MB", retention="7 days", level="INFO")

# Load environment variables
load_dotenv()

try:
    api_key = os.getenv("TAVILY_API_KEY")
    logger.info("Initializing Tavily client...")
    client = TavilyClient(api_key=api_key)
    logger.info("Tavily client initialized successfully.")
except Exception as e:
    logger.exception(f"Error initializing Tavily client: {e}")
    client = None


# State Definition

class FashionState(TypedDict):
    query: str
    response: str


# Node Function for LangGraph

def fashion_search_node(state: FashionState) -> FashionState:
    """
    Fashion search node for LangGraph.
    Uses Tavily to search fashion-related images and articles.
    Updates the state with formatted results.
    """
    query = state["query"]
    logger.info(f"fashion_search_node called with query: '{query}'")

    try:
        results = client.search(query=query, search_depth="advanced", max_results=2)
        formatted = []
        for r in results["results"]:
            title = r.get("title")
            url = r.get("url")
            formatted.append(f"🔗 [{title}]({url})")   # clickable link

        response = "\n".join(formatted)
        logger.info(f"fashion_search_node response: {response}")
        state["response"] = response
        return state

    except Exception as e:
        logger.exception(f"Error in fashion_search_node with query '{query}': {e}")
        state["response"] = f"Error: {str(e)}"
        return state
