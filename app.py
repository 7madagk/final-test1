import streamlit as st
from openai import OpenAI
import re

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
PROMPT_ID = "pmpt_69b0fd8821a0819584dd64dc7e982545033762b21dcb4523"

st.set_page_config(page_title="Math 2 AI Tutor", layout="centered")

st.markdown("<h1 style='text-align: center;'>Math 2 AI Tutor Tester</h1>", unsafe_allow_html=True)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');

.stApp {
    font-family: 'Cairo', 'Arial', sans-serif;
    background-color: #0e1117;
    color: #e0e0e0;
}

[data-testid="stMarkdownContainer"] {
    direction: rtl;
    text-align: right;
    line-height: 2;
    font-size: 16px;
    font-family: 'Cairo', Arial, sans-serif;
}

[data-testid="stMarkdownContainer"] p {
    direction: rtl;
    text-align: right;
    unicode-bidi: plaintext;
}

[data-testid="stMarkdownContainer"] strong,
[data-testid="stMarkdownContainer"] b {
    color: #00bfff;
    font-weight: 700;
}

[data-testid="stMarkdownContainer"] h3 {
    color: #00d4ff;
    border-bottom: 1px solid #00d4ff33;
    padding-bottom: 4px;
    direction: rtl;
    text-align: right;
}

[data-testid="stMarkdownContainer"] code {
    direction: ltr !important;
    unicode-bidi: isolate !important;
    display: inline-block;
    background-color: #1a2035;
    border: 1px solid #00bfff55;
    border-radius: 5px;
    padding: 1px 7px;
    color: #00e5ff;
    font-family: 'Courier New', monospace;
    font-size: 14px;
    text-align: left;
    vertical-align: middle;
}

[data-testid="stMarkdownContainer"] pre {
    direction: ltr !important;
    unicode-bidi: isolate !important;
    text-align: left !important;
    background-color: #111827 !important;
    border: 1px solid #00bfff44 !important;
    border-radius: 10px !important;
    padding: 14px 18px !important;
    overflow-x: auto;
    font-family: 'Courier New', monospace !important;
    font-size: 14px !important;
    color: #e0f7ff !important;
    margin: 12px 0 !important;
}

[data-testid="stMarkdownContainer"] pre code {
    direction: ltr !important;
    background: none !important;
    border: none !important;
    padding: 0 !important;
    color: inherit !important;
    display: block;
}

[data-testid="stMarkdownContainer"] span {
    unicode-bidi: isolate;
}

.stChatInput textarea {
    font-family: 'Cairo', Arial, sans-serif !important;
    direction: rtl;
    font-size: 15px;
}

.stChatMessage { border-radius: 12px !important; margin-bottom: 8px !important; }
.stAlert { direction: rtl; text-align: right; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)


def escape_html(text: str) -> str:
    return (text
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;'))


def process_content(content: str) -> str:
    code_blocks = {}
    counter = [0]

    # حماية code blocks (``` ... ```)
    def save_code_block(m):
        code = m.group(2).strip()
        key = f"CODEBLOCK{counter[0]}ENDBLOCK"
        code_blocks[key] = f'<pre><code>{escape_html(code)}</code></pre>'
        counter[0] += 1
        return key

    content = re.sub(r'```(\w*)\n?([\s\S]*?)```', save_code_block, content)

    # حماية inline code (` ... `)
    inline_codes = {}

    def save_inline(m):
        code = m.group(1)
        key = f"INLINE{counter[0]}ENDINLINE"
        inline_codes[key] = f'<code>{escape_html(code)}</code>'
        counter[0] += 1
        return key

    content = re.sub(r'`([^`\n]+)`', save_inline, content)

    # Bold
    content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content)
    content = re.sub(r'__(.+?)__', r'<strong>\1</strong>', content)

    # Headers
    content = re.sub(r'^### (.+)$', r'<h3>\1</h3>', content, flags=re.MULTILINE)
    content = re.sub(r'^## (.+)$',  r'<h2 style="color:#00d4ff;direction:rtl;text-align:right">\1</h2>', content, flags=re.MULTILINE)
    content = re.sub(r'^# (.+)$',   r'<h1 style="color:#00d4ff;direction:rtl;text-align:right">\1</h1>', content, flags=re.MULTILINE)

    # رجّع الـ code blocks والـ inline
    for key, val in code_blocks.items():
        content = content.replace(key, val)
    for key, val in inline_codes.items():
        content = content.replace(key, val)

    # حماية الـ pre من الـ <br>
    pre_blocks = {}

    def save_pre(m):
        key = f"PREBLOCK{counter[0]}ENDPRE"
        pre_blocks[key] = m.group(0)
        counter[0] += 1
        return key

    content = re.sub(r'<pre>[\s\S]*?</pre>', save_pre, content)
    content = content.replace('\n', '<br>')
    for key, val in pre_blocks.items():
        content = content.replace(key, val)

    return content


def render_message(content: str):
    html = process_content(content)
    wrapped = (
        '<div style="direction:rtl;text-align:right;unicode-bidi:plaintext;'
        'font-family:Cairo,Arial,sans-serif;line-height:2;font-size:16px;">'
        + html +
        '</div>'
    )
    st.markdown(wrapped, unsafe_allow_html=True)


if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        render_message(msg["content"])

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
            placeholder = st.empty()
            total_tokens = None

            for event in stream:
                if getattr(event, "type", "") == "response.output_text.delta":
                    full_text += event.delta
                    placeholder.markdown(full_text + "▌", unsafe_allow_html=True)

                if hasattr(event, "response") and hasattr(event.response, "usage") and event.response.usage:
                    total_tokens = event.response.usage.total_tokens

            placeholder.empty()
            render_message(full_text)

            st.session_state.messages.append({"role": "assistant", "content": full_text})

            if total_tokens is not None:
                st.info(f"🔢 Tokens المستخدمة: {total_tokens}")
            else:
                st.warning("الـ API مبعتش التوكنز في الاستريم.")

        except Exception as e:
            st.error(f"حصلت مشكلة: {e}")
