import os
from dotenv import load_dotenv

# Load .env
load_dotenv()

print("\nAPI Connectivity Check\n")

# ----------------------------
# 1. Test Cohere API
# ----------------------------
try:
    import cohere
    co = cohere.Client(os.getenv("CohereAPI"))
    resp = co.generate(model="command-xlarge-nightly", prompt="Say hello in one word")
    print("Cohere OK:", resp.generations[0].text.strip())
except Exception as e:
    print("Cohere FAILED:", e)

# ----------------------------
# 2. Test Tavily API
# ----------------------------
try:
    import requests
    tavily_key = os.getenv("TAVILY_API_KEY")
    resp = requests.post(
        "https://api.tavily.com/search",
        headers={"Authorization": f"Bearer {tavily_key}"},
        json={"query": "What is AI?", "search_depth": "basic"}
    )
    if resp.status_code == 200:
        data = resp.json()
        print("Tavily OK:", data.get("results", [{}])[0].get("title", "No title"))
    else:
        print("Tavily FAILED: HTTP", resp.status_code, resp.text)
except Exception as e:
    print("Tavily FAILED:", e)

# ----------------------------
# 3. Test Gemini API
# ----------------------------
try:
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel("gemini-1.5-flash")
    resp = model.generate_content("Say hello in one word")
    print("Gemini OK:", resp.text)
except Exception as e:
    print("Gemini FAILED:", e)

# ----------------------------
# 4. Test Google Custom Search API
# ----------------------------
try:
    g_api = os.getenv("GOOGLE_API_KEY")
    g_cse = os.getenv("GOOGLE_CSE_ID")
    import requests
    url = f"https://www.googleapis.com/customsearch/v1?key={g_api}&cx={g_cse}&q=AI"
    resp = requests.get(url)
    if resp.status_code == 200:
        data = resp.json()
        items = data.get("items", [])
        print("Google CSE OK:", items[0]["title"] if items else "No results")
    else:
        print("Google CSE FAILED: HTTP", resp.status_code, resp.text)
except Exception as e:
    print("Google CSE FAILED:", e)

# ----------------------------
# 5. Test Twilio API
# ----------------------------
try:
    from twilio.rest import Client
    sid = os.getenv("account_sid")
    token = os.getenv("auth_token")
    from_num = os.getenv("FROM")   # must be like whatsapp:+14155238886
    to_num = os.getenv("TO")       # must be like whatsapp:+91XXXXXXXXXX

    client = Client(sid, token)
    message = client.messages.create(
        from_=from_num,
        to=to_num,
        body="Twilio test message OK"
    )
    print("Twilio OK: Sent message SID", message.sid)
except Exception as e:
    print("Twilio FAILED:", e)

print("\nAPI check finished.\n")
