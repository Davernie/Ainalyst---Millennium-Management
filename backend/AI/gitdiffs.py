import os
import litellm
from dotenv import load_dotenv
from backend.app.Jira.Jira import get_jira_description

load_dotenv()

# Load API key from environment variable for security (Message me your tcd email so I can add you to the project on OpenAI's site)
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("API key not found. Set OPENAI_API_KEY environment variable.")

jira_description = get_jira_description()

# Reads the Git diff from a file
def analyze_git_diff(file_path="git_diff_output.txt"):
    try:
        with open(file_path, "r") as file:
            git_diff_content = file.read()

        # If the git diff content is non-empty, it's analysed by the LLM
        if git_diff_content:
            response = litellm.completion(
                model="gpt-4o-mini",  # Replace with actual model ID as needed
                messages=[
                    {"role": "system", "content": "You analyze Git diffs for common code smells and suggest improvements."},
                    {"role": "user", "content": f"Analyze the following Git diff and suggest improvements:\n\n{git_diff_content}\n\nAlso, analyze the following JIRA issue description to see if the code addresses all the issues and features mentioned:\n\n{jira_description}"}
                ],
                temperature=0.0,
                max_tokens=1500,
                top_p=0.95,
                frequency_penalty=0.1,
                presence_penalty=0.0,
                api_key=api_key
            )
            print(response["choices"][0]["message"]["content"])

            with open(output_file, "w") as out_file:
                out_file.write(analysis_result)

        else:
            print("Git diff file is empty. No analysis performed.")
    except FileNotFoundError:
        print(f"The file {file_path} was not found.")
    except Exception as e:
        print(f"An error occurred while reading the file or making the API request: {e}")

file_path = "git_diff_output.txt"  # Path to existing git diff text file, only populated by endpoint if there is a git diff
output_file = "git_diffs_report.txt"
analyze_git_diff(file_path)
