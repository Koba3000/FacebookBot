# Facebook Messenger Bot

**Disclaimer**: This tool is intended for testing and educational purposes only. Use it responsibly and ensure compliance with Facebook's terms of service.

## Description
This bot automates sending private messages to members of a specified Facebook group.

---

## Requirements
- **Python 3.8+**
- The following Python libraries (specified in `requirements.txt`):
  - `selenium`
  - `webdriver-manager`
- **Google Chrome** or **Chromium**
- A compatible version of ChromeDriver or ChromiumDriver (automatically managed via `webdriver-manager`)

---

## Setup Instructions for Windows

### 1. Clone the Repository
Run the following command to clone the repository:
```bash
git clone https://github.com/your-repo/FacebookBot.git
cd FacebookBot
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python FacebookLogging.py
```
## Setup Instructions for Linux/macOS

### 1. Clone the Repository
Run the following command to clone the repository:
```bash
git clone https://github.com/your-repo/FacebookBot.git
cd FacebookBot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python FacebookLogging.py
```
Example interaction
- Enter your email: example@gmail.com
- Enter your password: MySecurePassword
- Enter the message to send: Hello, this is a test message.
- Enter the group URL: https://www.facebook.com/groups/123456789/people
  (make sure URL contains numbers like .../123456789/ rather than string like .../example/)

