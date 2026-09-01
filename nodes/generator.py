import client
from state import AgentState
from client import OpenAI
import os 
import instructor

gemini_api_key = os.getenv("GEMINI_API_KEY")


def generate_legal_answer(state:AgentState):
    print("\n--- [NODE] EXECUTING RESPONSE GENERATOR ---")
    query=state["user_query"]
    context="\n\n".join(state["retrieved_clauses"])
    feedback=state.get("critique_feedback")

    system_instruction = (
        "You are a precise corporate legal counsel. Answer the user's question "
        "using ONLY the provided source context. Do not make assumptions, do not "
        "extrapolate, and do not introduce outside legal principles or facts. "
        "If the answer cannot be found in the context, state that clearly."
    )

    if feedback:
        print(f"[GENERATOR NOTICE]: Self-correction loop triggered due to hallucination.")
        user_prompt = f"""
        Your previous response failed a strict compliance audit due to a hallucination.
        You must completely rewrite the response, stripping out the unverified details.
        
        [AUDIT CRITIQUE FEEDBACK]:
        {feedback}
        
        [APPROVED SOURCE CONTEXT]:
        {context}
        
        [USER QUESTION]:
        {query}
        
        Rewrite the answer cleanly, ensuring absolutely zero components violate the approved context.
        """
    else:
        print(f"[GENERATOR NOTICE]: Drafting initial response.")
        user_prompt = f"""
        Answer the user question based strictly on the approved context below.
        
        [APPROVED SOURCE CONTEXT]:
        {context}
        
        [USER QUESTION]:
        {query}
        """

    

# 2. Initialize the client using Gemini's OpenAI-compatible base URL
    gemini_client = instructor.from_openai(
        OpenAI(
            api_key=gemini_api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
    )

    # 3. Replace 'ollama_client' and update the model name
    draft = gemini_client.chat.completions.create(
        model="gemini-2.5-flash", # You can also use "gemini-1.5-flash" or "gemini-2.5-pro"
        response_model=str,
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_prompt}
        ]
    )

    print(f"[GENERATOR OUTPUT]: Generated a draft of {len(draft)} characters.")
    return {"current_draft": draft}
