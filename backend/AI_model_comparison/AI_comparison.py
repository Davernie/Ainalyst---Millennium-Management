import litellm

api_key = "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"

response = litellm.completion(
    model="gpt-4o-mini",  # OpenAI model (for testing before switching)
    messages=[
        {"role": "system", "content": "You are a helpful assistant for a hedge fund's coding standards."},
        {"role": "user", "content": "Return a suitable name for a Jira ticket and a Jira description given the error returned by Flak8 is: test.py:5:1: F401 'os' imported but unused"}
    ],
    api_key=api_key,
    temperature=0.2,  # Controls randomness (lower = more deterministic)
    max_tokens=1500,  # Limits response length
    top_p=0.9,  # Alternative to temperature, controls diversity of output
    frequency_penalty=0.2,  # Reduces repetition
    presence_penalty=0.0  # Encourages new topic mentions
)

print(response["choices"][0]["message"]["content"])
