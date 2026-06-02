import sys
import requests

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

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 main.py <github_pr_url>")
        return

    pr_url = sys.argv[1]

    owner, repo, pr_number = parse_pr_url(pr_url)

    print(f"Owner: {owner}")
    print(f"Repo: {repo}")
    print(f"PR: {pr_number}")

    diff = fetch_pr_diff(owner, repo, pr_number)

    print("\nFirst 1000 characters of diff:\n")
    print(diff[:1000])

if __name__ == "__main__":
    main()