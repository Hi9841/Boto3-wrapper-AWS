# Boto3 Wrapper AWS

A secure, self-service CLI tool for automating AWS resource provisioning. This tool acts as a wrapper around `boto3`, allowing developers to request resources (like EC2 and S3) within strict safety limits and pre-defined standards.

## 🚀 Features

* **Smart Provisioning:** Automatically fetches the latest AMIs for Ubuntu and Amazon Linux via SSM Parameter Store.
* **S3 Management:** Create secure storage buckets with automatic "Public/Private" access controls and UUID-based naming.
* **Secure Uploads:** Upload files to S3 with built-in validation that ensures you only write to buckets created by this tool.
* **Global Safety Guardrails:** Enforces a hard cap of **2 total resources** (EC2 Instances + S3 Buckets combined) to prevent billing surprises.
* **Tag Enforcement:** Automatically tags all resources (`CreatedBy: Hi-platform-cli`) and refuses to touch resources created outside the tool.
* **Interactive CLI:** Built with `click` for a robust command-line experience.

## 🛠️ Prerequisites

* Python 3.x
* AWS Credentials (Access Key & Secret Key)

## 📦 Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/Hi9841/boto3-wrapper-aws.git](https://github.com/Hi9841/boto3-wrapper-aws.git)
    cd boto3-wrapper-aws
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## 💻 Usage

### 1. Setup
First, configure your local environment with your AWS keys.
```bash
python main.py configure

EC2 Management
Create an Instance: Choose between amazon-linux or ubuntu, and t3.micro or t2.small.

Bash
python main.py ec2 create --type t3.micro --os amazon-linux
List Instances: See only the instances created by this tool.

Bash
python main.py ec2 list
Manage Power State: Start or stop instances by ID (protected by tag checks).

Bash
python main.py ec2 manage --stop --instance-id i-0123456789abcdef0
python main.py ec2 manage --start --instance-id i-0123456789abcdef0

S3 Management
Create a Bucket: Buckets are private by default. Use --pub to make them public (enables ACLs and ownership controls automatically).

Bash
# Create Private Bucket (Default)
python main.py s3 create

# Create Public Bucket
python main.py s3 create --pub
List Buckets: Lists only buckets owned by this tool (verified via Tags).

Bash
python main.py s3 list
Upload a File: Securely upload a file. The tool verifies the destination bucket belongs to you before uploading. Note: Use quotes if your file path has spaces.

Bash
python main.py s3 upload --bucket hi-platform-cli-storage-abcd1234 --file "C:\Users\docs\my file.txt"

🛡️ Global Limits
This tool implements a Global Resource Limit.

Max Resources: 2

Logic: (Running EC2s) + (Active S3 Buckets) <= 2

If you have 1 EC2 and 1 Bucket, you cannot create another resource until you delete/terminate one.