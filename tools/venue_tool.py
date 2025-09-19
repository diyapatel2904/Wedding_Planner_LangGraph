import json
from loguru import logger
from langchain.tools import tool

# Configure logger
logger.add("agents.log", rotation="10 MB", retention="7 days", level="INFO")

# Load dataset from JSON
try:
    with open("data/venue.json", "r") as f:
        venues_data = json.load(f)
    logger.info(f"Loaded {len(venues_data)} venues from dataset.")
except Exception as e:
    logger.exception(f"Error loading venues dataset: {e}")
    venues_data = []


@tool("VenueSearch", return_direct=True)
def search_venues(query: str) -> str:
    """
    Search and shortlist venues from the dataset based on city, budget, and style.
    Query example: "Ahmedabad 10 lakh Banquet"
    """
    logger.info(f"search_venues called with query: '{query}'")
    results = []

    try:
        q = query.lower()
        for venue in venues_data:
            if venue["city"].lower() in q:
                if "lakh" in q:
                    try:
                        budget_limit = int(q.split("lakh")[0].split()[-1]) * 100000
                        if venue["budget"] > budget_limit:
                            continue
                    except Exception:
                        logger.warning(f"Budget parsing failed for query: '{q}'")

                results.append(venue)

        if not results:
            logger.warning(f"No venues found for query: '{query}'")
            return "No venues found matching your query."

        formatted = "Here are some venues matching your query:\n"
        for v in results[:3]:
            formatted += (
                f"- {v['name']} ({v['style']}) Capacity: {v['capacity']}"
                f" Budget: ₹{v['budget']/100000:.1f} lakhs Link: {v['link']}\n"
            )

        logger.info(f"search_venues response: {formatted}")
        return formatted

    except Exception as e:
        logger.exception(f"Error in search_venues with query '{query}': {e}")
        return f"Error processing venue search: {e}"

