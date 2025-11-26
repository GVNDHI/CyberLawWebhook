from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

GEMINI_KEY = os.getenv("GOOGLE_GEMINI_API_KEY")
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

REGIONS = {
    "uae-region": {"label": "United Arab Emirates","portal":"https://www.desc.gov.ae/","report":"https://www.desc.gov.ae/contact-us/"},
    "germany-region": {"label":"Germany","portal":"https://www.bsi.bund.de/","report":"https://www.bsi.bund.de/"},
    "nj-region": {"label":"New Jersey","portal":"https://www.cyber.nj.gov/","report":"https://www.cyber.nj.gov/report"}
}

def call_gemini(prompt):
    payload = {"contents":[{"parts":[{"text":prompt}]}]}
    r = requests.post(f"{GEMINI_URL}?key={GEMINI_KEY}", json=payload, timeout=20)
    r.raise_for_status()
    return r.json()["candidates"][0]["content"]["parts"][0]["text"]

@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json()
    user_msg = req["queryResult"].get("queryText", "")
    contexts = req["queryResult"].get("outputContexts", [])
    region = None
    for c in contexts:
        name = c["name"].split("/")[-1]
        if name in REGIONS:
            region = name
            break
    if not region:
        return jsonify({"fulfillmentText":"Please select UAE, Germany, or New Jersey first."})
    reg = REGIONS[region]
    prompt = f"Region: {reg['label']}\nPortal: {reg['portal']}\nReport: {reg['report']}\nDo NOT provide legal advice.\nUser question: {user_msg}"
    try:
        answer = call_gemini(prompt)
    except Exception as e:
        return jsonify({"fulfillmentText":"Could not reach AI service. Try again later."})
    return jsonify({"fulfillmentText": answer})

if __name__ == "__main__":
    app.run(port=5000, debug=True)
  