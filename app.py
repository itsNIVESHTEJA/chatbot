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
    st.session_state["messages"] = [
        {"role": "assistant", "content": "Hello! Let's begin your interview screening."}
    ]

if "form_submitted" not in st.session_state:
    st.session_state["form_submitted"] = False

if "tech_questions" not in st.session_state:
    st.session_state["tech_questions"] = []

if "answered_questions" not in st.session_state:
    st.session_state["answered_questions"] = []

if "candidate_info" not in st.session_state:
    st.session_state["candidate_info"] = {}

if "current_question_index" not in st.session_state:
    st.session_state["current_question_index"] = 0

# Display Chat History
for msg in st.session_state["messages"]:
    st.chat_message(msg["role"]).write(msg["content"])

# Function to Generate Technical Questions
def generate_questions(tech_stack):
    try:
        prompt = f"Generate 5 technical interview questions for {tech_stack}."
        response = client.text_generation(prompt, max_new_tokens=200)
        return response.strip().split("\n") if response else []
    except Exception as e:
        return [f"API Error: {e}"]

# Candidate Form
if not st.session_state["form_submitted"]:
    with st.form(key="candidate_form"):
        name = st.text_input("Full Name", placeholder="Full name")
        email = st.text_input("Email Address", placeholder="email@example.com")
        phone = st.text_input("Phone Number", placeholder="+123456789")
        experience = st.selectbox("Years of Experience", ["0-1", "2-3", "4-6", "7+"])
        position = st.text_input("Desired Position", placeholder="Software Engineer")
        location = st.text_input("Current Location", placeholder="Hyderabad")
        tech_stack = st.text_area("Tech Stack (comma-separated)", placeholder="Python, Machine Learning, SQL")

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
                    {"role": "assistant", "content": f"Thank you, {name}! Now, let's assess your skills."}
                )
                st.session_state["tech_questions"] = generate_questions(tech_stack)
                st.session_state["answered_questions"] = []
                st.session_state["current_question_index"] = 0  # Start at the first question
                st.rerun()

# Display All Questions Initially
if st.session_state["form_submitted"] and st.session_state["tech_questions"]:
    st.subheader("Technical Questions:")
    for i, question in enumerate(st.session_state["tech_questions"]):
        st.write(f"{i+1}. {question}")  # Display all questions first

# Ask One Question at a Time
if (
    st.session_state["form_submitted"]
    and st.session_state["tech_questions"]
    and st.session_state["current_question_index"] < len(st.session_state["tech_questions"])
):
    current_question = st.session_state["tech_questions"][st.session_state["current_question_index"]]
    st.subheader("Current Question:")
    st.write(current_question)

# Chatbot User Input Handling
user_input = st.chat_input("Reply here...")
if user_input:
    st.session_state["messages"].append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)

    # Handle exit
    if user_input.lower() in ["exit", "quit", "bye"]:
        st.session_state["messages"].append(
            {"role": "assistant", "content": "Thank you for your time! We will review your responses."}
        )
        st.rerun()

    # Answer personal queries
    if "what is my name" in user_input.lower():
        name = st.session_state["candidate_info"].get("name", "I don't have your name on record.")
        st.session_state["messages"].append({"role": "assistant", "content": f"Your name is {name}."})
        st.chat_message("assistant").write(f"Your name is {name}.")
        st.rerun()

    if "how many questions answered" in user_input.lower():
        answered_count = len(st.session_state["answered_questions"])
        total_questions = len(st.session_state["tech_questions"])
        st.session_state["messages"].append(
            {"role": "assistant", "content": f"You have answered {answered_count} out of {total_questions} questions."}
        )
        st.chat_message("assistant").write(f"You have answered {answered_count} out of {total_questions} questions.")
        st.rerun()

    # Evaluate Answer & Move to Next Question
    if st.session_state["current_question_index"] < len(st.session_state["tech_questions"]):
        try:
            ai_response = client.text_generation(f"Evaluate this answer: {user_input}", max_new_tokens=200)
            ai_reply = ai_response.strip() if ai_response else "I'm unable to process your response."
        except Exception as e:
            ai_reply = f"Error: {e}"

        st.session_state["messages"].append({"role": "assistant", "content": ai_reply})
        st.chat_message("assistant").write(ai_reply)

        # Mark question as answered
        st.session_state["answered_questions"].append(st.session_state["tech_questions"][st.session_state["current_question_index"]])
        st.session_state["current_question_index"] += 1  # Move to next question

        # If all questions are answered
        if st.session_state["current_question_index"] >= len(st.session_state["tech_questions"]):
            st.session_state["messages"].append({"role": "assistant", "content": "You have answered all questions. Thank you!"})
            st.chat_message("assistant").write("You have answered all questions. Thank you!")

    st.rerun()
