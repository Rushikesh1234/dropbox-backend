
# Dropbox Clone - Deployment on AWS EC2

This documentation covers the deployment of the Dropbox Clone app backend (FastAPI) and frontend (Streamlit) on an AWS EC2 instance, with secure secrets management via AWS Secrets Manager, and setting up persistent services using `systemd`.

---

## Prerequisites

- AWS account with IAM permissions for EC2 and Secrets Manager
- EC2 instance (Amazon Linux 2023 recommended)
- SSH key to connect to the EC2 instance
- Python 3.9+ installed
- AWS CLI configured (optional)

---

## 1. EC2 Instance Setup

- Launch an EC2 instance (e.g., t2.micro) in your desired region.
- Assign **IAM Role** with `SecretsManagerReadWrite` policy attached (e.g., `EC2SecretsAccessRole`).
- Open Security Group ports for:
  - `8000` (FastAPI backend)
  - `8501` (Streamlit frontend)
- SSH into the instance:
  ```bash
  ssh -i dropbox-key.pem ec2-user@<EC2-Public-IP>
  ```

---

## 2. Project Setup on EC2

- Clone your project repo or upload files.
- Create and activate Python virtual environment:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```
- Install required packages:
  ```bash
  pip install -r requirements.txt
  ```
- Your secrets are stored in AWS Secrets Manager under:
  ```
  secret_name = "dropbox-clone/dev/env"
  ```
- Your `secrets.py` file loads secrets via boto3 and falls back to `.env` if unavailable.

---

## 3. Database Configuration

- `database.py` loads `DATABASE_URL` from environment variables loaded by `secrets.py`.
- SQLAlchemy engine is created using this URL.

---

## 4. Running the Application

- To run FastAPI backend manually:
  ```bash
  uvicorn main:app --host 0.0.0.0 --port 8000
  ```
- To run Streamlit frontend manually:
  ```bash
  streamlit run streamlit_ui.py --server.address 0.0.0.0 --server.port 8501
  ```

---

## 5. Running Services Permanently with systemd

### 5.1 Create FastAPI Service

Create file `/etc/systemd/system/fastapi.service`:

```ini
[Unit]
Description=FastAPI Uvicorn Service
After=network.target

[Service]
User=ec2-user
WorkingDirectory=/home/ec2-user/dropbox-backend
Environment="PATH=/home/ec2-user/dropbox-backend/venv/bin"
ExecStart=/home/ec2-user/dropbox-backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

### 5.2 Create Streamlit Service

Create file `/etc/systemd/system/streamlit.service`:

```ini
[Unit]
Description=Streamlit UI Service
After=network.target

[Service]
User=ec2-user
WorkingDirectory=/home/ec2-user/dropbox-backend
Environment="PATH=/home/ec2-user/dropbox-backend/venv/bin"
ExecStart=/home/ec2-user/dropbox-backend/venv/bin/streamlit run streamlit_ui.py --server.address=0.0.0.0 --server.port=8501
Restart=always

[Install]
WantedBy=multi-user.target
```

### 5.3 Enable and Start/Stop Services

```bash
sudo systemctl daemon-reload
sudo systemctl enable fastapi.service
sudo systemctl enable streamlit.service
sudo systemctl start fastapi.service
sudo systemctl start streamlit.service
sudo systemctl stop fastapi.service
sudo systemctl stop streamlit.service
```

### 5.4 Check service status and logs

```bash
sudo systemctl status fastapi
sudo systemctl status streamlit
journalctl -u fastapi -f
journalctl -u streamlit -f
```

### 5.5 Start/Stop EC2 Instance

```bash
# From AWS console: Actions > Instance State > Stop
# Or AWS CLI:
aws ec2 stop-instances --instance-ids i-0a8beee0a8750039a
```

```bash
# From AWS console: Actions > Instance State > Start
# Or AWS CLI:
aws ec2 start-instances --instance-ids i-0a8beee0a8750039a
```

---

## 6. Access the Application

- FastAPI backend: `http://<EC2-Public-IP>:8000`
- Streamlit UI: `http://<EC2-Public-IP>:8501`

Share the Streamlit URL for frontend access and interaction.

---

## 7. Notes and Recommendations

- Ensure security group ports 8000 and 8501 are open in AWS console.
- For production, secure your app with HTTPS using Nginx and Let’s Encrypt.
- Tokens are handled for authentication—do not expose sensitive APIs publicly.
- Monitor and maintain logs via `journalctl` or centralized logging.

---

## 8. Troubleshooting

- If environment variables don't load, check AWS Secrets Manager permissions and IAM role.
- Use `sudo journalctl -u fastapi -f` or `streamlit` to debug service startup issues.
- Restart services after code changes:
  ```bash
  sudo systemctl restart fastapi.service
  sudo systemctl restart streamlit.service
  ```

---