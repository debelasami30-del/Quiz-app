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
if "tier_unlocked" not in st.session_state:
    st.session_state.tier_unlocked = 1  # 1: Normal, 2: 20 Birr Tier, 3: 30 Birr Tier

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
        url = "https://opentdb.com/api.php?amount=15&category=9&type=multiple"
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

# --- 1. INITIAL AUTHENTICATION & SHORTCODE PAYMENT WALL (10 Birr) ---
if not st.session_state.logged_in:
    st.markdown("## 🔐 Smart Quiz & Rewards - መግቢያ (10 ብር)")
    st.info(f"💳 **የቴሌብር ክፍያ ማሳሰቢያ:**\n1. ገንዘቡን ወደዚህ ቁጥር ያስተላልፉ: **{TELEBIRR_PHONE}** ({TELEBIRR_NAME})\n2. ከቴሌብር የሚመጣለትን ወይም የሾርት ኮድ ማረጋገጫ ቁጥር ከታች ያስገቡ።")
    
    with st.form("auth_form"):
        email_input = st.text_input("የኢሜል አድራሻ (Email Address)")
        password_input = st.text_input("የሚስጥር ቁጥር (Password)", type="password")
        payer_phone = st.text_input("የእርስዎ የቴሌብር ስልክ ቁጥር (ለምሳሌ: 0912345678)")
        ussd_code = st.text_input("የቴሌብር ማረጋገጫ ሾርት ኮድ / የክፍያ ማረጋገጫ (ለምሳሌ: *127# ወይም ሩብ ኮድ)")
        
        submit_btn = st.form_submit_button("ክፍያ አረጋግጥ እና ጀምር")
        
        if submit_btn:
            if not email_input or "@" not in email_input or "." not in email_input:
                st.error("እባክዎ ትክክለኛ ኢሜል ያስገቡ!")
            elif not password_input or len(password_input) < 4:
                st.error("ፓስወርዱ ቢያንስ ከ 4 ፊደላት በላይ መሆን አለበት!")
            elif not payer_phone or len(payer_phone) < 9:
                st.error("እባክዎ ትክክለኛ ስልክ ቁጥር ያስገቡ!")
            elif not ussd_code:
                st.error("እባክዎ የቴሌብር ማረጋገጫ ሾርት ኮድ/ቁጥር ያስገቡ!")
            else:
                st.session_state.users_db[email_input] = password_input
                st.session_state.user_email = email_input
                st.session_state.logged_in = True
                st.success("ክፍያዎ በሾርት ኮድ ተረጋግጧል! ወደ ጨዋታው እየገባ ነው...")
                st.rerun()
    st.stop()

# --- 2. MAIN QUIZ APP INTERFACE ---
st.markdown("⭐️ **Smart Quiz, Psychology & Rewards Hub**")
st.write(f"👤 ተጠቃሚ: **{st.session_state.user_email}** | 💰 ያገኙት ገንዘብ: **{st.session_state.money_earned:.4f} ብር**")
st.write(f"🏆 ውጤት: **{st.session_state.score} ነጥብ**")

# Total registered users counter view
total_registered_users = len(st.session_state.users_db)
st.write(f"📊 አጠቃላይ አፑን የተጠቀሙ ሰዎች ብዛት: {total_registered_users}")
st.markdown("---")

q_idx = st.session_state.current_question_index
total_q = len(st.session_state.shuffled_questions)

if q_idx < total_q:
    current_q = st.session_state.shuffled_questions[q_idx]
    
    st.subheader(f"ጥያቄ {q_idx + 1} ከ {total_q}")
    st.write(current_q["question"])
    
    st.warning("⏱️ ለዚህ ጥያቄ የሚሰጥዎ ጊዜ: **10 ሰከንድ**")
    
    selected_option = st.radio("መልስ ይምረጡ:", current_q["options"], key=f"q_radio_{q_idx}")
    
    if st.button("መልስ አረጋግጥ (Submit)"):
        if selected_option == current_q["answer"]:
            if q_idx not in st.session_state.answered_questions:
                st.success("ትክክለኛ መልስ! 🌟 +0.001 ብር እና +10 ነጥብ አግኝተዋል")
                st.session_state.score += 10
                st.session_state.money_earned += 0.001
                st.session_state.answered_questions.add(q_idx)
            else:
                st.info("ይህ ጥያቄ ቀድሞ ተመልሷል!")
        else:
            st.error(f"ስህተት! ትክክለኛው መልስ፦ {current_q['answer']}")
            st.info(f"💡 **ማብራሪያ:** {current_q['explanation']}")
        
        with st.spinner("⏳ ወደ ቀጣይ ጥያቄ በ 5 ሰከንድ ውስጥ እያለፈ ነው..."):
            time.sleep(5)
        
        st.session_state.current_question_index += 1
        st.rerun()
else:
    st.success("🎉 የመጀመሪያዎቹን ጥያቄዎች ጨርሰዋል!")
    st.write(f"ያገኙት ገንዘብ: **{st.session_state.money_earned:.4f} ብር**")
    st.markdown("---")
    
    # --- TIER UPGRADES (20 Birr & 30 Birr Options) ---
    if st.session_state.tier_unlocked == 1:
        st.markdown("### 🚀 ተጨማሪ ጥያቄዎችን ለመክፈት (20 ብር):")
        st.info(f"📱 **ቴሌብር ቁጥር:** `{TELEBIRR_PHONE}` | **ስም:** {TELEBIRR_NAME}")
        
        with st.form("tier2_form"):
            phone_20 = st.text_input("የቴሌብር ስልክ ቁጥር (ለ 20 ብር)")
            code_20 = st.text_input("የቴሌብር ማረጋገጫ ሾርት ኮድ (USSD/SMS Code)")
            submit_20 = st.form_submit_button("20 ብር ክፍያ አረጋግጥ እና ክፈት")
            
            if submit_20:
                if phone_20 and code_20:
                    st.session_state.tier_unlocked = 2
                    fetch_online_questions()
                    st.session_state.shuffled_questions = list(st.session_state.question_bank)
                    st.success("ክፍያዎ በሾርት ኮድ ተረጋግጧል! 20 ብር ጥያቄዎች ተከፍተዋል...")
                    st.rerun()
                else:
                    st.error("እባክዎ ስልክ ቁጥር እና የሾርት ኮድ ቁጥር በትክክል ይሙሉ!")
                    
    elif st.session_state.tier_unlocked == 2:
        st.markdown("### 🔥 ልዩ ተጨማሪ (Advanced) ጥያቄዎችን ለመክፈት (30 ብር):")
        st.info(f"📱 **ቴሌብር ቁጥር:** `{TELEBIRR_PHONE}` | **ስም:** {TELEBIRR_NAME}")
        
        with st.form("tier3_form"):
            phone_30 = st.text_input("የቴሌብር ስልክ ቁጥር (ለ 30 ብር)")
            code_30 = st.text_input("የቴሌብር ማረጋገጫ ሾርት ኮድ (USSD/SMS Code)")
            submit_30 = st.form_submit_button("30 ብር ክፍያ አረጋግጥ እና ክፈት")
            
            if submit_30:
                if phone_30 and code_30:
                    st.session_state.tier_unlocked = 3
                    fetch_online_questions()
                    fetch_online_questions()
                    st.session_state.shuffled_questions = list(st.session_state.question_bank)
                    st.success("ክፍያዎ በሾርት ኮድ ተረጋግጧል! 30 ብር ልዩ ጥያቄዎች ተከፍተዋል...")
                    st.rerun()
                else:
                    st.error("እባክዎ ስልክ ቁጥር እና የሾርት ኮድ ቁጥር በትክክል ይሙሉ!")
    else:
        st.success("🌟 ሁሉንም ከፍተኛ ደረጃ ጥያቄዎች ከፍተዋል!")

    st.markdown("---")
    st.markdown("### 💸 የገንዘብ ማውጫ (Withdrawal) እና 500 ብር ገደብ")
    if st.session_state.money_earned >= 500.0:
        st.success(f"🎉 እንኳን ደስ አለዎት! 500 ብር እና ከዚያ በላይ አከማችተዋል። ሽልማትዎን ለመውሰድ ቴሌግራም ላይ ያነጋግሩን: `{TELEGRAM_CONTACT}`")
    else:
        remaining_needed = 500.0 - st.session_state.money_earned
        st.warning(f"⚠️ ከዋናው አፕ ገንዘብ አውጥተው ለመውሰድ ጠቅላላ ያገኙት ገንዘብ **500 ብር** መሞላት አለበት። እስካሁን ያገኙት: **{st.session_state.money_earned:.4f} ብር** ነው። ለማውጣት ገና `{remaining_needed:.4f} ብር` ይቀርዎታል!")

    st.markdown("---")
    st.markdown("### ✍️ የራስዎን ጥያቄ ወደ አፑ መጨመር ይፈልጋሉ? (50 ብር)")
    st.info(f"📱 **ቴሌብር ቁጥር:** `{TELEBIRR_PHONE}` | **ስም:** {TELEBIRR_NAME}")
    
    with st.form("add_question_form"):
        phone_50 = st.text_input("የቴሌብር ስልክ ቁጥር (ለ 50 ብር)")
        code_50 = st.text_input("የቴሌብር ማረጋገጫ ሾርት ኮድ (USSD/SMS Code)")
        new_q_text = st.text_input("የጥያቄው ጽሑፍ (Question)")
        opt1 = st.text_input("አማራጭ 1 (Option 1)")
        opt2 = st.text_input("አማራጭ 2 (Option 2)")
        opt3 = st.text_input("አማራጭ 3 (Option 3)")
        opt4 = st.text_input("አማራጭ 4 (Option 4)")
        correct_ans = st.text_input("ትክክለኛው መልስ (Exact Correct Answer from above options)")
        explanation_text = st.text_area("የመልሱ ማብራሪያ (Explanation)")
        
        submit_custom_q = st.form_submit_button("ጥያቄውን ወደ አፑ ጨምር")
        
        if submit_custom_q:
            if phone_50 and code_50 and new_q_text and opt1 and opt2 and opt3 and opt4 and correct_ans:
                custom_question = {
                    "question": f"[User Added] {new_q_text}",
                    "options": [opt1, opt2, opt3, opt4],
                    "answer": correct_ans,
                    "explanation": explanation_text if explanation_text else "ይህ ጥያቄ በተጠቃሚ የተጨመረ ነው።",
                    "reward": 0.001
                }
                st.session_state.question_bank.append(custom_question)
                st.session_state.shuffled_questions.append(custom_question)
                st.success("🎉 ጥያቄዎ በተሳካ ሁኔታ ወደ አፑ ተጨምሯል!")
            else:
                st.error("እባክዎ የቴሌብር ቁጥር፣ ሾርት ኮድ እና ሁሉንም ባዶ ቦታዎች በትክክል ይሙሉ!")

    if st.button("እንደገና ጀምር (Play Again)"):
        st.session_state.current_question_index = 0
        st.session_state.answered_questions = set()
        st.session_state.shuffled_questions = list(st.session_state.question_bank[:5])
        random.shuffle(st.session_state.shuffled_questions)
        st.rerun()
