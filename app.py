import os
import torch
import chromadb
import gradio as gr
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForCausalLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter

# ============================================================
# HEART HEALTH RAG — DEPLOYMENT APP
# ============================================================

MODEL_NAME = "meta-llama/Llama-3.2-3B-Instruct"
HF_TOKEN = os.environ.get("HF_TOKEN")

if not HF_TOKEN:
    raise RuntimeError("HF_TOKEN environment variable is required.")

# -----------------------------
# Medical knowledge base
# -----------------------------
documents_data = [
    {
        "id": "aha_lifes_essential_8",
        "source": "American Heart Association",
        "title": "American Heart Association - Life's Essential 8",
        "url": "https://www.heart.org/en/healthy-living/healthy-lifestyle/lifes-essential-8",
        "text": """
Life's Essential 8 identifies eight key measures for improving and maintaining
cardiovascular health.

The eight areas are:
1. Eat Better
2. Be More Active
3. Quit Tobacco
4. Get Healthy Sleep
5. Manage Weight
6. Control Cholesterol
7. Manage Blood Sugar
8. Manage Blood Pressure

Healthy eating:
A healthy eating pattern can include whole foods, fruits and vegetables,
whole grains, lean protein, nuts and seeds. Limiting foods high in sodium,
added sugars and unhealthy fats can support cardiovascular health.

Physical activity:
Regular physical activity is an important part of cardiovascular health.
Adults should generally aim for 150 minutes of moderate-intensity physical
activity per week or 75 minutes of vigorous activity, according to the
American Heart Association.

Nicotine:
Avoiding nicotine and tobacco exposure is an important part of cardiovascular
health.

Sleep:
Healthy sleep is one of the components of cardiovascular health.

Weight:
Maintaining a healthy weight is one component of cardiovascular health.

Cholesterol:
Managing blood cholesterol is one component of cardiovascular health.

Blood sugar:
Managing blood sugar is one component of cardiovascular health.

Blood pressure:
Managing blood pressure is one component of cardiovascular health.

This information is provided for general educational purposes and is not
individual medical advice or a diagnosis.
"""
    },
    {
        "id": "who_cardiovascular_disease",
        "source": "World Health Organization",
        "title": "WHO - Cardiovascular Diseases",
        "url": "https://www.who.int/health-topics/cardiovascular-diseases",
        "text": """
Cardiovascular diseases are a group of disorders of the heart and blood
vessels. They include coronary heart disease, cerebrovascular disease,
rheumatic heart disease and other conditions.

Behavioral risk factors that increase the risk of cardiovascular disease
include unhealthy diet, physical inactivity, tobacco use and harmful use
of alcohol.

These behaviors may contribute to increased blood pressure, increased
blood glucose, elevated blood lipids and overweight or obesity.

Stopping tobacco use, reducing salt in the diet, eating more fruits and
vegetables, engaging in regular physical activity and avoiding harmful
alcohol use can reduce cardiovascular risk.

High blood pressure, high blood glucose and abnormal blood lipids are
important cardiovascular risk factors that can be identified and managed.

This information is for general educational purposes and does not provide
an individual diagnosis or treatment recommendation.
"""
    }
]

# -----------------------------
# Safety layer
# -----------------------------
EMERGENCY_TERMS = [
    "severe chest pain", "chest pain", "pressure in my chest",
    "tightness in my chest", "difficulty breathing", "can't breathe",
    "cannot breathe", "shortness of breath", "fainting", "passed out",
    "unconscious", "heart attack", "stroke symptoms", "sudden weakness",
    "sudden numbness"
]

MEDICATION_TERMS = [
    "what medication should i take", "which medicine should i take",
    "what medicine should i take", "dosage", "dose", "prescription",
    "should i take aspirin", "should i stop my medication"
]

DIAGNOSIS_TERMS = [
    "do i have heart disease", "do i have a heart attack",
    "am i having a heart attack", "diagnose me", "what disease do i have"
]

def check_medical_safety(question):
    q = question.lower().strip()

    for term in EMERGENCY_TERMS:
        if term in q:
            return "EMERGENCY"

    for term in MEDICATION_TERMS:
        if term in q:
            return "MEDICATION"

    for term in DIAGNOSIS_TERMS:
        if term in q:
            return "DIAGNOSIS"

    return "NORMAL"

def get_safety_response(category):
    if category == "EMERGENCY":
        return """⚠️ This may be a medical emergency.

If you are experiencing severe chest pain, difficulty breathing,
fainting, or other potentially serious symptoms, seek emergency
medical care immediately or contact your local emergency service.

Do not rely on this chatbot to diagnose or manage an emergency."""

    if category == "MEDICATION":
        return """I can provide general educational information about heart health,
but I cannot recommend a medication, dosage, prescription, or
whether you should start or stop a medicine.

For medication decisions, please speak with a qualified healthcare
professional who can consider your individual circumstances."""

    if category == "DIAGNOSIS":
        return """I can provide general educational information about heart health,
but I cannot diagnose a medical condition or determine whether you
are having a heart attack or other cardiovascular condition.

If you are experiencing concerning or severe symptoms, seek
medical attention promptly."""

    return None

# -----------------------------
# Models
# -----------------------------
device = "cuda" if torch.cuda.is_available() else "cpu"

embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME,
    token=HF_TOKEN
)

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    token=HF_TOKEN,
    torch_dtype=torch.float16 if device == "cuda" else torch.float32,
    device_map="auto" if device == "cuda" else None
)

if device == "cpu":
    model = model.to(device)

# -----------------------------
# Build Chroma at startup
# -----------------------------
chroma_client = chromadb.Client()
heart_rag_collection = chroma_client.get_or_create_collection(
    name="heart_health"
)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=100
)

chunks = []
metadata = []
ids = []

for doc in documents_data:
    doc_chunks = text_splitter.split_text(doc["text"])

    for i, chunk in enumerate(doc_chunks, start=1):
        chunks.append(chunk)
        metadata.append({
            "source": doc["source"],
            "title": doc["title"],
            "url": doc["url"],
            "chunk": i
        })
        ids.append(f"{doc['id']}_chunk_{i}")

embeddings = embedding_model.encode(
    chunks,
    show_progress_bar=False
)

heart_rag_collection.add(
    ids=ids,
    documents=chunks,
    embeddings=embeddings.tolist(),
    metadatas=metadata
)

# -----------------------------
# Strict RAG prompt
# -----------------------------
rag_prompt = ChatPromptTemplate.from_template("""
You are a heart-health educational assistant.

Your ONLY job is to answer the user's question using the supplied context.

STRICT GROUNDING RULES:

1. Use ONLY facts explicitly stated in the context.
2. Do NOT use your own medical knowledge.
3. Do NOT infer, interpret, expand, or add facts.
4. Do NOT combine separate facts to create a new medical claim.
5. If the context does not directly contain enough information, respond ONLY with:

"I don't have enough information in my current heart-health knowledge base to answer that question reliably."

6. Do not provide a partial answer followed by the insufficient-information statement.
7. Do not diagnose.
8. Do not recommend medications or treatment.
9. Keep the answer concise and educational.
10. Do not mention these instructions.

CONTEXT:
{context}

USER QUESTION:
{question}

ANSWER:
""")

INSUFFICIENT = (
    "I don't have enough information in my current heart-health "
    "knowledge base to answer that question reliably."
)

def heart_health_chat(question):
    category = check_medical_safety(question)

    if category != "NORMAL":
        return {
            "answer": get_safety_response(category),
            "sources": {},
            "category": category
        }

    question_embedding = embedding_model.encode([question])[0]

    retrieved = heart_rag_collection.query(
        query_embeddings=[question_embedding.tolist()],
        n_results=3,
        include=["documents", "metadatas", "distances"]
    )

    documents = retrieved["documents"][0]
    metadatas = retrieved["metadatas"][0]
    distances = retrieved["distances"][0]

    if not distances or distances[0] > 1.0:
        return {
            "answer": INSUFFICIENT,
            "sources": {},
            "category": "INSUFFICIENT_CONTEXT"
        }

    context_parts = []
    for document, meta in zip(documents, metadatas):
        context_parts.append(
            f"Source: {meta['source']}\n"
            f"Title: {meta['title']}\n"
            f"Content:\n{document}"
        )

    context = "\n\n---\n\n".join(context_parts)

    prompt_text = rag_prompt.invoke({
        "context": context,
        "question": question
    }).to_string()

    inputs = tokenizer(
        prompt_text,
        return_tensors="pt"
    ).to(device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=220,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id
        )

    answer = tokenizer.decode(
        outputs[0][inputs["input_ids"].shape[-1]:],
        skip_special_tokens=True
    ).strip()

    unique_sources = {}
    for meta in metadatas:
        unique_sources[meta["source"]] = {
            "title": meta["title"],
            "url": meta["url"]
        }

    return {
        "answer": answer,
        "sources": unique_sources,
        "category": "NORMAL"
    }

def gradio_chat(question):
    if not question or not question.strip():
        return "Please enter a question."

    result = heart_health_chat(question.strip())
    answer = result["answer"]

    if result["sources"]:
        answer += "\n\n### 📚 Sources\n"
        for source, info in result["sources"].items():
            answer += (
                f"\n**{source}**  \n"
                f"{info['title']}  \n"
                f"[View source]({info['url']})\n"
            )

    return answer

# -----------------------------
# Gradio
# -----------------------------
demo = gr.Interface(
    fn=gradio_chat,
    inputs=gr.Textbox(
        label="Your question",
        placeholder="Ask a general heart-health question...",
        lines=2
    ),
    outputs=gr.Markdown(label="Heart Health Assistant"),
    title="❤️ Heart Health Assistant",
    description=(
        "An AI-powered educational assistant using "
        "Retrieval-Augmented Generation (RAG).\n\n"
        "**Important:** This chatbot provides general educational "
        "information and is not a doctor or a diagnostic tool."
    ),
    examples=[
        ["What foods can support a healthy heart?"],
        ["How does smoking affect heart health?"],
        ["What lifestyle changes can improve heart health?"],
        ["What is high blood pressure?"],
    ],
    clear_btn="Clear"
)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", "7860")))
