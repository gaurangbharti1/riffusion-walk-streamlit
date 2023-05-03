import streamlit as st
import requests
import time

API_KEY = str(st.secrets['SIEVE_API_KEY'])

st.title("Stable Diffusion Music Video")
st.markdown('Built by [Gaurang Bharti](https://twitter.com/gaurang_bharti) powered by [Sieve](https://www.sievedata.com)')
st.markdown("This web app allows you to create your own Music Video using Stable Diffusion!")

def check_status(url, interval, job_id):
    finished = False
    headers = {
        'X-API-Key': API_KEY
        }
    while True:
        response = requests.get(url, headers=headers)
        assert response.json()['data'], print(response.json())
        data = response.json()['data']
        
        for job in data:
            if job['id'] == job_id:
            
                if job['status'] == 'processing':
              
                    time.sleep(interval)
                if job['status'] == 'finished':
                   
                    finished = True
                    return finished
                if job['status'] == 'error':
                    st.error("An error occured, please try again. If the error persists, please inform the developers.")
                    print(job['error'])
                    return job['error']

def fetch_video(job_id):
    url = f"https://mango.sievedata.com/v1/jobs/{job_id}"
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY
    }
    response = requests.get(url, headers = headers)
    data = response.json()
    url = data['data'][0]['url']
    return url

def send_data(audio_text, video_text, duration, name):
    url = "https://mango.sievedata.com/v1/push"
    
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY
    } 
    data = {
        "workflow_name": name,
        "inputs": {
            "video_prompt": video_text,
            "audio_prompt": audio_text,
            "duration": duration
            }
        }
    try:
        response = requests.post(url, headers=headers, json=data)
        if ('id') not in response.json():
            st.error(response.json()['description'])
            return False
        return (response.json()['id'])
    except Exception as e:
        return (f'An error occurred: {e}')
    
#Streamlit App
st.subheader("Music")
audio_in = st.text_input('What kind of music would you like?', max_chars=100)

music_options = ["None", "Guitar riff", "Jazz Solo", "new orleans blues", "Berlin and Paris electronic fused together with acoustic tunes"]
music_example = st.radio("Or pick one of these!", music_options)

if music_example != "None":
    audio_in = music_example

st.subheader("Video")

video_in = st.text_input("Describe the visuals of the video", max_chars=100)

input_duration = st.slider("Duration (seconds)", 4, 7, 5)

st.write("Pick one of these models for the video")
options = ["Openjourney", "Stable Diffusion v1.5"]
col1, col2 = st.columns([1, 1])
with col1:
    selected_option = st.radio("Select an option", options)
with col2:
    if selected_option == "Stable Diffusion v1.5":
        st.image("sd_21_2.jpg", width=300)
        workflow_name = "stable-riffusion-walk"
    elif selected_option == "Openjourney":
        st.image("openjourney_1.png", width=300)
        workflow_name = "openjourney-test"
    
#workflow_names = ["stable-riffusion-walk", "openjourney-test"]

button1 = st.button("Generate Music Video")

if st.session_state.get('button') != True:
    st.session_state['button'] = button1

if st.session_state['button'] == True:

    job = send_data(audio_in, video_in, input_duration, workflow_name)
    if job:
        with st.spinner("Processing Video"):
            status = check_status('https://mango.sievedata.com/v1/jobs', 5, str(job))
            if status == True:
                video = fetch_video(job)
                st.video(video)