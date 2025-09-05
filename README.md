# 📄 Document Portal

A lightweight and extensible document management system designed to streamline the storage, retrieval, and organization of digital documents. This portal provides a simple interface for managing documents with support for metadata tagging, search, and version control.

## 🚀 Features 

- 📁 Upload and analyze PDF documents
- 🔍 Chat on multi-format document (.pdf, .txt, .docx, .xlsx)
- 📜 Compare Documents for version control

## 🛠️ Tech Stack

- Backend: Python (FastAPI)
- Frontend: HTML/CSS/Streamlit
- Database: FAISS
- Deployment: AWS Fargate (via ECS)
- CI/CD: Git-based pipeline (GitHub Actions)

# 📦 Installation (Local Development)

````
- git clone https://github.com/saGit1990/document_portal.git
- cd document_portal
- python -m venv .venv

- if windows: 
    .venv/scripts/activate
- if Linux/MAC:
    source .venv/bin/activate

- pip install -r requirements.txt
- uvicorn api.main:app --port 8080 
````

# 📜 CI/CD configuration

This project uses a Git-based CI/CD pipeline to automate the build and deployment of the containerized application to AWS Fargate via Amazon ECS.

## 🧱 Pipeline Overview
- Source Control: GitHub repository (main or release branch)
- CI/CD Tool: GitHub Actions (can be adapted to GitLab CI or Bitbucket Pipelines)
- Container Registry: Amazon Elastic Container Registry (ECR)
- Deployment Target: Amazon ECS (Fargate launch type)

## 🛠️ GitHub Actions Workflow
A sample .github/workflows/aws.yaml file:

````
name: Deploy to AWS Fargate

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: ap-south-1

    - name: Login to Amazon ECR
      run: |
        aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin <your-account-id>.dkr.ecr.ap-south-1.amazonaws.com

    - name: Build and push Docker image
      run: |
        docker build -t document-portal .
        docker tag document-portal:latest <your-account-id>.dkr.ecr.ap-south-1.amazonaws.com/document-portal:latest
        docker push <your-account-id>.dkr.ecr.ap-south-1.amazonaws.com/document-portal:latest

    - name: Update ECS service
      run: |
        aws ecs update-service \
          --cluster document-portal-cluster \
          --service document-portal-service \
          --force-new-deployment
````

## 🔐 Secrets Required
Set the following secrets in your GitHub repository:
````
- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY
````

## 📦 ECS Setup
Ensure the following are configured in AWS:
````
- ECS Cluster (document-portal-cluster)
- ECS Service (document-portal-service)
- Task Definition with container image from ECR
- IAM roles for ECS tasks and GitHub Actions
````

# 🧑‍💻 Contributing
Contributions are welcome! Please fork the repository and submit a pull request.

# 📄 License
This project is licensed under the MIT License.