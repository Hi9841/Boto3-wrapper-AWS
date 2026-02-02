# Boto3 Wrapper AWS

A secure, self-service CLI tool for automating AWS resource provisioning. This tool acts as a wrapper around `boto3`, allowing developers to request resources (like EC2) within strict safety limits and pre-defined standards.

## 🚀 Features

* **Smart Provisioning:** Automatically fetches the latest AMIs for Ubuntu and Amazon Linux via SSM Parameter Store.
* **Safety Guardrails:** Enforces a hard cap of **2 running instances** to prevent billing surprises.
* **Tag Enforcement:** Automatically tags all resources (`CreatedBy: Hi-platform-cli`) and refuses to touch resources created outside the tool.
* **State Awareness:** Checks if an instance is already running or stopped before attempting actions to prevent errors.
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