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

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "Hello! Let's begin your interview screening."}
    ]

if "form_submitted" not in st.session_state:
    st.session_state["form_submitted"] = False

if "tech_questions" not in st.session_state:
    st.session_state["tech_questions"] = None

if "candidate_info" not in st.session_state:
    st.session_state["candidate_info"] = {}

# Display Chat History
for msg in st.session_state["messages"]:
    st.chat_message(msg["role"]).write(msg["content"])

# Function to Generate Technical Questions
def generate_questions(tech_stack):
    try:
        prompt = f"Generate 5 technical interview questions for {tech_stack}."
        response = client.text_generation(prompt, max_new_tokens=100)
        return response if response else "Error generating questions."
    except Exception as e:
        return f"API Error: {e}"

# Candidate Form
if not st.session_state["form_submitted"]:
    with st.form(key="candidate_form"):
        name = st.text_input("Full Name", placeholder="John Doe")
        email = st.text_input("Email Address", placeholder="johndoe@example.com")
        phone = st.text_input("Phone Number", placeholder="+123456789")
        experience = st.selectbox("Years of Experience", ["0-1", "2-3", "4-6", "7+"])
        position = st.text_input("Desired Position", placeholder="Software Engineer")
        location = st.text_input("Current Location", placeholder="New York")
        tech_stack = st.text_area("Tech Stack (comma-separated)", placeholder="Python, Django, React, PostgreSQL")

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
                st.rerun()

# Generate Questions After Form Submission
if st.session_state["form_submitted"] and not st.session_state["tech_questions"]:
    tech_stack = st.session_state["candidate_info"]["tech_stack"]
    tech_questions = generate_questions(tech_stack)
    
    st.session_state["tech_questions"] = tech_questions
    st.session_state["messages"].append(
        {"role": "assistant", "content": f"Here are your technical questions:\n\n{tech_questions}"}
    )
    st.rerun()

# Display Technical Questions
if st.session_state["tech_questions"]:
    st.subheader("Technical Questions:")
    st.write(st.session_state["tech_questions"])

# Chatbot User Input
user_input = st.chat_input("Reply here...")
if user_input:
    st.session_state["messages"].append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)

    if user_input.lower() in ["exit", "quit", "bye"]:
        st.session_state["messages"].append(
            {"role": "assistant", "content": "Thank you for your time! We will review your responses."}
        )
    else:
        # AI Response Handling
        try:
            ai_response = client.text_generation(f"Analyze the candidate's response: {user_input}", max_new_tokens=100)
            ai_reply = ai_response if ai_response else "I'm unable to process your response."
        except Exception as e:
            ai_reply = f"Error: {e}"

        st.session_state["messages"].append({"role": "assistant", "content": ai_reply})
        st.chat_message("assistant").write(ai_reply)

    st.rerun()
