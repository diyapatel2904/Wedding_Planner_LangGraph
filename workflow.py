from typing import TypedDict
from langgraph.graph import StateGraph, END
from tools.fashion_tool import fashion_search_node


# 1. Define State

class WeddingState(TypedDict):
    query: str
    intent: str     # What kind of request it is (fashion, venue, etc.)
    response: str   # The agent’s answer
    memory: list  # you can store past conversations here if needed


# 2. Router Node (Intent Classifier)

def classify_intent(state: WeddingState) -> WeddingState:
    query = state["query"]

    # 👉 Replace this with an LLM classifier later if you want
    if "venue" in query.lower():
        state["intent"] = "venue"
    elif "fashion" in query.lower():
        state["intent"] = "fashion"
    elif "catering" in query.lower():
        state["intent"] = "catering"
    else:
        state["intent"] = "general"

    return state

# 3. Agent Nodes
# Nodes = functions that take the state, do something, and return the updated state.

def fashion_agent(state: WeddingState) -> WeddingState:
    # Wrap your fashion agent executor here
    state["response"] = f"👗 Fashion Agent: Found outfits for '{state['query']}'"
    return state

def venue_agent(state: WeddingState) -> WeddingState:
    state["response"] = f"🏛️ Venue Agent: Suggested venues for '{state['query']}'"
    return state

def catering_agent(state: WeddingState) -> WeddingState:
    state["response"] = f"🍽️ Catering Agent: Menu options for '{state['query']}'"
    return state

def general_agent(state: WeddingState) -> WeddingState:
    state["response"] = f"💡 General Agent: Answer for '{state['query']}'"
    return state



# 4. Build Graph

def build_workflow():
    graph = StateGraph(WeddingState)

    # Add nodes
    graph.add_node("router", classify_intent)
    graph.add_node("fashion", fashion_search_node)
    graph.add_node("venue", venue_agent)
    graph.add_node("catering", catering_agent)
    graph.add_node("general", general_agent)

    # Set entry point
    graph.set_entry_point("router")

    # Conditional edges from router
    graph.add_conditional_edges(
        "router",
        lambda state: state["intent"],
        {
            "fashion": "fashion",
            "venue": "venue",
            "catering": "catering",
            "general": "general",
        }
    )

    # All agents go to END
    graph.add_edge("fashion", END)
    graph.add_edge("venue", END)
    graph.add_edge("catering", END)
    graph.add_edge("general", END)

    return graph.compile()

# 5. Run Example

if __name__ == "__main__":
    app = build_workflow()

    # Example queries
    queries = [
        "Suggest some wedding outfits",
        "Find me a banquet hall in Ahmedabad",
        "What catering options do you suggest?",
        "Tell me about wedding traditions"
    ]

    for q in queries:
        state = {"query": q, "intent": "", "response": "", "memory": []}
        result = app.invoke(state)
        print(f"User: {q}")
        print(f"Bot: {result['response']}")
        print("-" * 50)
       