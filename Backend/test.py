from google.genai import Client
import time

client = Client(api_key="AIzaSyB7twadV111dJgciCpZrSwbexdCuqPwOvA")

for attempt in range(3):
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Hello!"
        )
        print(response.text)
        break
    except Exception as e:
        print(f"Attempt {attempt+1} failed, retrying...")
        time.sleep(2)
