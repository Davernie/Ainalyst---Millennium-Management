import argparse
import base64
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
import requests
import urllib.parse
import litellm
from dotenv import load_dotenv
import subprocess
import tiktoken  # For token counting

# Import services for code analysis
from backend.app.services.ast_parsing_service import astParser
from backend.app.services.code_smells_service import check_code_smell
from backend.app.services.liniting_service import run_pep8_linter

# Load environment variables
load_dotenv()

# Define constants for token limits (adjust as needed)
MAX_TOTAL_TOKENS = 4096
OUTPUT_TOKENS = 300  # Tokens reserved for model output

def enforce_token_limit(prompt, max_total=MAX_TOTAL_TOKENS, output_tokens=OUTPUT_TOKENS):
    """
    Ensure the prompt does not exceed the token limit (input + output <= max_total).
    Uses tiktoken to encode and truncate the prompt if necessary.
    """
    input_limit = max_total - output_tokens
    enc = tiktoken.get_encoding("cl100k_base")
    tokens = enc.encode(prompt)
    if len(tokens) > input_limit:
        tokens = tokens[:input_limit]
        prompt = enc.decode(tokens)
        prompt += "\n... (truncated to fit token limit)"
    return prompt

# ------------------------
# Database setup
# ------------------------
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, JSON, TIMESTAMP, VARCHAR, insert, update
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://avnadmin:AVNS_d4bV5orCyjUIYKdkJiQ@pg-298e7c66-senthilnaveen003-3105.k.aivencloud.com:26260/defaultdb?sslmode=require"
)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
metadata = MetaData()
response_data = Table(
    "response_data",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("username", VARCHAR(20), nullable=True),
    Column("filename", VARCHAR(100), nullable=True),
    Column("timestamp", TIMESTAMP, default=lambda: datetime.now(timezone.utc)),
    Column("code", JSON, nullable=False),
    Column("report_response", JSON, nullable=False),
)

# ------------------------
# Code analysis functions
# ------------------------
def analyze_code(code):
    """Analyze Python code for AST issues, PEP8 violations, and code smells."""
    ast_parser = astParser()
    ast_issues = ast_parser.analyze(code)
    pep8_issues = run_pep8_linter(code)
    code_smells = check_code_smell(code)
    return {
        "AST Issues": ast_issues if ast_issues else "No AST issues found.",
        "PEP8 Issues": pep8_issues,
        "Code Smells": code_smells
    }

def save_to_db(filename, code, analysis_result):
    """Save individual file analysis results to the database and return the inserted record's ID."""
    db = SessionLocal()
    try:
        stmt = insert(response_data).values(
            username="Gitlab CI",
            filename=filename,
            timestamp=datetime.now(timezone.utc),
            code=json.dumps(code),
            report_response=json.dumps(analysis_result)
        ).returning(response_data.c.id)
        result = db.execute(stmt)
        db.commit()
        inserted_id = result.fetchone()[0]
        return inserted_id
    except Exception as e:
        db.rollback()
        print(f"Database insertion failed for {filename}: {e}")
        return None
    finally:
        db.close()

def format_analysis_results(filename, results, inserted_id):
    """Print formatted analysis results."""
    print(f"\n# Code Analysis Report for {filename}\n")
    print(f"## Status: Successfully Added to Database with ID: {inserted_id}\n")
    print("## AST Issues")
    if results["AST Issues"] and isinstance(results["AST Issues"], list):
        print("\n".join(f"- {issue}" for issue in results["AST Issues"]))
    else:
        print("- No AST issues found.")
    print("\n## PEP8 Compliance")
    if results["PEP8 Issues"]:
        print(results["PEP8 Issues"].strip())
    else:
        print("All checks passed!\n")
    print("\n## Code Smells")
    if results["Code Smells"]:
        print(results["Code Smells"].strip())
    else:
        print("No code smells detected.\n")

# ------------------------
# Jira Integration with Optional User Credentials
# ------------------------
def get_jira_ticket_details(ticket_id, jira_url=None, jira_email=None, jira_api_token=None):
    """
    Fetch Jira ticket details using provided credentials if available; otherwise, use environment variables.
    """
    jira_url = jira_url or os.getenv("JIRA_URL")
    jira_email = jira_email or os.getenv("JIRA_EMAIL")
    jira_api_token = jira_api_token or os.getenv("JIRA_API_TOKEN")

    if not (jira_url and jira_email and jira_api_token):
        print("Jira credentials are not fully set. Skipping Jira integration.")
        return None

    url = f"{jira_url}/rest/api/2/issue/{ticket_id}"
    auth_str = f"{jira_email}:{jira_api_token}"
    b64_auth = base64.b64encode(auth_str.encode()).decode()
    headers = {"Authorization": f"Basic {b64_auth}", "Content-Type": "application/json"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        summary = data["fields"].get("summary", "No summary available")
        description = data["fields"].get("description", "No description provided")
        return {"ticket_id": ticket_id, "summary": summary, "description": description}
    except requests.RequestException as e:
        print(f"Error fetching Jira ticket {ticket_id}: {e}")
        return None

def update_jira_ticket(ticket_id, pr_title, pr_description, jira_url=None, jira_email=None, jira_api_token=None):
    """
    Post a comment to the specified Jira ticket using provided credentials if available; otherwise, fall back to environment variables.
    """
    jira_url = jira_url or os.getenv("JIRA_URL")
    jira_email = jira_email or os.getenv("JIRA_EMAIL")
    jira_api_token = jira_api_token or os.getenv("JIRA_API_TOKEN")

    if not (jira_url and jira_email and jira_api_token):
        print("Jira credentials are not fully set. Cannot update ticket.")
        return False

    url = f"{jira_url}/rest/api/2/issue/{ticket_id}/comment"
    auth_str = f"{jira_email}:{jira_api_token}"
    b64_auth = base64.b64encode(auth_str.encode()).decode()
    headers = {"Authorization": f"Basic {b64_auth}", "Content-Type": "application/json"}
    comment_body = {"body": f"Automated PR Update:\n\n**PR Title:** {pr_title}\n\n**PR Description:**\n{pr_description}"}
    try:
        response = requests.post(url, headers=headers, json=comment_body)
        response.raise_for_status()
        print(f"Successfully updated Jira ticket {ticket_id} with PR details.")
        return True
    except requests.RequestException as e:
        print(f"Error updating Jira ticket {ticket_id}: {e}")
        return False

# ------------------------
# GitLab Project ID Lookup
# ------------------------
def get_project_id_from_url(repo_url):
    """
    Fetch the GitLab project ID using the repository URL.
    """
    GITLAB_API_TOKEN = os.getenv("GITLAB_API_TOKEN")
    GITLAB_API_URL = os.getenv("GITLAB_API_URL", "https://gitlab.com")
    if not GITLAB_API_TOKEN:
        print("GitLab API Token is missing. Skipping project ID lookup.")
        return None
    if not repo_url.startswith(GITLAB_API_URL):
        print("Invalid GitLab repository URL. Please enter a valid project URL.")
        return None
    if repo_url.endswith(".git"):
        repo_url = repo_url[:-4]
    project_path = repo_url.replace(GITLAB_API_URL + "/", "", 1)
    encoded_path = urllib.parse.quote(project_path, safe="")
    url = f"{GITLAB_API_URL}/api/v4/projects/{encoded_path}"
    headers = {"PRIVATE-TOKEN": GITLAB_API_TOKEN}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json().get("id")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching project ID: {e}")
        return None

# ------------------------
# Overall Report and PR Update Functions
# ------------------------
def insert_overall_report(overall_report, jira_details=None, branch_name=None):
    """
    Insert the overall analysis report into the database and return the inserted record's ID.
    Also writes the overall report to 'overall_report.txt' and its ID to 'overall_report_id.txt'.
    """
    db = SessionLocal()
    try:
        report_data = {"analysis": overall_report}
        if jira_details:
            report_data["jira_ticket"] = jira_details
        if branch_name:
            report_data["branch_name"] = branch_name
        stmt = insert(response_data).values(
            username="Gitlab CI",
            filename="Analysis Report",
            timestamp=datetime.now(timezone.utc),
            code="",
            report_response=json.dumps(report_data)
        ).returning(response_data.c.id)
        result = db.execute(stmt)
        db.commit()
        inserted_id = result.fetchone()[0]
        print(f"Overall analysis report saved in DB with ID: {inserted_id}")
        with open("overall_report.txt", "w", encoding="utf-8") as f:
            f.write(overall_report)
        with open("overall_report_id.txt", "w", encoding="utf-8") as f:
            f.write(str(inserted_id))
        return inserted_id
    except Exception as e:
        db.rollback()
        print(f"Error inserting overall analysis report: {e}")
        return None
    finally:
        db.close()

def update_report_with_pr(response_id, pr_title, pr_description, overall_report, jira_details=None, branch_name=None):
    """
    Update the same database record with PR details and the final overall report.
    """
    db = SessionLocal()
    try:
        new_report_data = {
            "analysis": overall_report,
            "pr_title": pr_title,
            "pr_description": pr_description
        }
        if jira_details:
            new_report_data["jira_ticket"] = jira_details
        if branch_name:
            new_report_data["branch_name"] = branch_name
        stmt = update(response_data).where(response_data.c.id == response_id).values(
            report_response=json.dumps(new_report_data)
        )
        db.execute(stmt)
        db.commit()
        print(f"Updated record {response_id} with PR details and final report.")
    except Exception as e:
        db.rollback()
        print(f"Error updating record with PR details: {e}")
    finally:
        db.close()

# ------------------------
# Code Fixing Function
# ------------------------
def fix_code(code):
    """
    Generate a fixed version of the provided code using the model.
    """
    prompt = "Refactor the following code to adhere to best practices, follow PEP8 guidelines, and remove code smells. Provide only the updated code:\n" + code
    try:
        response = litellm.completion(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You refactor code to adhere to best practices, follow PEP8 guidelines, and remove code smells."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            max_tokens=1500,
            top_p=0.95,
            frequency_penalty=0.1,
            presence_penalty=0.0,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        fixed = response["choices"][0]["message"]["content"].strip()
        return fixed
    except Exception as e:
        print(f"Error generating code fix: {e}")
        return code

# ------------------------
# GitLab Diff & PR Generation with Caching and Truncation
# ------------------------
pr_details_cache = {}

def truncate_text(text, max_length):
    """Truncate text to max_length characters, appending a note if truncated."""
    if len(text) > max_length:
        return text[:max_length] + "\n... (truncated)"
    return text

def get_cache_key(*args):
    """Generate a hash-based cache key for the provided arguments."""
    combined = "|".join(args)
    return hashlib.sha256(combined.encode('utf-8')).hexdigest()

def get_latest_commits(project_id, limit=5):
    """Fetch the latest commits for the given project ID."""
    GITLAB_API_TOKEN = os.getenv("GITLAB_API_TOKEN")
    GITLAB_API_URL = os.getenv("GITLAB_API_URL", "https://gitlab.com")
    url = f"{GITLAB_API_URL}/api/v4/projects/{project_id}/repository/commits"
    headers = {"PRIVATE-TOKEN": GITLAB_API_TOKEN}
    params = {"per_page": limit}
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return [commit["id"] for commit in response.json()]
    except requests.RequestException as e:
        print(f"Error fetching commits: {e}")
        return []

def get_commit_message(project_id, commit_sha):
    """Fetch the commit message for a given commit SHA."""
    GITLAB_API_TOKEN = os.getenv("GITLAB_API_TOKEN")
    GITLAB_API_URL = os.getenv("GITLAB_API_URL", "https://gitlab.com")
    url = f"{GITLAB_API_URL}/api/v4/projects/{project_id}/repository/commits/{commit_sha}"
    headers = {"PRIVATE-TOKEN": GITLAB_API_TOKEN}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data.get("title") or data.get("message")
    except requests.RequestException as e:
        print(f"Error fetching commit message for {commit_sha}: {e}")
        return None

def get_git_diff(project_id, commit_sha):
    """
    Fetch the diff for the specified commit.
    First attempt to use a local git diff command (to capture the diff as seen in your diff picture).
    If that fails, fall back to the GitLab API.
    """
    try:
        # Use local git diff, which usually produces a complete diff
        diff_output = subprocess.check_output(["git", "diff", f"{commit_sha}^!", "--"]).decode()
        if diff_output:
            return diff_output
    except Exception as e:
        print(f"Local git diff command failed: {e}")
    # Fall back to the GitLab API diff
    GITLAB_API_TOKEN = os.getenv("GITLAB_API_TOKEN")
    GITLAB_API_URL = os.getenv("GITLAB_API_URL", "https://gitlab.com")
    url = f"{GITLAB_API_URL}/api/v4/projects/{project_id}/repository/commits/{commit_sha}/diff"
    headers = {"PRIVATE-TOKEN": GITLAB_API_TOKEN}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        diffs = response.json()
        return "\n".join([f"File: {diff['new_path']}\n{diff['diff']}" for diff in diffs])
    except requests.RequestException as e:
        print(f"Error fetching diff via API for commit {commit_sha}: {e}")
        return None

def generate_pr_details(commit_messages, git_diff, analysis_report, jira_details=None, branch_name=None):
    """
    Generate a GitLab PR title and description using commit messages, Git diff, and the analysis report.
    Optionally incorporates Jira ticket details.
    """
    commit_messages_str = truncate_text("\n".join(f"- {msg}" for msg in commit_messages), 500)
    git_diff = truncate_text(git_diff, 1000)
    analysis_report = truncate_text(analysis_report, 2000)
    prompt = (
        "Based on the following commit messages:\n" + commit_messages_str + "\n\n" +
        "And the following Git diff:\n" + git_diff + "\n\n" +
        "And the analysis report from the analysis stage:\n" + analysis_report + "\n\n"
    )
    if branch_name:
        prompt += f"This analysis was performed on branch: {branch_name}\n\n"
    if jira_details:
        prompt += (
            "Additionally, incorporate the following Jira ticket details for context:\n" +
            f"- Ticket ID: {jira_details.get('ticket_id')}\n" +
            f"- Summary: {jira_details.get('summary')}\n" +
            f"- Description: {jira_details.get('description')}\n\n"
        )
    prompt += (
        "Generate a concise GitLab PR title and a detailed PR description summarizing these changes. "
        "Mark the title with 'Title:' and the description with 'Description:' in your response."
    )
    
    prompt = enforce_token_limit(prompt, max_total=MAX_TOTAL_TOKENS, output_tokens=OUTPUT_TOKENS)
    cache_key = get_cache_key(prompt)
    if cache_key in pr_details_cache:
        return pr_details_cache[cache_key]
    try:
        response = litellm.completion(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You generate concise GitLab PR titles and detailed PR descriptions based on commit messages, Git diffs, analysis reports, and optionally Jira ticket details and branch information."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            max_tokens=OUTPUT_TOKENS,
            top_p=0.95,
            frequency_penalty=0.1,
            presence_penalty=0.0,
            api_key=os.getenv("OPENAI_API_KEY"),
        )
        pr_output = response["choices"][0]["message"]["content"].strip()
        if "Title:" in pr_output and "Description:" in pr_output:
            title_part = pr_output.split("Title:")[1].split("Description:")[0].strip()
            description_part = pr_output.split("Description:")[1].strip()
        else:
            lines = pr_output.splitlines()
            title_part = lines[0].strip()
            description_part = "\n".join(lines[1:]).strip()
        pr_details_cache[cache_key] = (title_part, description_part)
        return title_part, description_part
    except Exception as e:
        print(f"Error generating PR details: {e}")
        fallback_title = "Fallback PR Title"
        fallback_description = (
            "The PR details could not be generated automatically due to rate limit constraints or another error. "
            "Please review the changes manually."
        )
        return fallback_title, fallback_description

def analyze_jira_issue_coverage(jira_description, git_diff):
    """
    Analyze the Jira issue description and the Git diff to determine if the code addresses
    all the issues and features mentioned in the Jira ticket. Returns a summary.
    """
    prompt = (
        f"JIRA Issue Description:\n{jira_description}\n\n"
        f"Git Diff:\n{git_diff}\n\n"
        "Based on the above, analyze whether the code changes address all the issues and features "
        "mentioned in the Jira ticket. Provide a summary indicating which issues or features are well-covered "
        "and which may be missing or need further attention."
    )
    try:
        response = litellm.completion(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You analyze whether code changes address the issues and features described in a Jira issue."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            max_tokens=OUTPUT_TOKENS,
            top_p=0.95,
            frequency_penalty=0.1,
            presence_penalty=0.0,
            api_key=os.getenv("OPENAI_API_KEY"),
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"Error analyzing JIRA issue coverage: {e}")
        return "Error analyzing JIRA issue coverage. Please review manually."

# ------------------------
# Helper: Get Changed Python Files
# ------------------------
def get_changed_python_files():
    """
    Return a list of unique changed Python files (as Path objects) using git diff.
    In CI environments, if CI_MERGE_REQUEST_TARGET_BRANCH_NAME is set, compute the merge base
    between HEAD and the target branch; otherwise, use CI_COMMIT_BEFORE_SHA (if available)
    or fall back to HEAD~1.
    """
    target_branch = os.getenv("CI_MERGE_REQUEST_TARGET_BRANCH_NAME")
    if target_branch:
        try:
            merge_base = subprocess.check_output(["git", "merge-base", "HEAD", target_branch]).decode().strip()
            print(f"Using merge-base between HEAD and {target_branch}: {merge_base}")
            diff_command = ["git", "diff", "--name-only", merge_base, "HEAD"]
        except Exception as e:
            print(f"Error finding merge base for target branch {target_branch}: {e}")
            diff_command = ["git", "diff", "--name-only", "HEAD~1"]
    else:
        before_sha = os.getenv("CI_COMMIT_BEFORE_SHA")
        if before_sha and before_sha != "0000000000000000000000000000000000000000":
            diff_command = ["git", "diff", "--name-only", before_sha, "HEAD"]
        else:
            diff_command = ["git", "diff", "--name-only", "HEAD~1"]
    try:
        output = subprocess.check_output(diff_command).decode().splitlines()
        unique_files = set(f for f in output if f.endswith(".py"))
        return [Path(f) for f in unique_files]
    except Exception as e:
        print("Error determining changed files:", e)
        return []

# ------------------------
# Helper: Remove Duplicate Sections from Report
# ------------------------
def remove_duplicate_sections(report_text, header):
    """
    Remove duplicate occurrences of blocks that start with the given header.
    Only the first occurrence (and its content until the next header) is retained.
    """
    pattern = re.compile(r"(^" + re.escape(header) + r".*?)(?=^\s*" + re.escape(header) + r"|\Z)", re.MULTILINE | re.DOTALL)
    matches = pattern.findall(report_text)
    if len(matches) > 1:
        first_occurrence = matches[0]
        report_text = pattern.sub(lambda m: m.group(1) if m.start() == 0 else "", report_text)
    return report_text

# ------------------------
# Main Execution
# ------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Analyze Python files, generate PR details, and optionally fix code issues."
    )
    parser.add_argument("--dirPath", type=str, help="Path to the directory to analyze")
    parser.add_argument("--filePath", type=str, help="Path to a single file to analyze")
    parser.add_argument("--repoURL", type=str, help="GitLab repository URL for PR details generation (optional)")
    parser.add_argument("--jiraTicket", type=str, help="Jira ticket ID to include in the PR details (optional)")
    parser.add_argument("--fix", action="store_true", help="Fix code issues and update files with automated code fixes")
    args = parser.parse_args()

    branch_name = os.getenv("BRANCH_NAME")
    if branch_name:
        print(f"Using branch: {branch_name}")

    # Automatically detect repository URL if not provided.
    repo_url = args.repoURL or os.getenv("CI_PROJECT_URL")
    if not repo_url:
        print("Error: Repository URL not provided and CI_PROJECT_URL not set.")
        sys.exit(1)

    jira_details = None
    if args.jiraTicket:
        jira_details = get_jira_ticket_details(args.jiraTicket)
        if jira_details:
            print("Fetched Jira ticket details:", jira_details)
        else:
            print("Failed to fetch Jira ticket details. Continuing without them.")

    # Determine overall report: analyze only the changed Python files if no explicit path is provided.
    if not args.fix:
        overall_report_parts = []
        files_to_analyze = []
        if args.filePath:
            file_path = Path(args.filePath).resolve()
            if not file_path.exists() or not file_path.is_file():
                print("Error: Provided file path is not valid.")
                sys.exit(1)
            files_to_analyze.append(file_path)
        elif args.dirPath:
            directory_path = Path(args.dirPath).resolve()
            if not directory_path.exists() or not directory_path.is_dir():
                print("Error: Provided path is not a valid directory.")
                sys.exit(1)
            for root, _, files in os.walk(directory_path):
                for file in files:
                    if file.endswith(".py"):
                        files_to_analyze.append(Path(root) / file)
        else:
            files_to_analyze = get_changed_python_files()
            if not files_to_analyze:
                print("No changed Python files found. Exiting analysis.")
                sys.exit(0)

        for file in files_to_analyze:
            try:
                with open(file, "r", encoding="utf-8") as f:
                    code = f.read()
                result = analyze_code(code)
                report_text = (
                    f"Report for {file.name}:\n"
                    f"AST Issues: {result.get('AST Issues')}\n"
                    f"PEP8: {result.get('PEP8 Issues')}\n"
                    f"Code Smells: {result.get('Code Smells')}\n"
                )
                overall_report_parts.append(report_text)
                inserted_id = save_to_db(file.name, code, result)
                if inserted_id:
                    format_analysis_results(file.name, result, inserted_id)
                else:
                    print(f"Error: Could not save results for {file} to database.")
            except Exception as e:
                print(f"Error processing {file}: {e}")
        overall_report = "\n".join(overall_report_parts) if overall_report_parts else "No analysis report available."
        with open("overall_report.txt", "w", encoding="utf-8") as f:
            f.write(overall_report)
        overall_response_id = insert_overall_report(overall_report, jira_details, branch_name)
    else:
        try:
            with open("overall_report.txt", "r", encoding="utf-8") as f:
                overall_report = f.read()
        except Exception as e:
            try:
                with open("report.md", "r", encoding="utf-8") as f:
                    overall_report = f.read()
                print("Warning: overall_report.txt not found, using report.md instead.")
            except Exception as e:
                overall_report = "No analysis report available."
                print(f"Error reading overall_report.txt and report.md: {e}")
        overall_response_id = os.getenv("LATEST_OVERALL_REPORT_ID", "unknown")

    if overall_response_id is None:
        print("Failed to insert overall analysis report. Exiting.")
        sys.exit(1)

    jira_coverage = None
    if repo_url:
        project_id = get_project_id_from_url(repo_url)
        if not project_id:
            print("Could not retrieve project ID. Exiting...")
            sys.exit(1)
        commit_shas = get_latest_commits(project_id, limit=1)
        if not commit_shas:
            print("No commits found. Exiting...")
            sys.exit(1)
        latest_commit = commit_shas[0]
        git_diff = get_git_diff(project_id, latest_commit)
        if not git_diff:
            print("Git diff is empty. Exiting...")
            sys.exit(1)
        if jira_details:
            jira_coverage = analyze_jira_issue_coverage(jira_details.get("description"), git_diff)
            # Highlight the JIRA Issue Coverage Analysis as a heading.
            overall_report += "\n\n## JIRA Issue Coverage Analysis\n" + jira_coverage
            print("\nJIRA Issue Coverage Analysis:\n", jira_coverage)

    if repo_url:
        commit_shas_for_title = get_latest_commits(project_id, limit=3)
        commit_messages = []
        for sha in commit_shas_for_title:
            msg = get_commit_message(project_id, sha)
            if msg:
                commit_messages.append(msg)
        if not commit_messages:
            print("No commit messages available for generating PR details.")
            sys.exit(1)
        if not os.getenv("OPENAI_API_KEY"):
            print("Error: OPENAI_API_KEY environment variable is not set. Exiting.")
            sys.exit(1)
        pr_title, pr_description = generate_pr_details(commit_messages, git_diff, overall_report, jira_details, branch_name)
    else:
        pr_title, pr_description = "N/A", "N/A"

    if not args.fix:
        update_report_with_pr(overall_response_id, pr_title, pr_description, overall_report, jira_details, branch_name)
        final_report = (
            f"## Analysis Report\n{overall_report}\n\n"
            f"## PR Title\n{pr_title}\n\n"
            f"## PR Description\n{pr_description}\n\n"
        )
        if jira_details:
            final_report += (
                "## Jira Ticket Details\n"
                f"- Ticket ID: {jira_details.get('ticket_id')}\n"
                f"- Summary: {jira_details.get('summary')}\n"
                f"- Description: {jira_details.get('description')}\n"
            )
            if jira_coverage:
                final_report += f"- Coverage Summary: {jira_coverage}\n"
        # Remove duplicate occurrences of key headers.
        final_report = remove_duplicate_sections(final_report, "## JIRA Issue Coverage Analysis")
        final_report = remove_duplicate_sections(final_report, "Summary of Findings:")
        with open("report.md", "w", encoding="utf-8") as f:
            f.write(final_report)
    # In fix mode, do not overwrite report.md.

    if args.fix:
        files_to_fix = []
        try:
            changed_files = subprocess.check_output(["git", "diff", "--name-only", "HEAD~1"]).decode().splitlines()
            files_to_fix = [Path(f) for f in changed_files if f.endswith(".py")]
            if not files_to_fix:
                print("No changed Python files found for fixes.")
                sys.exit(0)
        except Exception as e:
            print(f"Error determining changed files: {e}")
            sys.exit(1)
        for file in files_to_fix:
            try:
                with open(file, "r", encoding="utf-8") as f:
                    original_code = f.read()
                fixed_code = fix_code(original_code)
                with open(file, "w", encoding="utf-8") as f:
                    f.write(fixed_code)
                print(f"Updated {file} with fixed code.")
            except Exception as e:
                print(f"Error fixing {file}: {e}")
        pipeline_id = os.getenv("CI_PIPELINE_ID", "local")
        new_branch = f"fixes-{pipeline_id}"
        try:
            subprocess.check_call(["git", "checkout", "-b", new_branch])
            subprocess.check_call(["git", "add", "."])
            commit_msg = "Apply automated code fixes with full analysis report"
            subprocess.check_call(["git", "commit", "-m", commit_msg])
            gitlab_api_token = os.getenv("GITLAB_API_TOKEN")
            if not gitlab_api_token:
                print("Error: GITLAB_API_TOKEN is not set. Cannot push fixes.")
                sys.exit(1)
            push_url = f"https://oauth2:{gitlab_api_token}@{os.getenv('CI_SERVER_HOST')}/{os.getenv('CI_PROJECT_PATH')}.git"
            subprocess.check_call(["git", "push", push_url, new_branch])
            print(f"Fixed code committed and pushed to branch {new_branch} along with the full report.")
        except subprocess.CalledProcessError as e:
            print(f"Error during git operations for code fixes: {e}")

if __name__ == "__main__":
    main()
