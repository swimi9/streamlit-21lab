import streamlit as st
from openai import OpenAI
import tempfile

st.title("4. ChatPDF (PDF 기반 챗봇)")

# -----------------------------
# API Key 입력
# -----------------------------
api_key = st.text_input("OpenAI API Key를 입력하세요", type="password")

if api_key:
    client = OpenAI(api_key=api_key)
else:
    client = None

# Vector Store 유지
if "vector_store_id" not in st.session_state:
    st.session_state.vector_store_id = None


# -----------------------------
# 1) PDF 업로드 → File → Vector Store 생성
# -----------------------------
uploaded_pdf = st.file_uploader("PDF 파일 업로드", type=["pdf"])

if uploaded_pdf and client:

    # 임시 파일로 변환
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_pdf.read())
        tmp_path = tmp.name

    # PDF 파일 업로드 (assistants 용도)
    file_obj = client.files.create(
        file=open(tmp_path, "rb"),
        purpose="assistants"
    )

    # 벡터스토어 생성
    vector_store = client.vector_stores.create(name="pdf-store")

    client.vector_stores.add_files(
        vector_store_id=vector_store.id,
        file_ids=[file_obj.id]
    )

    st.session_state.vector_store_id = vector_store.id

    st.success("PDF 업로드 및 Vector Store 생성 완료!")


# -----------------------------
# 2) Vector Store 삭제 기능
# -----------------------------
if st.button("Clear Vector Store"):
    st.session_state.vector_store_id = None
    st.success("Vector Store 제거됨.")


# -----------------------------
# 3) 질문 → PDF 기반 검색 + 답변 생성
# -----------------------------
question = st.text_input("PDF 내용과 관련된 질문을 입력하세요")
ask_btn = st.button("질문하기")

if ask_btn:
    if not client:
        st.error("API Key를 먼저 입력하세요.")
    elif not st.session_state.vector_store_id:
        st.error("먼저 PDF를 업로드하세요.")
    else:
        response = client.responses.create(
            model="gpt-5-mini",
            input=question,
            vector_store_ids=[st.session_state.vector_store_id]
        )

        st.write("### 답변:")
        st.write(response.output_text)
