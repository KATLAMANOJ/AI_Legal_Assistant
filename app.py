import streamlit as st
import os
import shutil
from dotenv import load_dotenv

from loaders.data_loader import load_documents
from utils.text_splitter import split_documents
from embeddings.embedding_model import load_embedding_model
from vectordb.vector_store import create_vector_store
from search.search_engine import search_documents
from chains.rag_chain import create_rag_chain

# Setup page configurations
st.set_page_config(
    page_title="AI Legal Assistant",
    page_icon="⚖️",
    layout="wide"
)

# Custom premium styling
st.markdown("""
    <style>
    /* Styling for Streamlit app */
    .stApp {
        background-color: #0f172a;
        color: #f8fafc;
    }
    /* Title text gradient */
    .main-title {
        background: linear-gradient(135deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 2.8rem;
        margin-bottom: 0.2rem;
    }
    .subtitle-text {
        font-size: 1.1rem;
        color: #94a3b8;
        margin-bottom: 2rem;
    }
    /* Accent borders and widgets */
    div[data-testid="stSidebar"] {
        background-color: #1e293b;
        border-right: 1px solid #334155;
    }
    /* Card design for details */
    .context-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1rem;
    }
    /* Dynamic Hover/Status Styles */
    .success-badge {
        background-color: #064e3b;
        color: #34d399;
        border: 1px solid #059669;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Main Title and Subheader
st.markdown('<h1 class="main-title">⚖️ AI Legal Assistant</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle-text">Upload legal documents, enter your API key, and extract answers or insights instantly using AI.</p>', unsafe_allow_html=True)

# Initialize Session State
if "processed" not in st.session_state:
    st.session_state["processed"] = False
if "processed_files" not in st.session_state:
    st.session_state["processed_files"] = []
if "num_chunks" not in st.session_state:
    st.session_state["num_chunks"] = 0

TEMP_DIR = "temp_data"

def save_uploaded_files(uploaded_files):
    if os.path.exists(TEMP_DIR):
        try:
            shutil.rmtree(TEMP_DIR)
        except Exception:
            for f in os.listdir(TEMP_DIR):
                try:
                    os.remove(os.path.join(TEMP_DIR, f))
                except Exception:
                    pass
    os.makedirs(TEMP_DIR, exist_ok=True)
    
    saved_paths = []
    for uploaded_file in uploaded_files:
        file_path = os.path.join(TEMP_DIR, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        saved_paths.append(file_path)
    return saved_paths

# Sidebar Layout
with st.sidebar:
    st.markdown('<h2 style="color: #38bdf8; font-size: 1.5rem; margin-top: 0;">⚙️ Document Processing</h2>', unsafe_allow_html=True)
    st.write("Provide your Google Gemini API Key and upload the PDF documents to analyze.")
    
    # 1. API Key Input
    google_api_key = st.text_input(
        "Google API Key", 
        type="password", 
        placeholder="AIzaSy...", 
        help="Your key is processed locally and never stored persistently on our servers."
    )
    
    st.write("---")
    
    # 2. PDF Files Uploader
    uploaded_files = st.file_uploader(
        "Upload PDF Documents", 
        type=["pdf"], 
        accept_multiple_files=True,
        help="Select one or more PDF contracts, agreements, or legal files."
    )
    
    st.write("---")
    
    # 3. Process Button
    process_button = st.button("Process Legal Documents", use_container_width=True)
    
    if process_button:
        if not google_api_key:
            st.error("🔑 Google API Key is required to run the AI assistant.")
        elif not uploaded_files:
            st.error("📄 Please upload at least one PDF document first.")
        else:
            with st.spinner("Saving uploaded files..."):
                save_uploaded_files(uploaded_files)
                
            with st.spinner("Extracting content from documents..."):
                documents = load_documents(TEMP_DIR)
                
            if not documents:
                st.error("⚠️ No text content could be extracted from the uploaded PDF(s).")
            else:
                with st.spinner("Splitting documents into chunks..."):
                    chunks = split_documents(documents)
                    st.session_state["num_chunks"] = len(chunks)
        
                with st.spinner("Loading embedding model..."):
                    embedding_model = load_embedding_model()
        
                with st.spinner("Creating vector database..."):
                    create_vector_store(chunks, embedding_model)
                    from search.search_engine import reload_vector_db
                    reload_vector_db()
                
                st.session_state["processed"] = True
                st.session_state["processed_files"] = [f.name for f in uploaded_files]
                st.success("🎉 Documents processed successfully!")

# Main Section - UI Routing & Interaction
if st.session_state["processed"]:
    st.markdown(
        f'<div class="success-badge">✅ Currently Active: Loaded {len(st.session_state["processed_files"])} document(s) ({st.session_state["num_chunks"]} chunks)</div>', 
        unsafe_allow_html=True
    )
    
    # Display processed files list inside an expander
    with st.expander("Show loaded files"):
        for f in st.session_state["processed_files"]:
            st.markdown(f"- `{f}`")

    st.write("---")
    st.subheader("💡 Ask Questions or Explore FAQs")
    
    predefined_questions = [
        "What are the main obligations under this contract?",
        "What is the termination clause and notice period?",
        "Are there any confidentiality or non-compete clauses?",
        "What is the governing law and jurisdiction of this agreement?",
        "What are the liability limits and indemnification terms?"
    ]
    
    selected_faq = st.selectbox(
        "Select a predefined question to populate the query field:",
        options=predefined_questions,
        index=None,
        placeholder="Choose a question..."
    )
    
    user_question = st.text_input(
        "Ask Legal Question",
        value=selected_faq if selected_faq else "",
        placeholder="Type your question or choose a predefined one above..."
    )
    
    if user_question:
        if not google_api_key:
            st.error("🔑 Google API Key is missing. Please enter it in the sidebar.")
        else:
            with st.spinner("Searching relevant legal context..."):
                docs = search_documents(user_question)
        
            if len(docs) == 0:
                st.error("No vector database matches found. Try processing the documents again.")
            else:
                # Pass the user's API Key dynamically to the RAG chain
                chain = create_rag_chain(google_api_key=google_api_key)
                context = "\n\n".join(doc.page_content for doc in docs)
        
                with st.spinner("Generating answer..."):
                    try:
                        response = chain.invoke({
                            "context": context,
                            "question": user_question
                        })
                        
                        st.markdown('<div class="context-card">', unsafe_allow_html=True)
                        st.subheader("Answer")
                        st.write(response)
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        with st.expander("Show Relevant Legal Context Chunks"):
                            for i, doc in enumerate(docs):
                                st.markdown(f"**Chunk {i+1}**")
                                st.info(doc.page_content)
                    except Exception as e:
                        st.error(f"Failed to generate answer. Please verify your Google API Key. Error: {str(e)}")
else:
    # State when no files are processed yet
    st.info("👈 Please enter your Google API Key, upload one or more legal PDF files in the sidebar, and click 'Process Legal Documents' to get started.")
    
    # Beautiful mockup description of what the assistant can do
    st.markdown("""
    <div style="background-color: #1e293b; padding: 2rem; border-radius: 12px; border: 1px solid #334155;">
        <h3 style="color: #38bdf8; margin-top: 0;">What you can do with AI Legal Assistant:</h3>
        <ul style="line-height: 1.6;">
            <li><strong>Analyze Contracts:</strong> Upload lease agreements, employment contracts, NDAs, etc.</li>
            <li><strong>Perform Similarity Search:</strong> Instantly retrieve the most relevant sections of your documents matching your questions.</li>
            <li><strong>Automate FAQ Retrieval:</strong> Quickly run predefined queries on compliance obligations, governing laws, and termination details.</li>
            <li><strong>Keep Data Local & Safe:</strong> The document index is saved locally, and your API key is only shared directly with Google Gemini endpoints.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)