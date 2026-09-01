import numpy as np
import faiss
from state import AgentState
from injection import DocumentLoader
from Indexing import Indexer
from reranker import DocumentReranker

# 1. Warm-up retrieval assets globally so they persist in memory
print("[SYSTEM INITIALIZATION]: Bootstrapping Core Vector Assets...")
indexer_instance = Indexer(dense_model_name="BAAI/bge-small-en-v1.5")
indexer_instance.load_indexes(save_dir="db/")

reranker_instance = DocumentReranker(model_name="cross-encoder/ms-marco-MiniLM-L-6-v2")

def retrieve_contract_context(state: AgentState) -> dict:
    """
    LangGraph Production Node: Executes a dense bi-encoder vector search, 
    applies cross-encoder re-ranking with dropoff filtering, and populates state.
    """
    print("\n--- [NODE] EXECUTING STRUCTURAL RAG ENGINE ---")
    query = state["user_query"]
    
    try:
        # A. Encode the runtime query vector
        query_vector = indexer_instance.dense_encoder.encode([query], convert_to_numpy=True)
        faiss.normalize_L2(query_vector) # Crucial: Must normalize query to match L2 normalization of index
        
        # B. Raw Vector Retrieval (Extracting Top 10 broad candidates)
        # IndexFlatIP search returns: distances, indices
        _, indices = indexer_instance.faiss_index.search(query_vector, k=10)
        
        # C. Map raw database indices back to full LangChain Document structures
        retrieved_docs = []
        for idx in indices[0]:
            if idx != -1 and idx < len(indexer_instance.documents):
                retrieved_docs.append(indexer_instance.documents[idx])
        
        print(f"[RAG SEARCH]: Vector search matched {len(retrieved_docs)} structural candidate blocks.")
        
        # D. Execute Cross-Encoder Re-Ranking & Factual Dropoff Filtering
        print("[RAG RERANKER]: Running Cross-Encoder scoring matrix...")
        optimized_docs = reranker_instance.rerank(
            query=query,
            documents=retrieved_docs,
            top_k=3,
            score_dropoff=3.0
        )
        
        # E. Extract the processed text strings for the LLM context prompt
        final_context_strings = [doc.page_content for doc in optimized_docs]
        
    except Exception as e:
        print(f"[CRITICAL EXTRACTION FAILURE]: Structural pipeline crash: {e}")
        final_context_strings = []

    # Inject clean structured insights back into LangGraph memory state
    return {
        "retrieved_clauses": final_context_strings,
        "loop_count": state.get("loop_count", 0) + 1
    }