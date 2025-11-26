from flask import Flask, request, jsonify

app = Flask(__name__)

REGIONS = {
    "uae-region": {
        "label": "United Arab Emirates (DESC)",
        "portal": "https://www.desc.gov.ae/",
        "report": "https://www.desc.gov.ae/contact-us/",
        "advice": [
            "Document suspicious activity: screenshots, timestamps, email headers and URLs.",
            "Do not click further links or attachments.",
            "If this is a work device, inform your organisation's IT or security team immediately.",
            "Report the incident via the DESC contact page and the relevant sector regulator if applicable.",
            "Preserve logs and evidence; avoid deleting files until instructed by professionals."
        ]
    },
    "germany-region": {
        "label": "Germany (BSI)",
        "portal": "https://www.bsi.bund.de/",
        "report": "https://www.bsi.bund.de/EN/Home/home_node.html",
        "advice": [
            "Record incident details (affected systems, time, screenshots and error messages).",
            "Isolate or disconnect affected systems to contain the incident when safe to do so.",
            "If you operate critical infrastructure (KRITIS), follow mandatory reporting timelines.",
            "Report IT incidents via BSI's guidance/incident reporting pages and notify internal SOC/CSIRT.",
            "If criminal activity is suspected, contact local Polizei or the BKA."
        ]
    },
    "nj-region": {
        "label": "New Jersey (NJCCIC)",
        "portal": "https://www.cyber.nj.gov/",
        "report": "https://www.cyber.nj.gov/report",
        "advice": [
            "Collect evidence (phishing email headers, message body, sender address, timestamps).",
            "Stop interacting with the suspicious message or links.",
            "Report the incident to your internal IT/security team if applicable.",
            "Submit incident details to NJCCIC using their reporting resources.",
            "For fraud or identity theft, file with local law enforcement and consider IC3.gov."
        ]
    }
}

KEYWORDS = {
    "phish": ["phish", "phishing", "phisher", "phishy"],
    "malware": ["malware", "virus", "ransom", "ransomware", "trojan"],
    "account": ["account", "password", "login", "credential", "hacked", "compromise"],
    "report": ["report", "where do i", "how do i", "who do i", "contact", "reporting"]
}

def detect_intent_type(text: str) -> str:
    t = (text or "").lower()
    if any(k in t for k in KEYWORDS["phish"]):
        return "phishing"
    if any(k in t for k in KEYWORDS["malware"]):
        return "malware"
    if any(k in t for k in KEYWORDS["account"]):
        return "account"
    if any(k in t for k in KEYWORDS["report"]):
        return "reporting"
    return "general"

def build_response(region_key: str, intent_type: str, user_text: str) -> str:
    reg = REGIONS[region_key]
    lines = []
    lines.append(f"According to official guidance for {reg['label']}:")
    lines.append("")
    if intent_type == "phishing":
        lines.append("Immediate steps:")
        lines.extend([f"- {reg['advice'][0]}", f"- {reg['advice'][1]}", f"- {reg['advice'][2]}"])
    elif intent_type == "malware":
        lines.append("Immediate steps:")
        lines.extend([f"- {reg['advice'][1]}", f"- {reg['advice'][3]}"])
    elif intent_type == "account":
        lines.append("Immediate steps:")
        lines.extend([f"- {reg['advice'][0]}", "- Change passwords and enable MFA where possible.", "- Notify your provider or internal security team."])
    elif intent_type == "reporting":
        lines.append("How to report:")
        lines.append(f"- Use the official reporting page: {reg['report']}")
        lines.append(f"- Include timestamps, affected systems, and any logs or screenshots.")
    else:
        lines.append("Recommended steps:")
        for a in reg["advice"]:
            lines.append(f"- {a}")
    lines.append("")
    lines.append(f"Official portal: {reg['portal']}")
    lines.append(f"Reporting / contact page: {reg['report']}")
    lines.append("")
    lines.append("I provide informational guidance based on official portal recommendations and not legal advice.")
    return "\n".join(lines)

@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json(silent=True, force=True)
    if not req or "queryResult" not in req:
        return jsonify({"fulfillmentText": "Invalid request"}), 400

    user_text = req["queryResult"].get("queryText", "")
    contexts = req["queryResult"].get("outputContexts", [])
    region_key = None
    for c in contexts:
        name = c.get("name", "")
        key = name.split("/")[-1]
        if key in REGIONS:
            region_key = key
            break

    if not region_key:
        return jsonify({"fulfillmentText": "Please select a region first (UAE, Germany, or New Jersey)."}), 200

    intent_type = detect_intent_type(user_text)
    reply = build_response(region_key, intent_type, user_text)
    return jsonify({"fulfillmentText": reply}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
