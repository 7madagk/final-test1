import streamlit as st
from openai import OpenAI
import re

# إعداد الـ API
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# الـ Prompt ID بتاعك
PROMPT_ID = "pmpt_69b0fd8821a0819584dd64dc7e982545033762b21dcb4523"

# ضبط الصفحة
st.set_page_config(page_title="Math 2 AI Tutor", layout="centered")

# كود العنوان
st.markdown("<h1 style='text-align: center;'>Math 2 AI Tutor Tester</h1>", unsafe_allow_html=True)

# CSS شامل
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');

.stApp {
    font-family: 'Cairo', 'Arial', sans-serif;
    background-color: #0e1117;
    color: #e0e0e0;
}

/* RTL للمحتوى العربي */
[data-testid="stMarkdownContainer"] {
    direction: rtl !important;
    text-align: right !important;
    line-height: 1.9 !important;
    font-size: 16px;
}

[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] ul,
[data-testid="stMarkdownContainer"] ol {
    direction: rtl !important;
    text-align: right !important;
}

/* المعادلات الرياضية تبقى LTR */
[data-testid="stMarkdownContainer"] code,
[data-testid="stMarkdownContainer"] pre {
    direction: ltr !important;
    unicode-bidi: isolate !important;
    display: block;
    background-color: #1e2533 !important;
    border: 1px solid #00bfff44 !important;
    border-radius: 8px !important;
    padding: 10px 16px !important;
    margin: 10px 0 !important;
    color: #e0f7ff !important;
    font-family: 'Courier New', monospace !important;
    font-size: 15px !important;
    text-align: left !important;
    overflow-x: auto;
}

/* الـ inline code */
[data-testid="stMarkdownContainer"] p code {
    display: inline !important;
    padding: 2px 6px !important;
    background-color: #1e2533 !important;
    border-radius: 4px !important;
    color: #00e5ff !important;
}

/* الـ Bold بلون مميز */
strong, b {
    color: #00bfff !important;
    font-weight: 700;
}

/* الـ h3 */
h3 {
    color: #00d4ff !important;
    border-bottom: 1px solid #00d4ff33;
    padding-bottom: 4px;
}

/* رسائل الشات */
.stChatMessage {
    border-radius: 12px !important;
    margin-bottom: 8px !important;
}

/* الـ info box */
.stAlert {
    direction: rtl;
    text-align: right;
    border-radius: 10px;
}

/* input الكتابة */
.stChatInput textarea {
    font-family: 'Cairo', Arial, sans-serif !important;
    direction: rtl;
    font-size: 15px;
}
</style>
""", unsafe_allow_html=True)


def render_message(content: str):
    """
    بيعرض الرسالة مع:
    - HTML styling (ألوان، عناوين)
    - المعادلات الرياضية في كود بلوك مستقل
    """
    # نقسم المحتوى على أساس code blocks (``` ... ```) أو inline code (` ... `)
    # ونعرض كل جزء منفصل عشان الـ RTL/LTR يتحكم فيه صح

    # الحل: نفصل الـ code blocks عن باقي النص ونعرضهم كـ st.code
    parts = re.split(r'(```[\s\S]*?```|`[^`]+`)', content)

    for part in parts:
        if part.startswith("```") and part.endswith("```"):
            # code block كامل
            inner = re.sub(r'^```\w*\n?', '', part)
            inner = re.sub(r'```$', '', inner).strip()
            st.code(inner, language=None)

        elif part.startswith("`") and part.endswith("`") and len(part) > 2:
            # inline code - نعرضه كـ code block صغير
            inner = part[1:-1]
            st.code(inner, language=None)

        else:
            # نص عادي أو HTML
            if part.strip():
                st.markdown(part, unsafe_allow_html=True)


# تهيئة الـ session
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض المحادثة السابقة
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        render_message(msg["content"])

# إدخال المستخدم
user_input = st.chat_input("اكتب رسالتك هنا...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        try:
            stream = client.responses.create(
                model="gpt-4o-mini",
                prompt={"id": PROMPT_ID},
                input=st.session_state.messages,
                stream=True
            )

            full_text = ""
            response_placeholder = st.empty()
            total_tokens = None

            for event in stream:
                if getattr(event, "type", "") == "response.output_text.delta":
                    full_text += event.delta
                    # أثناء الـ streaming نعرض النص كما هو
                    response_placeholder.markdown(full_text + "▌", unsafe_allow_html=True)

                if hasattr(event, "response") and hasattr(event.response, "usage") and event.response.usage:
                    total_tokens = event.response.usage.total_tokens

            # بعد ما الـ stream خلص، نمسح الـ placeholder ونعرض بـ render_message
            response_placeholder.empty()
            render_message(full_text)

            st.session_state.messages.append({"role": "assistant", "content": full_text})

            if total_tokens is not None:
                st.info(f"🔢 Tokens المستخدمة في العملية دي: {total_tokens}")
            else:
                st.warning("الـ API مبعتش التوكنز في الاستريم.")

        except Exception as e:
            st.error(f"حصلت مشكلة: {e}")
