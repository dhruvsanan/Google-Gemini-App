import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GOOGLE_API _KEY"))

from htmlTemplates import css, bot_template, user_template

import textwrap

model=genai.GenerativeModel("gemini-pro")
def make_query_prompt(query):
  prompt = textwrap.dedent("""you are a teaching expert with high in compansioness and are willing to try anything and everything and have a unique style of explaining things.\
  explain the query like you are explaining to a five years old! \
            Be sure to respond in a complete sentence, being comprehensive, including all relevant background information. \
            be sure to break down complicated concepts and \
            strike a friendly and converstional tone. \
            be sure to have a vocabulary and examples like a five year old\
  QUESTION: '{query}'

    ANSWER: 
  """).format(query=query)

  return prompt


def main():
    load_dotenv()
    st.set_page_config(page_title="Explain Like A Five Year Old using Gemini",
                    page_icon='❤️',
                    layout='centered',
                    initial_sidebar_state='collapsed')
    
    
    st.title("Simplify Difficult Topics 📚")
    st.write(css, unsafe_allow_html=True)
    if "messages" not in st.session_state:
        st.session_state.messages = []

    input = st.text_input("What topic do you want to know more about?",key="input")
    row1 = st.columns(3)
    submit = row1[0].button("Explain Me")
    clear = row1[1].button("Clear Conversation")
    history = row1[2].button("Show History")

    if history:
        if st.session_state.messages:
            st.write("Conversation History:")
            for turn in reversed(st.session_state.messages):
                if turn['role']== "user":
                    st.write(user_template.replace(
                        "{{MSG}}", turn['parts'][0]), unsafe_allow_html=True)
                else:
                    st.write(bot_template.replace(
                        "{{MSG}}", turn['parts'][0]), unsafe_allow_html=True)
        else:
            st.write( "No conversation history yet")
            
    if clear:
        st.session_state.messages = []

    if submit:
        if input:
            with st.spinner("Processing"): 
                # response = chat.send_message(input,stream= True)
                # st.session_state.messages = st.session_state.messages or []
                messages = [
                    {'role':'user',
                    'parts': [input]}
                ]
                st.write(user_template.replace(
                        "{{MSG}}", input), unsafe_allow_html=True)
                st.session_state.messages.extend(messages)
                # response= model.generate_content(st.session_state.messages)
                # st.write(st.session_state.messages)
                prompt=""
                for i, turn in enumerate(reversed(st.session_state.messages), 1):
                    if i%2 == 1:
                        prompt = turn['parts'][0] + ". " +prompt
                final_prompt = make_query_prompt(prompt)
                response = model.generate_content(final_prompt)
                st.session_state.messages.append({'role':'model',
                    'parts':[response.text]})
                st.write(bot_template.replace(
                        "{{MSG}}", response.text), unsafe_allow_html=True)
                # clear_input_box()
                st.warning('If you do not get desired response, try to clear conversation', icon="⚠️")

if __name__== '__main__':
    main()
