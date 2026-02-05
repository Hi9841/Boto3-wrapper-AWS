# 🛡️ Boto3 Wrapper AWS

A secure, self-service **CLI tool** for automating AWS resource provisioning with built-in safety guardrails.  
This project acts as a controlled wrapper around **boto3**, allowing developers to create and manage AWS resources **without risking runaway costs or accidental production damage**.

---

## 🚀 Features

### 🔐 Smart & Safe Provisioning
- Automatically fetches the **latest AMIs** for:
  - Ubuntu
  - Amazon Linux  
  via **SSM Parameter Store**
- Prevents interaction with any AWS resources **not created by this tool**

### 🖥️ EC2 Management
- Launch EC2 instances with:
  - Instance types: `t3.micro`, `t2.small`
  - OS options: `amazon-linux`, `ubuntu`
- Start and stop instances safely
- List only instances owned by this CLI

### 🪣 S3 Management
- Create secure S3 buckets
- Buckets are **private by default**
- Public buckets require **explicit confirmation**
- Upload files only to buckets owned by this tool

### 🌐 Route53 Management
- Create public hosted zones
- Create, update (UPSERT), and delete DNS records
- Prevents modification of zones not created by this CLI

### 🛡️ Global Safety Guardrails
- **Hard cap of 2 total resources**
- Prevents unexpected AWS bills

### 🏷️ Mandatory Tag Enforcement
Every resource created by this tool is automatically tagged:

| Key | Value | Purpose |
| :--- | :--- | :--- |
| **CreatedBy** | `Hi-platform-cli` | Ownership & safety enforcement |
| **Name** | `Hi-platform-cli-...` | Human-readable identifier |

> ⚠️ The CLI will **ignore, refuse to modify, or delete** any AWS resource that does **not** contain the `CreatedBy: Hi-platform-cli` tag.

### 💻 Interactive CLI
- Built with **Click**
- Clear prompts and confirmations
- Designed for safe self-service usage

---

## 🛠️ Prerequisites

- Python **3.x**
- AWS Credentials with permissions for:
  - EC2
  - S3
  - Route53

---

## 📦 Installation

```bash
git clone [https://github.com/Hi9841/boto3-wrapper-aws.git](https://github.com/Hi9841/boto3-wrapper-aws.git)
cd boto3-wrapper-aws
pip install -r requirements.txt
⚙️ Configuration
Run this once to configure your AWS credentials locally:

Bash
python main.py configure
🖥️ EC2 Management
Create an EC2 Instance

Bash
python main.py ec2 create --type t3.micro --os amazon-linux
List EC2 Instances

Bash
python main.py ec2 list
Manage Power State

Bash
# Stop an instance
python main.py ec2 manage --stop --instance-id i-0123456789abcdef0

# Start an instance
python main.py ec2 manage --start --instance-id i-0123456789abcdef0
🪣 S3 Management
Create a Bucket

Bash
# Private bucket (default)
python main.py s3 create

# Public bucket (requires confirmation)
python main.py s3 create --pub
List Buckets

Bash
python main.py s3 list
Upload a File

Bash
# Use quotes if your file path contains spaces
python main.py s3 upload \
  --bucket hi-platform-cli-storage-abcd1234 \
  --file "C:\Users\docs\myfile.txt"
🌐 Route53 Management
Create a Hosted Zone

Bash
python main.py route53 create --domain my-project.com
Manage DNS Records

Bash
# Create an A record
python main.py route53 manage \
  --create \
  --zone my-project.com \
  --name api.my-project.com \
  --value 1.2.3.4

# Update (UPSERT) a record
python main.py route53 manage \
  --update \
  --zone my-project.com \
  --name api.my-project.com \
  --value 10.0.0.5

# Delete a record (must match existing value)
python main.py route53 manage \
  --delete \
  --zone my-project.com \
  --name api.my-project.com \
  --value 10.0.0.5
List Hosted Zones and Records

Bash
python main.py route53 list
