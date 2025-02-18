import os
import litellm

# Load API key from environment variable for security (Message me your tcd email so I can add you to the project on OpenAI's site)
api_key = os.getenv("OPENAI_API_KEY")

def check_code_smell(code):
    codesmells = litellm.completion(
        model="gpt-4o-mini",
        messages=[
            {"role": "system",
             "content": "You analyze code snippets for common code smells and provide suggestions for improvement."},
            {"role": "user", "content": code}
        ],
        temperature=0.0,
        max_tokens=1500,
        top_p=0.95,
        frequency_penalty=0.1,
        presence_penalty=0.0,
        api_key=api_key
    )

    return codesmells["choices"][0]["message"]["content"]
