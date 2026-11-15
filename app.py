
 import streamlit as st
import random
import urllib.request
import json
import time

# Page Config
st.set_page_config(page_title="Smart Quiz & Rewards App", page_icon="🧠", layout="centered")

# --- 💡 የእርስዎ የቴሌብር እና የቴሌግራም መረጃዎች ---
TELEBIRR_PHONE = "0913367787"
TELEBIRR_NAME = "Samuel Debela"
TELEGRAM_CONTACT = "@Mom_me2"

# Initialize Session State
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "users_db" not in st.session_state:
    st.session_state.users_db = {}
if "score" not in st.session_state:
    st.session_state.score = 0
if "money_earned" not in st.session_state:
    st.session_state.money_earned = 0.0
if "coins" not in st.session_state:
    st.session_state.coins = 10
if "current_question_index" not in st.session_state:
    st.session_state.current_question_index = 0
if "answered_questions" not in st.session_state:
    st.session_state.answered_questions = set()
if "paid_for_more" not in st.session_state:
    st.session_state.paid_for_more = False

# --- Initial 5 Core Questions ---
if "question_bank" not in st.session_state:
    st.session_state.question_bank = [
        {
            "question": "የኢትዮጵያ ዋና ከተማ የት ናት?",
            "options": ["አዲስ አበባ", "ባህር ዳር", "ሀዋሳ", "ድሬዳዋ"],
            "answer": "አዲስ አበባ",
            "explanation": "አዲስ አበባ ከ 1879 ዓ.ም ጀምሮ የኢትዮጵያ ፖለቲካዊ፣ ኢኮኖሚያዊ እና የባህል ማዕከል እንዲሁም ዋና ከተማ ናት።",
            "reward": 0.001
        },
        {
            "question": "በዓለም ላይ ትልቁ ውቅያኖስ የቱ ነው?",
            "options": ["አትላንቲክ ውቅያኖስ", "ፓስፊክ ውቅያኖስ", "ህንድ ውቅያኖስ", "አርክቲክ ውቅያኖስ"],
            "answer": "ፓስፊክ ውቅያኖስ",
            "explanation": "ፓስፊክ ውቅያኖስ በስፋቱም ሆነ በጥልቀቱ ከሌሎቹ ውቅያኖሶች ሁሉ የሚበልጥ ትልቁ የምድር የውሃ አካል ነው።",
            "reward": 0.001
        },
        {
            "question": "የሰው ልጅ አካል ትልቁ ውጫዊ አካል የቱ ነው?",
            "options": ["ልብ", "ጉበት", "ቆዳ", "አንጎል"],
            "answer": "ቆዳ",
            "explanation": "ቆዳ የሰው አካልን ከውጪ ከሚመጡ አደጋዎች የሚከላከል እና በስፋቱ ትልቁ የሰው አካል ክፍል ነው።",
            "reward": 0.001
        },
        {
            "question": "የውሃ ኬሚካላዊ መጠሪያ (Chemical Formula) ምንድን ነው?",
            "options": ["CO2", "H2O", "O2", "NaCl"],
            "answer": "H2O",
            "explanation": "አንድ የኦክስጅን እና ሁለት የሃይድሮጅን አተሞች በመዋሃድ H2O (ውሃ) ይፈጥራሉ።",
            "reward": 0.001
        },
        {
            "question": "የፀሐይ ስርዓት (Solar System) መሃል ላይ የሚገኘው የቱ ነው?",
            "options": ["ምድር", "ጨረቃ", "ፀሐይ", "ማርስ"],
            "answer": "ፀሐይ",
            "explanation": "የፀሐይ ስርዓት አካል የሆኑት ፕላኔቶች በሙሉ በስበት ኃይል የሚዞሩት መሃል ላይ ባለችው ፀሐይ ዙሪያ ነው።",
            "reward": 0.001
        }
    ]

# --- Function to fetch more online questions ---
def fetch_online_questions():
    try:
        url = "https://opentdb.com/api.php?amount=10&category=9&type=multiple"
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
                        "answer": correct,
                        "explanation": f"ይህ ጥያቄ ከኦንላይን የመጣ ሲሆን፣ ትክክለኛው መልስ '{correct}' መሆኑ ተረጋግጧል።",
                        "reward": 0.001
                    }
                    if not any(d['question'] == new_q['question'] for d in st.session_state.question_bank):
                        st.session_state.question_bank.append(new_q)
    except Exception as e:
        pass

if "shuffled_questions" not in st.session_state or len(st.session_state.shuffled_questions) == 0:
    st.session_state.shuffled_questions = list(st.session_state.question_bank[:5])
    random.shuffle(st.session_state.shuffled_questions)

# --- 1. INITIAL AUTHENTICATION WALL ---
if not st.session_state.logged_in:
    
   
