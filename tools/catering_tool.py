import json
from loguru import logger
from langchain.tools import tool

# Configure logger (shared log file)
logger.add("agents.log", rotation="10 MB", retention="7 days", level="INFO")

# Load Zomato Menu Dataset
try:
    logger.info("Loading Zomato dataset from data/zomato.json...")
    with open("data/zomato.json", "r") as f:
        zomato_data = json.load(f)
    logger.info(f"Loaded {len(zomato_data)} menu items from Zomato dataset.")
except Exception as e:
    logger.exception(f"Error loading Zomato dataset: {e}")
    zomato_data = []

# Convert list into lookup dictionary
menu_lookup = {item["item_name"].lower(): item for item in zomato_data}
logger.debug(f"Menu lookup initialized with {len(menu_lookup)} items.")


@tool("CateringSearch", return_direct=True)
def catering_search(query: str) -> str:
    """
    Lookup dish price and calculate catering cost.
    Query format: "dish_name:num_guests"
    Example: "Paneer Butter Masala:200"
    """
    logger.info(f"Received catering search query: {query}")
    try:
        item_name, guests = query.split(":")
        item_name = item_name.strip().lower()
        guests = int(guests.strip())
        logger.debug(f"Parsed item_name='{item_name}', guests={guests}")

        if item_name not in menu_lookup:
            logger.warning(f"Item '{item_name}' not found in menu lookup.")
            return f"Item '{item_name}' not found in Zomato dataset."

        item = menu_lookup[item_name]
        prices = item["prices"]
        total_cost = prices * guests

        response = (f"Item: {item['item_name']} ({item['cuisine']})\n"
                    f"Price per plate: ₹{prices}\n"
                    f"Guests: {guests}\n"
                    f"Total Catering Cost: ₹{total_cost}")

        logger.info(f"Catering search successful. Response: {response}")
        return response

    except Exception as e:
        logger.exception(f"Error processing catering search query '{query}': {e}")
        return f"Error processing query: {e}"
