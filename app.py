import streamlit as st
import random

# የገጹ አቀማመጥ (Page Configuration)
st.set_page_config(
    page_title="Smart Quiz & Reward App",
    page_icon="🎁",
    layout="centered"
)

# የስታይል ማስተካከያ (Custom CSS Styling)
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# ርዕስ እና መግቢያ
st.title("🧠 Smart Quiz, Psychology & Reward App")
st.write("እውቀትዎን እያዳበሩ፣ ጥያቄዎችን በመጨመር እና ፈተናዎችን በመፈተን ነጥብ (Points) ይሰብስቡ!")

# የሰስተር ስቴት (Session State) ለነጥቦች እና ለጥያቄዎች ማከማቻ
if "points" not in st.session_state:
    st.session_state.points = 10  # ለመጀመሪያ መግቢያ የሚሆን ቦነስ ነጥብ

if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = {
        "General Knowledge": [
            {
                "question": "የኢትዮጵያ ንግድ ባንክ (CBE) የተመሰረተበት ዓመተ ምህረት ስንት ነው?",
                "options": ["1942 እ.ኤ.አ", "1960 እ.ኤ.አ", "1908 እ.ኤ.አ", "1950 እ.ኤ.አ"],
                "answer": "1908 እ.ኤ.አ"
            }
        ],
        "Psychology & Mindset": [
            {
                "question": "ሰዎች አዳዲስ ልማዶችን ለመልመድ በአማካይ ስንት ቀናት ይወስድባቸዋል ተብሎ ይታመናል?",
                "options": ["7 ቀናት", "21 ቀናት", "66 ቀናት", "365 ቀናት"],
                "answer": "66 ቀናት"
            }
        ],
        "Python Programming": [
            {
                "question": "ለተጠቃሚዎች ዳታ ለማሳየት በ Streamlit የምንጠቀመው ትዕዛዝ የቱ ነው?",
                "options": ["print()", "echo()", "st.write()", "display()"],
                "answer": "st.write()"
            }
        ]
    }

# የጎንዮሽ ምናሌ (Sidebar Navigation)
menu = st.sidebar.selectbox(
    "ምናሌ ይምረጡ (Menu):",
    ["ፈተና መውሰድ (Take Quiz)", "ጥያቄ ማከል (Add Question)", "የኔ ነጥብ እና ሽልማት (Points & Rewards)"]
)

# የነጥብ ማሳያ በሲድባር ላይ
st.sidebar.divider()
st.sidebar.metric(label="💰 ያገኙት ጠቅላላ ነጥብ (Points)", value=f"{st.session_state.points} ነጥብ")

# 1. ፈተና የመውሰድ ክፍል
if menu == "ፈተና መውሰድ (Take Quiz)":
    st.subheader("📝 ፈተና ይውሰዱ")
    category = st.selectbox("ምድብ ይምረጡ:", list(st.session_state.quiz_data.keys()))
    
    questions = st.session_state.quiz_data[category]
    score = 0

    for i, q in enumerate(questions):
        st.write(f"**ጥያቄ {i+1}: {q['question']}**")
        user_choice = st.radio(f"ምርጫ ({i+1}):", q['options'], key=f"q_{category}_{i}")
        
        if user_choice == q['answer']:
            score += 1
        st.write("---")

    if st.button("ውጤቴን አስረክብ (Submit Quiz)"):
        earned_points = score * 5
        st.session_state.points += earned_points
        st.success(f"🎉 እንኳን ደስ አለዎት! ከ {len(questions)} ውስጥ {score} በትክክል መልሰዋል። +{earned_points} ነጥብ አግኝተዋል!")
        st.balloons()

# 2. ጥያቄ የማከያ ክፍል (Add Question)
elif menu == "ጥያቄ ማከል (Add Question)":
    st.subheader("✍️ አዲስ ጥያቄ ይጨምሩ (ነጥብ ያግኙ!)")
    st.write("ጥያቄዎችን በመጨመር አፕሊኬሽኑን እንዲያድግ ያግዙ፤ ለእያንዳንዱ የተሳካ ጥያቄ **20 ነጥብ** ያገኛሉ!")

    with st.form("add_question_form"):
        new_category = st.selectbox("የጥያቄው ምድብ:", list(st.session_state.quiz_data.keys()))
        new_q = st.text_input("ጥያቄውን እዚህ ይጻፉ:")
        opt1 = st.text_input("ምርጫ 1 (ትክክለኛውን መልስ ጨምሮ)")
        opt2 = st.text_input("ምርጫ 2")
        opt3 = st.text_input("ምርጫ 3")
        opt4 = st.text_input("ምርጫ 4")
        correct_ans = st.text_input("ትክክለኛው መልስ (ልክ ከላይ ከጻፏቸው ምርጫዎች አንዱን በትክክል ይጻፉ):")
        
        submit_btn = st.form_submit_button("ጥያቄውን አስገባ (Submit)")
        
        if submit_btn:
            if new_q and opt1 and opt2 and opt3 and opt4 and correct_ans:
                new_question_dict = {
                    "question": new_q,
                    "options": [opt1, opt2, opt3, opt4],
                    "answer": correct_ans
                }
                st.session_state.quiz_data[new_category].append(new_question_dict)
                st.session_state.points += 20  # ለጥያቄ ማስተዋጽኦ የሚሰጥ ቦነስ
                st.success("✅ ጥያቄዎ በተሳካ ሁኔታ ታክሏል! +20 ነጥብ ተሸልመዋል!")
            else:
                st.warning("⚠️ እባክዎ ሁሉንም ባዶ ቦታዎች በትክክል ይሙሉ!")

# 3. ነጥቦች እና ሽልማት ክፍል
elif menu == "የኔ ነጥብ እና ሽልማት (Points & Rewards)":
    st.subheader("🎁 የነጥብ እና የሽልማት ማዕከል")
    st.write(f"አሁን ላይ ያሎት ጠቅላላ ሚዛን: **{st.session_state.points} ነጥብ**")
    
    st.info("💡 **እንዴት ነጥብ ማግኘት ይቻላል?**\n- ጥያቄዎችን በትክክል በመመለስ\n- አዳዲስ ጥያቄዎችን ወደ አፑ በመጨመር\n- አፑን ለጓደኞችዎ በማካፈል (Sharing)")
    
    if st.button("ነጥቤን ወደ ገንዘብ / የሞባይል ካርድ መቀየሪያ (Redeem) ጠይቅ"):
        if st.session_state.points >= 100:
            st.success("🎉 የሽልማት ጥያቄዎ ተመዝግቧል! አስተዳዳሪው በቅርቡ ያነጋግርዎታል።")
        else:
            st.warning("⚠️ ሽልማት ለመጠየቅ ቢያንስ 100 ነጥብ ሊኖርዎት ይገባል። እባክዎ ተጨማሪ ፈተናዎችን ይውሰዱ ወይም ጥያቄዎችን ይጨምሩ!")


