import streamlit as st
from openai import OpenAI

st.title("2. Chat 페이지 (OpenAI Responses 기반)")

# -----------------------------
# 세션 초기화
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "api_key" not in st.session_state:
    st.session_state.api_key = ""


# -----------------------------
# API Key 입력
# -----------------------------
api_key_input = st.text_input("OpenAI API Key", type="password",
                              value=st.session_state.api_key)

st.session_state.api_key = api_key_input


# -----------------------------
# Clear 버튼
# -----------------------------
if st.button("Clear 대화"):
    st.session_state.messages = []


# -----------------------------
# 이전 메시지 렌더링
# -----------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])


# -----------------------------
# 입력창
# -----------------------------
user_input = st.chat_input("메시지를 입력하세요")

if user_input:
    if not st.session_state.api_key:
        st.error("API Key를 입력하세요.")
    else:
        client = OpenAI(api_key=st.session_state.api_key)

        # 유저 메시지 저장
        st.session_state.messages.append({"role": "user", "content": user_input})

        # 모델 응답 생성
        response = client.responses.create(
            model="gpt-5-mini",
            messages=st.session_state.messages
        )

        bot_text = response.output_text

        st.session_state.messages.append({"role": "assistant", "content": bot_text})

        st.rerun()
