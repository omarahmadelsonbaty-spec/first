from flask import Flask, render_template, request, jsonify, session

import r
from r import chat_once, refresh_watchlist

app = Flask(__name__)
app.secret_key = "test-chat-site-local-secret"


@app.route("/")
def home():
    return render_template("quant.html")


@app.route("/watchlist")
def watchlist():
    return jsonify({"symbols": r.watchlist})


@app.route("/refresh", methods=["POST"])
def refresh():
    data = refresh_watchlist()
    return jsonify({"symbols": data})


@app.route("/chat", methods=["POST"])
def chat():
    payload = request.get_json(silent=True) or {}
    user_input = (payload.get("message") or "").strip()
    if not user_input:
        return jsonify({"error": "Message cannot be empty."}), 400

    history = session.get("history", [])
    try:
        reply = chat_once(user_input, history)
    except Exception as exc:
        return jsonify({"error": f"Quant assistant failed: {exc}"}), 502

    history.append({"role": "user", "content": user_input})
    history.append({"role": "assistant", "content": reply})
    session["history"] = history[-20:]

    return jsonify({"reply": reply})


@app.route("/reset", methods=["POST"])
def reset():
    session["history"] = []
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False, host="127.0.0.1", port=5050)
