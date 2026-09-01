from langgraph.graph import StateGraph, START, END
from state import AgentState
from supervisor import route_query
from web_search import web_search,sql_agent
# Import the node functions we wrote
from nodes.retriever import retrieve_contract_context
from nodes.critics import verify_relevance, audit_generation
from nodes.generator import generate_legal_answer

# =====================================================================
# 1. ROUTING LOGIC (CONDITIONAL EDGES)
# =====================================================================

def route_relevance(state: AgentState) -> str:
    """
    Decides where to go after the Relevance Critic runs.
    """
    if state.get("is_relevant") == "yes":
        print("[ROUTER]: Context is relevant. Routing to Generator.")
        return "generator"
    
    print("[ROUTER]: Context is irrelevant. Halting execution.")
    return END

def route_supervision(state:AgentState)->str:
    """Reads the Supervisor's decision and tells LangGraph where to go."""
    return state["route_destination"]



def route_hallucination(state: AgentState) -> str:
    """
    Decides where to go after the Hallucination Critic runs.
    Checks the loop count to prevent infinite API calls.
    """
    # Safety Check: Kill the loop if it fails 3 times
    if state.get("loop_count", 0) >= 3:
        print("[ROUTER]: Maximum correction loops reached. Halting to prevent infinite loop.")
        return END

    # Verification Check
    status = state.get("audit_status")
    
    # THE FIX: Match the exact string from your Pydantic schema! 
    if status == "Approved":
        print("[ROUTER]: Draft passed audit. Finalizing output.")
        return END
    
    # If it is "Refuted", loop backward
    print(f"[ROUTER]: Draft failed audit ({status}). Looping back to Generator.")
    return "generator"


# =====================================================================
# 2. GRAPH ASSEMBLY
# =====================================================================

builder = StateGraph(AgentState)

# Register the nodes

builder.add_node("supervisor",route_query)
builder.add_node("web_search",web_search)
builder.add_node("sql_db",sql_agent)
builder.add_node("retriever", retrieve_contract_context)
builder.add_node("relevance_critic", verify_relevance)
builder.add_node("generator", generate_legal_answer)
builder.add_node("hallucination_critic", audit_generation)

# Define the standard edges
builder.add_edge(START, "supervisor")
# The conditional fork! 
builder.add_conditional_edges("supervisor", route_supervision, {
    "legal_rag": "retriever",  # If legal_rag, go to the retriever
    "web_search": "web_search",
    "sql_db":"sql_db"})
builder.add_edge("retriever", "relevance_critic")

# Define the conditional edges
builder.add_conditional_edges("relevance_critic", route_relevance)

# After generation, we ALWAYS audit it
builder.add_edge("generator", "hallucination_critic")

# After the audit, we branch based on the grade
builder.add_conditional_edges("hallucination_critic", route_hallucination)

# When web_search or sql_db finishes, they exit the loop cleanly
builder.add_edge("web_search", END)
builder.add_edge("sql_db", END)

# Compile the graph into an executable app
app = builder.compile()