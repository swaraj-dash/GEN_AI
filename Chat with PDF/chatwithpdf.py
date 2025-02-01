import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai
from langchain.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
    return text

def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    return text_splitter.split_text(text)

def get_vector_store(text_chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")

def get_conversational_chain():
    prompt_template = """
    Answer the question as detailed as possible from the provided context. If the answer is not in
    the provided context, just say, 'Answer is not available in the context.' Do not provide incorrect answers.
    
    Context:
    {context}
    
    Question: 
    {question}
    
    Answer:
    """
    model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    return load_qa_chain(model, chain_type="stuff", prompt=prompt)

def user_input(user_question):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    docs = new_db.similarity_search(user_question)
    chain = get_conversational_chain()
    response = chain({"input_documents": docs, "question": user_question}, return_only_outputs=True)
    st.markdown("### 🤖 AI Response:")
    st.write(response["output_text"])

st.set_page_config(page_title="Chat with PDF", layout="wide")
st.markdown("""
    <h1 style='text-align: center;'>📄 Chat with PDF 💁</h1>
    <hr>
""", unsafe_allow_html=True)

st.sidebar.title("📂 Upload PDF Files")
pdf_docs = st.sidebar.file_uploader("Upload PDFs", accept_multiple_files=True)

if st.sidebar.button("📥 Process PDF"):
    with st.spinner("Processing... ⏳"):
        raw_text = get_pdf_text(pdf_docs)
        text_chunks = get_text_chunks(raw_text)
        get_vector_store(text_chunks)
        st.sidebar.success("✅ Processing Completed!")

st.markdown("### 💬 Ask a Question About Your PDF")
user_question = st.text_input("🔍 Type your question here")
if user_question:
    user_input(user_question)
    
st.sidebar.markdown("""
    <h3>ℹ️ Instructions</h3>
    <ul>
        <li>Upload one or multiple PDF files.</li>
        <li>Click 'Process PDF' to analyze the content.</li>
        <li>Type your question in the input box.</li>
        <li>Get AI-powered responses based on the PDF content.</li>
    </ul>
""", unsafe_allow_html=True)
