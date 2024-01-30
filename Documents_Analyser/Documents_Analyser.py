import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
import google.generativeai as genai
from htmlTemplates import css, bot_template, user_template
import os

genai.configure(api_key=os.getenv("GOOGLE_API _KEY"))

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
# from langchain.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI

from langchain_community.vectorstores import FAISS
from langchain.text_splitter  import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

import requests
from bs4 import BeautifulSoup

def get_text_from_urls(urls):
    def get_text_from_url(url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        texts = soup.get_text()
        if "403 Forbidden" in texts:
            st.warning( f"You don't have permission to access {url}")
        else:
            return texts
    texts = "" 
    for url in urls.split("\n"): 
        if get_text_from_url(url):
            texts +=(get_text_from_url(url))
    st.write(texts)
    return texts

def get_pdf_text(pdf_docs):
    text=""
    for pdf in pdf_docs:
        pdf_reader= PdfReader(pdf)
        for page in pdf_reader.pages:
            text+= page.extract_text()
    return  text


def get_retriever(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    text = text_splitter.split_text(text)
    embeddings = GoogleGenerativeAIEmbeddings(model = "models/embedding-001")
    vector_store = FAISS.from_texts(text, embedding=embeddings)
    retriever = vector_store.as_retriever()
    return retriever

def get_response(retriever,chat_history,question):

    model = ChatGoogleGenerativeAI(model="gemini-pro", convert_system_message_to_human=True,
                                temperature=0.3)
    prompt = ChatPromptTemplate.from_messages([
    ("system", "{context}\n\n Answer the user's questions based only on the above context and if answer is not available in the above context don't provide the wrong answer, instead say sorry I cannot answer this question."),
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{input}")
    ])
    document_chain = create_stuff_documents_chain(model, prompt)
    conversational_retrieval_chain = create_retrieval_chain(retriever, document_chain)
    response = conversational_retrieval_chain.invoke({
    'chat_history': chat_history,
    "input": question
    })
    return response['answer']

def main():
    load_dotenv()
    st.set_page_config(page_title="Multiple Pdf Analyser Gemini",
                    page_icon='❤️',
                    layout='centered',
                    initial_sidebar_state='collapsed')
    
    st.write(css, unsafe_allow_html=True)

    
    st.title("Chat with multiple PDFs :books:")
    st.header("Upload your document in the sidebar")
    pdf_docs = st.file_uploader("Upload your PDFs here", accept_multiple_files=True)
    urls = st.text_area("Enter the URLs (one per line):")
    question = st.text_input("Ask a Question about your pdf: ",key="input")

    row1 = st.columns(3)
    submit = row1[0].button("Ask the Question")
    clear = row1[1].button("Clear Conversation")

    if clear:
        st.session_state.chat_history = []

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        
    if submit:
        if urls or pdf_docs:
            if urls and pdf_docs:
                docs= get_text_from_urls(urls)
                text = get_pdf_text( pdf_docs)
                text +=docs
            elif urls:
                text= get_text_from_urls(urls)
            else:
                text = get_pdf_text( pdf_docs)
                retriever= get_retriever(text)
                response = get_response(retriever,st.session_state.chat_history,question)
                st.session_state.chat_history = [
                HumanMessage(content=question),
                AIMessage(content=response)
                ]
                st.write(response)

        else:
            st.write("Please provide url of website or upload your docs")

        
if __name__== '__main__':
    main()