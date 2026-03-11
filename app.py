import streamlit as st
from openai import OpenAI

# إعداد الـ API

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# الـ Prompt ID بتاعك
PROMPT_ID = "pmpt_69b0fd8821a0819584dd64dc7e982545033762b21dcb4523"
# كود العنوان في النص
st.markdown("<h1 style='text-align: center;'>Math 2 AI Tutor Tester</h1>", unsafe_allow_html=True)

# كود الـ CSS لضبط العربي والماث والألوان
st.markdown("""
<style>
/* الفونت العام */
.stApp, .stChatMessage, .stChatInput textarea {
    font-family: 'Arial', sans-serif;
}

/* إجبار الحاوية الأساسية والنصوص إنها تكون من اليمين للشمال */
[data-testid="stMarkdownContainer"] {
    direction: rtl !important;
    text-align: right !important;
}

[data-testid="stMarkdownContainer"] p, 
[data-testid="stMarkdownContainer"] ul, 
[data-testid="stMarkdownContainer"] ol {
    direction: rtl !important;
    text-align: right !important;
}

/* السر هنا: عزل الماث والإنجليزي عشان ميتشقلبش وسط العربي */
code, pre, .katex, .katex-html {
    direction: ltr !important;
    unicode-bidi: isolate !important;
    display: inline-block;
}

/* تلوين الكلام المهم (الـ Bold) بلون لبني */
strong, b {
    color: #00bfff !important; 
}
</style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)

user_input = st.chat_input("اكتب رسالتك هنا...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

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
                    response_placeholder.markdown(
                        full_text, unsafe_allow_html=True)

                if hasattr(event, "response") and hasattr(event.response, "usage") and event.response.usage:
                    total_tokens = event.response.usage.total_tokens

            st.session_state.messages.append(
                {"role": "assistant", "content": full_text})

            if total_tokens is not None:
                st.info(f"Tokens المستخدمة في العملية دي: {total_tokens}")
            else:
                st.warning("الـ API مبعتش التوكنز في الاستريم.")

        except Exception as e:
            st.error(f"حصلت مشكلة: {e}")
