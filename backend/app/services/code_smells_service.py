import os
import litellm

# Load API key from environment variable for security (Message me your tcd email so I can add you to the project on OpenAI's site)
api_key = "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"


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
