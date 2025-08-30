from flask import Flask, render_template, request, jsonify, session
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "mitra-secret")  # set SECRET_KEY in Render if you want

BOT_NAME = "Mitra (మిత్ర)"

# ----- Main menu shown after Hello / Start -----
MENU_OPTIONS = [
    "About Us",
    "Our Services",
    "Pricing / Plans",
    "Start Your Journey",
    "Talk to Support",
    "FAQs",
    "Exit"
]

# ----- Copy you can tweak anytime -----
ABOUT_TEXT = (
    "I’m Mitra —your friendly SyncAI assistant. We build practical AI & automation for businesses. "
    "We keep things simple, affordable and outcome-driven."
)

SERVICES_TEXT = (
    "SyncAI services:\n"
    "• AI/LLM solutions & chatbots\n"
    "• NLP, CV, analytics & ML pipelines\n"
    "• Data engineering & integrations (APIs, apps, CRMs)\n"
    "• Web & app development\n"
    "• Deployment, MLOps & ongoing support"
)

PRICING_TEXT = (
    "Pricing depends on scope & complexity. We offer:\n"
    "• Starter (MVP/PoC)\n"
    "• Growth (production roll-out)\n"
    "• Custom (enterprise/regulated)\n"
    "Tell me your rough scope and timeline, and I’ll suggest a plan."
)

CONTACT_TEXT = (
    "You can reach us at 📧 contact@syncai.com or ☎️ +91-90000-00000. "
    "Share your preferred contact method and we’ll get back within 1 business day."
)

FAQ_TEXT = (
    "Common questions:\n"
    "• How long does a chatbot take? → 2–4 weeks for an MVP.\n"
    "• Do you support on-prem? → Yes.\n"
    "• Can you fine-tune LLMs? → Yes, budget-friendly options available."
)

# ----- Keyword → intent mapping for free typing -----
KEYWORDS = {
    "About Us": ["about", "company", "who are you", "intro", "syncai"],
    "Our Services": ["service", "services", "solutions", "what do you do", "offer", "llm", "chatbot", "blockchain", "web", "app"],
    "Pricing / Plans": ["price", "pricing", "cost", "budget", "charge", "plan"],
    "Talk to Support": ["contact", "phone", "email", "support", "talk", "reach"],
    "Start Your Journey": ["start", "begin", "register", "kickoff", "company", "setup", "incorporate"],
    "FAQs": ["faq", "questions", "help", "doubt"],
    "Exit": ["exit", "quit", "bye", "goodbye"]
}

# ----- 7-step guided flow (buttons only for a smooth demo) -----
START_FLOW_NAME = "start_company"

FLOW_QUESTIONS = [
    {"q": "1) Which industry best describes you?", "options": ["E-commerce", "EdTech", "FinTech", "Healthcare", "Other"]},
    {"q": "2) Company stage?", "options": ["Idea / Pre-seed", "Startup", "SME", "Enterprise"]},
    {"q": "3) What do you want to build first?", "options": ["AI Chatbot", "Website", "Mobile App", "Data Pipeline", "Not sure"]},
    {"q": "4) Target timeline?", "options": ["ASAP", "1–3 months", "3–6 months"]},
    {"q": "5) Budget range (rough)?", "options": ["Low", "Medium", "High", "Discuss"]},
    {"q": "6) Need ongoing support?", "options": ["Yes", "No", "Maybe"]},
    {"q": "7) Preferred contact?", "options": ["Email", "Phone", "WhatsApp"]}
]

def menu_response(text):
    return {"reply": text, "options": MENU_OPTIONS}

def start_menu():
    # Always collect basic details at the start of a chat
    session["onboard"] = {"index": 0, "data": {}}
    session.pop("profile", None)
    return {"reply": ONBOARDING_QUESTIONS[0]["q"], "options": []}

def detect_intent(message):
    m = message.lower()
    for intent, words in KEYWORDS.items():
        if any(w in m for w in words):
            return intent
    # common greetings
    if m in ["hi", "hello", "hey", "start", "__start__"]:
        return "__start__"
    return None

def handle_intent(intent):
    if intent == "About Us":
        return {"reply": ABOUT_TEXT, "options": []}
    if intent == "Our Services":
        return {"reply": SERVICES_TEXT, "options": []}
    if intent == "Pricing / Plans":
        return {"reply": PRICING_TEXT, "options": []}
    if intent == "Talk to Support":
        return {"reply": CONTACT_TEXT, "options": []}
    if intent == "FAQs":
        return {"reply": FAQ_TEXT, "options": []}
    if intent == "Exit":
        return {"reply": "Thanks for chatting with Mitra 🙏 Take care!", "options": []}
    if intent == "Start Your Journey":
        session["flow"] = {"name": START_FLOW_NAME, "stage": "confirm", "index": 0, "answers": []}
        return {"reply": "I have 7 simple questions to get you started. Shall we begin?", "options": ["Start now", "Maybe later"]}
    return {"reply": "Sorry, I didn’t understand. You can ask about services, pricing, contact, or FAQs.", "options": []}

def in_flow():
    f = session.get("flow")
    return f if f and f.get("name") == START_FLOW_NAME else None

def flow_reply(user_msg):
    f = in_flow()
    if not f:
        return None

    msg = user_msg.lower().strip()

    # Confirmation stage
    if f["stage"] == "confirm":
        if msg in ["start now", "yes", "y", "begin", "ok", "okay"]:
            f["stage"] = "q"
            f["index"] = 0
            session["flow"] = f
            q = FLOW_QUESTIONS[0]
            return {"reply": q["q"], "options": q["options"]}
        else:
            session.pop("flow", None)
            return menu_response("No problem. Whenever you’re ready, choose an option below.")

    # Question stage
    if f["stage"] == "q":
        # store previous answer if any question was shown
        if f["index"] < len(FLOW_QUESTIONS):
            f["answers"].append(user_msg)

        f["index"] += 1
        if f["index"] >= len(FLOW_QUESTIONS):
            # Completed
            answers = f["answers"]
            session.pop("flow", None)
            summary = (
                "Great! Here’s your summary:\n"
                f"• Industry: {answers[0]}\n"
                f"• Stage: {answers[1]}\n"
                f"• First build: {answers[2]}\n"
                f"• Timeline: {answers[3]}\n"
                f"• Budget: {answers[4]}\n"
                f"• Support: {answers[5]}\n"
                f"• Contact pref: {answers[6]}\n\n"
                "Next step: Share your email/phone and we’ll propose a plan within 1 business day. "
                "Or choose something else below."
            )
            return menu_response(summary)

        # Ask next question
        q = FLOW_QUESTIONS[f["index"]]
        session["flow"] = f
        return {"reply": q["q"], "options": q["options"]}

    # Fallback
    return menu_response("Please choose one of the options to continue.")

# ----- Simple onboarding: collect name, phone, email (once per session) -----
ONBOARDING_QUESTIONS = [
    {"key": "name", "q": "Hi there! Before we begin, may I know your name?"},
    {"key": "phone", "q": "Thanks! Could you share your contact number?"},
    {"key": "email", "q": "And your email address?"}
]

def is_valid_phone(s: str) -> bool:
    import re
    s = s.strip()
    # Accept digits, spaces, dashes, leading +
    return bool(re.fullmatch(r"\+?[0-9][0-9\s\-]{6,14}[0-9]", s))


def is_valid_email(s: str) -> bool:
    import re
    s = s.strip()
    return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", s))


def in_onboarding():
    return session.get("onboard")


def onboarding_reply(user_msg: str):
    o = session.get("onboard")
    if not o:
        return None

    idx = o.get("index", 0)
    data = o.setdefault("data", {})

    # Step 0: name (any non-empty)
    if idx == 0:
        name = user_msg.strip()
        if not name:
            return {"reply": ONBOARDING_QUESTIONS[0]["q"], "options": []}
        data["name"] = name
        o["index"] = 1
        session["onboard"] = o
        return {"reply": ONBOARDING_QUESTIONS[1]["q"], "options": []}

    # Step 1: phone (basic validation)
    if idx == 1:
        phone = user_msg.strip()
        if not is_valid_phone(phone):
            return {"reply": "Please enter a valid contact number (digits, +, -, spaces).", "options": []}
        data["phone"] = phone
        o["index"] = 2
        session["onboard"] = o
        return {"reply": ONBOARDING_QUESTIONS[2]["q"], "options": []}

    # Step 2: email (basic validation), then finish
    if idx == 2:
        email = user_msg.strip()
        if not is_valid_email(email):
            return {"reply": "That email doesn’t look right. Please enter a valid email (e.g., name@example.com).", "options": []}
        data["email"] = email
        # Save profile and clear onboarding
        session["profile"] = data
        session.pop("onboard", None)
        name = data.get("name") or "there"
        return menu_response(f"Thanks, {name}! You’re all set. How can I help you today?")

    # Fallback: reset onboarding
    session.pop("onboard", None)
    return menu_response("All set. How can I help you today?")


@app.route("/")
def home():
    # pass name so the header can show Telugu + emoji nicely
    return render_template("index.html", bot_name=BOT_NAME)

@app.route("/chat", methods=["POST"])
def chat():
    user_msg = (request.json.get("message") or "").strip()

    # Onboarding first (if active)
    if in_onboarding():
        return jsonify(onboarding_reply(user_msg))

    # Flow next (if active)
    f = in_flow()
    if f:
        return jsonify(flow_reply(user_msg))

    # Start / greeting
    if user_msg.lower() in ["__start__", "hi", "hello", "hey", "start"]:
        return jsonify(start_menu())

    # If user clicked a main menu option, handle directly
    if user_msg in MENU_OPTIONS or user_msg in ["Start now", "Maybe later"]:
        # It might be a flow confirmation
        if user_msg in ["Start now", "Maybe later"] and in_flow():
            return jsonify(flow_reply(user_msg))
        return jsonify(handle_intent(user_msg))

    # Keyword detection for free text
    intent = detect_intent(user_msg)
    if intent:
        if intent == "__start__":
            return jsonify(start_menu())
        return jsonify(handle_intent(intent))

    # Unknown
    return jsonify(menu_response(
        "Sorry, I didn’t catch that. You can ask about our services, pricing, support, or tap a button below."
    ))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)