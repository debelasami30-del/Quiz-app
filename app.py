

import streamlit as st
import random
import urllib.request
import json

# Page Config
st.set_page_config(page_title="Smart Quiz & Rewards App", page_icon="🧠", layout="centered")

# Initialize Session State
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "users_db" not in st.session_state:
    st.session_state.users_db = {} # Stores email: password
if "score" not in st.session_state:
    st.session_state.score = 0
if "current_question_index" not in st.session_state:
    st.session_state.current_question_index = 0

# --- Default Dynamic Question Pool ---
if "question_bank" not in st.session_state:
    st.session_state.question_bank = [
        {
            "question": "የኢትዮጵያ ዋና ከተማ የት ናት?",
            "options": ["አዲስ አበባ", "ባህር ዳር", "ሀዋሳ", "ድሬዳዋ"],
            "answer": "አዲስ አበባ"
        },
        {
            "question": "በዓለም ላይ ትልቁ ውቅያኖስ የቱ ነው?",
            "options": ["አትላንቲክ ውቅያኖስ", "ፓስፊክ ውቅያኖስ", "ህንድ ውቅያኖስ", "አርክቲክ ውቅያኖስ"],
            "answer": "ፓስፊክ ውቅያኖስ"
        },
        {
            "question": "የሰው ልጅ አካል ትልቁ ውጫዊ አካል የቱ ነው?",
            "options": ["ልብ", "ጉበት", "ቆዳ", "አንጎል"],
            "answer": "ቆዳ"
        },
        {
            "question": "የውሃ ኬሚካላዊ መጠሪያ (Chemical Formula) ምንድን ነው?",
            "options": ["CO2", "H2O", "O2", "NaCl"],
            "answer": "H2O"
        },
        {
            "question": "የፀሐይ ስርዓት (Solar System) መሃል ላይ የሚገኘው የቱ ነው?",
            "options": ["ምድር", "ጨረቃ", "ፀሐይ", "ማርስ"],
            "answer": "ፀሐይ"
        },
        {
            "question": "በዓለም ላይ እጅግ ረጅሙ ወንዝ የቱ ነው?",
            "options": ["አባይ ወንዝ", "አማዞን ወንዝ", "ሚሲሲፒ ወንዝ", "ያንግትሴ ወንዝ"],
            "answer": "አባይ ወንዝ"
        }
    ]

# --- Function to fetch online general knowledge questions automatically ---
def fetch_online_questions():
    try:
        url = "https://opentdb.com/api.php?amount=5&category=9&type=multiple"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            if data["results"]:
                for item in data["results"]:
                    q_text = item["question"].replace("&quot;", '"').replace("&#039;", "'")
                    correct = item["correct_answer"].replace("&quot;", '"').replace("&#039;", "'")
                    incorrects = [ans.replace("&quot;", '"').replace("&#039;", "'") for ans in item["incorrect_answers"]]
                    
                    options = incorrects + [correct]
                    random.shuffle(options)
                    
                    new_q = {
                        "question": f"[Online] {q_text}",
                        "options": options,
                        "answer": correct
                    }
                    if not any(d['question'] == new_q['question'] for d in st.session_state.question_bank):
                        st.session_state.question_bank.append(new_q)
    except Exception as e:
        pass

if len(st.session_state.question_bank) < 15:
    fetch_online_questions()

# --- 1. EMAIL & PASSWORD AUTHENTICATION WALL ---
if not st.session_state.logged_in:
    st.markdown("## 🔐 መግቢያ ወይም ምዝገባ (Login / Register)")
    st.write("እባክዎ ለመቀጠል ኢሜልዎን እና የሚፈልጉትን ፓስወርድ ያስገቡ:")
    
    auth_mode = st.radio("አማራጭ ይምረጡ:", ["ግባ (Login)", "ተመዝገብ (Register)"])
    
    with st.form("auth_form"):
        email_input = st.text_input("የኢሜል አድራሻ (Email Address)")
        password_input = st.text_input("የሚስጥር ቁጥር (Password)", type="password")
        
        submit_btn = st.form_submit_button("አረጋግጥ (Submit)")
        
        if submit_btn:
            if not email_input or "@" not in email_input or "." not in email_input:
                st.error("እባክዎ ትክክለኛ ኢሜል ያስገቡ!")
            elif not password_input or len(password_input) < 4:
                st.error("ፓስወርዱ ቢያንስ ከ 4 ፊደላት/ቁጥሮች በላይ መሆን አለበት!")
            else:
                if auth_mode == "ተመዝገብ (Register)":
                    if email_input in st.session_state.users_db:
                        st.warning("ይህ ኢሜል უკድ ተመዝግቧል! እባክዎ ይግቡ (Login)።")
                    else:
                        st.session_state.users_db[email_input] = password_input
                        st.session_state.user_email = email_input
                        st.session_state.logged_in = True
                        st.success("ምዝገባው ተሳክቷል! ወደ አፑ እየገባ ነው...")
                        st.rerun()
                else: # Login
                    if email_input in st.session_state.users_db and st.session_state.users_db[email_input] == password_input:
                        st.session_state.user_email = email_input
                        st.session_state.logged_in = True
                        st.success("በተሳካ ሁኔታ ገብተዋል!")
                        st.rerun()
                    else:
                        # Allow flexible first-time entry even if not pre-registered
                        st.session_state.users_db[email_input] = password_input
                        st.session_state.user_email = email_input
                        st.session_state.logged_in = True
                        st.rerun()
    
    st.stop()

# --- 2. MAIN QUIZ APP INTERFACE ---
st.markdown("⭐️ **Smart Quiz, Psychology & Rewards Hub**")
st.write(f"👤 ገብተዋልበት ኢሜል: **{st.session_state.user_email}**")
st.write(f"🏆 ያገኙት ነጥብ: **{st.session_state.score} / 100**")
st.markdown("---")

if "shuffled_questions" not in st.session_state or len(st.session_state.shuffled_questions) == 0:
    st.session_state.shuffled_questions = list(st.session_state.question_bank)
    random.shuffle(st.session_state.shuffled_questions)

q_idx = st.session_state.current_question_index

if q_idx < len(st.session_state.shuffled_questions):
    current_q = st.session_state.shuffled_questions[q_idx]
    
    st.subheader(f"ጥያቄ {q_idx + 1}")
    st.write(current_q["question"])
    
    selected_option = st.radio("መልስ ይምረጡ:", current_q["options"], key=f"q_{q_idx}_{q_idx}")
    
    if st.button("መልሱን ላክ (Submit)"):
        if selected_option == current_q["answer"]:
            st.success("ትክክለኛ መልስ! 🌟 +10 ነጥብ አግኝተዋል")
            st.session_state.score += 10
        else:
            st.error(f"ስህተት! ትክክለኛው መልስ፦ {current_q['answer']}")
        
        st.session_state.current_question_index += 1
        st.rerun()
else:
    st.success("🎉 እንኳን ደስ አለዎት! ሁሉንም ጥያቄዎች ጨርሰዋል!")
    st.write(f"ጠቅላላ ውጤትዎ: **{st.session_state.score} ነጥብ**")
    
    fetch_online_questions()
    
    if st.session_state.score >= 50:
        st.markdown("🎁 **100 ነጥብ ሞልተዋል? ሽልማትዎን ለመውሰድ ቴሌግራም ላይ ያነጋግሩን!**")
        st.markdown("ቴሌግራም አድራሻ: **@Mom_me2**")
    
    if st.button("ቀጣይ ጥያቄዎችን አጫውት (Play Again)"):
        st.session_state.current_question_index = 0
        st.session_state.shuffled_questions = list(st.session_state.question_bank)
        random.shuffle(st.session_state.shuffled_questions)
        st.rerun()

