import os
import litellm

# Load API key from environment variable for security (Message me your tcd email so I can add you to the project on OpenAI's site)
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("API key not found. Set OPENAI_API_KEY environment variable.")

with open("error_report.txt", "r") as file:
    errors = file.read()

response = litellm.completion(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful assistant for a hedge fund's coding standards."},
        {
            "role": "user",
            "content": "Return a suitable name for a Jira ticket and a Jira description given the error returned by Flak8 is:" + errors
        }
    ],
    temperature=0.2,
    max_tokens=1000,
    top_p=0.9,
    frequency_penalty=0.2,
    presence_penalty=0.0,
    api_key=api_key
)

print(response["choices"][0]["message"]["content"])