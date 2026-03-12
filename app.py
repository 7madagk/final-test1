import streamlit as st
from openai import OpenAI

# 🚀 السطر ده بيفرد الصفحة ويخليها تاخد العرض كله (لازم يكون أول أمر لـ Streamlit) 🚀
st.set_page_config(page_title="Math 2 AI Tutor", layout="wide")

# إعداد الـ API
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# الـ Prompt ID بتاعك
PROMPT_ID = "pmpt_69b0fd8821a0819584dd64dc7e982545033762b21dcb4523"

# 1. العنوان 
st.markdown("<h1>Math 2 AI Tutor Tester 🤖</h1>", unsafe_allow_html=True)

# 2. بلوك الـ CSS المتكامل (عالجنا فيه عرض الموبايل)
st.markdown("""
<style>
    /* الفونت العام والاتجاه */
    .stApp { font-family: 'Arial', sans-serif; }
    
    /* 📱 السر هنا: إجبار Streamlit ياخد عرض الشاشة كله للموبايل واللاب 📱 */
    .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        padding-top: 2rem !important;
        max-width: 100% !important;
    }

    /* تقليل المسافات أكتر لو الشاشة موبايل */
    @media (max-width: 768px) {
        .block-container {
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
        }
    }

    /* إجبار الحاوية الأساسية والنصوص إنها تكون من اليمين للشمال */
    [data-testid="stMarkdownContainer"] {
        direction: rtl !important;
        text-align: right !important;
    }

    /* تظبيط المسافات بتاعت النقط والأرقام (عشان متدخلش لجوه أوي) */
    [data-testid="stMarkdownContainer"] ul, 
    [data-testid="stMarkdownContainer"] ol {
        direction: rtl !important;
        text-align: right !important;
        padding-left: 0 !important; 
        padding-right: 1.5rem !important; /* قللناها عشان الموبايل */
    }

    [data-testid="stMarkdownContainer"] li {
        direction: rtl !important;
        text-align: right !important;
        margin-bottom: 0.5rem !important; 
    }

    /* 🔵 العناوين والمواضيع باللون اللبني 🔵 */
    [data-testid="stMarkdownContainer"] h2, 
    [data-testid="stMarkdownContainer"] h3, 
    [data-testid="stMarkdownContainer"] h4 {
        color: #00bfff !important;
        direction: rtl !important;
        margin-top: 1.5rem !important; 
    }

    /* 🟡 الكلام المهم (الـ Bold) باللون الذهبي/الأصفر 🟡 */
    strong, b { 
        color: #ffd700 !important; 
    }

    /* العنوان الرئيسي للصفحة */
    h1 { text-align: center !important; color: white; }
    @media (max-width: 768px) { h1 { font-size: 26px !important; margin-bottom: 10px; } }
    @media (min-width: 769px) { h1 { font-size: 50px !important; } }

    /* 🔴 الحل النهائي لمعادلات KaTeX 🔴 */
    .katex-display {
        display: block !important;
        text-align: center !important;
        direction: ltr !important;
        width: 100% !important;
        margin: 1.5rem auto !important;
    }

    .katex {
        direction: ltr !important;
        unicode-bidi: embed !important; 
        display: inline-block !important;
    }

    /* عزل الأكواد البرمجية */
    code, pre {
        direction: ltr !important;
        unicode-bidi: embed !important;
        text-align: left !important;
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
                    response_placeholder.markdown(full_text, unsafe_allow_html=True)

                if hasattr(event, "response") and hasattr(event.response, "usage") and event.response.usage:
                    total_tokens = event.response.usage.total_tokens

            st.session_state.messages.append({"role": "assistant", "content": full_text})

            if total_tokens is not None:
                st.info(f"Tokens المستخدمة في العملية دي: {total_tokens}")

        except Exception as e:
            st.error(f"حصلت مشكلة: {e}")
