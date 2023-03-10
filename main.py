import streamlit as st
import requests
import time

API_KEY = str(st.secrets["SIEVE_API_KEY"])

st.title("Stable Riffusion Walk")
st.markdown('Built by [Gaurang Bharti](https://twitter.com/gaurang_bharti) powered by [Sieve](https://www.sievedata.com)')
st.markdown("This web app uses a workflow that combines [Stable Riffusion](https://github.com/riffusion/riffusion) with [Stable Diffusion Walk](https://github.com/nateraw/stable-diffusion-videos)")
st.write("This workflow generates music and a video based on the input prompt that is then combined")

def check_status(url, interval, job_id):
    finished = False
    headers = {
        'X-API-Key': API_KEY
        }
    while True:
        response = requests.get(url, headers=headers)
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

def send_data(text, duration, name):
    url = "https://mango.sievedata.com/v1/push"
    
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY
    } 
    data = {
        "workflow_name": name,
        "inputs": {
            "prompt": text,
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

text_in = st.text_input('Enter a prompt describing an audiovisual', max_chars=100)
input_duration = st.slider("Duration (seconds)", 4, 7, 5)
workflow_name = "stable-riffusion-walk"

button1 = st.button("Riffusion Walk")

if st.session_state.get('button') != True:
    st.session_state['button'] = button1

if st.session_state['button'] == True:

    job = send_data(text_in, input_duration, workflow_name)
    if job:
        with st.spinner("Processing Video"):
            status = check_status('https://mango.sievedata.com/v1/jobs', 5, str(job))
            if status == True:
                video = fetch_video(job)
                st.video(video)