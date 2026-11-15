import streamlit as st
import random

# Page Config
st.set_page_config(page_title="Smart Quiz & Rewards App", page_icon="🧠", layout="centered")

# Initialize Session State for Authentication and Score
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "score" not in st.session_state:
    st.session_state.score = 0
if "current_question_index" not in st.session_state:
    st.session_state.current_question_index = 0

# --- 1. EMAIL AUTHENTICATION WALL ---
if not st.session_state.logged_in:
    st.markdown("## 🔐 መግቢያ (Login)")
    st.write("እባክዎ ለመጀመር ኢሜልዎን ያስገቡ:")
    
    with st.form("login_form"):
        email_input = st.text_input("የኢሜል አድራሻ (Email Address)")
        submit_login = st.form_submit_button("ግባ (Login)")
        
        if submit_login:
            if email_input and "@" in email_input and "." in email_input:
                st.session_state.user_email = email_input
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("እባክዎ ትክክለኛ ኢሜል ያስገቡ!")
    
    st.stop() # Stops execution here until user logs in

# --- 2. EXPANDED & DYNAMIC QUESTION BANK ---
question_bank = [
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
        "question": "የሰው ልጅ አካል ትልቁ አካል (የውጪው) የቱ ነው?",
        "options": ["ልብ", "ጉበት", "ቆዳ", "አንጎል"],
        "answer": "ቆዳ"
    },
    {
        "question": "በኢትዮጵያ ስንት ብሔር ብሔረሰቦች እና ህዝቦች ይኖራሉ ተብሎ ይታወቃል?",
        "options": ["ከ 40 በታች", "በግምት 80+", "10 ብቻ", "150"],
        "answer": "በግምት 80+"
    },
    {
        "question": "የውሃ ኬሚካላዊ መጠሪያ (Chemical Formula) ምንድን ነው?",
        "options": ["CO2", "H2O", "O2", "NaCl"],
        "answer": "H2O"
    },
    {
        "question": "ሰውን አእምሮ ከሚቆጣጠሩት ዋና ዋና ክፍሎች ውስጥ 'Logic' የሚሰለፍበት የትኛው አእምሮ ክፍል ነው?",
        "options": ["ግራኝ አእምሮ (Left Brain)", "ቀኝ አእምሮ (Right Brain)", "ልብ", "የጀርባ አጥንት"],
        "answer": "ግራኝ አእምሮ (Left Brain)"
    }
]

# --- 3. MAIN QUIZ APP INTERFACE ---
st.markdown("⭐️ **Smart Quiz, Psychology & Rewards Hub**")
st.write(f"👤 ገብተዋልበት ኢሜል: **{st.session_state.user_email}**")
st.write(f"🏆 ያገኙት ነጥብ: **{st.session_state.score} / 100**")
st.markdown("---")

# Shuffle questions once to make it dynamic
if "shuffled_questions" not in st.session_state:
    st.session_state.shuffled_questions = random.sample(question_bank, len(question_bank))

q_idx = st.session_state.current_question_index

if q_idx < len(st.session_state.shuffled_questions):
    current_q = st.session_state.shuffled_questions[q_idx]
    
    st.subheader(f"ጥያቄ {q_idx + 1}")
    st.write(current_q["question"])
    
    selected_option = st.radio("መልስ ይምረጡ:", current_q["options"], key=f"q_{q_idx}")
    
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
    
    if st.session_state.score >= 50:
        st.markdown("🎁 **100 ነጥብ ሞልተዋል? ሽልማትዎን ለመውሰድ ቴሌግራም ላይ ያነጋግሩን!**")
        st.markdown("ቴሌግራም አድራሻ: **@Mom_me2**")
    
    if st.button("እንደገና ጀምር (Play Again)"):
        st.session_state.current_question_index = 0
        random.shuffle(st.session_state.shuffled_questions)
        st.session_state.score = 0
        st.rerun()


