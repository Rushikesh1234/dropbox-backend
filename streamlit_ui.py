import streamlit as st
import requests

from utils.secrets import load_secrets
import os

load_secrets()

API_URL = os.getenv("API_URL")

if 'token' not in st.session_state:
    st.session_state['token'] = None

def build_tree(files):
    tree = {}

    for file in files:
        path = file["s3_key"].split("/")
        current = tree

        for part in path[:-1]:
            current = current.setdefault(part, {})
        
        filename = path[-1]
        current.setdefault("_files", []).append({**file, "filename":filename})
    
    return tree

def show_tree(tree, level=0):
    for key, value in tree.items():
        if key == "_files":
            for file in value:
                st.markdown(" " * level + f"📄 **{file['filename']}**")
                st.caption(" " * level + f"Uploaded: {file['uploaded_at']}")
                if st.button(f"⬇️ Download {file['filename'].split('_')[1]}", key=file["s3_key"]):
                    res = requests.get(f"{API_URL}/download", params={"key":file["s3_key"]}, headers=headers)
                    if res.status_code == 200:
                        url = res.json()["url"]
                        st.markdown(" " * level + f"[🔗 Click to download]({url})", unsafe_allow_html=True)
                    else:
                        st.error(f"❌ Failed to generate link ({res.status_code})")
        else:
            with st.expander(" " * level + f"📁 {key}"):
                show_tree(value, level+1)                         

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
        folder_tree = build_tree(files)
        show_tree(folder_tree)

    st.header("Upload File")
    folder = st.text_input("Optional Folder name. (e.g. folder_name or folder_name/sub_folder_name)")
    uploaded_file = st.file_uploader("Choose a file to upload")
    if st.button("Upload") and uploaded_file:
        files = {'file': (uploaded_file.name, uploaded_file, uploaded_file.type)}
        res = requests.post(f"{API_URL}/upload", files=files, data={"folder":folder}, headers=headers)

        if res.status_code == 200:
            st.success("Upload successful")
            st.write(res.json())
        else:
            st.error("Upload failed {res.status_code}")

    st.header("Download File")
    file_key = st.text_input("Enter file key")
    if st.button("Get Download File"):
        res = requests.get(f"{API_URL}/download", params={"key": file_key}, headers=headers)
        if res.status_code == 200:
            url = res.json()['url']
            st.markdown(f"[Click here to download]({url})")
        else:
            st.error("Failed to generate link {res.status_code}")