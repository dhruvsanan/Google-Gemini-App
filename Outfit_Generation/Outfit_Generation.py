import replicate
import textwrap
from htmlTemplates import css, bot_template, user_template
from stqdm import stqdm
from time import sleep
import json
import requests
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])


model = genai.GenerativeModel("gemini-pro")

REPLICATE_API_TOKEN = st.secrets["REPLICATE_API_TOKEN"]


def mistral(prompt):
    output = replicate.run(
        "mistralai/mixtral-8x7b-instruct-v0.1:cf18decbf51c27fed6bbdc3492312c1c903222a56e3fe9ca02d6cbe5198afc10",
        input={
            "top_k": 50,
            "top_p": 0.9,
            "prompt": prompt,
            "temperature": 0.6,
            "max_new_tokens": 512,
            "prompt_template": "<s>[INST] {prompt} [/INST]"
        }
    )
    text = ""
    for line in output:
        text += line
    return (text)


def google_raw_response(prompt):
    response = model.generate_content(prompt, safety_settings=[
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_NONE",
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_NONE",
        }, {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_NONE",
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS",
            "threshold": "BLOCK_NONE",
        }
    ]
    )
    return (response)


def google_response(prompt):
    response = model.generate_content(prompt,
                                      generation_config=genai.types.GenerationConfig(
                                          temperature=1.0))
    return (response)


def realvisxl_request(prompt):
    response = replicate.run(
        "lucataco/realvisxl-v2.0:7d6a2f9c4754477b12c14ed2a58f89bb85128edcdd581d24ce58b6926029de08",
        input={
            "width": 1024,
            "height": 1024,
            "prompt": prompt,
            "scheduler": "DPMSolverMultistep",
            "lora_scale": 0.6,
            "num_outputs": 1,
            "guidance_scale": 7,
            "apply_watermark": True,
            # "negative_prompt": "(deformed iris, deformed pupils, semi-realistic, cgi, 3d, render, sketch, cartoon, drawing, anime:1.4), text, close up, cropped, out of frame, worst quality, low quality, jpeg artifacts, ugly, duplicate, morbid, mutilated, extra fingers, mutated hands, poorly drawn hands, poorly drawn face, mutation, deformed, blurry, dehydrated, bad anatomy, bad proportions, extra limbs, cloned face, disfigured, gross proportions, malformed limbs, missing arms, missing legs, extra arms, extra legs, fused fingers, too many fingers, long neck,",
            "negative_prompt": "deformed iris, deformed pupils, semi-realistic, cgi, 3d, render, sketch, cartoon, drawing, text, close up, cropped, out of frame, worst quality, low quality, jpeg artifacts, ugly, duplicate, morbid, mutilated, extra fingers, mutated hands, poorly drawn hands, poorly drawn face, mutation, deformed, blurry, dehydrated, bad anatomy, bad proportions, extra limbs, cloned face, disfigured, gross proportions, malformed limbs, missing arms, missing legs, extra arms, extra legs, fused fingers, too many fingers, long neck",
            "prompt_strength": 0.8,
            "num_inference_steps": 40,
            "disable_safety_checker": True
        }
    )
    return (response)


def stable_diffusion_request(prompt, num_output):
    response = replicate.run(
        "stability-ai/stable-diffusion:ac732df83cea7fff18b8472768c88ad041fa750ff7682a21affe81863cbe77e4",
        input={
            "width": 1024,
            "height": 1024,
            "prompt": prompt,
            "scheduler": "DPMSolverMultistep",
            "lora_scale": 0.6,
            "num_outputs": num_output,
            "guidance_scale": 7,
            "apply_watermark": True,
            "negative_prompt": "deformed iris, deformed pupils, semi-realistic, cgi, 3d, render, sketch, cartoon, drawing, text, close up, cropped, out of frame, worst quality, low quality, jpeg artifacts, ugly, duplicate, morbid, mutilated, extra fingers, mutated hands, poorly drawn hands, poorly drawn face, mutation, deformed, blurry, dehydrated, bad anatomy, bad proportions, extra limbs, cloned face, disfigured, gross proportions, malformed limbs, missing arms, missing legs, extra arms, extra legs, fused fingers, too many fingers, long neck",
            "prompt_strength": 0.8,
            "num_inference_steps": 40,
            "disable_safety_checker": True
        }
    )
    return (response)


def stable_request(prompt, no_of_images):

    url = "https://modelslab.com/api/v6/images/text2img"

    payload = json.dumps({
        "key": "7IP8mVT61ZNusPjOwLAWyLGca8OBjJD7GowNJVnUDubyTAmKbNr8E2VUVEWP",
        "model_id": "realvisxl-v30-turbo",
        "prompt": prompt,
        "negative_prompt": "deformed iris, deformed pupils, semi-realistic, cgi, 3d, render, sketch, cartoon, drawing, text, close up, cropped, out of frame, worst quality, low quality, jpeg artifacts, ugly, duplicate, morbid, mutilated, extra fingers, mutated hands, poorly drawn hands, poorly drawn face, mutation, deformed, blurry, dehydrated, bad anatomy, bad proportions, extra limbs, cloned face, disfigured, gross proportions, malformed limbs, missing arms, missing legs, extra arms, extra legs, fused fingers, too many fingers, long neck, anime",
        "width": "512",
        "height": "512",
        "samples": no_of_images,
        "num_inference_steps": "30",
        "safety_checker": "no",
        "enhance_prompt": "yes",
        "seed": None,
        "guidance_scale": 7.5,
        "multi_lingual": "no",
        "panorama": "no",
        "self_attention": "no",
        "upscale": "no",
        "embeddings_model": None,
        "lora_model": None,
        "tomesd": "yes",
        "use_karras_sigmas": "yes",
        "vae": None,
        "lora_strength": None,
        "scheduler": "UniPCMultistepScheduler",
        "webhook": None,
        "track_id": None
    })

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    return (response.text)


def make_outfit_prompt(query, gender):
    prompt = textwrap.dedent("""you are a fashion expert with high in openness and are willing to try anything and everything and have a unique sense of design understanding modern trends.\
  give 1 detailed outfit suggestions about {gender} for : \
            outfit \
            for each one suggest appropriate footwear accessories. \

            give output like this: \
            Sure here's your outfit suggestion \
            Title : Traditional Elegance \
            Outfit: Emerald green silk saree with subtle gold embroidery, paired with a matching embellished blouse. \
            Footwear: Gold-toned embellished juttis. \
            Accessories: Delicate gold necklace, thin bangles, small pearl studs, and a simple emerald green potli bag. \

            describe only the outfits, dont type anything else like sure here are outfits \
  QUESTION: '{query}'

    ANSWER: sure here are outfits
  """).format(query=query, gender=gender)

    return prompt


def make_image_prompt(query):
    prompt = textwrap.dedent("""Craft fashion image descriptions for user input, enhancing appeal. Given attire details, generate aesthetic vivid model and setting depiction in 100 words, boosting allure for potential buyers.

                example input : Outfit: Peach-colored lehenga choli with floral embroidery, paired with a matching net dupatta.
                 Footwear: Beige embroidered mojris.
                Accessories: Pearl drop earrings, a delicate gold waist belt, and a peach-colored potli bag with gold accents.

                example output : Elegance personified, our model graces the scene in a resplendent peach-hued lehenga choli, a canvas of delicate floral embroidery that tells a story of craftsmanship. 
                The matching net dupatta drapes like a whisper, adding an ethereal touch. Her feet adorned with beige embroidered mojris, each step is a dance of comfort and style. 
                The ensemble is not complete without the pearl drop earrings, their luster echoing her grace. A delicate gold waist belt cinches the look, a gleaming homage to tradition. To hold secrets and dreams, 
                she carries a peach potli bag, its gold accents glinting like the promises of a magical evening. \
  QUESTION: '{query}'

    ANSWER:
  """).format(query=query)

    return prompt


def main():
    load_dotenv()
    st.set_page_config(page_title="Outfit Generator using Gemini",
                       page_icon='❤️',
                       layout='centered',
                       initial_sidebar_state='collapsed')

    st.title("Generate Mulitple Outfits:")
    st.write(css, unsafe_allow_html=True)
    if "messages" not in st.session_state:
        st.session_state.messages = []

    input = st.text_input(
        "Give a specific description of the attire you have in mind or leave it blank to let AI choose for you.", key="input")
    num_output = st.number_input("Desired number of images", value=1,
                                 placeholder="Type a number...", max_value=4, min_value=1)
    gender = st.radio(
        "Gender",
        ["Man", "Woman", "Other"])
    if gender == 'Other':
        input = st.text_input("Describe your identity ", key="other_input")
    row1 = st.columns(3)
    submit = row1[0].button("Generate Outfit")
    clear = row1[1].button("Clear Conversation")
    history = row1[2].button("Show History")

    if history:
        if st.session_state.messages:
            st.header("Conversation History:")
            for i, turn in enumerate(reversed(st.session_state.messages), 1):
                if turn['role'] == "user":
                    st.write(turn['parts'][0])
                else:
                    a = int(i/2+.5)
                    st.header("Outfit Number: " + str(a))
                    st.image(turn['parts'][0])
        else:
            st.write("No conversation history yet")

    if clear:
        st.session_state.messages = []

    if submit:
        with st.spinner("Processing"):
            if input:
                for i in stqdm(range(num_output)):
                    outfit_prompt = make_outfit_prompt(input, gender)
                    outfit_answer = google_response(outfit_prompt)
                    image_prompt = make_image_prompt(outfit_answer.text)
                    image_answer = google_response(image_prompt)
                    # st.write(outfit_answer.text)
                    # st.write(image_prompt)
                    st.write(i+1)
                    st.write(image_answer.text)
                    prompt = " The " + gender + \
                        " should have a detailed beautiful/ handsome realistic facial features." + image_answer.text
                    # st.write(prompt)
                    output = realvisxl_request(prompt)
                    # output= "https://replicate.delivery/pbxt/6BcZ1RqeYpSJMaqffeQon4fsfsQrsk6bM1j1IxG9Ce9DnErFJA/out-0.png"
                    # # response_dict = json.loads(output)
                    # # output_url = response_dict["output"]
                    # # st.write(output)
                    # for output_image_url in output:
                    #     # output_image_url = output[0]
                    #     st.image(output_image_url)
                    st.image(output)
                    messages = [
                        {'role': 'user',
                         'parts': [image_answer.text]}
                    ]
                    st.session_state.messages.extend(messages)
                    st.session_state.messages.append({'role': 'model',
                                                      'parts': [output]})
            else:
                for i in stqdm(range(num_output)):
                    input = "Go super imaginative and create sexy outfit for" + gender
                    outfit_prompt = make_outfit_prompt(input, gender)
                    outfit_answer = google_response(outfit_prompt)
                    image_prompt = make_image_prompt(outfit_answer.text)
                    image_answer = google_response(image_prompt)
                    # st.write(outfit_answer.text)
                    # st.write(image_prompt)
                    st.write(i+1)
                    st.write(image_answer.text)
                    prompt = " The " + gender + \
                        " should have a detailed beautiful/ handsome realistic facial features." + image_answer.text
                    # st.write(prompt)
                    output = realvisxl_request(prompt)
                    # output= "https://replicate.delivery/pbxt/6BcZ1RqeYpSJMaqffeQon4fsfsQrsk6bM1j1IxG9Ce9DnErFJA/out-0.png"
                    # # response_dict = json.loads(output)
                    # # output_url = response_dict["output"]
                    # # st.write(output)
                    # for output_image_url in output:
                    #     # output_image_url = output[0]
                    #     st.image(output_image_url)
                    st.image(output)
                    messages = [
                        {'role': 'user',
                         'parts': [image_answer.text]}
                    ]
                    st.session_state.messages.extend(messages)
                    st.session_state.messages.append({'role': 'model',
                                                      'parts': [output]})


if __name__ == '__main__':
    main()
