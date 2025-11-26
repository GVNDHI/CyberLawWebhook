from flask import Flask, request, jsonify

app = Flask(__name__)

# --- Local Smart Catalog (LLM-free) ---
REGIONS = {
    "uae-region": {
        "label": "United Arab Emirates (DESC)",
        "authority": "Dubai Electronic Security Center (DESC)",
        "portal": "https://www.desc.gov.ae/",
        "report": "https://www.desc.gov.ae/contact-us/",
    },
    "germany-region": {
        "label": "Germany (BSI)",
        "authority": "Bundesamt für Sicherheit in der Informationstechnik (BSI)",
        "portal": "https://www.bsi.bund.de/",
        "report": "https://www.bsi.bund.de/EN/Service-Navi/Contact/contact_node.html",
    },
    "nj-region": {
        "label": "New Jersey (NJCCIC)",
        "authority": "New Jersey Cybersecurity & Communications Integration Cell",
        "portal": "https://www.cyber.nj.gov/",
        "report": "https://www.cyber.nj.gov/report",
    }
}

# --- Keyword-based LLM-style intent detection ---
PATTERNS = {
    "phishing": ["phish", "phishing", "scam mail", "fake email", "fraudulent email"],
    "hacked": ["hacked", "compromised", "breach", "someone logged in", "unauthorized access"],
    "malware": ["virus", "malware", "trojan", "ransomware", "worm"],
    "fraud": ["scam", "fraud", "stolen money", "identity theft"],
    "general": []
}

def detect_incident_type(text):
    text = text.lower()
    for incident_type, words in PATTERNS.items():
        if any(w in text for w in words):
            return incident_type
    return "general"


# --- AI-like Response Generator (No Gemini Required) ---
def generate_incident_response(region_key, incident_type, user_message):
    r = REGIONS[region_key]

    base_intro = (
        f"Here is guidance based on official cybersecurity practices for "
        f"{r['label']} through {r['authority']}."
    )

    # --- INCIDENT RESPONSE LOGIC ---
    if incident_type == "hacked":
        response = f"""
{base_intro}

🔐 **Account or Device Compromise Detected**
Since you mentioned **you have been hacked**, here is an immediate action plan:

**1. Contain the Incident**
- Disconnect the affected device from Wi-Fi or mobile data.
- Log out of all sessions on other devices if possible.
- Change your passwords from a clean device using strong, unique credentials.

**2. Collect Evidence**
- Record timestamps, suspicious activity, and screenshots.
- Note any unfamiliar IP logins, SMS codes, unauthorized transactions, etc.

**3. Official Reporting for {r['label']}**
- Report the incident here: {r['report']}
- Clearly describe the compromise, what systems were affected, and any data exposed.

**4. Escalation**
- If financial fraud or criminal misuse is suspected, contact local law enforcement immediately.

**5. Additional Notes**
- Avoid wiping devices before authorities or IT teams review them.
- Enable MFA on all accounts as a preventive measure.

Let me know if you want help identifying whether the hack is system-level, account-level, or network-level.
"""
        return response.strip()

    elif incident_type == "phishing":
        response = f"""
{base_intro}

📧 **Phishing Attempt Identified**
Since you received a **phishing email**, here is what you should do next:

**1. Do NOT interact with the email**
- Do not click links, download attachments, or reply.
- Take a screenshot or save the email for evidence.

**2. Validate the message**
- Check the sender domain, grammar, and URL structure.
- Verify whether the organisation truly sent it.

**3. Report the phishing attempt**
- Submit it through the official reporting page: {r['report']}
- Forward the email (if required) according to the authority's instructions.

**4. If you already clicked the link**
- Change your passwords immediately.
- Enable Multi-Factor Authentication (MFA).
- Monitor your accounts for unusual activity.

**5. Extra Safety Tips for {r['label']}**
- Hover over URLs before clicking.
- Avoid logging into accounts via email links.

I can also help you evaluate whether the email is part of a known phishing campaign.
"""
        return response.strip()

    elif incident_type == "malware":
        response = f"""
{base_intro}

🦠 **Possible Malware Infection**
Since your message suggests malware, here is the recommended procedure:

**1. Isolate the device**
- Disconnect it from networks to prevent spread.

**2. Run scans**
- Use trusted antivirus or EDR tools.

**3. Document symptoms**
- Pop-ups, slow performance, unknown apps, encryption behavior.

**4. Reporting**
- Use the region's designated cyber-incident reporting channel: {r['report']}

**5. If ransomware is suspected**
- Do NOT pay ransom.
- Preserve encrypted files for forensic investigation.

I can guide you to determine if the malware is Trojan, ransomware, or spyware.
"""
        return response.strip()

    else:
        response = f"""
{base_intro}

🛡️ **General Cybersecurity Support**

Here are best-practice steps based on your message:

- Document suspicious behavior (screenshots, timestamps, URLs)
- Avoid interacting with unknown links or files
- Update passwords if you sense any compromise
- Enable MFA wherever possible

For official guidance or incident reporting:
👉 {r['report']}

Tell me more and I can narrow down the type of threat you're dealing with.
"""
        return response.strip()


# --- Webhook Route ---
@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json(silent=True, force=True)

    user_text = req["queryResult"].get("queryText", "")
    contexts = req["queryResult"].get("outputContexts", [])

    region_key = None
    for c in contexts:
        name = c["name"].split("/")[-1]
        if name in REGIONS:
            region_key = name
            break

    if not region_key:
        return jsonify({"fulfillmentText": "Please select a region first (UAE, Germany, or New Jersey)."}), 200

    incident_type = detect_incident_type(user_text)
    reply = generate_incident_response(region_key, incident_type, user_text)

    return jsonify({"fulfillmentText": reply}), 200


@app.route("/")
def home():
    return "CyberLawAdvisor Webhook Running", 200


if __name__ == "__main__":
    app.run(port=5000, host="0.0.0.0")
