import streamlit as st
from openai import OpenAI
import tempfile

st.title("4. ChatPDF (Assistant + Retrieval 기반)")

api_key = st.text_input("OpenAI API Key", type="password")
client = OpenAI(api_key=api_key) if api_key else None

if "assistant_id" not in st.session_state:
    st.session_state.assistant_id = None

uploaded_pdf = st.file_uploader("PDF 파일 업로드", type=["pdf"])

if uploaded_pdf and client:
    # 임시 저장
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_pdf.read())
        pdf_path = tmp.name

    # 파일 업로드
    file_obj = client.files.create(
        file=open(pdf_path, "rb"),
        purpose="assistants"
    )

    # Assistant 생성 (retrieval tool 자동 사용)
    assistant = client.assistants.create(
        name="PDF Assistant",
        instructions="Uploaded PDF 내용을 기반으로 사용자 질문에 답하세요.",
        model="gpt-5-mini",
        tools=[{"type": "retrieval"}],
        file_ids=[file_obj.id]
    )

    st.session_state.assistant_id = assistant.id

    st.success("PDF 업로드 완료! 이제 질문할 수 있어요.")

# 질문 입력
question = st.text_input("PDF 내용에 대해 질문해보세요")
ask = st.button("질문하기")

if ask:
    if not api_key:
        st.error("API Key를 입력하세요.")
    elif not st.session_state.assistant_id:
        st.error("PDF를 먼저 업로드하세요.")
    else:
        # 스레드 생성 후 메시지 추가
        thread = client.threads.create()
        client.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=question
        )

        # 실행
        run = client.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=st.session_state.assistant_id
        )

        # 메시지 받기
        messages = client.threads.messages.list(thread_id=thread.id)
        answer = messages.data[0].content[0].text.value

        st.write("### 답변:")
        st.write(answer)
