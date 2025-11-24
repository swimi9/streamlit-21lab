import streamlit as st
from openai import OpenAI
import tempfile

st.title("4. ChatPDF (PDF 기반 챗봇 - File Search)")

# -----------------------------
# 0. API Key 입력
# -----------------------------
api_key = st.text_input("OpenAI API Key를 입력하세요", type="password")
client = OpenAI(api_key=api_key) if api_key else None

# Vector Store ID를 세션에 저장
if "vector_store_id" not in st.session_state:
    st.session_state.vector_store_id = None

# -----------------------------
# 1. PDF 업로드 → Vector Store 생성
# -----------------------------
uploaded_pdf = st.file_uploader("PDF 파일을 업로드하세요", type=["pdf"])

if uploaded_pdf and client:
    # 업로드된 파일을 임시 파일로 저장
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_pdf.read())
        tmp_path = tmp.name

    # 새 vector store 생성 (beta API!)
    vector_store = client.beta.vector_stores.create(name="pdf-store")

    # 파일을 vector store에 업로드 (업로드 끝날 때까지 기다림)
    with open(tmp_path, "rb") as f:
        client.beta.vector_stores.file_batches.upload_and_poll(
            vector_store_id=vector_store.id,
            files=[f],
        )

    st.session_state.vector_store_id = vector_store.id
    st.success("PDF가 업로드되고 Vector Store가 생성되었습니다!")

# -----------------------------
# 2. Vector Store 초기화 버튼
# -----------------------------
if st.button("Clear Vector Store"):
    st.session_state.vector_store_id = None
    st.success("Vector Store가 초기화되었습니다.")

# -----------------------------
# 3. 질문 → Responses + File Search
# -----------------------------
question = st.text_input("PDF 내용에 대해 질문해보세요")
ask_btn = st.button("질문하기")

if ask_btn:
    if not client:
        st.error("먼저 API Key를 입력하세요.")
    elif not st.session_state.vector_store_id:
        st.error("먼저 PDF 파일을 업로드하세요.")
    elif not question.strip():
        st.error("질문을 입력하세요.")
    else:
        # File Search가 걸린 Responses 호출
        resp = client.responses.create(
            model="gpt-5-mini",  # 강의에서 쓰는 모델
            input=question,
            vector_store_ids=[st.session_state.vector_store_id],
        )

        # 텍스트 꺼내기 (Responses 정식 구조)
        try:
            answer = resp.output[0].content[0].text.value
        except Exception:
            answer = str(resp)

        st.write("### 답변")
        st.write(answer)
