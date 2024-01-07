import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
import google.generativeai as genai
from htmlTemplates import css, bot_template, user_template
import os

genai.configure(api_key=os.getenv("GOOGLE_API _KEY"))



from langchain.text_splitter import CharacterTextSplitter
from htmlTemplates import css, bot_template, user_template
import pandas as pd
import numpy as np
import textwrap

model = 'models/embedding-001'

def get_pf_text(pdf_docs):
    text=[]
    for pdf in pdf_docs:
        doc=""
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            doc += page.extract_text()
        text.append(doc)
    return text


def get_text_chunks(raw_text):
    text_splitter= CharacterTextSplitter(
        separator="\n",
        chunk_size=1000, 
        chunk_overlap=200, 
        length_function = len)
    text_chunks=text_splitter.split_text(raw_text)
    return text_chunks


def text_to_df(raw_text):
    df = pd.DataFrame(raw_text)
    df.columns = ['Text']
    embeddings=genai.embed_content(model=model,
                             content=raw_text,
                             task_type="retrieval_document")["embedding"]
    df['Embeddings'] = embeddings
    return df


def find_best_passage(query, dataframe):
  """
  Compute the distances between the query and each document in the dataframe
  using the dot product.
  """
  query_embedding = genai.embed_content(model=model,
                                        content=query,
                                        task_type="retrieval_query")
  dot_products = np.dot(np.stack(dataframe['Embeddings']), query_embedding["embedding"])
  idx = np.argmax(dot_products)
  return dataframe.iloc[idx]['Text'] # Return text from index with max value

def make_prompt(query, relevant_passage):
  escaped = relevant_passage.replace("'", "").replace('"', "").replace("\n", " ")
  prompt = textwrap.dedent("""You are a helpful and informative bot that answers questions using text from the reference passage included below. \
  Be sure to respond in a complete sentence, being comprehensive, including all relevant background information. \
  However, you are talking to a non-technical audience, so be sure to break down complicated concepts and \
  strike a friendly and converstional tone. \
  If the passage is irrelevant to the answer, you may ignore it.
  QUESTION: '{query}'
  PASSAGE: '{relevant_passage}'

    ANSWER:
  """).format(query=query, relevant_passage=escaped)

  return prompt

def main():
    load_dotenv()
    st.set_page_config(page_title="Multiple Pdf Analyser Gemini",
                    page_icon='❤️',
                    layout='centered',
                    initial_sidebar_state='collapsed')
    
    st.write(css, unsafe_allow_html=True)

    if "df" not in st.session_state:
        st.session_state.df = None

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None
    
    st.header("Chat with multiple PDFs :books:")

    input = st.text_input("Ask a Question about your pdf: ",key="input")
    submit = st.button("Ask the Question")
    clear= st.button("clear conversation")
    if clear:
        st.session_state.messages = []

    if "messages" not in st.session_state:
        st.session_state.messages = []

    with st.sidebar:
        st.subheader("Your Documents:")
        pdf_docs = st.file_uploader("Upload your PDFs here", accept_multiple_files=True)
        if st.button("Upload"):
            with st.spinner("Processing"): 
                # get pdf text
                raw_text= get_pf_text(pdf_docs)
                
                # get the text chunks
                # text_chunks= get_text_chunks(raw_text)
                # st.write(text_chunks)
                st.write(raw_text)
                # create vector store
                st.session_state.df = text_to_df(raw_text)
                st.write(st.session_state.df)
                #docs = vectorstore.similarity_search(text_input)
                # create conversation gain
                # st.session_state.conversation = get_conversation_chain(vectorstore)

    if submit:
        with st.spinner("Processing"): 
            # response = chat.send_message(input,stream= True)
            # st.session_state.messages = st.session_state.messages or []
            passage = find_best_passage(input, st.session_state.df)
            prompt = make_prompt(input, passage)
            text_model = genai.GenerativeModel('gemini-pro')
            answer = text_model.generate_content(prompt)
            messages = [
                {'role':'user',
                'parts': [input]}
            ]
            st.session_state.messages.extend(messages)            
            # ai_messages = [
            #     {'role':'model',
            #     'parts': [response.text]}
            # ]
            # st.session_state.messages.append(ai_messages)
            # for chunk in response:           
            st.session_state.messages.append({'role':'model',
                'parts':[answer.text]})
            # st.session_state.conversation.append((input, response))
            st.subheader("The Response is ")
            # st.write(response.text)
            # st.session_state.chat
            st.write("Conversation History:")
            # for turn in st.session_state.messages:  # Iterate through the updated messages list
            #     st.write(f"**{turn['role']}:** {turn['parts'][0]}")
            for turn in st.session_state.messages:
                if turn['role']== "user":
                    st.write(user_template.replace(
                        "{{MSG}}", turn['parts'][0]), unsafe_allow_html=True)
                else:
                    st.write(bot_template.replace(
                        "{{MSG}}", turn['parts'][0]), unsafe_allow_html=True)


if __name__== '__main__':
    main()

# src= https://colab.research.google.com/github/google/generative-ai-docs/blob/main/site/en/examples/doc_search_emb.ipynb#scrollTo=J76TNa3QDwCc
# src= https://colab.research.google.com/github/google/generative-ai-docs/blob/main/site/en/tutorials/python_quickstart.ipynb?authuser=0#scrollTo=QvvWFy08e5c5
# src= https://ai.google.dev/docs/semantic_retriever
# src= https://ai.google.dev/examples?keywords=prompt