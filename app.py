import streamlit as st
import fitz  # PyMuPDF
from nltk.tokenize import sent_tokenize
import nltk
import random
import os

# --- make sure NLTK data works on Streamlit Cloud ---
nltk_data_dir = os.path.join(os.getcwd(), "nltk_data")
os.makedirs(nltk_data_dir, exist_ok=True)
nltk.data.path.append(nltk_data_dir)
for pkg in ["punkt", "punkt_tab"]:
    try:
        nltk.data.find(f"tokenizers/{pkg}")
    except LookupError:
        nltk.download(pkg, download_dir=nltk_data_dir)

st.set_page_config(page_title="AI Quiz Generator", layout="wide")
st.title("AI Quiz Generator - IILM")
st.write("Upload a PDF and let AI generate a fun multiple-choice quiz from it!")

uploaded_file = st.file_uploader(" Upload your PDF file", type=["pdf"])

def extract_text_from_pdf(file):
    text = ""
    with fitz.open(stream=file.read(), filetype="pdf") as pdf:
        for page in pdf:
            text += page.get_text("text") + "\n"
    return text

def generate_mcqs(text, num_questions=5):
    sentences = sent_tokenize(text)
    sentences = [s.strip() for s in sentences if len(s.split()) > 6]
    if not sentences:
        return []
    selected = random.sample(sentences, min(num_questions, len(sentences)))
    questions = []
    for s in selected:
        words = [w for w in s.split() if any(c.isalnum() for c in w)]
        if len(words) > 6:
            answer = random.choice(words)
            question = s.replace(answer, "______", 1)
            options = random.sample(words, min(4, len(words)))
            if answer not in options:
                options[random.randint(0, len(options)-1)] = answer
            random.shuffle(options)
            questions.append((question, options, answer))
    return questions

if uploaded_file is not None:
    text = extract_text_from_pdf(uploaded_file)
    if not text.strip():
        st.error("Uploaded PDF contained no extractable text.")
    else:
        st.success(" PDF uploaded successfully!")
        num_q = st.number_input("How many questions?", min_value=1, max_value=20, value=5)
        if st.button("Generate Quiz"):
            mcqs = generate_mcqs(text, num_q)
            if not mcqs:
                st.warning("Could not generate questions.")
            else:
                st.session_state["quiz"] = mcqs
                st.session_state["answers"] = {}

if "quiz" in st.session_state:
    st.subheader("Your Quiz")
    for i, (q, opts, ans) in enumerate(st.session_state["quiz"], 1):
        sel = st.radio(f"Q{i}. {q}", opts, key=f"q{i}")
        st.session_state["answers"][i] = {"selected": sel, "correct": ans}
    if st.button("Submit All"):
        score = sum(1 for a in st.session_state["answers"].values()
                    if a["selected"] == a["correct"])
        st.success(f"Final Score: {score}/{len(st.session_state['answers'])}")
        del st.session_state["quiz"]
