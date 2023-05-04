import streamlit as st
import requests
import time

API_KEY = str(st.secrets['SIEVE_API_KEY'])

st.title("Stable Riffusion Walk")
st.markdown('Built by [Gaurang Bharti](https://twitter.com/gaurang_bharti) Powered by [Sieve](https://www.sievedata.com)')
st.markdown("Stable Riffusion Walk combines [Stable Diffusion Walk](https://github.com/nateraw/stable-diffusion-videos) and [Stable Riffusion](https://www.riffusion.com) to generate music videos through Stable Diffusion!")
st.caption("Generations can take anywhere from 3-5 mins to 10+ mins depending on demand. Please be patient :)")

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
audio_in = st.text_input('Try your favorite styles, instruments like saxophone or violin, modifiers like arabic or jamaican, genres like jazz or gospel, sounds like church bells or rain, or any combination', placeholder="Enter prompt for music here", max_chars=100)

with st.expander("Music examples"):
    st.write("Alarm Clock")
    st.audio("Audios/alarm_clock.mp3")
    st.write("Class Rock Mellow Gold Progressive")
    st.audio("Audios/classic_rock_mellow_gold_progressive.mp3")
    st.write("Guitar Riff")
    st.audio("Audios/guitar_riff.mp3")
    st.write("Reggae Fusion")
    st.audio("Audios/reggae_fusion.mp3")
    st.write("Rock & Roll")
    st.audio("Audios/rock_and_roll.mp3")

music_options = ["None", "Alarm Clock", "Classic Rock Mellow Gold Progressive", "Guitar Riff", "Reggae Fusion", "Rock & Roll"]
music_example = st.radio("Or try something from the examples! (Set to None if you're using a custom prompt)", options=music_options)

if music_example != "None":
    audio_in = music_example

st.subheader("Video")

video_in = st.text_input("Describe the visuals of the video! You can try any Stable Diffusion or Midjourney prompts. Some examples below!", placeholder="Enter prompt for video here")

st.caption("Note: More complex prompts will take longer")
with st.expander("Music Video examples"):
        col1, col2 = st.columns([1, 1])
        with col1:
            st.write("Audio prompt: Hans Zimmer")
            st.write("Video prompt: Skull demon sorcerer Concept art portrait by Terese Nielsen, Brom, Miho Hirano, hyperdetailed intricately detailed gothic art trending on Artstation triadic colors Unreal Engine 5 detailed matte painting, Dark Black Velvet Background, art nouveau, deep color, fantastical, intricate detail, splash screen, complementary colors, fantasy concept art, gothic deviantart masterpiece, Vivid colors, 16k, UHD, HDR10, (Masterpiece:1. 5), Absurdres, (best quality:1. 5) Model: ReV Animated v1. 21")
        with col2:
            st.video("Videos/skull_demon.mp4")
        col3, col4 = st.columns([1, 1])
        with col3:
            st.write("Audio prompt: Relaxing, Floating, Waterfall")
            st.write("Video prompt: floating island in the clouds, nice weather, trees, a wooden house, waterfall")
        with col4:
            st.video("Videos/floating_island_waterfall.mp4")
        col5, col6 = st.columns([1, 1])
        with col5:
            st.write("Audio prompt: New Orleans Blues")
            st.write("Video prompt: pixel video game with fighting dragons, high quality")
        with col6:
            st.video("Videos/pixel_fighting_game_new_orleans_blues.mp4")

input_duration = st.slider("Duration (seconds)", 4, 7, 5)

workflow_name = "openjourney-test"

# Experimental

#workflow_names = ["stable-riffusion-walk", "openjourney-test"]

# st.write("Pick one of these models for the video")
# options = ["OpenJourney", "Stable Diffusion v1.5"]
# col1, col2 = st.columns([1, 1])
# with col1:
#     selected_option = st.radio("Select an option", options)
# with col2:
#     if selected_option == "Stable Diffusion v1.5":
#         st.image("sd_21_2.jpg", width=300)
#         workflow_name = "stable-riffusion-walk"
#     elif selected_option == "Openjourney":
#         st.image("openjourney_1.png", width=300)
#         workflow_name = "openjourney-test"
    
button1 = st.button("Diffuse!")

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