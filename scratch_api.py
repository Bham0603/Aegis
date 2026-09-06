import os

from dotenv import load_dotenv
from openai import OpenAI

# Load variables from .env
load_dotenv()

# Read API key from environment
api_key = os.getenv("EXPLABS_API_KEY")

if not api_key:
    raise RuntimeError(
        "EXPLABS_API_KEY is not set. Create an API key under "
        "Settings -> API keys and export it before running this test."
    )

# Create API client
client = OpenAI(
    base_url="https://api.experientiallabs.ai/v1",
    api_key=api_key,
)

# Send request
response = client.chat.completions.create(
    model="gpt-6-astra",
    messages=[{"role": "user", "content": "Say hello to Aegis in one sentence."}],
)

# Print response
print(response.choices[0].message.content)

if response.usage is None:
    print("Token usage: unavailable")
else:
    print(
        "Token usage: "
        f"prompt={response.usage.prompt_tokens}, "
        f"completion={response.usage.completion_tokens}, "
        f"total={response.usage.total_tokens}"
    )
