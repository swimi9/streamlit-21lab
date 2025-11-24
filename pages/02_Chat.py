import streamlit as st
from openai import OpenAI
from streamlit_chat import message   # pip install streamlit-chat 필요

st.title("My ChatBot2")

# -----------------------------
# API Key 관리
# -----------------------------
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

st.session_state.api_key = st.text_input(
    "OpenAI API Key", 
    type="password", 
    value=st.session_state.api_key
)

if st.session_state.api_key:
    client = OpenAI(api_key=st.session_state.api_key)
else:
    client = None


# -----------------------------
# 대화 저장
# -----------------------------
if "past" not in st.session_state:
    st.session_state.past = []   # user messages
if "generated" not in st.session_state:
    st.session_state.generated = []  # bot messages


# -----------------------------
# Clear 버튼
# -----------------------------
if st.button("Clear"):
    st.session_state.past = []
    st.session_state.generated = []


# -----------------------------
# 메시지 렌더링
# -----------------------------
for i in range(len(st.session_state.past)):
    message(st.session_state.past[i], is_user=True, key=f"user_{i}")
    message(st.session_state.generated[i], key=f"bot_{i}")


# -----------------------------
# 입력창
# -----------------------------
user_input = st.chat_input("What is up?")

if user_input:
    if not client:
        st.error("Please enter API Key.")
    else:
        # 유저 메시지 출력
        st.session_state.past.append(user_input)

        # GPT-5-mini Chat Completion 호출
        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                *[
                    {"role": "user", "content": u}
                    for u in st.session_state.past
                ],
            ]
        )

        bot_output = response.choices[0].message.content

        st.session_state.generated.append(bot_output)

        # 화면 리프레시
        st.rerun()
