import streamlit as st
from huggingface_hub import InferenceClient

# Load API Key from Streamlit Secrets
if "HF_API_KEY" not in st.secrets:
    st.error("Hugging Face API Key is missing! Please set it in Streamlit Secrets.")
    st.stop()

HF_API_KEY = st.secrets["HF_API_KEY"]
client = InferenceClient(model="tiiuae/falcon-7b-instruct", token=HF_API_KEY)

# Streamlit App UI
st.title("TalentScout Hiring Assistant")

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state["messages"] = []

if "form_submitted" not in st.session_state:
    st.session_state["form_submitted"] = False

if "tech_questions" not in st.session_state:
    st.session_state["tech_questions"] = None

if "candidate_info" not in st.session_state:
    st.session_state["candidate_info"] = {}

if "current_question_index" not in st.session_state:
    st.session_state["current_question_index"] = 0  # Track which question is being asked

if "greeted" not in st.session_state:
    st.session_state["greeted"] = False

# Greeting Message
if not st.session_state["greeted"]:
    st.session_state["messages"].append(
        {"role": "assistant", "content": "👋 Hello! Welcome to TalentScout Hiring Assistant. I will guide you through a technical screening. Let's begin!"}
    )
    st.session_state["greeted"] = True
    st.rerun()

# Display Chat History
for msg in st.session_state["messages"]:
    st.chat_message(msg["role"]).write(msg["content"])

# Function to Generate Technical Questions
def generate_questions(tech_stack):
    try:
        prompt = f"Generate 5 technical interview questions for {tech_stack}. Only list the questions."
        response = client.text_generation(prompt, max_new_tokens=200)
        return response.split("\n") if response else []
    except Exception as e:
        return [f"API Error: {e}"]

# Candidate Form
if not st.session_state["form_submitted"]:
    with st.form(key="candidate_form"):
        name = st.text_input("Full Name", placeholder="Enter your full name")
        email = st.text_input("Email Address", placeholder="email@example.com")
        phone = st.text_input("Phone Number", placeholder="+123456789")
        experience = st.selectbox("Years of Experience", ["0-1", "2-3", "4-6", "7+"])
        position = st.text_input("Desired Position", placeholder="Software Engineer")
        location = st.text_input("Current Location", placeholder="Enter city name")
        tech_stack = st.text_area("Tech Stack (comma-separated)", placeholder="Python, machine learning, deep learning, SQL, Power BI")

        submit_button = st.form_submit_button("Submit")

        if submit_button:
            if not name or not email or not tech_stack:
                st.warning("Please fill in all required fields.")
            else:
                st.session_state["form_submitted"] = True
                st.session_state["candidate_info"] = {
                    "name": name, "email": email, "phone": phone,
                    "experience": experience, "position": position,
                    "location": location, "tech_stack": tech_stack
                }
                st.session_state["messages"].append(
                    {"role": "assistant", "content": f"Thank you, {name}! Now, let's assess your skills. Here are your technical questions:"}
                )
                st.rerun()

# Generate and Display Questions
if st.session_state["form_submitted"] and not st.session_state["tech_questions"]:
    tech_stack = st.session_state["candidate_info"]["tech_stack"]
    tech_questions = generate_questions(tech_stack)

    if tech_questions:
        st.session_state["tech_questions"] = tech_questions
        st.session_state["messages"].append(
            {"role": "assistant", "content": "\n".join(tech_questions)}
        )
        st.session_state["messages"].append(
            {"role": "assistant", "content": f"Let's start! Answer this question: {tech_questions[0]}"}
        )
        st.rerun()

# Asking Questions One by One
if st.session_state["tech_questions"]:
    index = st.session_state["current_question_index"]

    if index < len(st.session_state["tech_questions"]):
        current_question = st.session_state["tech_questions"][index]
        st.subheader(f"Question {index+1}: {current_question}")

# Chatbot User Input
user_input = st.chat_input("Your answer...")

if user_input:
    # Save user response
    st.session_state["messages"].append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)

    # Check for exit keywords
    exit_keywords = ["exit", "quit", "bye", "end", "stop"]
    if any(keyword in user_input.lower() for keyword in exit_keywords):
        st.session_state["messages"].append(
            {"role": "assistant", "content": "Thank you for your time! We will review your responses. Have a great day! 😊"}
        )
        st.rerun()

    # AI Evaluation of Answer
    try:
        ai_response = client.text_generation(
            f"Evaluate the candidate's answer: {user_input}. Provide constructive feedback.", max_new_tokens=150
        )
        ai_reply = ai_response if ai_response else "I'm unable to process your response."
    except Exception as e:
        ai_reply = f"Error: {e}"

    st.session_state["messages"].append({"role": "assistant", "content": ai_reply})
    st.chat_message("assistant").write(ai_reply)

    # Move to next question
    st.session_state["current_question_index"] += 1

    # If more questions remain, ask the next one
    if st.session_state["current_question_index"] < len(st.session_state["tech_questions"]):
        next_question = st.session_state["tech_questions"][st.session_state["current_question_index"]]
        st.session_state["messages"].append(
            {"role": "assistant", "content": f"Next question: {next_question}"}
        )
    else:
        st.session_state["messages"].append(
            {"role": "assistant", "content": "You have completed all questions. Thank you!"}
        )

    st.rerun()
