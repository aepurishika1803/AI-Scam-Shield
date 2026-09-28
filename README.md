## Problem

Scam and phishing messages are becoming increasingly convincing.

Users may receive messages containing:
- Urgent requests
- Threats or fear
- OTP requests
- Bank impersonation
- Suspicious links

Many users may not recognize these warning signs quickly.

AI Scam Shield helps users analyze suspicious messages and understand why they may be risky.
## Solution

AI Scam Shield is an AI-powered scam detection and protection system.

It analyzes suspicious messages and:
- Detects scam indicators
- Identifies the language
- Analyzes suspicious URLs
- Generates a Scam DNA profile
- Provides safety recommendations
- Uses Hindsight Memory to recall similar scam cases

The goal is to help users understand suspicious messages before they click, share sensitive information, or make payments.
## Hindsight Memory

Hindsight Memory is a core part of AI Scam Shield.

The system does not treat every scam message as a completely new case. It uses memory to recall similar previously analyzed scam cases and strengthen the current analysis.

### Memory Flow

Detect → Recall → Analyze → Reason → Protect → Remember

### How It Works

1. The user submits a suspicious message.
2. AI Scam Shield recalls similar cases from Hindsight.
3. The current message is analyzed for scam indicators.
4. Recalled memory provides additional context.
5. The system generates the risk assessment and safety recommendations.
6. The new case is retained in Hindsight for future analysis.

## Scam DNA

AI Scam Shield breaks suspicious messages into key behavioral indicators:

- Urgency
- Threat / fear
- OTP request
- Bank impersonation
- Suspicious URL

These indicators help users understand why a message may be considered risky.

## Multilingual Detection

AI Scam Shield supports scam analysis in:

- English
- Hindi
- Telugu

The system detects the language of the submitted message and provides localized results and safety recommendations.

## Screenshot Scanner

Users can upload a screenshot of a suspicious message.

The system:
1. Extracts text from the screenshot using OCR.
2. Analyzes the extracted message.
3. Calculates the scam risk.
4. Displays Scam DNA and safety recommendations.

## URL Intelligence

AI Scam Shield extracts URLs from suspicious messages and checks for suspicious indicators.

It looks for warning signs such as:

- Login
- Verify
- Secure
- Bank
- Account
- OTP

This helps identify potentially suspicious links before users interact with them.

## Tech Stack

### Frontend
- HTML
- CSS
- JavaScript

### Backend
- Python
- FastAPI

### AI & Memory
- Hindsight

### OCR
- Tesseract OCR
- Pytesseract
- Pillow

## Architecture

```text
User Message / Screenshot
          ↓
Language Detection
          ↓
Scam Pattern Detection
          ↓
URL Intelligence
          ↓
Scam DNA Analysis
          ↓
Hindsight Memory Recall
          ↓
Risk Assessment
          ↓
Safety Recommendation
          ↓
Hindsight Memory Retention

## Setup

```bash
git clone https://github.com/aepurishika1803/AI-Scam-Shield.git
cd AI-Scam-Shield

python -m venv venv

venv\Scripts\activate

pip install fastapi uvicorn hindsight-client python-dotenv python-multipart pytesseract Pillow
```
## How to Run

### Start the Backend

```bash
venv\Scripts\activate
uvicorn backend.app:app --reload
```

Backend URL:

```text
http://127.0.0.1:8000
```

### Start the Frontend

Open a second terminal:

```bash
cd frontend
python -m http.server 5500
```

Frontend URL:

```text
http://127.0.0.1:5500
```

Open the frontend URL in your browser.
## Demo

Example suspicious message:

```text
URGENT! Your bank account has been blocked.
Verify immediately by clicking https://secure-bank-login.com/verify
and send your OTP.
```

AI Scam Shield analyzes the message and provides:

- Risk score
- Risk level
- Detected scam patterns
- Scam DNA
- Suspicious URL indicators
- Hindsight Memory
- Safety recommendation
- Safe reply

## Hindsight Memory in Action

Hindsight Memory is used to recall similar scam cases and provide additional context during analysis.

When a new suspicious message is analyzed:

1. Hindsight recalls relevant previous scam cases.
2. AI Scam Shield analyzes the current message.
3. The recalled memory strengthens the risk assessment.
4. The new case is retained for future analysis.

This makes memory an active part of the detection and reasoning pipeline.

## Project Workflow

Detect → Understand Scam DNA → Recall with Hindsight → Reason → Protect → Remember

## Team

AI Scam Shield was developed as a hackathon project focused on using AI and Hindsight Memory to improve scam detection and user protection.

