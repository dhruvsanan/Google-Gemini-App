from dotenv import load_dotenv


import streamlit as st
import os
import google.generativeai as genai
from htmlTemplates import css, bot_template, user_template

genai.configure(api_key=os.getenv("GOOGLE_API _KEY"))

model=genai.GenerativeModel("gemini-pro")


def gemini_response(messages):
    # response = chat.send_message(question,stream= True)
    response = model.generate_content(messages)
    return response
    # return response

def clear_input_box():
    st.experimental_set_query_params(input="")


def main():
    load_dotenv()
    chat = model.start_chat(history=[])
    st.set_page_config(page_title="Gemini Q&A")
    st.header("Gemini Q&A")
    st.write(css, unsafe_allow_html=True)
    input = st.text_input("Input: ",key="input")
    row1 = st.columns(3)
    submit = row1[0].button("Ask the Question")
    clear = row1[1].button("Clear Conversation")
    history = row1[2].button("Show History")

    if clear:
        st.session_state.messages = []
    
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

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if submit:
        with st.spinner("Processing"): 
            # response = chat.send_message(input,stream= True)
            # st.session_state.messages = st.session_state.messages or []
            messages = [
                {'role':'user',
                'parts': [input]}
            ]
            st.session_state.messages.extend(messages)
            response= gemini_response(st.session_state.messages)
            
            # ai_messages = [
            #     {'role':'model',
            #     'parts': [response.text]}
            # ]
            # st.session_state.messages.append(ai_messages)
            # for chunk in response:           
            st.session_state.messages.append({'role':'model',
                'parts':[response.text]})
            # st.session_state.conversation.append((input, response))
            clear_input_box()
            # st.write(response.text)
            # st.session_state.chat
            st.write("Conversation History:")
            # for turn in st.session_state.messages:  # Iterate through the updated messages list
            #     st.write(f"**{turn['role']}:** {turn['parts'][0]}")
            for turn in reversed(st.session_state.messages):
                if turn['role']== "user":
                    st.write(user_template.replace(
                        "{{MSG}}", turn['parts'][0]), unsafe_allow_html=True)
                else:
                    st.write(bot_template.replace(
                        "{{MSG}}", turn['parts'][0]), unsafe_allow_html=True)


if __name__== '__main__':
    main()