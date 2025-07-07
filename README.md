
# Dropbox-like File Storage System

A simple Dropbox/Google Drive clone with:

- User registration & login (FastAPI)
- File upload/download using AWS S3
- File metadata storage using AWS RDS (PostgreSQL)
- Streamlit UI for user interaction
- Hosted locally or deployed on AWS EC2 (Amazon Linux)

---

## 🏗️ Architecture

```
Users (Web UI)  <--->  Streamlit UI (Port 8501)  
                            |  
                        FastAPI Backend (Port 8000)  
                            |  
         AWS RDS (Postgres)   AWS S3 (File Storage)
```

---

## 🚀 Features

- Register & login users
- Upload files to S3 with metadata in RDS
- List user files with metadata
- Download files from S3
- Basic folder structure support
- Deploy on AWS EC2 with Amazon Linux

---

## 🧰 Tech Stack

- Python 3.9+
- FastAPI (Backend API)
- Streamlit (Frontend UI)
- SQLAlchemy + PostgreSQL (Metadata DB)
- AWS S3 (File storage)
- AWS RDS (Postgres)
- AWS EC2 (Amazon Linux) for hosting

---

## 🔧 Local Setup

### Prerequisites

- Python 3.9+
- AWS Account with S3 + RDS set up
- AWS credentials configured locally (`~/.aws/credentials`)

### Steps

1. Clone repo

```bash
git clone https://github.com/Rushikesh1234/dropbox-backend.git
cd dropbox-backend
```

2. Create and activate virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Configure AWS and database environment variables in `.env`

```
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=your_region
S3_BUCKET=your_bucket_name
DATABASE_URL=postgresql://username:password@hostname:port/dbname
```

5. Run FastAPI backend

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

6. In another terminal, run Streamlit UI

```bash
streamlit run streamlit_ui.py --server.port 8501
```

7. Access:

- FastAPI docs: `http://localhost:8000/docs`
- Streamlit UI: `http://localhost:8501`

---

## ☁️ Deploy on AWS EC2 (Amazon Linux)

1. Launch Amazon Linux 2023 EC2 instance with ports open for SSH (22), FastAPI (8000), Streamlit (8501).

2. SSH into instance:

```bash
ssh -i dropbox-key.pem ec2-user@<your-ec2-ip>
```

3. Update packages and install python3, pip, git

```bash
sudo yum update -y
sudo yum install python3 git -y
```

4. Clone your repo or upload code via SCP.

5. Create virtual env and install dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

6. Run backend and UI

```bash
nohup uvicorn main:app --host 0.0.0.0 --port 8000 &
streamlit run streamlit_ui.py --server.port 8501
```

7. Access your app:

- API: `http://<your-ec2-ip>:8000`
- UI: `http://<your-ec2-ip>:8501`

---
