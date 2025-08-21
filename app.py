from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Predefined Q&A dictionary for SyncAI
qa_pairs = {
    "hi": "Hi, welcome to SyncAI! I am here to assist you.",
    "hello": "Hi, welcome to SyncAI! I am here to assist you.",
    "what are the services given by syncai": (
        "SyncAI provides services such as AI-powered automation, chatbot development, "
        "machine learning solutions, and business intelligence support."
    ),
    "services": (
        "SyncAI provides services such as AI-powered automation, chatbot development, "
        "machine learning solutions, and business intelligence support."
    ),
    "contact": "You can reach SyncAI at XYZ Street, ABC City, or email us at contact@syncai.com."
}

@app.route("/")
def home():
    return render_template("index.html")  # serve frontend

@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("message", "").lower().strip()
    response = qa_pairs.get(user_msg, "Sorry, I didn't understand.You can ask me about our services or how to contact us.")
    return jsonify({"reply": response})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
