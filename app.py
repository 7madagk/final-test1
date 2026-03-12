import streamlit as st
from openai import OpenAI

# إعداد الـ API
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# الـ Prompt ID بتاعك
PROMPT_ID = "pmpt_69b0fd8821a0819584dd64dc7e982545033762b21dcb4523"

# 1. العنوان (من غير ستايل داخلي عشان نتحكم فيه من الـ CSS)
st.markdown("<h1>Math 2 AI Tutor Tester 🤖</h1>", unsafe_allow_html=True)

# 2. بلوك الـ CSS المتكامل (شامل الألوان والماث)
st.markdown("""
<style>
    /* الفونت العام والاتجاه */
    .stApp { font-family: 'Arial', sans-serif; }
    
    /* إجبار الحاوية الأساسية والنصوص إنها تكون من اليمين للشمال */
    [data-testid="stMarkdownContainer"] {
        direction: rtl !important;
        text-align: right !important;
    }

    /* 🟢 السر هنا: تظبيط المسافات بتاعت النقط والأرقام (Lists Fix) 🟢 */
    [data-testid="stMarkdownContainer"] ul, 
    [data-testid="stMarkdownContainer"] ol {
        direction: rtl !important;
        text-align: right !important;
        padding-left: 0 !important; /* بنلغي المسافة الأجنبي اللي على الشمال */
        padding-right: 2rem !important; /* بنحط المسافة الصح على اليمين */
    }

    [data-testid="stMarkdownContainer"] li {
        direction: rtl !important;
        text-align: right !important;
        margin-bottom: 0.5rem !important; /* مسافة خفيفة بين السطور عشان شكلها يبقى أنضف */
    }

    /* 🔵 العناوين والمواضيع (Topics) باللون اللبني 🔵 */
    [data-testid="stMarkdownContainer"] h2, 
    [data-testid="stMarkdownContainer"] h3, 
    [data-testid="stMarkdownContainer"] h4 {
        color: #00bfff !important;
        direction: rtl !important;
        margin-top: 1.5rem !important; /* مسافة فوق العنوان عشان ميبقاش لازق في اللي قبله */
    }

    /* 🟡 الكلام المهم (الـ Bold) باللون الذهبي/الأصفر 🟡 */
    strong, b { 
        color: #ffd700 !important; 
    }

    /* العنوان الرئيسي للصفحة يفضل أبيض وفي النص */
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

