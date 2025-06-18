from flask import Flask, request, jsonify
import openai
import os
import time

app = Flask(__name__)

# Load API key from environment variable
openai_api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=openai_api_key)
# ASSISTANT_ID = "asst_eGaU51vpRsSfGvMGGjbd7KUb"

@app.route('/')
def serve_frontend():
    return open("index.html").read()

@app.route('/api/process-text', methods=['POST'])
def process_text():
    data = request.json
    user_text = data.get("text", "")

    if not user_text:
        return jsonify({"error": "No text provided"}), 400

    try:
        thread = client.beta.threads.create()
        thread_id = thread.id

        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_text
        )

        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=ASSISTANT_ID
        )

        while True:
            run_status = client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )
            if run_status.status == "completed":
                break
            elif run_status.status in ["failed", "cancelled"]:
                return jsonify({"error": f"Run {run_status.status}"}), 500
            time.sleep(1)

        messages = client.beta.threads.messages.list(thread_id=thread_id)
        bot_response = messages.data[0].content[0].text.value

        return jsonify({"output": bot_response})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
