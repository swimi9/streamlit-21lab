import streamlit as st
from openai import OpenAI

st.title("1. GPT-5-mini 질의응답")

# --------------------------
# API KEY 입력 + session_state 저장
# --------------------------
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

api_key_input = st.text_input("OpenAI API Key를 입력하세요", 
                              type="password",
                              value=st.session_state.api_key)

st.session_state.api_key = api_key_input

# --------------------------
# 캐시 기능 (같은 질문이면 재사용)
# --------------------------
@st.cache_data
def ask_gpt(api_key, question):
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[{"role": "user", "content": question}],
    )
    return response.choices[0].message.content

# --------------------------
# 질문 입력
# --------------------------
question = st.text_input("질문을 입력하세요")
submit = st.button("질문 보내기")

if submit:
    if not st.session_state.api_key:
        st.error("API Key를 입력하세요.")
    elif not question.strip():
        st.error("질문을 입력하세요.")
    else:
        answer = ask_gpt(st.session_state.api_key, question)
        st.write("### 응답:")
        st.write(answer)
