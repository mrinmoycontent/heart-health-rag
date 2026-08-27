import json
import re
from http.server import BaseHTTPRequestHandler


DOCUMENTS = [
    {
        "source": "American Heart Association",
        "title": "American Heart Association - Life's Essential 8",
        "url": "https://www.heart.org/en/healthy-living/healthy-lifestyle/lifes-essential-8",
        "text": """
Life's Essential 8 identifies eight key measures for cardiovascular health:
Eat Better, Be More Active, Quit Tobacco, Get Healthy Sleep, Manage Weight,
Control Cholesterol, Manage Blood Sugar, and Manage Blood Pressure.

A healthy eating pattern can include whole foods, fruits and vegetables,
whole grains, lean protein, nuts and seeds.

Limiting foods high in sodium, added sugars and unhealthy fats can support
cardiovascular health.

Adults should generally aim for 150 minutes of moderate-intensity physical
activity per week or 75 minutes of vigorous activity.

Avoiding nicotine and tobacco exposure is an important part of cardiovascular
health.
"""
    },
    {
        "source": "World Health Organization",
        "title": "WHO - Cardiovascular Diseases",
        "url": "https://www.who.int/health-topics/cardiovascular-diseases",
        "text": """
Cardiovascular diseases are a group of disorders of the heart and blood
vessels.

Behavioral risk factors include unhealthy diet, physical inactivity,
tobacco use and harmful use of alcohol.

These behaviors may contribute to increased blood pressure, increased blood
glucose, elevated blood lipids and overweight or obesity.

Stopping tobacco use, reducing salt in the diet, eating more fruits and
vegetables, engaging in regular physical activity and avoiding harmful
alcohol use can reduce cardiovascular risk.
"""
    }
]


EMERGENCY_TERMS = [
    "severe chest pain",
    "chest pain",
    "difficulty breathing",
    "can't breathe",
    "cannot breathe",
    "shortness of breath",
    "fainting",
    "passed out",
    "unconscious",
    "heart attack",
    "stroke symptoms"
]


MEDICATION_TERMS = [
    "what medication should i take",
    "which medicine should i take",
    "what medicine should i take",
    "dosage",
    "dose",
    "prescription",
    "should i take aspirin",
    "should i stop my medication"
]


DIAGNOSIS_TERMS = [
    "do i have heart disease",
    "do i have a heart attack",
    "am i having a heart attack",
    "diagnose me",
    "what disease do i have"
]


INSUFFICIENT = (
    "I don't have enough information in my current heart-health "
    "knowledge base to answer that question reliably."
)


def category(question):

    q = question.lower().strip()

    if any(term in q for term in EMERGENCY_TERMS):
        return "EMERGENCY"

    if any(term in q for term in MEDICATION_TERMS):
        return "MEDICATION"

    if any(term in q for term in DIAGNOSIS_TERMS):
        return "DIAGNOSIS"

    return "NORMAL"


def safety_response(cat):

    if cat == "EMERGENCY":
        return (
            "⚠️ This may be a medical emergency.\n\n"
            "If you are experiencing severe chest pain, difficulty breathing, "
            "fainting, or other potentially serious symptoms, seek emergency "
            "medical care immediately or contact your local emergency service.\n\n"
            "Do not rely on this chatbot to diagnose or manage an emergency."
        )

    if cat == "MEDICATION":
        return (
            "I can provide general educational information about heart health, "
            "but I cannot recommend a medication, dosage, prescription, or "
            "whether you should start or stop a medicine.\n\n"
            "For medication decisions, please speak with a qualified healthcare professional."
        )

    if cat == "DIAGNOSIS":
        return (
            "I can provide general educational information about heart health, "
            "but I cannot diagnose a medical condition or determine whether "
            "you are having a heart attack or another cardiovascular condition.\n\n"
            "If you are experiencing concerning or severe symptoms, seek medical attention promptly."
        )

    return None


def retrieve(question):

    words = set(
        re.findall(
            r"[a-z0-9]+",
            question.lower()
        )
    )

    results = []

    for document in DOCUMENTS:

        document_words = set(
            re.findall(
                r"[a-z0-9]+",
                document["text"].lower()
            )
        )

        score = len(
            words.intersection(document_words)
        )

        if score > 0:
            results.append(
                (score, document)
            )

    results.sort(
        key=lambda item: item[0],
        reverse=True
    )

    return [
        document
        for score, document in results[:2]
    ]


def create_answer(question, documents):

    q = question.lower()

    if any(word in q for word in [
        "food",
        "eat",
        "diet",
        "eating"
    ]):

        return (
            "A heart-healthy eating pattern can include whole foods, "
            "fruits and vegetables, whole grains, lean protein, nuts and seeds. "
            "Limiting foods high in sodium, added sugars and unhealthy fats "
            "can support cardiovascular health."
        )

    if any(word in q for word in [
        "exercise",
        "activity",
        "physical",
        "workout"
    ]):

        return (
            "Adults should generally aim for 150 minutes of moderate-intensity "
            "physical activity per week or 75 minutes of vigorous activity. "
            "Regular physical activity is an important part of cardiovascular health."
        )

    if any(word in q for word in [
        "smoking",
        "tobacco",
        "nicotine"
    ]):

        return (
            "Avoiding nicotine and tobacco exposure is an important part of "
            "cardiovascular health. Stopping tobacco use can reduce cardiovascular risk."
        )

    if any(word in q for word in [
        "salt",
        "sodium"
    ]):

        return (
            "Reducing salt in the diet can help reduce cardiovascular risk. "
            "The American Heart Association also recommends limiting foods "
            "high in sodium."
        )

    if any(word in q for word in [
        "heart health",
        "cardiovascular health",
        "healthy heart"
    ]):

        return (
            "The American Heart Association's Life's Essential 8 identifies "
            "eight key measures for cardiovascular health: Eat Better, "
            "Be More Active, Quit Tobacco, Get Healthy Sleep, Manage Weight, "
            "Control Cholesterol, Manage Blood Sugar, and Manage Blood Pressure."
        )

    if any(word in q for word in [
        "risk",
        "risk factors",
        "cause",
        "causes"
    ]):

        return (
            "Important behavioral cardiovascular risk factors include an "
            "unhealthy diet, physical inactivity, tobacco use and harmful "
            "use of alcohol. These behaviors may contribute to increased "
            "blood pressure, blood glucose, blood lipids and overweight or obesity."
        )

    if documents:

        return (
            "Based on the current heart-health knowledge base: "
            + documents[0]["text"].strip()
        )

    return INSUFFICIENT


def generate_answer(question):

    cat = category(question)

    if cat != "NORMAL":

        return {
            "answer": safety_response(cat),
            "sources": [],
            "category": cat
        }

    documents = retrieve(question)

    if not documents:

        return {
            "answer": INSUFFICIENT,
            "sources": [],
            "category": "INSUFFICIENT_CONTEXT"
        }

    answer = create_answer(
        question,
        documents
    )

    return {
        "answer": answer,
        "sources": [
            {
                "source": document["source"],
                "title": document["title"],
                "url": document["url"]
            }
            for document in documents
        ],
        "category": "NORMAL"
    }


class handler(BaseHTTPRequestHandler):

    def send_json(self, status, data):

        body = json.dumps(
            data,
            ensure_ascii=False
        ).encode("utf-8")

        self.send_response(status)

        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8"
        )

        self.send_header(
            "Access-Control-Allow-Origin",
            "*"
        )

        self.send_header(
            "Access-Control-Allow-Headers",
            "Content-Type"
        )

        self.send_header(
            "Access-Control-Allow-Methods",
            "GET,POST,OPTIONS"
        )

        self.end_headers()

        self.wfile.write(body)


    def do_OPTIONS(self):

        self.send_json(
            200,
            {"ok": True}
        )


    def do_GET(self):

        self.send_json(
            200,
            {
                "status": "ok",
                "message": "Heart Health RAG API is running."
            }
        )


    def do_POST(self):

        try:

            length = int(
                self.headers.get(
                    "Content-Length",
                    "0"
                )
            )

            raw_body = self.rfile.read(
                length
            ).decode("utf-8")

            data = json.loads(
                raw_body
            )

            question = str(
                data.get(
                    "question",
                    ""
                )
            ).strip()

            if not question:

                self.send_json(
                    400,
                    {
                        "error": "Please enter a question."
                    }
                )

                return

            result = generate_answer(
                question
            )

            self.send_json(
                200,
                result
            )

        except Exception as e:

            self.send_json(
                500,
                {
                    "error": "Unable to process the request.",
                    "details": str(e)
                }
            )
