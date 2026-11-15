
import streamlit as st
import random
import urllib.request
import json

# Page Config
st.set_page_config(page_title="Smart Quiz & Rewards App", page_icon="🧠", layout="centered")

# --- 💡 እዚህ ጋር የራስዎን የቴሌብር ቁጥር እና ስም መቀየር ይችላሉ ---
TELEBIRR_PHONE = "0913367787"  # <--- የእርስዎን የቴሌብር ቁጥር እዚህ ያስገቡ
TELEBIRR_NAME = "Samuel Debela"   # <--- የባለቤቱን ስም እዚህ ያስገቡ

# Initialize Session State
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "users_db" not in st.session_state:
    st.session_state.users_db = {}
if "score" not in st.session_state:
    st.session_state.score = 0
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
            "explanation": "አዲስ አበባ ከ 1879 ዓ.ም ጀምሮ የኢትዮጵያ ፖለቲካዊ፣ ኢኮኖሚያዊ እና የባህል ማዕከል እንዲሁም ዋና ከተማ ናት።"
        },
        {
            "question": "በዓለም ላይ ትልቁ ውቅያኖስ የቱ ነው?",
            "options": ["አትላንቲክ ውቅያኖስ", "ፓስፊክ ውቅያኖስ", "ህንድ ውቅያኖስ", "አርክቲክ ውቅያኖስ"],
            "answer": "ፓስፊክ ውቅያኖስ",
            "explanation": "ፓስፊክ ውቅያኖስ በስፋቱም ሆነ በጥልቀቱ ከሌሎቹ ውቅያኖሶች ሁሉ የሚበልጥ ትልቁ የምድር የውሃ አካል ነው።"
        },
        {
            "question": "የሰው ልጅ አካል ትልቁ ውጫዊ አካል የቱ ነው?",
            "options": ["ልብ", "ጉበት", "ቆዳ", "አንጎል"],
            "answer": "ቆዳ",
            "explanation": "ቆዳ የሰው አካልን ከውጪ ከሚመጡ አደጋዎች የሚከላከል እና በስፋቱ ትልቁ የሰው አካል ክፍል ነው።"
        },
        {
            "question": "የውሃ ኬሚካላዊ መጠሪያ (Chemical Formula) ምንድን ነው?",
            "options": ["CO2", "H2O", "O2", "NaCl"],
            "answer": "H2O",
            "explanation": "አንድ የኦክስጅን እና ሁለት የሃይድሮጅን አተሞች በመዋሃድ H2O (ውሃ) ይፈጥራሉ።"
        },
        {
            "question": "የፀሐይ ስርዓት (Solar System) መሃል ላይ የሚገኘው የቱ ነው?",
            "options": ["ምድር", "ጨረቃ", "ፀሐይ", "ማርስ"],
            "answer": "ፀሐይ",
            "explanation": "የፀሐይ ስርዓት አካል የሆኑት ፕላኔቶች በሙሉ በስበት ኃይል የሚዞሩት መሃል ላይ ባለችው ፀሐይ ዙሪያ ነው።"
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
                        "explanation": f"ይህ ጥያቄ ከኦንላይን የመጣ ሲሆን፣ ትክክለኛው መልስ '{correct}' መሆኑ ተረጋግጧል።"
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
    st.markdown("## 🔐 Smart Quiz & Rewards - መግቢያ")
    st.write("እባክዎ ለመጀመር ኢሜልዎን እና ፓስወርድዎን ያስገቡ:")
    
    with st.form("auth_form"):
        email_input = st.text_input("የኢሜል አድራሻ (Email Address)")
        password_input = st.text_input("የሚስጥር ቁጥር (Password)", type="password")
        
        submit_btn = st.form_submit_button("ግባ (Login / Register)")
        
        if submit_btn:
            if not email_input or "@" not in email_input or "." not in email_input:
                st.error("እባክዎ ትክክለኛ ኢሜል ያስገቡ!")
            elif not password_input or len(password_input) < 4:
                st.error("ፓስወርዱ ቢያንስ ከ 4 ፊደላት በላይ መሆን አለበት!")
            else:
                st.session_state.users_db[email_input] = password_input
                st.session_state.user_email = email_input
                st.session_state.logged_in = True
                st.rerun()
    st.stop()

# --- 2. MAIN QUIZ APP INTERFACE ---
st.markdown("⭐️ **Smart Quiz, Psychology & Rewards Hub**")
st.write(f"👤 ተጠቃሚ: **{st.session_state.user_email}** | 🪙 ኮይኖች: **{st.session_state.coins} Coins**")
st.write(f"🏆 ያገኙት ነጥብ: **{st.session_state.score} / 50**")
st.markdown("---")

q_idx = st.session_state.current_question_index
total_q = len(st.session_state.shuffled_questions)

if q_idx < total_q:
    current_q = st.session_state.shuffled_questions[q_idx]
    
    st.subheader(f"ጥያቄ {q_idx + 1} ከ {total_q}")
    st.write(current_q["question"])
    
    selected_option = st.radio("መልስ ይምረጡ:", current_q["options"], key=f"q_radio_{q_idx}")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if q_idx > 0:
            if st.button("⬅️ Back (ተመለስ)"):
                st.session_state.current_question_index -= 1
                st.rerun()
                
    with col2:
        if st.button("መልስ አረጋግጥ (Submit)"):
            if selected_option == current_q["answer"]:
                if q_idx not in st.session_state.answered_questions:
                    st.success("ትክክለኛ መልስ! 🌟 +10 ነጥብ አግኝተዋል")
                    st.session_state.score += 10
                    st.session_state.coins += 2
                    st.session_state.answered_questions.add(q_idx)
                else:
                    st.info("ይህ ጥያቄ ቀድሞ ተመልሷል!")
            else:
                st.error(f"ስህተት! ትክክለኛው መልስ፦ {current_q['answer']}")
                st.info(f"💡 **ማብራሪያ:** {current_q['explanation']}")
                
    with col3:
        if q_idx < total_q - 1:
            if st.button("Next (ቀጣይ) ➡️"):
                st.session_state.current_question_index += 1
                st.rerun()
        else:
            if st.button("ጨርስ (Finish) 🏁"):
                st.session_state.current_question_index = total_q
                st.rerun()
else:
    # After finishing the first 5 questions
    if not st.session_state.paid_for_more:
        st.success("🎉 የመጀመሪያዎቹን 5 ጥያቄዎች ጨርሰዋል!")
        st.write(f"ያገኙት ውጤት: **{st.session_state.score} ነጥብ**")
        st.markdown("---")
        st.markdown("### 🚀 ተጨማሪ ማለቂያ የሌላቸውን ጥያቄዎች ለመክፈት:")
        st.markdown(f"💳 እባክዎ **10 ብር** ከዚህ በታች ባለው የቴሌብር ቁጥር ይክፈሉ:")
        st.info(f"📱 **ቴሌብር ቁጥር:** `{TELEBIRR_PHONE}`\n👤 **ስም:** {TELEBIRR_NAME}\n💰 **መጠን:** 10.00 ብር")
        
        with st.form("pay_form"):
            tx_id = st.text_input("የቴሌብር ትራንዛክሽን ቁጥር (TX ID) ያስገቡ")
            pay_submit = st.form_submit_button("ክፍያ አረጋግጥ እና ተጨማሪ ጥያቄዎችን ክፈት")
            
            if pay_submit:
                if tx_id:
                    st.session_state.paid_for_more = True
                    fetch_online_questions()
                    st.session_state.shuffled_questions = list(st.session_state.question_bank)
                    st.success("ክፍያዎ ተረጋግጧል! አዳዲስ ጥያቄዎች ተከፍተዋል...")
                    st.rerun()
                else:
                    st.error("እባክዎ የቴሌብር ትራንዛክሽን ቁጥር (TX ID) ያስገቡ!")
    else:
        st.success("🎉 ማለቂያ የሌላቸውን ጥያቄዎች እየመለሱ ነው!")
        st.write(f"ጠቅላላ ውጤትዎ: **{st.session_state.score} ነጥብ** | ኮይኖች: **{st.session_state.coins} Coins**")
        
        fetch_online_questions()
        
        if st.session_state.score >= 50:
            st.markdown("🎁 **ሽልማትዎን ለመውሰድ ቴሌግራም ላይ ያነጋግሩን!**")
            st.markdown("ቴሌግራም አድራሻ: **@Mom_me2**")
        
        if st.button("እንደገና ጀምር (Play Again)"):
            st.session_state.current_question_index = 0
            st.session_state.answered_questions = set()
            st.session_state.shuffled_questions = list(st.session_state.question_bank[:5])
            st.session_state.paid_for_more = False
            random.shuffle(st.session_state.shuffled_questions)
            st.rerun()
