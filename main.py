from graph import app
from state import AgentState

def main():
    print("=======================================================")
    print("🤖 INITIATING AUTONOMOUS LEGAL CONTRACT AUDITOR 🤖")
    print("      (Type 'exit' or 'quit' to close the system)      ")
    print("=======================================================\n")
    
    while True:
        # 1. Get input
        user_query = input("\nEnter your legal question: ")
        
        # 2. Clean the input to remove accidental spaces/tabs
        clean_query = user_query.strip()
        
        # 3. Check for exit FIRST (using the cleaned string)
        if clean_query.lower() in ['exit', 'quit']:
            print("\nShutting down the Legal Auditor. Goodbye!")
            break
            
        # 4. Skip if they just hit Enter with no text
        if not clean_query:
            continue

        # --- IMPORTANT: Ensure everything below is aligned exactly here ---
        print("\n⏳ Processing... (Routing through LangGraph State Machine)\n")
        
        initial_state: AgentState = {
            "user_query": clean_query,
            "retrieved_clauses": [],
            "current_draft": "",
            "is_relevant": "no",
            "audit_status": "Refuted",
            "critique_feedback": None,
            "loop_count": 0
        }

        #try:
        final_state = app.invoke(initial_state)
            
        print("\n=======================================================")
        print("✅ VERIFIED OUTPUT")
        print("=======================================================\n")   
        print(final_state.get("current_draft"))
            
        print("\n-------------------------------------------------------")
        print(f"📊 Metrics: {final_state.get('loop_count')} Graph Loops | "
        f"Final Audit: {final_state.get('audit_status')} | "
        f"Context Relevant: {final_state.get('is_relevant')}")
        print("-------------------------------------------------------\n")
            
        #except Exception as e:
            #print(f"\n[CRITICAL ERROR]: Graph execution failed: {e}")

if __name__ == "__main__":
    main()