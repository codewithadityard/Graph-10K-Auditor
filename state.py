from typing import TypedDict, List, Literal,Optional

class AgentState(TypedDict):
    #The raw input query from the user
    user_query: str

    # Tell wether to go for model genration or web search 
    route_destination: Optional[str]
    
    # The legal contract text clauses pulled by the retriever
    retrieved_clauses: List[str]
    
    # The active text response being crafted by the generator
    current_draft: str
    
    # The grading flag set by the Relevance Critic ("yes" or "no")
    is_relevant: Literal["yes", "no"]
    
    # The grading flag set by the Hallucination Critic
    audit_status: Literal["Fully Supported", "Partially Supported", "Refuted"]
    
    # The exact hallucinated phrase caught by the critic (used to fix loops)
    critique_feedback: str | None
    
    # A counter to prevent infinite loops if a document is completely broken
    loop_count: int
