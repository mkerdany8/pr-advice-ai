# PR Advice AI

A Python CLI that takes a GitHub pull request URL, fetches the raw diff, and uses an LLM to produce a structured code review written for a junior developer.

Built to answer a practical question: when you are new to a large codebase, a PR diff tells you *what* changed but not *why it matters*. This tool turns a diff into an explanation.

## Example

Run against a real VS Code PR:

```bash
python3 main.py https://github.com/microsoft/vscode/pull/123456
```

The model returns a review in four fixed sections — Summary, Main Changes, Potential Risks, and What a Junior Developer Can Learn. See [example-review.md](example-review.md) for full generated output on a real PR.

## How it works

1. **Parse** the PR URL into owner, repo, and PR number.
2. **Fetch** the diff directly from GitHub's `.diff` endpoint — no API token needed, since public PR diffs are served as plain text.
3. **Prompt** an LLM through the OpenRouter chat completions API, with a system framing that fixes the four output sections so results stay consistent across different PRs.
4. **Save** the review to `review.md` and print it to stdout.

The diff is truncated to 12,000 characters before being sent, to stay inside the model's context window on large PRs.

## Setup

```bash
git clone https://github.com/mkerdany8/pr-advice-ai
cd pr-advice-ai
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```
OPENROUTER_API_KEY=your_key_here
```

Get a key at [openrouter.ai](https://openrouter.ai). `.env` is gitignored and is never committed.

## Usage

```bash
# Default model
python3 main.py https://github.com/owner/repo/pull/123

# Pick a different model
python3 main.py https://github.com/owner/repo/pull/123 --model anthropic/claude-sonnet-4
```

Any model slug available on OpenRouter works.

## Design notes

- **Why OpenRouter rather than a single provider SDK** — one API surface for many models, so swapping between them is a CLI flag rather than a code change.
- **Why fixed output sections** — free-form summaries varied a lot between runs and between models. Pinning four sections in the prompt made output comparable across PRs and made it obvious when a model was underperforming.
- **Why raw `requests` rather than a framework** — the whole call is one POST. A framework would have added dependencies without removing any real complexity at this size.

## Limitations

- Truncates diffs at 12,000 characters, so very large PRs are only partially reviewed.
- Makes a single LLM call; it does not chunk large diffs or do multi-pass review.
- Public repositories only — there is no authentication for fetching private PR diffs.
- Review quality depends entirely on the model; it does not run or test the code it reviews.

## Possible next steps

- Chunk large diffs and synthesize a combined review across chunks.
- Add a GitHub token so private PRs can be reviewed.
- Post the review back as a PR comment via the GitHub API.
- Cache responses per PR so re-running does not re-bill the same diff.

## Tech

Python 3, `requests`, `python-dotenv`, OpenRouter chat completions API.
