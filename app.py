from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY") or "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"

conversation_memory = {}

@app.route('/api/getAIResponse', methods=['POST'])
def get_ai_response():
    data = request.json
    user_msg = data.get("message", "")
    persona = data.get("persona", "")
    player_id = data.get("player_id", "default")

    system_prompt = persona if persona else "You are a friendly Roblox NPC. Keep replies short and casual, no more than 30 words."

    if player_id not in conversation_memory or conversation_memory[player_id][0]["content"] != system_prompt:
        conversation_memory[player_id] = [{"role": "system", "content": system_prompt}]

    conversation_memory[player_id].append({"role": "user", "content": user_msg})

    memory_slice = [conversation_memory[player_id][0]] + conversation_memory[player_id][-49:]

    payload = {
    "model": "minimax/minimax-m1",
    "messages": memory_slice,
    "max_tokens": 4096
}

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        reply = response.json()["choices"][0]["message"]["content"].strip()
        conversation_memory[player_id].append({"role": "assistant", "content": reply})
    except Exception as e:
        print("OpenRouter error:", e)
        reply = "Sorry, something went wrong."

    return jsonify({"reply": reply})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)