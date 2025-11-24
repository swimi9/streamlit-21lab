import streamlit as st
from openai import OpenAI
import tempfile
import pypdf

st.title("4. ChatPDF (간단 버전)")

# 0. API Key
api_key = st.text_input("OpenAI API Key를 입력하세요", type="password")
client = OpenAI(api_key=api_key) if api_key else None

# 업로드한 PDF 텍스트를 세션에 저장
if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""

# 1) PDF 업로드
uploaded_pdf = st.file_uploader("PDF 파일을 업로드하세요", type=["pdf"])

if uploaded_pdf and client:
    # 임시 파일로 저장
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_pdf.read())
        tmp_path = tmp.name

    # pypdf로 내용 읽기
    reader = pypdf.PdfReader(tmp_path)
    all_text = ""
    for page in reader.pages:
        try:
            all_text += page.extract_text() or ""
        except Exception:
            pass

    if not all_text.strip():
        st.warning("PDF에서 텍스트를 추출하지 못했습니다. 스캔본 이미지 PDF일 수 있어요.")
    else:
        st.session_state.pdf_text = all_text
        st.success("PDF 텍스트를 성공적으로 불러왔습니다!")

# 2) 질문 입력
question = st.text_input("PDF 내용에 대해 질문해보세요")
ask_btn = st.button("질문하기")

if ask_btn:
    if not client:
        st.error("먼저 API Key를 입력하세요.")
    elif not st.session_state.pdf_text.strip():
        st.error("먼저 PDF를 업로드해서 텍스트를 불러오세요.")
    elif not question.strip():
        st.error("질문을 입력하세요.")
    else:
        # 너무 길면 앞부분만 잘라서 사용 (토큰 절약)
        context = st.session_state.pdf_text[:12000]

        prompt = f"""
다음은 사용자가 업로드한 PDF의 텍스트 일부야.

--- PDF 내용 ---
{context}
----------------

위 내용을 참고해서, 다음 질문에 한국어로 자세하게 답해줘.

질문: {question}
"""

        with st.spinner("PDF 내용을 기반으로 답변 생성 중..."):
            resp = client.chat.completions.create(
                model="gpt-5-mini",
                messages=[
                    {"role": "user", "content": prompt}
                ],
            )

        answer = resp.choices[0].message.content
        st.write("### 답변")
        st.write(answer)
