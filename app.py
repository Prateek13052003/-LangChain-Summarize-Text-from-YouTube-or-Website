import validators
import streamlit as st

from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain.chains.summarize import load_summarize_chain
from langchain_community.document_loaders import (
    YoutubeLoader,
    UnstructuredURLLoader
)
from youtube_transcript_api import NoTranscriptFound

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="LangChain: Summarize YouTube / Website",
    page_icon="👽"
)

st.title("☠️ LangChain: Summarize Text from YouTube or Website")

# ---------------- SIDEBAR ----------------
with st.sidebar:
    groq_api_key = st.text_input("Groq API Key", type="password")

# ---------------- URL INPUT ----------------
generic_url = st.text_input("Enter YouTube or Website URL")

# ---------------- SAFE GROQ MODELS ----------------
CANDIDATE_GROQ_MODELS = [
    "llama-3.1-8b-instant",
    "llama-3.1-70b-versatile",
    "mixtral-8x7b-32768",
    "gemma2-9b-it",
]

def get_working_groq_model(api_key):
    """Return first working Groq model for this API key"""
    for model in CANDIDATE_GROQ_MODELS:
        try:
            llm = ChatGroq(
                groq_api_key=api_key,
                model_name=model,
                timeout=5
            )
            llm.invoke("ping")
            return model
        except Exception:
            continue
    return None

# ---------------- BUTTON ----------------
if st.button("Summarize the content"):

    if not groq_api_key or not generic_url:
        st.error("❌ Please provide Groq API Key and URL")
        st.stop()

    if not validators.url(generic_url):
        st.error("❌ Invalid URL")
        st.stop()

    if "list=" in generic_url:
        st.error("❌ Please provide a direct YouTube video URL (not a playlist URL)")
        st.stop()

    with st.spinner("Checking available Groq models..."):
        model_name = get_working_groq_model(groq_api_key)

    if not model_name:
        st.error("❌ No working Groq models available for this API key")
        st.stop()

    try:
        with st.spinner("Loading content..."):

            # ---------- LOAD DATA ----------
            if "youtube.com" in generic_url or "youtu.be" in generic_url:
                try:
                    loader = YoutubeLoader.from_youtube_url(
                        generic_url,
                        add_video_info=False,
                        language=["en"]
                    )
                    data = loader.load()

                except NoTranscriptFound:
                    # fallback to Hindi
                    loader = YoutubeLoader.from_youtube_url(
                        generic_url,
                        add_video_info=False,
                        language=["hi"]
                    )
                    data = loader.load()
            else:
                loader = UnstructuredURLLoader(
                    urls=[generic_url],
                    ssl_verify=False,
                    headers={"User-Agent": "Mozilla/5.0"}
                )
                data = loader.load()

            if not data or not data[0].page_content.strip():
                st.error("❌ No usable text found to summarize")
                st.stop()

        # ---------- LLM ----------
        llm = ChatGroq(
            groq_api_key=groq_api_key,
            model_name=model_name
        )

        prompt = PromptTemplate(
            template="""
            The following text may be in Hindi or English.
            If it is in Hindi, first translate it into English.
            Then provide a concise and clear summary.

            TEXT:
            {text}

            SUMMARY:
            """,
            input_variables=["text"]
        )

        # ---------- SUMMARIZATION ----------
        chain = load_summarize_chain(
            llm=llm,
            chain_type="stuff",
            prompt=prompt
        )

        with st.spinner("Generating summary..."):
            summary = chain.run(data)

        st.success(f"✅ Summary Generated using `{model_name}`")
        st.write(summary)

    except Exception as e:
        st.error("❌ Something went wrong")
        st.exception(e)
