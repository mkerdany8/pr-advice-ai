import os
import sys
import argparse
import requests
from dotenv import load_dotenv

load_dotenv()

def parse_pr_url(url):
    parts = url.strip("/").split("/")
    owner = parts[-4]
    repo = parts[-3]
    pr_number = parts[-1]
    return owner, repo, pr_number

def fetch_pr_diff(owner, repo, pr_number):
    diff_url = f"https://github.com/{owner}/{repo}/pull/{pr_number}.diff"
    response = requests.get(diff_url)

    if response.status_code != 200:
        raise Exception("Could not fetch PR diff")

    return response.text

def generate_ai_summary(diff_text, model="google/gemini-3.1-flash-lite"):
    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        raise Exception("Missing OPENROUTER_API_KEY. Add it to your .env file.")

    prompt = f"""
You are a senior software developer reviewing a GitHub pull request.

Explain this PR in a clear way for a junior developer.

Include these sections:
1. Summary
2. Main Changes
3. Potential Risks
4. What a Junior Developer Can Learn

PR diff:
{diff_text[:12000]}
"""

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
    )

    if response.status_code != 200:
        raise Exception(f"OpenRouter error: {response.status_code}\n{response.text}")

    return response.json()["choices"][0]["message"]["content"]

def save_review(summary):
    with open("review.md", "w") as file:
        file.write(summary)

def main():
    parser = argparse.ArgumentParser(description="AI-powered GitHub PR reviewer")
    parser.add_argument("pr_url", help="GitHub PR URL")
    parser.add_argument("--model", default="google/gemini-3.1-flash-lite", help="OpenRouter model to use")
    args = parser.parse_args()

    pr_url = args.pr_url
    owner, repo, pr_number = parse_pr_url(pr_url)

    print(f"Owner: {owner}")
    print(f"Repo: {repo}")
    print(f"PR: {pr_number}")

    print("\nFetching PR diff...")
    diff = fetch_pr_diff(owner, repo, pr_number)

    print("Generating AI summary...")
    summary = generate_ai_summary(diff, model=args.model)

    print("\n--- AI REVIEW ---\n")
    print(summary)

    save_review(summary)
    print("\nSaved review to review.md")

if __name__ == "__main__":
    main()