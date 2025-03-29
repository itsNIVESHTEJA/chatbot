import streamlit as st
import pandas as pd
from huggingface_hub import InferenceClient

# Load API Key
if "HF_API_KEY" not in st.secrets:
    st.error("Hugging Face API Key is missing! Please set it in Streamlit Secrets.")
    st.stop()

HF_API_KEY = st.secrets["HF_API_KEY"]
client = InferenceClient(model="tiiuae/falcon-7b-instruct", token=HF_API_KEY)

# Streamlit App UI
st.title("TalentScout Hiring Assistant")

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "👋 Hello! Welcome to TalentScout Hiring Assistant. Let's begin!"}
    ]

if "form_submitted" not in st.session_state:
    st.session_state["form_submitted"] = False

if "tech_questions" not in st.session_state:
    st.session_state["tech_questions"] = None

if "candidate_info" not in st.session_state:
    st.session_state["candidate_info"] = {}

if "current_question_index" not in st.session_state:
    st.session_state["current_question_index"] = 0  

if "responses" not in st.session_state:
    st.session_state["responses"] = []  # Store candidate responses

if "difficulty" not in st.session_state:
    st.session_state["difficulty"] = "Intermediate"  # Default difficulty

# Display Chat History
for msg in st.session_state["messages"]:
    st.chat_message(msg["role"]).write(msg["content"])

# Generate Questions Based on Tech Stack & Difficulty
def generate_questions(tech_stack, difficulty):
    try:
        prompt = f"Generate 5 {difficulty}-level interview questions for {tech_stack}."
        response = client.text_generation(prompt, max_new_tokens=100)
        return response.split("\n") if response else ["Error generating questions."]
    except Exception as e:
        return [f"API Error: {e}"]

# Candidate Form
if not st.session_state["form_submitted"]:
    with st.form(key="candidate_form"):
        name = st.text_input("Full Name", placeholder="Full Name")
        email = st.text_input("Email Address", placeholder="email@example.com")
        experience = st.selectbox("Years of Experience", ["0-1", "2-3", "4-6", "7+"])
        tech_stack = st.text_area("Tech Stack", placeholder="Python, Machine Learning, Deep Learning, SQL")
        difficulty = st.radio("Choose Difficulty Level", ["Beginner", "Intermediate", "Advanced"])

        submit_button = st.form_submit_button("Submit")

        if submit_button:
            if not name or not email or not tech_stack:
                st.warning("Please fill in all required fields.")
            else:
                st.session_state["form_submitted"] = True
                st.session_state["candidate_info"] = {
                    "name": name, "email": email, "experience": experience, "tech_stack": tech_stack, "difficulty": difficulty
                }
                st.session_state["difficulty"] = difficulty
                st.session_state["messages"].append({"role": "assistant", "content": f"Thank you, {name}! Now, let's begin the technical assessment."})
                st.rerun()

# Generate Questions After Form Submission
if st.session_state["form_submitted"] and not st.session_state["tech_questions"]:
    tech_stack = st.session_state["candidate_info"]["tech_stack"]
    difficulty = st.session_state["difficulty"]
    
    tech_questions = generate_questions(tech_stack, difficulty)
    st.session_state["tech_questions"] = tech_questions

    st.session_state["messages"].append(
        {"role": "assistant", "content": "Here are your questions:\n\n" + "\n".join([f"{i+1}. {q}" for i, q in enumerate(tech_questions)])}
    )
    st.rerun()

# Ask Questions One by One
if st.session_state["current_question_index"] < len(st.session_state["tech_questions"]):
    next_question = st.session_state["tech_questions"][st.session_state["current_question_index"]]
    st.session_state["messages"].append({"role": "assistant", "content": f"Question {st.session_state['current_question_index'] + 1}: {next_question}"})
    st.rerun()

# Chatbot User Input
user_input = st.chat_input("Reply here...")
if user_input:
    st.session_state["messages"].append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)

    # Check for exit commands
    if user_input.lower() in ["exit", "quit", "bye"]:
        st.session_state["messages"].append({"role": "assistant", "content": "Thank you for your time! We will review your responses."})
        st.rerun()

    # AI Response & Scoring
    else:
        try:
            feedback_prompt = f"Evaluate this response (score 0-10) and give feedback: {user_input}"
            ai_response = client.text_generation(feedback_prompt, max_new_tokens=150)
            ai_reply = ai_response if ai_response else "I'm unable to process your response."
        except Exception as e:
            ai_reply = f"Error: {e}"

        st.session_state["messages"].append({"role": "assistant", "content": ai_reply})
        st.chat_message("assistant").write(ai_reply)

        # Store Response
        st.session_state["responses"].append({
            "Question": st.session_state["tech_questions"][st.session_state["current_question_index"]],
            "Response": user_input,
            "Feedback": ai_reply
        })

        # Move to next question
        st.session_state["current_question_index"] += 1

        if st.session_state["current_question_index"] < len(st.session_state["tech_questions"]):
            next_question = st.session_state["tech_questions"][st.session_state["current_question_index"]]
            st.session_state["messages"].append({"role": "assistant", "content": f"Question {st.session_state['current_question_index'] + 1}: {next_question}"})
        else:
            st.session_state["messages"].append({"role": "assistant", "content": "You have completed all questions. Thank you!"})

        st.rerun()

# Download Responses as CSV
if len(st.session_state["responses"]) > 0:
    st.subheader("Download Responses")
    df = pd.DataFrame(st.session_state["responses"])
    st.download_button("Download as CSV", df.to_csv(index=False), file_name="candidate_responses.csv", mime="text/csv")
