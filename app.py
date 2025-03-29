import streamlit as st
from huggingface_hub import InferenceClient

# Load API Key from Streamlit Secrets
if "HF_API_KEY" not in st.secrets:
    st.error("Hugging Face API Key is missing! Please set it in Streamlit Secrets.")
    st.stop()

HF_API_KEY = st.secrets["HF_API_KEY"]
client = InferenceClient(model="tiiuae/falcon-7b-instruct", token=HF_API_KEY)

# Streamlit App UI
st.title("TalentScout Hiring Assistant 🤖")
st.markdown("👋 Hello! Welcome to **TalentScout Hiring Assistant**. I will guide you through a technical screening. Let's begin!")

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Hello! Let's begin your interview screening."}]

if "form_submitted" not in st.session_state:
    st.session_state["form_submitted"] = False

if "tech_questions" not in st.session_state:
    st.session_state["tech_questions"] = None

if "current_question_index" not in st.session_state:
    st.session_state["current_question_index"] = 0

if "responses" not in st.session_state:
    st.session_state["responses"] = []

if "candidate_info" not in st.session_state:
    st.session_state["candidate_info"] = {}

# Display Chat History
for msg in st.session_state["messages"]:
    st.chat_message(msg["role"]).write(msg["content"])

# Function to Generate Technical Questions
def generate_questions(tech_stack):
    try:
        prompt = f"Generate 5 technical interview questions for {tech_stack}."
        response = client.text_generation(prompt, max_new_tokens=200)
        return response.strip().split("\n") if response else ["Error generating questions."]
    except Exception as e:
        return [f"API Error: {e}"]

# Candidate Form
if not st.session_state["form_submitted"]:
    with st.form(key="candidate_form"):
        name = st.text_input("Full Name", placeholder="Enter full name")
        email = st.text_input("Email Address", placeholder="email@example.com")
        phone = st.text_input("Phone Number", placeholder="+123456789")
        experience = st.selectbox("Years of Experience", ["0-1", "2-3", "4-6", "7+"])
        position = st.text_input("Desired Position", placeholder="Software Engineer")
        location = st.text_input("Current Location", placeholder="Hyderabad")
        tech_stack = st.text_area("Tech Stack (comma-separated)", placeholder="Python, machine learning, SQL, Power BI")

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
                st.session_state["messages"].append({"role": "assistant", "content": f"Thank you, {name}! Now, let's assess your skills."})
                st.session_state["tech_questions"] = generate_questions(tech_stack)
                st.rerun()

# Display Technical Questions Initially
if st.session_state["form_submitted"] and st.session_state["tech_questions"]:
    if st.session_state["current_question_index"] == 0:
        st.subheader("Here are your technical questions:")
        for i, q in enumerate(st.session_state["tech_questions"], 1):
            st.write(f"{i}. {q}")

    # Ask Questions One by One
    if st.session_state["current_question_index"] < len(st.session_state["tech_questions"]):
        current_question = st.session_state["tech_questions"][st.session_state["current_question_index"]]
        st.subheader(f"Question {st.session_state['current_question_index'] + 1}: {current_question}")

# Capture User Response
user_input = st.chat_input("Reply here...")

if user_input:
    # Convert input to lowercase for exit handling
    if user_input.lower() in ["exit", "quit", "bye"]:
        st.session_state["messages"].append({"role": "assistant", "content": "Thank you for your time! Exiting the interview session."})
        st.rerun()  # Restart session to clear the chat

    st.session_state["messages"].append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)

    # AI Response Evaluation
    try:
        feedback_prompt = f"Evaluate this response (score 0-10) and give feedback: {user_input}"
        ai_response = client.text_generation(feedback_prompt, max_new_tokens=150)
        ai_reply = ai_response if ai_response else "I'm unable to process your response."
    except Exception as e:
        ai_reply = f"Error: {e}"

    st.session_state["messages"].append({"role": "assistant", "content": ai_reply})
    st.chat_message("assistant").write(ai_reply)

    # Store the response
    st.session_state["responses"].append({
        "Question": current_question,
        "Response": user_input,
        "Feedback": ai_reply
    })

    # Move to next question
    st.session_state["current_question_index"] += 1

    # End the interview if all questions are answered
    if st.session_state["current_question_index"] >= len(st.session_state["tech_questions"]):
        st.session_state["messages"].append({"role": "assistant", "content": "You have completed all questions. Thank you!"})

    st.rerun()
