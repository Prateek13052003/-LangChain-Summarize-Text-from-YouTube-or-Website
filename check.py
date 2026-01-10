from langchain_groq import ChatGroq

GROQ_API_KEY = "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"

# Candidate models that exist in Groq ecosystem
CANDIDATE_MODELS = [
    "llama-3.1-8b-instant",
    "llama-3.1-70b-versatile",
    "mixtral-8x7b-32768",
    "gemma2-9b-it",
]

print("Checking models for THIS API key:\n")

for model in CANDIDATE_MODELS:
    try:
        llm = ChatGroq(
            groq_api_key=GROQ_API_KEY,
            model_name=model,
            timeout=5
        )
        llm.invoke("ping")
        print(f"✅ AVAILABLE: {model}")

    except Exception as e:
        print(f"❌ NOT AVAILABLE: {model}")
