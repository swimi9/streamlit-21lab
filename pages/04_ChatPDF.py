import streamlit as st
from openai import OpenAI
import tempfile

st.title("4. ChatPDF (PDF 기반 챗봇)")

# API Key
api_key = st.text_input("OpenAI API Key", type="password")
client = OpenAI(api_key=api_key) if api_key else None

# Vector Store 저장용
if "vector_store_id" not in st.session_state:
    st.session_state.vector_store_id = None

uploaded = st.file_uploader("PDF 파일 업로드", type=["pdf"])

if uploaded and client:
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(uploaded.read())
        pdf_path = tmp.name

    # Upload
    file = client.files.create(file=open(pdf_path, "rb"), purpose="assistants")

    # Create Vector Store
    store = client.vector_stores.create(name="pdf-store")
    client.vector_stores.files.add(store.id, file_ids=[file.id])

    st.session_state.vector_store_id = store.id
    st.success("PDF가 성공적으로 처리되었습니다.")

# Clear 버튼
if st.button("Clear Vector Store"):
    st.session_state.vector_store_id = None
    st.success("Vector Store 삭제됨.")

# 질문
question = st.text_input("PDF 내용에 대해 질문해보세요.")
ask = st.button("질문하기")

if ask:
    if not api_key:
        st.error("API Key 입력 필요.")
    elif not st.session_state.vector_store_id:
        st.error("먼저 PDF 파일을 업로드하세요.")
    else:
        run = client.responses.create(
            model="gpt-5-mini",
            vector_store_ids=[st.session_state.vector_store_id],
            input=question
        )
        st.write(run.output_text)
