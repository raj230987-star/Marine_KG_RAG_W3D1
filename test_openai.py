
from dotenv import load_dotenv
from openai import OpenAI
import os

# Load environment variables
load_dotenv()

# Read API key
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("API key not found!")
else:
    client = OpenAI(api_key=api_key)

    print("OpenAI API key loaded successfully!")

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "user", "content": "Say Hello from Marine KG-RAG!"}
            ]
        )

        print("\nLLM Response:")
        print(response.choices[0].message.content)

    except Exception as e:
        print("API Error:", e)
