import os
from Indexing import Indexer
from injection import DocumentLoader

def main():
    print("==================================================")
    print("🔨 INITIALIZING VECTOR DATABASE BUILDER")
    print("==================================================\n")
    
    # Define where your PDF is and where the DB should be saved
    pdf_source = "data/jpmorgan_sec_10k_report.pdf"
    database_directory = "db/"
    
    # Safety check
    if not os.path.exists(pdf_source):
        print(f"[ERROR]: Could not find a PDF at {pdf_source}.")
        print("Please make sure you have a 'data' folder with a PDF inside it named 'real_contract.pdf'.")
        return

    print("1. Parsing PDF Text & Tables...")
    loader = DocumentLoader(file_path=pdf_source)
    parsed_documents = loader.loader()
    print(f"   -> Extracted {len(parsed_documents)} elements.")

    print("\n2. Generating Vector Embeddings (This might take a minute)...")
    indexer = Indexer(dense_model_name="BAAI/bge-small-en-v1.5")
    indexer.build_indexes(parsed_documents)

    print("\n3. Saving Database to Disk...")
    indexer.save_indexes(save_dir=database_directory)
    print(f" Success! Your FAISS index is saved in the '{database_directory}' folder.")

if __name__ == "__main__":
    main()