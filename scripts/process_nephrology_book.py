"""
Process Comprehensive Clinical Nephrology PDF into chunks and create FAISS vector store
"""
import os
import fitz  # PyMuPDF
import pickle
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from dotenv import load_dotenv

load_dotenv()

def extract_text_from_pdf(pdf_path, max_pages=None):
    """
    Extract text from PDF using PyMuPDF
    max_pages: Limit pages for testing (None = all pages)
    """
    print(f"📖 Opening PDF: {pdf_path}")
    
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    pages_to_process = min(max_pages, total_pages) if max_pages else total_pages
    
    print(f"📄 Total pages: {total_pages}")
    print(f"📄 Processing: {pages_to_process} pages")
    
    texts = []
    for page_num in range(pages_to_process):
        page = doc[page_num]
        text = page.get_text()
        
        # Skip pages with minimal content
        if len(text.strip()) > 100:
            texts.append({
                "text": text,
                "page": page_num + 1,
                "source": os.path.basename(pdf_path)
            })
        
        if (page_num + 1) % 50 == 0:
            print(f"   Processed {page_num + 1}/{pages_to_process} pages...")
    
    doc.close()
    print(f"✅ Extracted text from {len(texts)} pages")
    return texts

def create_chunks(texts, chunk_size=1000, chunk_overlap=200):
    """
    Split texts into chunks for embedding
    """
    print(f"\n🔪 Chunking text (size={chunk_size}, overlap={chunk_overlap})...")
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    
    documents = []
    for item in texts:
        chunks = text_splitter.split_text(item["text"])
        for i, chunk in enumerate(chunks):
            doc = Document(
                page_content=chunk,
                metadata={
                    "page": item["page"],
                    "source": item["source"],
                    "chunk_id": i
                }
            )
            documents.append(doc)
    
    print(f"✅ Created {len(documents)} chunks")
    return documents

def create_faiss_vectorstore(documents, output_dir="data/vectorstore"):
    """
    Create FAISS vector store from documents
    """
    print(f"\n🧬 Creating embeddings and FAISS index...")
    
    # Initialize embeddings
    print("Loading HuggingFace embedding model...")
    embeddings = HuggingFaceEmbeddings(
    model_name=os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"),
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': True}
    )
    print("✅ Embedding model loaded")
    
    # Create FAISS vector store
    vectorstore = FAISS.from_documents(documents, embeddings)
    
    # Save to disk
    os.makedirs(output_dir, exist_ok=True)
    vectorstore.save_local(output_dir)
    
    print(f"✅ FAISS index saved to: {output_dir}")
    print(f"📊 Total vectors: {vectorstore.index.ntotal}")
    
    return vectorstore

def test_vectorstore(vectorstore):
    """
    Test the vector store with a sample query
    """
    print(f"\n🧪 Testing vector store...")
    
    query = "What are the symptoms of chronic kidney disease?"
    results = vectorstore.similarity_search(query, k=3)
    
    print(f"Query: {query}")
    print(f"Top result (page {results[0].metadata['page']}):")
    print(f"   {results[0].page_content[:200]}...")

def main():
    """
    Main processing pipeline
    
    IMPORTANT: Update pdf_path to your actual PDF location
    For testing: Use max_pages=100 to process only first 100 pages
    For production: Set max_pages=None to process entire book
    """
    
    # ⚠️ UPDATE THIS PATH TO YOUR PDF FILE
    pdf_path = "data/comprehensive-clinical-nephrology.pdf"
    
    # For testing: process only first 100 pages (faster)
    # For full: set max_pages=None
    MAX_PAGES = 100  # Change to None for full book
    
    try:
        # Step 1: Extract text from PDF
        texts = extract_text_from_pdf(pdf_path, max_pages=MAX_PAGES)
        
        # Step 2: Create chunks
        documents = create_chunks(texts, chunk_size=1000, chunk_overlap=200)
        
        # Step 3: Create FAISS vector store
        vectorstore = create_faiss_vectorstore(documents)
        
        # Step 4: Test
        test_vectorstore(vectorstore)
        
        print("\n" + "="*50)
        print("✅ SUCCESS! Vector store is ready to use")
        print("="*50)
        print(f"\n📂 Location: data/vectorstore/")
        print(f"📊 Total chunks: {len(documents)}")
        
        if MAX_PAGES:
            print(f"\n⚠️  Note: Processed only first {MAX_PAGES} pages for testing")
            print(f"   Set MAX_PAGES=None to process entire book")
        
    except FileNotFoundError:
        print("\n❌ ERROR: PDF file not found!")
        print(f"   Expected location: {pdf_path}")
        print(f"   Please place your nephrology textbook PDF in the data/ folder")
        print(f"   and update the pdf_path variable in this script")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        raise

if __name__ == "__main__":
    main()