import os, requests
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("GEMINI_API_KEY")
models_to_test = [
    "gemini-3.1-flash-lite",
    "gemini-3.5-flash-lite",
    "gemini-3.5-flash",
    "gemini-3.6-flash",
    "gemini-3.7-flash",
    "gemini-flash-latest",
    "gemini-pro-latest"
]

for m in models_to_test:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={key}"
    try:
        r = requests.post(
            url,
            json={"contents": [{"parts": [{"text": "Return JSON: {\"ping\": \"pong\"}"}]}]},
            timeout=8
        )
        print(f"{m} -> {r.status_code}")
        if r.status_code == 200:
            print("  Response:", r.json()["candidates"][0]["content"]["parts"][0]["text"].strip())
            break
    except Exception as e:
        print(f"{m} -> error: {e}")

