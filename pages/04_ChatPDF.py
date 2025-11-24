import streamlit as st
from openai import OpenAI
import tempfile

st.title("4. ChatPDF (File search 버전)")

# 0. API Key
api_key = st.text_input("OpenAI API Key를 입력하세요", type="password")
client = OpenAI(api_key=api_key) if api_key else None

# Vector store ID 보관
if "vector_store_id" not in st.session_state:
    st.session_state.vector_store_id = None

# 1. PDF 업로드 → 파일 + 벡터스토어 생성
uploaded_pdf = st.file_uploader("PDF 파일을 업로드하세요", type=["pdf"])

if uploaded_pdf and client:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_pdf.read())
        tmp_path = tmp.name

    # 파일 업로드
    file_obj = client.files.create(
        file=open(tmp_path, "rb"),
        purpose="assistants"
    )

    # 벡터스토어 생성 + 파일 바로 연결
    vector_store = client.vector_stores.create(
        name="pdf-store",
        file_ids=[file_obj.id],
    )

    st.session_state.vector_store_id = vector_store.id
    st.success("PDF 업로드 및 Vector Store 생성 완료!")

# 2. 초기화 버튼
if st.button("Clear Vector Store"):
    st.session_state.vector_store_id = None
    st.success("Vector Store가 초기화되었습니다.")

# 3. 질문 → File Search + Responses
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
        resp = client.responses.create(
            model="gpt-5-mini",
            input=question,
            tools=[{
                "type": "file_search",
                "vector_store_ids": [st.session_state.vector_store_id],
            }],
        )

        # 답변 텍스트 뽑기
        answer = getattr(resp, "output_text", None)
        if answer is None:
            try:
                answer = resp.output[0].content[0].text.value
            except Exception:
                answer = str(resp)

        st.write("### 답변")
        st.write(answer)
