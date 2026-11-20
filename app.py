import streamlit as st
import random
import urllib.request
import json
import time

# Page Config
st.set_page_config(page_title="Smart Quiz & Psychology App", page_icon="🧠", layout="centered")

# --- 💡 የእርስዎ የቴሌብር፣ የባንክ እና የቴሌግራም መረጃዎች ---
TELEBIRR_PHONE = "0913367787"
TELEBIRR_NAME = "Samuel Debela"
BANK_NAME = "Bank of Abyssinia"
BANK_ACCOUNT = "272833141"
BANK_HOLDER = "Samuel Debela"
TELEGRAM_CONTACT = "@Mom_me2"

# Initialize Session State
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = ""
if "users_db" not in st.session_state:
    st.session_state.users_db = {}
if "used_tx_ids" not in st.session_state:
    st.session_state.used_tx_ids = set()
if "score" not in st.session_state:
    st.session_state.score = 0
if "coins" not in st.session_state:
    st.session_state.coins = 0
if "spin_chances" not in st.session_state:
    st.session_state.spin_chances = 3
if "selected_category" not in st.session_state:
    st.session_state.selected_category = "General Knowledge"
if "current_question_index" not in st.session_state:
    st.session_state.current_question_index = 0
if "question_start_time" not in st.session_state:
    st.session_state.question_start_time = None
if "answered_questions" not in st.session_state:
    st.session_state.answered_questions = set()
if "tier_unlocked" not in st.session_state:
    st.session_state.tier_unlocked = 1  # 1: Normal, 2: 20 Birr Tier, 3: 30 Birr Tier
if "psych_game_done" not in st.session_state:
    st.session_state.psych_game_done = False

def validate_tx_id(tx_raw):
    tx = tx_raw.strip().upper()
    if len(tx) < 6:
        return False, "የትራንዛክሽን ቁጥር (TX ID) ቢያንስ ከ 6 ፊደላት ወይም ቁጥሮች በላይ መሆን አለበት!"
    if tx in st.session_state.used_tx_ids:
        return False, "ይህ የትራንዛክሽን ቁጥር (TX ID) ቀድሞ ጥቅም ላይ ውሏል! እባክዎ ትክክለኛ እና አዲስ TX ID ያስገቡ።"
    return True, tx

def show_payment_info(amount_birr):
    st.info(
        f"💰 **የሚከፈል መጠን:** {amount_birr} ብር\n\n"
        f"📱 **ቴሌብር:** `{TELEBIRR_PHONE}` | **ስም:** {TELEBIRR_NAME}\n\n"
        f"🏦 **ባንክ:** {BANK_NAME} | **አካውንት:** `{BANK_ACCOUNT}` | **ስም:** {BANK_HOLDER}\n\n"
        f"🌍 **ቴሌብር/ባንክ የሌላቸው ወይም ከውጭ:** ቴሌግራም ላይ ያነጋግሩን: `{TELEGRAM_CONTACT}`"
    )

# --- Categorized Question Bank ---
if "question_bank" not in st.session_state:
    st.session_state.question_bank = {
        "General Knowledge": [
            {
                "question": "የኢትዮጵያ ዋና ከተማ የት ናት?",
                "options": ["አዲስ አበባ", "ባህር ዳር", "ሀዋሳ", "ድሬዳዋ"],
                "answer": "አዲስ አበባ",
                "explanation": "አዲስ አበባ የኢትዮጵያ ዋና ከተማ እና ዋነኛ የዲፕሎማሲ ማዕከል ናት።",
                "coins": 10
            },
            {
                "question": "በዓለም ላይ ትልቁ ውቅያኖስ የቱ ነው?",
                "options": ["አትላንቲክ ውቅያኖስ", "ፓስፊክ ውቅያኖስ", "ህንድ ውቅያኖስ", "አርክቲክ ውቅያኖስ"],
                "answer": "ፓስፊክ ውቅያኖስ",
                "explanation": "ፓስፊክ ውቅያኖስ በስፋቱም ሆነ በጥልቀቱ ከሌሎቹ ውቅያኖሶች ሁሉ ይበልጣል።",
                "coins": 10
            },
            {
                "question": "የፀሐይ ስርዓት (Solar System) መሃል ላይ የሚገኘው የቱ ነው?",
                "options": ["ምድር", "ጨረቃ", "ፀሐይ", "ማርስ"],
                "answer": "ፀሐይ",
                "explanation": "ፕላኔቶች በሙሉ በስበት ኃይል የሚዞሩት በፀሐይ ዙሪያ ነው።",
                "coins": 10
            },
            {
                "question": "በአፍሪካ በህዝብ ብዛት ከፍተኛዋ ሀገር የትኛዋ ናት?",
                "options": ["ኢትዮጵያ", "ናይጄሪያ", "ግብጽ", "ደቡብ አፍሪካ"],
                "answer": "ናይጄሪያ",
                "explanation": "ናይጄሪያ በአፍሪካ ውስጥ በህዝብ ብዛት የመጀመሪያዋ ሀገር ናት።",
                "coins": 10
            },
            {
                "question": "የኦሎምፒክ ጨዋታዎች በየስንት ዓመቱ ይካሄዳሉ?",
                "options": ["በየ 2 ዓመቱ", "በየ 4 ዓመቱ", "በየ 5 ዓመቱ", "በየ 1 ዓመቱ"],
                "answer": "በየ 4 ዓመቱ",
                "explanation": "ዋናዎቹ የኦሎምፒክ ጨዋታዎች በየ 4 ዓመቱ ይካሄዳሉ።",
                "coins": 10
            }
        ],
        "Psychology": [
            {
                "question": "በሳይኮሎጂ ውስጥ 'Confirmation Bias' ማለት ምንድን ነው?",
                "options": [
                    "ቀድሞ የያዝነውን እምነት የሚደግፉ መረጃዎችን ብቻ መምረጥ እና ማመን",
                    "የማስታወስ ችሎታን በድንገት ማጣት",
                    "በህልም ውስጥ የሚከሰት ፍርሃት",
                    "የሰዎችን ድምጽ በፍጥነት የመለየት ችሎታ"
                ],
                "answer": "ቀድሞ የያዝነውን እምነት የሚደግፉ መረጃዎችን ብቻ መምረጥ እና ማመን",
                "explanation": "ሰዎች ብዙውን ጊዜ ከራሳቸው አስተሳሰብ ጋር የሚስማሙ መረጃዎችን በቀላሉ ይቀበላሉ፣ የሚቃረኑትን ደግሞ ችላ ይላሉ።",
                "coins": 10
            },
            {
                "question": "የሰው ልጅ አንጎል ጭንቀት (Stress) ሲገጥመው የሚያመነጨው ዋና ሆርሞን የቱ ነው?",
                "options": ["Cortisol", "Melatonin", "Insulin", "Oxytocin"],
                "answer": "Cortisol",
                "explanation": "ኮርቲሶል (Cortisol) የሰውነትን የጭንቀት ምላሽ የሚቆጣጠር ዋና ሆርሞን ነው።",
                "coins": 10
            },
            {
                "question": "የእንቅልፍ ዑደትን (Sleep Cycle) የሚቆጣጠረው ሆርሞን የቱ ነው?",
                "options": ["Adrenaline", "Melatonin", "Dopamine", "Serotonin"],
                "answer": "Melatonin",
                "explanation": "ሜላቶኒን (Melatonin) ምሽት ላይ ጨለማ ሲሆን እንቅልፍ እንዲመጣን ይረዳል።",
                "coins": 10
            },
            {
                "question": "በባህሪ ሳይኮሎጂ 'Habituation' ማለት ምንድን ነው?",
                "options": [
                    "ተደጋጋሚ የሚከሰትን ነገር እየለመዱ ምላሽ መቀነስ",
                    "አዲስ ቋንቋ በፍጥነት መማር",
                    "በቁጣ ውስጥ በፍጥነት መወሰን",
                    "የራስ መተማመን ማጣት"
                ],
                "answer": "ተደጋጋሚ የሚከሰትን ነገር እየለመዱ ምላሽ መቀነስ",
                "explanation": "ለምሳሌ ቤት አጠገብ ያለ ድምጽ መጀመሪያ ቢያስቸግርም ቆይቶ አእምሮ ይለምደዋል።",
                "coins": 10
            },
            {
                "question": "በማህበራዊ ሳይኮሎጂ ውስጥ 'Bystander Effect' ምን ያሳያል?",
                "options": [
                    "ብዙ ሰዎች ባሉበት አደጋ ሲፈጠር እርዳታ የመስጠት ዕድል መቀነስ",
                    "በቡድን ስራ ውስጥ ፍጥነት መጨመር",
                    "መሪን በፍጥነት የመምረጥ ባህሪ",
                    "የብቸኝነት ስሜት መጨመር"
                ],
                "answer": "ብዙ ሰዎች ባሉበት አደጋ ሲፈጠር እርዳታ የመስጠት ዕድል መቀነስ",
                "explanation": "ሰዎች 'ሌላው ይረዳዋል' ብለው ኃላፊነትን በመጋራት ራሳቸው እርምጃ ላለመውሰድ ይችላሉ።",
                "coins": 10
            }
        ],
        "Educational": [
            {
                "question": "የውሃ ኬሚካላዊ መጠሪያ (Chemical Formula) ምንድን ነው?",
                "options": ["CO2", "H2O", "O2", "NaCl"],
                "answer": "H2O",
                "explanation": "አንድ የኦክስጅን (O) እና ሁለት የሃይድሮጅን (H) አተሞች ተጣምረው H2O ይፈጥራሉ።",
                "coins": 10
            },
            {
                "question": "የሰው ልጅ አካል ትልቁ ውጫዊ አካል የቱ ነው?",
                "options": ["ልብ", "ጉበት", "ቆዳ", "ሳንባ"],
                "answer": "ቆዳ",
                "explanation": "ቆዳ የሰውነትን ውስጣዊ ክፍሎች ይከላከላል እና በስፋቱ ትልቁ አካል ነው።",
                "coins": 10
            },
            {
                "question": "የእጽዋት ምግብ ማዘጋጀት ሂደት (Photosynthesis) በዋናነት በየትኛው ክፍል ይከናወናል?",
                "options": ["በስር", "በቅጠል (Chlorophyll)", "በግንድ", "በአበባ"],
                "answer": "በቅጠል (Chlorophyll)",
                "explanation": "ቅጠሎች የፀሐይ ብርሃንን በመጠቀም ምግብ እንዲዘጋጅ ያግዛሉ።",
                "coins": 10
            },
            {
                "question": "የ 12 × 8 ውጤት ስንት ነው?",
                "options": ["86", "96", "104", "108"],
                "answer": "96",
                "explanation": "12 ሲባዛ በ 8 እኩል ይሆናል 96።",
                "coins": 10
            },
            {
                "question": "በፊዚክስ ውስጥ የኃይል መለኪያ (SI Unit of Force) ምንድን ነው?",
                "options": ["Joule", "Watt", "Newton", "Pascal"],
                "answer": "Newton",
                "explanation": "የኃይል መደበኛ መለኪያ ኒውተን (Newton - N) ነው።",
                "coins": 10
            }
        ]
    }

# --- Function to fetch more online questions for the active category ---
def fetch_online_questions(category):
    cat_map = {
        "General Knowledge": "9",
        "Psychology": "9",
        "Educational": "17"
    }
    cat_id = cat_map.get(category, "9")
    try:
        url = f"https://opentdb.com/api.php?amount=10&category={cat_id}&type=multiple"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            if data.get("results"):
                for item in data["results"]:
                    q_text = item["question"].replace("&quot;", '"').replace("&#039;", "'")
                    correct = item["correct_answer"].replace("&quot;", '"').replace("&#039;", "'")
                    incorrects = [ans.replace("&quot;", '"').replace("&#039;", "'") for ans in item["incorrect_answers"]]
                    options = incorrects + [correct]
                    random.shuffle(options)
                    new_q = {
                        "question": f"[{category} - Online] {q_text}",
                        "options": options,
                        "answer": correct,
                        "explanation": f"ትክክለኛው መልስ '{correct}' ነው።",
                        "coins": 10
                    }
                    if not any(d['question'] == new_q['question'] for d in st.session_state.question_bank[category]):
                        st.session_state.question_bank[category].append(new_q)
    except Exception:
        pass

def load_category_questions(category):
    st.session_state.selected_category = category
    st.session_state.current_question_index = 0
    st.session_state.question_start_time = time.time()
    st.session_state.answered_questions = set()
    qs = list(st.session_state.question_bank[category])
    random.shuffle(qs)
    st.session_state.shuffled_questions = qs

if "shuffled_questions" not in st.session_state or len(st.session_state.shuffled_questions) == 0:
    load_category_questions(st.session_state.selected_category)

# --- 1. INITIAL AUTHENTICATION & ENTRY FEE WALL (10 Birr) ---
if not st.session_state.logged_in:
    st.markdown("## 🔐 Smart Quiz, Psychology & Coins - መግቢያ (10 ብር)")
    show_payment_info("10.00")

    auth_mode = st.radio(
        "የመግቢያ መንገድ ይምረጡ:",
        ["📱 በስልክ ቁጥር እና የራስ ኮድ (ኢሜል የሌላቸው)", "📧 በኢሜል እና በፓስወርድ"],
        horizontal=True
    )

    if auth_mode.startswith("📱"):
        with st.form("phone_auth_form"):
            phone_input = st.text_input("ስልክ ቁጥር (Phone Number, e.g. 09...)")
            custom_code = st.text_input("የራስዎን ኮድ ይፍጠሩ (Create Your Own Code / PIN, min 4 chars)", type="password")
            payment_method = st.selectbox("የክፍያ መንገድ ይምረጡ", ["ቴሌብር (Telebirr)", "ባንክ (Bank Transfer)", "ሌላ / ቴሌግራም"], key="pm_phone")
            tx_entry = st.text_input("የክፍያ ማረጋገጫ / ትራንዛክሽን ቁጥር (TX ID)", key="tx_phone")
            confirm_paid = st.checkbox("10 ብር መላኬን እና ትክክለኛ TX ID ማስገባቴን አረጋግጣለሁ", key="chk_phone")

            submit_phone_btn = st.form_submit_button("ኮድ ፍጠር፣ ክፍያ አረጋግጥ እና ጀምር")

            if submit_phone_btn:
                clean_phone = phone_input.strip()
                tx_ok, tx_val = validate_tx_id(tx_entry)
                if not clean_phone or len(clean_phone) < 9:
                    st.error("እባክዎ ትክክለኛ የስልክ ቁጥር ያስገቡ!")
                elif not custom_code or len(custom_code) < 4:
                    st.error("የሚፈጥሩት ኮድ ቢያንስ ከ 4 ፊደላት ወይም ቁጥሮች በላይ መሆን አለበት!")
                elif not confirm_paid:
                    st.error("እባክዎ ክፍያ መላክዎን የሚያረጋግጥ ሳጥን ምልክት ያድርጉ!")
                elif not tx_ok:
                    st.error(tx_val)
                else:
                    if clean_phone in st.session_state.users_db and st.session_state.users_db[clean_phone] != custom_code:
                        st.error("ይህ ስልክ ቁጥር በሌላ ኮድ ተመዝግቧል። እባክዎ የቀድሞ ኮድዎን ያስገቡ!")
                    else:
                        st.session_state.users_db[clean_phone] = custom_code
                        st.session_state.used_tx_ids.add(tx_val)
                        st.session_state.user_id = clean_phone
                        st.session_state.question_start_time = time.time()
                        st.session_state.logged_in = True
                        st.success("የራስዎ ኮድ ተፈጥሯል እና TX ID ተመዝግቧል! ወደ ጨዋታው እየገባ ነው...")
                        st.rerun()
    else:
        with st.form("email_auth_form"):
            email_input = st.text_input("የኢሜል አድራሻ (Email Address)")
            password_input = st.text_input("የሚስጥር ቁጥር (Password)", type="password")
            payment_method = st.selectbox("የክፍያ መንገድ ይምረጡ", ["ቴሌብር (Telebirr)", "ባንክ (Bank Transfer)", "ሌላ / ቴሌግራም"], key="pm_email")
            tx_entry = st.text_input("የክፍያ ማረጋገጫ / ትራንዛክሽን ቁጥር (TX ID)", key="tx_email")
            confirm_paid_em = st.checkbox("10 ብር መላኬን እና ትክክለኛ TX ID ማስገባቴን አረጋግጣለሁ", key="chk_email")

            submit_btn = st.form_submit_button("ክፍያ አረጋግጥ እና ጀምር")

            if submit_btn:
                tx_ok, tx_val = validate_tx_id(tx_entry)
                if not email_input or "@" not in email_input or "." not in email_input:
                    st.error("እባክዎ ትክክለኛ ኢሜል ያስገቡ!")
                elif not password_input or len(password_input) < 4:
                    st.error("ፓስወርዱ ቢያንስ ከ 4 ፊደላት በላይ መሆን አለበት!")
                elif not confirm_paid_em:
                    st.error("እባክዎ ክፍያ መላክዎን የሚያረጋግጥ ሳጥን ምልክት ያድርጉ!")
                elif not tx_ok:
                    st.error(tx_val)
                else:
                    st.session_state.users_db[email_input] = password_input
                    st.session_state.used_tx_ids.add(tx_val)
                    st.session_state.user_id = email_input
                    st.session_state.question_start_time = time.time()
                    st.session_state.logged_in = True
                    st.success("TX ID ተረጋግጧል! ወደ ጨዋታው እየገባ ነው...")
                    st.rerun()
    st.stop()

# --- 2. MAIN INTERFACE ---
st.markdown("⭐️ **Smart Quiz, Psychology & Coins Hub**")
st.write(f"👤 ተጠቃሚ: **{st.session_state.user_id}**")
st.write(f"🪙 ያገኙት ሳንቲም: **{st.session_state.coins:,} Coins** | 🏆 ውጤት: **{st.session_state.score} ነጥብ** | 🎮 የጨዋታ ዕድል: **{st.session_state.spin_chances}**")
st.markdown("---")

tab1, tab2 = st.tabs(["🧠 ጥያቄዎች (Quiz by Category)", "🧩 የሳይኮሎጂ እና የዕድል ጨዋታዎች"])

with tab1:
    st.markdown("### 📂 የጥያቄ ምድብ ይምረጡ (Category)")
    cat_choice = st.radio(
        "መጫወት የሚፈልጉትን ምድብ ብቻ ይምረጡ:",
        ["General Knowledge", "Psychology", "Educational"],
        index=["General Knowledge", "Psychology", "Educational"].index(st.session_state.selected_category),
        horizontal=True
    )
    if cat_choice != st.session_state.selected_category:
        load_category_questions(cat_choice)
        st.rerun()

    st.markdown("---")
    q_idx = st.session_state.current_question_index
    total_q = len(st.session_state.shuffled_questions)

    if q_idx < total_q:
        if st.session_state.question_start_time is None:
            st.session_state.question_start_time = time.time()

        elapsed = time.time() - st.session_state.question_start_time
        remaining = max(0, int(10 - elapsed))

        # 10 ሰከንድ ካለፈ ወዲያውኑ ወደ ቀጣይ ጥያቄ ያልፋል
        if elapsed >= 10.0:
            st.session_state.current_question_index += 1
            st.session_state.question_start_time = time.time()
            st.rerun()

        current_q = st.session_state.shuffled_questions[q_idx]
        
        st.subheader(f"[{st.session_state.selected_category}] ጥያቄ {q_idx + 1} ከ {total_q}")
        st.write(current_q["question"])
        timer_placeholder = st.empty()
        timer_placeholder.warning(f"⏱️ ቀሪ ጊዜ: **{remaining} ሰከንድ** (10 ሰከንድ ሲያልቅ በራሱ ወደ ቀጣይ ጥያቄ ያልፋል)")
        
        selected_option = st.radio("መልስ ይምረጡ:", current_q["options"], key=f"q_radio_{st.session_state.selected_category}_{q_idx}")
        
        if st.button("መልስ አረጋግጥ (Submit)"):
            if selected_option == current_q["answer"]:
                if q_idx not in st.session_state.answered_questions:
                    st.success("ትክክለኛ መልስ! 🌟 +10 Coins እና +10 ነጥብ አግኝተዋል")
                    st.session_state.score += 10
                    st.session_state.coins += 10
                    st.session_state.answered_questions.add(q_idx)
                    if len(st.session_state.answered_questions) % 3 == 0:
                        st.session_state.spin_chances += 1
                        st.balloons()
                        st.info("🎁 3 ጥያቄ ስለመለሱ +1 ተጨማሪ የጨዋታ ዕድል አግኝተዋል!")
                else:
                    st.info("ይህ ጥያቄ ቀድሞ ተመልሷል!")
            else:
                st.error(f"ስህተት! ትክክለኛው መልስ፦ {current_q['answer']}")
                st.info(f"💡 **ማብራሪያ:** {current_q['explanation']}")
            
            time.sleep(1.5)
            st.session_state.current_question_index += 1
            st.session_state.question_start_time = time.time()
            st.rerun()

        # የ 1 ሰከንድ ቆጠራ Loop እስከ 10 ሰከንድ
        for sec in range(remaining, 0, -1):
            timer_placeholder.warning(f"⏱️ ቀሪ ጊዜ: **{sec} ሰከንድ** (10 ሰከንድ ሲያልቅ በራሱ ወደ ቀጣይ ጥያቄ ያልፋል)")
            time.sleep(1)

        st.session_state.current_question_index += 1
        st.session_state.question_start_time = time.time()
        st.rerun()
    else:
        st.success(f"🎉 የ **{st.session_state.selected_category}** ጥያቄዎችን ጨርሰዋል!")
        st.write(f"ጠቅላላ ያገኙት ሳንቲም: **{st.session_state.coins:,} Coins**")
        st.markdown("---")
        
        if st.session_state.tier_unlocked == 1:
            st.markdown("### 🚀 ተጨማሪ ጥያቄዎችን ለመክፈት (20 ብር):")
            show_payment_info("20.00")
            with st.form("tier2_form"):
                method_20 = st.selectbox("የክፍያ መንገድ (20 ብር)", ["ቴሌብር (Telebirr)", "ባንክ (Bank Transfer)", "ሌላ / ቴሌግራም"], key="m20")
                tx_20 = st.text_input("የክፍያ ማረጋገጫ / TX ID (ለ 20 ብር)")
                submit_20 = st.form_submit_button("20 ብር ከፍሎ ተጨማሪ ጥያቄዎችን ክፈት")
                if submit_20:
                    tx_ok, tx_val = validate_tx_id(tx_20)
                    if tx_ok:
                        st.session_state.used_tx_ids.add(tx_val)
                        st.session_state.tier_unlocked = 2
                        st.session_state.spin_chances += 3
                        fetch_online_questions(st.session_state.selected_category)
                        st.session_state.shuffled_questions = list(st.session_state.question_bank[st.session_state.selected_category])
                        random.shuffle(st.session_state.shuffled_questions)
                        st.session_state.current_question_index = 0
                        st.session_state.question_start_time = time.time()
                        st.success("ክፍያዎ ተረጋግጧል! ተጨማሪ ጥያቄዎች ተከፍተዋል...")
                        st.rerun()
                    else:
                        st.error(tx_val)
                        
        elif st.session_state.tier_unlocked == 2:
            st.markdown("### 🔥 ልዩ ተጨማሪ (Advanced) ጥያቄዎችን ለመክፈት (30 ብር):")
            show_payment_info("30.00")
            with st.form("tier3_form"):
                method_30 = st.selectbox("የክፍያ መንገድ (30 ብር)", ["ቴሌብር (Telebirr)", "ባንክ (Bank Transfer)", "ሌላ / ቴሌግራም"], key="m30")
                tx_30 = st.text_input("የክፍያ ማረጋገጫ / TX ID (ለ 30 ብር)")
                submit_30 = st.form_submit_button("30 ብር ከፍሎ ልዩ ጥያቄዎችን ክፈት")
                if submit_30:
                    tx_ok, tx_val = validate_tx_id(tx_30)
                    if tx_ok:
                        st.session_state.used_tx_ids.add(tx_val)
                        st.session_state.tier_unlocked = 3
                        st.session_state.spin_chances += 5
                        fetch_online_questions(st.session_state.selected_category)
                        st.session_state.shuffled_questions = list(st.session_state.question_bank[st.session_state.selected_category])
                        random.shuffle(st.session_state.shuffled_questions)
                        st.session_state.current_question_index = 0
                        st.session_state.question_start_time = time.time()
                        st.success("ክፍያዎ ተረጋግጧል! ልዩ ጥያቄዎች ተከፍተዋል...")
                        st.rerun()
                    else:
                        st.error(tx_val)

        if st.session_state.coins >= 500000:
            st.markdown("---")
            st.success(f"🎉 እንኳን ደስ አለዎት! ሽልማትዎን ለመቀበል ቴሌግራም ላይ ያነጋግሩን: `{TELEGRAM_CONTACT}`")

        st.markdown("---")
        st.markdown("### ✍️ የራስዎን ጥያቄ ወደ አፑ መጨመር ይፈልጋሉ? (50 ብር)")
        show_payment_info("50.00")
        with st.form("add_question_form"):
            method_50 = st.selectbox("የክፍያ መንገድ (50 ብር)", ["ቴሌብር (Telebirr)", "ባንክ (Bank Transfer)", "ሌላ / ቴሌግራም"], key="m50")
            target_cat = st.selectbox("ጥያቄው የሚገባበት ምድብ", ["General Knowledge", "Psychology", "Educational"])
            user_tx = st.text_input("የክፍያ ማረጋገጫ / TX ID (ለ 50 ብር)")
            new_q_text = st.text_input("የጥያቄው ጽሑፍ (Question)")
            opt1 = st.text_input("አማራጭ 1 (Option 1)")
            opt2 = st.text_input("አማራጭ 2 (Option 2)")
            opt3 = st.text_input("አማራጭ 3 (Option 3)")
            opt4 = st.text_input("አማራጭ 4 (Option 4)")
            correct_ans = st.text_input("ትክክለኛው መልስ (Exact Correct Answer from above options)")
            explanation_text = st.text_area("የመልሱ ማብራሪያ (Explanation)")
            
            submit_custom_q = st.form_submit_button("ጥያቄውን ወደ አፑ ጨምር")
            if submit_custom_q:
                tx_ok, tx_val = validate_tx_id(user_tx)
                if tx_ok and new_q_text and opt1 and opt2 and opt3 and opt4 and correct_ans:
                    st.session_state.used_tx_ids.add(tx_val)
                    custom_question = {
                        "question": f"[User Added] {new_q_text}",
                        "options": [opt1, opt2, opt3, opt4],
                        "answer": correct_ans,
                        "explanation": explanation_text if explanation_text else "ይህ ጥያቄ በተጠቃሚ የተጨመረ ነው።",
                        "coins": 10
                    }
                    st.session_state.question_bank[target_cat].append(custom_question)
                    if target_cat == st.session_state.selected_category:
                        st.session_state.shuffled_questions.append(custom_question)
                    st.success("🎉 ጥያቄዎ በተሳካ ሁኔታ ወደ አፑ ተጨምሯል!")
                elif not tx_ok:
                    st.error(tx_val)
                else:
                    st.error("እባክዎ ሁሉንም ባዶ ቦታዎች በትክክል ይሙሉ!")

        if st.button("እንደገና ጀምር (Play Again)"):
            load_category_questions(st.session_state.selected_category)
            st.rerun()

with tab2:
    st.markdown("### 🧩 የሳይኮሎጂ ውሳኔ እና የአስተሳሰብ ጨዋታ (Psychology Mind Game)")
    st.write("በአስቸጋሪ ሁኔታ ውስጥ የእርስዎን የውሳኔ አሰጣጥ ባህሪ ይመርምሩ እና **+20 Coins** ያሸንፉ!")
    
    scenario_choice = st.radio(
        "ሁኔታ፡ በአንድ ፕሮጀክት ላይ የቡድን አባል ስህተት ፈጥሮ ጊዜ አጥቷል። ምን ያደርጋሉ?",
        [
            "መጀመሪያ ምክንያቱን በትዕግስት አዳምጣለሁ፣ ከዚያ መፍትሄ አመጣለሁ",
            "ቀጥታ ስህተቱን ለሁሉም እገልጻለሁ",
            "ራሴ ብቻዬን ሰርቼ እጨርሰዋለሁ"
        ],
        key="psych_scenario_radio"
    )
    if st.button("የሳይኮሎጂ ውጤቴን እይ እና Coins ውሰድ"):
        if not st.session_state.psych_game_done:
            st.session_state.coins += 20
            st.session_state.score += 20
            st.session_state.psych_game_done = True
            st.balloons()
        if "ትዕግስት" in scenario_choice:
            st.success("🧠 የሳይኮሎጂ ፕሮፋይል፡ **ከፍተኛ ስሜታዊ ብስለት (Emotional Intelligence)** ያለዎት መሪ ነዎት! (+20 Coins)")
        elif "ስህተቱን" in scenario_choice:
            st.info("🧠 የሳይኮሎጂ ፕሮፋይል፡ **ቀጥተኛ እና ግልጽነትን የሚወዱ (Direct & Task-Focused)** ሰው ነዎት! (+20 Coins)")
        else:
            st.info("🧠 የሳይኮሎጂ ፕሮፋይል፡ **ራስን የሚተማመኑ እና ኃላፊነት ወሳኝ (Self-Reliant)** ነዎት! (+20 Coins)")

    st.markdown("---")
    st.markdown("### 🧠 የትኩረት ፈተና (Stroop Focus Psychology Game - ከባድና አእምሮ የሚያላውስ)")
    st.write("⚠️ **መመሪያ:** በቃሉ (Word) አትታለሉ! ጽሑፉ የተጻፈበትን **ቀለም (Ink Color)** ብቻ ይምረጡ። (+30 Coins)")
    st.info(f"🎯 በትክክል የመለሱት የትኩረት ዙሮች: **{st.session_state.stroop_solved_count}**")

    STROOP_ITEMS = [
        {"word": "ቀይ (Red)", "ink_name": "ሰማያዊ (Blue)", "ink_hex": "#1E88E5"},
        {"word": "አረንጓዴ (Green)", "ink_name": "ቀይ (Red)", "ink_hex": "#E53935"},
        {"word": "ቢጫ (Yellow)", "ink_name": "አረንጓዴ (Green)", "ink_hex": "#43A047"},
        {"word": "ሰማያዊ (Blue)", "ink_name": "ቢጫ (Yellow)", "ink_hex": "#FDD835"},
    ]
    if "stroop_current" not in st.session_state:
        st.session_state.stroop_current = random.choice(STROOP_ITEMS)
    stroop_item = st.session_state.stroop_current
    st.markdown(
        f"<div style='text-align:center; padding:18px; border-radius:10px; background:#111827; margin:10px 0;'>"
        f"<span style='font-size:32px; font-weight:bold; color:{stroop_item['ink_hex']};'>{stroop_item['word']}</span>"
        f"</div>",
        unsafe_allow_html=True
    )

    color_options = ["ቀይ (Red)", "ሰማያዊ (Blue)", "አረንጓዴ (Green)", "ቢጫ (Yellow)"]
    chosen_color = st.radio("ጽሑፉ የተጻፈበት ቀለም የቱ ነው?", color_options, key="stroop_color_radio")

    if st.button("የቀለም ትኩረቴን አረጋግጥ (+30 Coins)"):
        if chosen_color == stroop_item["ink_name"]:
            st.session_state.coins += 30
            st.session_state.score += 30
            st.session_state.stroop_solved_count += 1
            st.session_state.stroop_current = random.choice(STROOP_ITEMS)
            st.balloons()
            st.success("🔥 በጣም ጥሩ ትኩረት! አእምሮዎ በቃሉ ሳይታለል ቀለሙን በትክክል ለይቷል። **+30 Coins** አግኝተዋል!")
        else:
            st.error(f"❌ አእምሮዎ በቃሉ ተታለለ! ትክክለኛው የቀለም ቀለም (Ink) **{stroop_item['ink_name']}** ነበር።")
            st.session_state.stroop_current = random.choice(STROOP_ITEMS)
        time.sleep(1)
        st.rerun()

    st.markdown("---")
    st.markdown("### 🎰 ዕድልዎን ይሞክሩ (Lucky Coin Spin)")
    st.info(f"🎮 ያለዎት የጨዋታ ዕድል: **{st.session_state.spin_chances}**")
    
    if st.button("🎲 አሽከርክር (Spin Now!)"):
        if st.session_state.spin_chances > 0:
            st.session_state.spin_chances -= 1
            with st.spinner("🎰 እየተሽከረከረ ነው..."):
                time.sleep(1.5)
            prizes = [5, 10, 15, 25, 50, 0, 20]
            won_coins = random.choice(prizes)
            if won_coins > 0:
                st.session_state.coins += won_coins
                st.session_state.score += won_coins
                st.balloons()
                st.success(f"🎉 እንኳን ደስ አለዎት! **{won_coins} Coins** አሸንፈዋል!")
            else:
                st.warning("😅 በዚህ ዙር አልወጣልዎትም፤ እንደገና ይሞክሩ!")
            time.sleep(1)
            st.rerun()
        else:
            st.error("የጨዋታ ዕድልዎ አልቋል! ተጨማሪ ዕድል ለማግኘት ጥያቄዎችን ይመልሱ።")

    st.markdown("---")
    st.markdown("### 🎯 ቁጥር ገምት (Quick Number Guess - 5 Coins ለመጫወት)")
    guess = st.selectbox("ቁጥር ይምረጡ:", [1, 2, 3, 4, 5], key="num_guess")
    if st.button("ገምት (Guess & Win)"):
        if st.session_state.coins >= 5:
            st.session_state.coins -= 5
            secret_num = random.randint(1, 5)
            if guess == secret_num:
                st.session_state.coins += 25
                st.balloons()
                st.success(f"🔥 ትክክል! ቁጥሩ **{secret_num}** ነበር። **+25 Coins** አሸንፈዋል!")
            else:
                st.error(f"❌ አልተሳካም! ቁጥሩ **{secret_num}** ነበር።")
            time.sleep(1)
            st.rerun()
        else:
            st.warning("ለዚህ ጨዋታ ቢያንስ **5 Coins** ያስፈልግዎታል!")

