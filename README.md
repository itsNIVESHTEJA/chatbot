# TalentScout Hiring Assistant

## Overview

TalentScout Hiring Assistant is an AI-powered chatbot designed to make **technical screening** easier for recruiters. It interacts with candidates, collects their details, and evaluates their technical skills using AI-generated questions and feedback. The chatbot is built using **Streamlit** and a **pre-trained LLM (Falcon-7B-Instruct)** for response evaluation.

## Features

### **1. Candidate Interaction**
- Greets the candidate and explains the interview process.
- Collects details like **name, email, experience, desired position, location, and tech stack**.

### **2. Question Handling**
- Generates **five technical questions** based on the candidate’s tech stack.
- Displays all questions upfront, then asks them one by one.
- Prevents duplication or skipping, ensuring a smooth experience.

### **3. AI-Powered Evaluation**
- Analyzes candidate responses and provides **real-time AI-generated feedback**.
- Helps maintain a fair and structured assessment for each candidate.

### **4. Exit Handling**
- Candidates can exit the interview at any time by typing **"exit"**, **"quit"**, or **"bye"**.
- The chatbot confirms when all questions are answered.

### **5. Data Storage**
- Keeps track of **questions, responses, and feedback** for recruiter review.
- Helps in making informed hiring decisions.

### **6. Conversation Context Management**
- Remembers previous interactions to ensure a **coherent conversation flow**.
- Avoids asking the same questions repeatedly.

### **7. Error Handling & Fallback Mechanism**
- Detects unclear inputs and prompts users to clarify.
- Provides default responses to unexpected inputs while maintaining context.

## Installation

### **Prerequisites**
Ensure you have the following installed:
- **Python 3.8+**
- **Streamlit** (`pip install streamlit`)
- **Hugging Face InferenceClient** (`pip install huggingface_hub`)

### **Setup Steps**

1. Clone the repository:
   ```sh
   git clone https://github.com/your-repo/talentscout-bot.git
   cd talentscout-bot
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Set up your **Hugging Face API Key** in Streamlit secrets:
   ```sh
   mkdir -p ~/.streamlit
   echo "[secrets]" > ~/.streamlit/secrets.toml
   echo "HF_API_KEY='your-huggingface-api-key'" >> ~/.streamlit/secrets.toml
   ```
4. Run the chatbot:
   ```sh
   streamlit run app.py
   ```

## Deployment

### **Deploy on Streamlit Cloud**
1. Push your project to **GitHub**.
2. Go to [Streamlit Cloud](https://share.streamlit.io/).
3. Connect your repository and deploy.

## Usage Guide

1. Open the chatbot.
2. Enter your details in the candidate form.
3. View the **technical questions** generated based on your tech stack.
4. Answer each question one by one.
5. Receive **real-time AI feedback** for each response.
6. Exit anytime by typing **"exit"**, **"quit"**, or **"bye"**.

## Future Enhancements

- **Score-based evaluation & summary report**
- **PDF generation for candidate responses**
- **Integration with HR systems**
- **Voice-based interaction**
- **Multi-language support**
- **Sentiment analysis for candidate responses**
- **Adaptive difficulty levels for technical questions**

## Contributors

- **Name** – NIVESH TEJA SUPPALA
- **Organization** – TalentScout AI
- 
##LOOM video link:- https://www.loom.com/share/e30c751f335d40e69a7df007ed473fa6?sid=6c92a907-c4d9-478b-91af-210af3d2ceba

## License


This project is licensed under the **MIT License**.

