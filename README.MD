# Boto3 Wrapper AWS

A secure, self-service CLI tool for automating AWS resource provisioning. This tool acts as a wrapper around `boto3`, allowing developers to request resources (EC2, S3, Route53) within strict safety limits and pre-defined standards.

## 🚀 Features

* **Smart Provisioning:** Automatically fetches the latest AMIs for Ubuntu and Amazon Linux via SSM Parameter Store.
* **S3 Management:** Create secure storage buckets with automatic "Public/Private" access controls.
* **Route53 Management:** Create Hosted Zones and manage DNS records with safety checks.
* **Global Safety Guardrails:** Enforces a hard cap of **2 total resources** (EC2 Instances + S3 Buckets + Hosted Zones combined) to prevent billing surprises.
* **Tag Enforcement:** Automatically tags all resources (`CreatedBy: Hi-platform-cli`) and refuses to touch resources created outside the tool.
* **Interactive CLI:** Built with `click` for a robust command-line experience.

## 🛠️ Prerequisites

* Python 3.x
* AWS Credentials (Access Key & Secret Key) with permissions for EC2, S3, and Route53.

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

## 🏷️ Tagging Convention (Important)

To ensure safety and ownership, this tool applies the following tag to **every** resource it creates:

| Key | Value | Purpose |
| :--- | :--- | :--- |
| `CreatedBy` | `Hi-platform-cli` | Identifies resources managed by this tool. |
| `Name` | `Hi-platform-cli-...` | Human-readable name for the resource. |

**Note:** The tool's `manage`, `list`, and `delete` commands will **ignore** any resource that does not have the `CreatedBy: Hi-platform-cli` tag. This prevents accidental deletion of your production resources.

## 💻 Usage

### 1. Configuration
Run this once to set up your AWS credentials locally.
```bash
python main.py configure
2. EC2 Management (Virtual Machines)
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
3. S3 Management (Storage)
Create a Bucket: Buckets are private by default. Use --pub to make them public (requires explicit confirmation).

Bash
# Create Private Bucket (Default)
python main.py s3 create

# Create Public Bucket (Will ask "Are you sure?")
python main.py s3 create --pub
List Buckets: Lists only buckets owned by this tool.

Bash
python main.py s3 list
Upload a File: Securely upload a file. The tool verifies the destination bucket belongs to you before uploading.

Bash
# Note: Use quotes if your file path has spaces
python main.py s3 upload --bucket hi-platform-cli-storage-abcd1234 --file "C:\Users\docs\myfile.txt"
4. Route53 Management (DNS)
Create a Hosted Zone: Creates a public hosted zone for a domain.

Bash
python main.py route53 create --domain my-project.com
Manage Records: Create, Update, or Delete records within your managed zones.

Bash
# Create an A record
python main.py route53 manage --create --zone my-project.com --name api.my-project.com --value 1.2.3.4

# Update the record (UPSERT)
python main.py route53 manage --update --zone my-project.com --name api.my-project.com --value 10.0.0.5

# Delete the record (Must match current value)
python main.py route53 manage --delete --zone my-project.com --name api.my-project.com --value 10.0.0.5
List Zones: View only the zones and records created by this tool.

Bash
python main.py route53 list
🛡️ Global Limits
This tool implements a strict Global Resource Limit.

Max Resources: 2

Logic: (Running EC2s) + (Active S3 Buckets) + (Hosted Zones) <= 2

If you have 1 EC2 and 1 Bucket, you cannot create another resource until you delete or terminate one.