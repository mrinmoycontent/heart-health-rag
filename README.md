# ❤️ Heart Health Assistant

🌐 Live App: https://heart-health-rag.vercel.app/
The Heart Health Assistant is an AI-powered educational web application that uses Retrieval-Augmented Generation (RAG) to provide source-grounded information about heart health. Users can ask general questions about healthy eating, physical activity, smoking and tobacco, sleep, weight, cholesterol, blood sugar, blood pressure, and cardiovascular health. The application retrieves relevant information from a curated heart-health knowledge base and uses an AI model to generate concise educational responses.

The current knowledge base contains information from the American Heart Association's Life's Essential 8 and the World Health Organization's Cardiovascular Diseases resources. The application displays supporting sources with normal answers so users can identify where the information comes from.

The application also includes a medical safety layer. Questions involving potentially serious symptoms such as severe chest pain, difficulty breathing, shortness of breath, fainting, unconsciousness, heart attack, or stroke symptoms receive an emergency safety response instead of a normal AI-generated answer. Medication-related questions are also handled separately, and the assistant does not recommend medication, dosage, prescriptions, or whether a person should start or stop a medicine.

The assistant does not diagnose medical conditions. Questions asking whether a user has heart disease, whether they are having a heart attack, or asking for a diagnosis receive a safety response explaining that the application cannot provide an individual medical diagnosis. Users with concerning or severe symptoms are advised to seek appropriate medical attention.

The RAG workflow starts when a user enters a question. The application first performs safety classification. If the question does not fall into a safety category, the application searches the available knowledge base for relevant information. The retrieved information is then provided as context to the AI model. The model is instructed to answer only from the supplied context and not to introduce unsupported information. If the knowledge base does not contain enough information, the application returns an insufficient-information response.

The application has been tested with different types of questions, including heart-healthy foods, reducing salt, physical activity, medication questions, emergency symptoms, and diagnosis questions. Normal questions successfully return educational answers with supporting sources, while medication, emergency, and diagnosis questions trigger the appropriate safety responses.

The backend API is deployed using Vercel. The API health check returns a response confirming that the Heart Health RAG API is running. The application uses Python, Retrieval-Augmented Generation, Hugging Face, Vercel, and a Python HTTP API as its main technologies.

The project uses an environment variable called `HF_TOKEN` for AI authentication. The actual token must never be placed inside the source code, README, or GitHub repository. It should remain securely stored as an environment variable in the deployment platform.

This project is intended for general educational purposes only. It does not provide individual medical advice, medical diagnosis, treatment recommendations, medication recommendations, or emergency medical management. Users experiencing potentially serious symptoms should seek appropriate emergency medical care rather than relying on this application.

The current project is a working prototype demonstrating RAG, document retrieval, context-grounded AI generation, source attribution, medical safety controls, and cloud deployment.

## Project Status

Working Prototype ✅

## Live Demo

🌐 Heart Health Assistant: https://heart-health-rag-mrinmoyseo-s-projects.vercel.app

## Author

Mrinmoy Choudhury
