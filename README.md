# ❤️ Heart Health RAG Assistant

An educational heart-health chatbot built with Retrieval-Augmented Generation (RAG).

## Architecture

User → Safety Layer → Sentence Transformer → Chroma → Strict RAG Prompt → Llama 3.2 3B → Gradio

## Knowledge Sources

- American Heart Association — Life's Essential 8
- World Health Organization — Cardiovascular Diseases

## Safety

The application has dedicated handling for:
- Emergency symptoms
- Medication requests
- Diagnosis requests
- Out-of-context questions

It is an educational prototype and is not a diagnostic tool or a substitute for professional medical care.

## Local / GPU deployment

Set the Hugging Face token as an environment variable:

```bash
export HF_TOKEN="your_token"
```

Then run:

```bash
pip install -r requirements.txt
python app.py
```

The Llama 3.2 3B model is intended to run on GPU for practical performance.
