# Backend/RealtimeSearchEngine.py
import requests
from dotenv import dotenv_values
import google.generativeai as genai

env = dotenv_values(".env")
GEMINI_API_KEY = env.get("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

headers = {
    "User-Agent": "Mozilla/5.0"
}

def fetch_web_data(query):
    """Scrapes search results from DuckDuckGo (works without API key)"""
    try:
        url = "https://duckduckgo.com/html/"
        resp = requests.post(url, data={"q": query}, headers=headers, timeout=5)
        text = resp.text

        # crude snippet extraction
        results = []
        for line in text.split("\n"):
            if "result__snippet" in line and len(results) < 5:
                cleaned = line.replace("<b>", "").replace("</b>", "")
                cleaned = cleaned.replace("<span class=\"result__snippet\">", "").replace("</span>", "")
                results.append(cleaned.strip())

        if not results:
            results = [f"No direct results found for {query}"]

        return results

    except Exception as e:
        return [f"Error fetching search results: {e}"]

def RealtimeSearchEngine(prompt):
    """Web results → summarize using Gemini"""
    try:
        results = fetch_web_data(prompt)
        text_blob = "\n".join(results)

        model = genai.GenerativeModel("gemini-pro", transport="rest")
        answer = model.generate_content(
            f"User asked: '{prompt}'. Using this web information:\n{text_blob}\n\nGive a short accurate answer."
        ).text

        return answer.strip()

    except Exception as e:
        print("Realtime search error:", e)
        return "Sorry, unable to fetch live information right now."

if __name__ == "__main__":
    while True:
        q = input("Search: ")
        print(RealtimeSearchEngine(q))
