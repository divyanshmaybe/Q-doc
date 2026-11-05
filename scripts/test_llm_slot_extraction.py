import os, json, requests
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("GEMINI_API_KEY")
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite:generateContent?key={key}"

system_prompt = """Extract clinical dermatology slots from user speech into JSON.
Slots:
- body_site: string (e.g. arms, legs, face, hands, underarms, groin, torso, etc.) or null
- lesion_type: string (morphological description in patient words) or null
- duration_days: integer (approximate days, e.g. 1 year = 365) or null
- has_itching: boolean or null
- has_fever: boolean or null
- household_contacts_affected: boolean or null
"""

user_speech = "My underarms are really dark right now and it has been there for an year with no itching."

payload = {
    "contents": [{
        "parts": [{"text": f"{system_prompt}\nUser: {user_speech}\nOutput JSON only."}]
    }],
    "generationConfig": {
        "responseMimeType": "application/json",
        "temperature": 0.1
    }
}

r = requests.post(url, json=payload, timeout=12)
print("Status:", r.status_code)
if r.status_code == 200:
    print("Parsed JSON Output:")
    print(r.json()["candidates"][0]["content"]["parts"][0]["text"])
else:
    print("Error:", r.text[:200])

