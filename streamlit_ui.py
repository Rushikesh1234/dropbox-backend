import streamlit as st
import requests
import math, io
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
    TWO_HUNDRED_MB = 200 * 1024 * 1024

    if uploaded_file:
        st.write(f"File size: {uploaded_file.size / (1024 ** 2):.2f} MB")
        if uploaded_file.size < TWO_HUNDRED_MB:
            if st.button("Upload Small File"):
                files = {'file': (uploaded_file.name, uploaded_file, uploaded_file.type)}
                res = requests.post(f"{API_URL}/upload", files=files, data={"folder":folder}, headers=headers)
                if res.status_code == 200:
                    st.success("Upload successful")
                    st.write(res.json())
                else:
                    st.error("Upload failed {res.status_code}")
        else:
            if st.button("Upload Large File"):
                CHUNK_SIZE = 20 * 1024 * 1024
                filename = uploaded_file.name
                upload_progress = st.empty()
                
                initiate_multipart_upload_res = requests.post(
                    f"{API_URL}/upload/initiate",
                    data={"filename": filename, "folder":folder},
                    headers=headers             
                )

                if initiate_multipart_upload_res != 200:
                    st.error("Failed to initiate upload")
                    st.stop()
                
                upload_id = initiate_multipart_upload_res.json()["upload_id"]
                s3_key = initiate_multipart_upload_res.json()["s3_key"]

                file_data = uploaded_file.read()
                file_size = len(file_data)
                total_parts = math.ceil(file_size / CHUNK_SIZE)

                st.info(f"Uploading {total_parts} chunks...")

                parts_info = []

                for i in range(total_parts):
                    part_number = i + 1
                    start = i * CHUNK_SIZE
                    end = min(start + CHUNK_SIZE, file_size)
                    chunk_bytes = file_data[start:end]

                    files = {
                        "chunk" : ("chunk", io.BytesIO(chunk_bytes), "application/octet-stream")
                    }

                    data = {
                        "upload_id": upload_id,
                        "s3_key": s3_key,
                        "part_number": part_number
                    }

                    chunk_response = requests.post(f"{API_URL}/upload/chunk", data=data, files=files)
                    if chunk_response != 200:
                        st.error(f"Failed on part {part_number}: {chunk_response.text}")
                        requests.post(f"{API_URL}/upload/abort", data={"upload_id": upload_id, "s3_key": s3_key})
                        st.stop()
                    
                    etag = chunk_response.json()["etag"]
                    parts_info.append({"part_number": part_number, "etag": etag})
                    upload_progress.progress(part_number/total_parts)
                
                complete_upload_payload = {
                    "upload_id": upload_id,
                    "s3_key": s3_key,
                    "filename": filename,
                    "folder": folder,
                    "parts": parts_info
                }

                final_res = requests.get(f"{API_URL}/upload/complete", json=complete_upload_payload, headers=headers)

                if final_res.status_code == 200:
                    st.success("Upload successful")
                    st.write(final_res.json())
                else:
                    st.error("Upload failed {final_res.status_code}")

    st.header("Download File")
    file_key = st.text_input("Enter file key")
    if st.button("Get Download File"):
        res = requests.get(f"{API_URL}/download", params={"key": file_key}, headers=headers)
        if res.status_code == 200:
            url = res.json()['url']
            st.markdown(f"[Click here to download]({url})")
        else:
            st.error("Failed to generate link {res.status_code}")