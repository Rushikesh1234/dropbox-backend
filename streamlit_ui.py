import streamlit as st
import requests
from dotenv import load_dotenv
import os

load_dotenv()

API_URL = os.getenv("API_URL")

if 'token' not in st.session_state:
    st.session_state['token'] = None

st.title("Dropbox Clone")

if st.session_state['token'] is None:
    action = st.selectbox("Choose action", ["Login", "Register"])
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button(action):
        res = requests.post(
            f"{API_URL}/{action.lower()}", 
            json={
                "username": username, 
                "password": password
            }
        )

        if res.status_code == 200:
            if action == "Login":
                st.session_state["token"] = res.json()["access_token"]
                st.success("Logged in!")
                st.rerun()
            else:
                st.success("Registered successfully. Please login.")
        else:
            st.error(res.json().get("detail"))
else:
    st.success("You are logged in!")
    
    if st.button("Logout"):
        st.session_state["token"] = None
        st.rerun()
    
    headers = {"Authorization": f"Bearer {st.session_state['token']}"}


    st.header("Your Files")
    res = requests.get(f"{API_URL}/files", headers=headers)

    if res.status_code == 200:
        files = res.json()

        for file in files:
            with st.expander(file["filename"]):
                st.write("Uploaded at: ", file["uploaded_at"])
                st.write("S3 Key: ", file["s3_key"])

                if st.button(f"Download {file['filename']}", key=file["s3_key"]):
                    res = requests.get(f"{API_URL}/download", params={"key": file["s3_key"]}, headers=headers)
                    if res.status_code == 200:
                        url = res.json()['url']
                        st.markdown(f"[Click here to download]({url})")
                    else:
                        st.error("Failed to generate link")

    st.header("Upload File")
    uploaded_file = st.file_uploader("Choose a file to upload")

    if st.button("Upload") and uploaded_file:
        files = {'file': (uploaded_file.name, uploaded_file, uploaded_file.type)}
        res = requests.post(f"{API_URL}/upload", files=files, headers=headers)

        if res.status_code == 200:
            st.success("Upload successful")
            st.write(res.json())
        else:
            st.error("Upload failed")

    st.header("Download File")
    file_key = st.text_input("Enter file key")

    if st.button("Get Download File"):
        res = requests.get(f"{API_URL}/download", params={"key": file_key}, headers=headers)
        if res.status_code == 200:
            url = res.json()['url']
            st.markdown(f"[Click here to download]({url})")
        else:
            st.error("Failed to generate link")