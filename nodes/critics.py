from typing import Literal
from pydantic import BaseModel, Field
from state import AgentState
from client import gemini_client,ollama_client



class ReEvaluationModel(BaseModel):
    reasoning:str=Field(
        description="Step-by-step analysis detailing if the legal context contains explicit data to address the query."
    )
    is_relevant:bool=Field(
        description="Set to True ONLY if the clause contains the necessary legal facts, obligations, or metrics to answer the user query."

    )

class HallucinationEvaluation(BaseModel):
    audit_trail:str=Field(
        description="Sentence-by-sentence alignment audit matching draft claims directly to the source text lines."
    )

    error_details: str | None = Field(
        description="Extract the exact phrase or sentence from the draft that failed validation. Leave null if Fully Supported.",
        default=None
    )

    support_status: Literal["Approved", "Refuted"] = Field(
        description="Must be 'Approved' if the draft contains zero external facts. Must be 'Refuted' if ANY detail, number, or deadline is missing from the source context."
    )

def verify_relevance(state:AgentState)->dict:
    query=state["user_query"]
    context = "\n\n".join(state["retrieved_clauses"])

    prompt=f""" Analyze the following legal context against the user query.
    
    [USER QUERY]
    {query}
    
    [RETRIEVED LEGAL CONTEXT]
    {context}
    
    Determine if this text context holds the factual basis to construct an accurate answer.
    """

    evaluation=ollama_client.chat.completions.create(
        model="llama3.1",
        response_model=ReEvaluationModel,
        messages=[
            {"role": "system", "content": "You are an unyielding, literal legal document evaluator."},
            {"role": "user", "content": prompt}
        ]
        )
    print(f"[RELEVANCE DECISION]: Is Relevant = {evaluation.is_relevant}")
    print(f"[RELEVANCE REASONING]: {evaluation.reasoning}")

    relevance_flag: Literal["yes", "no"] = "yes" if evaluation.is_relevant else "no"
    
    return {"is_relevant": relevance_flag}


def audit_generation(state: AgentState) -> dict:
    """
    LangGraph Node: Inspects the generated text response for factual accuracy 
    against the source clauses to catch hidden hallucinations.
    """
    print("\n--- [NODE] EXECUTING HALLUCINATION CRITIC ---")
    
    context = "\n\n".join(state["retrieved_clauses"])
    draft = state["current_draft"]
    
    prompt = f"""
    Perform a strict compliance audit on the generated draft. Cross-reference every 
    sentence against the approved source context.
    
    [APPROVED SOURCE CONTEXT]
    {context}
    
    [GENERATED DRAFT]
    {draft}
    
    Flag any deadlines, dollar amounts, responsibilities, or stipulations in the draft 
    that are not explicitly written in the source context.
    """

    evaluation = ollama_client.chat.completions.create(
        model="llama3.1",  # Utilizing a larger model capacity for rigorous alignment evaluation
        response_model=HallucinationEvaluation,
        messages=[
            {"role": "system", "content": "You are a zero-tolerance legal compliance auditor."},
            {"role": "user", "content": prompt}
        ]
    )
    
    print(f"[AUDIT DECISION]: Status = {evaluation.support_status}")
    print(f"[AUDIT DETAILS]: {evaluation.audit_trail}")
    if evaluation.error_details:
        print(f"[FOUND HALLUCINATION]: {evaluation.error_details}")

    return {
        "audit_status": evaluation.support_status,
        "critique_feedback": evaluation.error_details
    }