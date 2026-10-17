from flask import Flask, render_template, request, jsonify
from gpt4all import GPT4All

app = Flask(__name__)

# Load AI - This is the "brain"
print("Starting AI... Please wait.")
model = GPT4All("orca-mini-3b-gguf2-q4_0.gguf")

# We use a simple variable to act as 'credits' for now
user_credits = 5

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    global user_credits
    
    if user_credits <= 0:
        return jsonify({"error": "No credits left!"})

    user_input = request.json.get("message")
    user_credits -= 1 # Each question costs 1 credit
    
    with model.chat_session():
        response = model.generate(user_input, max_tokens=100)
    
    return jsonify({"answer": response, "credits_left": user_credits})

@app.route('/reload_credits', methods=['POST'])
def reload():
    global user_credits
    user_credits = 5
    return jsonify({"message": "Credits refilled!", "credits_left": user_credits})

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)