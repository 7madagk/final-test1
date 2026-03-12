import streamlit as st
from openai import OpenAI

# إعداد الـ API
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# الـ Prompt ID بتاعك
PROMPT_ID = "pmpt_69b0fd8821a0819584dd64dc7e982545033762b21dcb4523"

# 1. العنوان (من غير ستايل داخلي عشان نتحكم فيه من الـ CSS)
st.markdown("<h1>Math 2 AI Tutor Tester 🤖</h1>", unsafe_allow_html=True)

# 2. بلوك الـ CSS المتكامل (دمجنا الاتنين وظبطنا الماث عشان ييجي في النص)
st.markdown("""
<style>
    /* الفونت العام والاتجاه */
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

    /* السر هنا: تظبيط مقاس العنوان حسب الشاشة */
    h1 {
        text-align: center !important;
        color: white;
    }

    /* 📱 للموبايل (شاشة أصغر من 768px) */
    @media (max-width: 768px) {
        h1 {
            font-size: 26px !important;
            margin-bottom: 10px;
        }
    }

    /* 💻 للاب توب (شاشة أكبر من 768px) */
    @media (min-width: 769px) {
        h1 {
            font-size: 50px !important;
        }
    }

    /* عزل الأكواد البرمجية عشان متتشقلبش */
    code, pre {
        direction: ltr !important;
        unicode-bidi: isolate !important;
        display: inline-block;
    }

    /* 🔴 السر الجديد: تظبيط المعادلات (Math) عشان تظهر في النص بالضبط 🔴 */
    .katex-display {
        text-align: center !important;
        direction: ltr !important;
        display: block !important;
        margin: 1.5em auto !important; /* مسافة فوق وتحت عشان تبروز المعادلة */
    }

    /* تظبيط المعادلات الصغيرة اللي وسط الكلام (Inline Math) */
    .katex {
        direction: ltr !important;
        unicode-bidi: isolate !important;
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
                    response_placeholder.markdown(full_text, unsafe_allow_html=True)

                if hasattr(event, "response") and hasattr(event.response, "usage") and event.response.usage:
                    total_tokens = event.response.usage.total_tokens

            st.session_state.messages.append({"role": "assistant", "content": full_text})

            if total_tokens is not None:
                st.info(f"Tokens المستخدمة في العملية دي: {total_tokens}")
            else:
                st.warning("الـ API مبعتش التوكنز في الاستريم.")

        except Exception as e:
            st.error(f"حصلت مشكلة: {e}")
