import json
import os
import re
import subprocess
import sys

import requests

from pathlib import Path

from dandy import BaseIntel, Bot, Prompt
from pydantic import Field


GITHUB_API = 'https://api.github.com'

GH_TOKEN = os.environ['GH_TOKEN']
PR_NUMBER = os.environ['PR_NUMBER']
REPO_FULL_NAME = os.environ['REPO_FULL_NAME']

MAX_DIFF_LENGTH = 60000


class ReviewCommentIntel(BaseIntel):
    path: str
    body: str
    line: int


class CodeReviewIntel(BaseIntel):
    comments: list[ReviewCommentIntel] = Field(default_factory=list)


class CodeReviewBot(Bot):
    role = 'Senior Code Reviewer'
    task = 'Review the provided pull request diff and identify meaningful issues.'
    guidelines = Prompt().list([
        'Focus on bugs, logic errors, security issues, and performance concerns.',
        'Do NOT comment on style preferences, formatting, or minor naming opinions.',
        'Do NOT comment on things that are clearly intentional design decisions.',
        'If the code looks good, return an empty comments list.',
        'Ruff linting results are provided separately, do NOT duplicate them.',
    ])
    intel_class = CodeReviewIntel

    def process(self, diff: str, ruff_summary: str) -> CodeReviewIntel:
        prompt = Prompt()

        if ruff_summary:
            prompt.heading('Ruff Linting Results (already posted separately)')
            prompt.text(ruff_summary, triple_backtick=True)
            prompt.lb()

        prompt.heading('Pull Request Diff')
        prompt.text(diff, triple_backtick=True)

        return self.llm.prompt_to_intel(prompt=prompt)


def get_diff() -> str:
    with open('pr_diff.patch', 'r') as f:
        diff = f.read()

    if len(diff) > MAX_DIFF_LENGTH:
        diff = diff[:MAX_DIFF_LENGTH] + '\n\n... (diff truncated due to size)'

    return diff


def get_changed_files_from_diff(diff: str) -> list[str]:
    files = []

    for match in re.finditer(r'^diff --git a/.+ b/(.+)$', diff, re.MULTILINE):
        file_path = match.group(1)
        if file_path.endswith('.py'):
            files.append(file_path)

    return files


def run_ruff(changed_files: list[str]) -> list[dict]:
    existing_files = [f for f in changed_files if Path(f).is_file()]

    if not existing_files:
        return []

    try:
        result = subprocess.run(
            [sys.executable, '-m', 'ruff', 'check', '--output-format=json', *existing_files],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        print('ruff not found, skipping lint step.')
        return []

    if not result.stdout.strip():
        return []

    return json.loads(result.stdout)


def ruff_results_to_review_comments(ruff_results: list[dict]) -> list[dict]:
    comments = []

    for violation in ruff_results:
        path = violation.get('filename', '')
        line = violation.get('location', {}).get('row', 0)
        code = violation.get('code', '')
        message = violation.get('message', '')
        url = violation.get('url', '')

        body = f'**Ruff [{code}]({url})**: {message}'

        comments.append({
            'path': path,
            'body': body,
            'line': line,
            'side': 'RIGHT',
        })

    return comments


def ruff_results_to_summary(ruff_results: list[dict]) -> str:
    if not ruff_results:
        return ''

    lines = []

    for violation in ruff_results:
        path = violation.get('filename', '')
        line = violation.get('location', {}).get('row', 0)
        code = violation.get('code', '')
        message = violation.get('message', '')
        lines.append(f'{path}:{line} {code} {message}')

    return '\n'.join(lines)


def post_review_comments(comments: list[dict]) -> None:
    if not comments:
        return

    response = requests.post(
        f'{GITHUB_API}/repos/{REPO_FULL_NAME}/pulls/{PR_NUMBER}/reviews',
        headers={
            'Authorization': f'Bearer {GH_TOKEN}',
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28',
        },
        json={
            'body': 'AI Code Review',
            'event': 'COMMENT',
            'comments': comments,
        },
        timeout=30,
    )
    response.raise_for_status()

    print(f'Posted {len(comments)} review comment(s).')


def main() -> None:
    diff = get_diff()

    if not diff.strip():
        print('AI review: empty diff, skipping.')
        return

    changed_files = get_changed_files_from_diff(diff)
    ruff_results = run_ruff(changed_files)
    ruff_comments = ruff_results_to_review_comments(ruff_results)
    ruff_summary = ruff_results_to_summary(ruff_results)

    if ruff_comments:
        print(f'Ruff found {len(ruff_comments)} issue(s).')
        post_review_comments(ruff_comments)

    try:
        review_intel = CodeReviewBot().process(diff=diff, ruff_summary=ruff_summary)
    except Exception as e:
        print(f'AI review failed: {e}', file=sys.stderr)
        sys.exit(1)

    ai_comments = [
        {
            'path': comment.path,
            'body': comment.body,
            'line': comment.line,
            'side': 'RIGHT',
        }
        for comment in review_intel.comments
    ]

    if ai_comments:
        post_review_comments(ai_comments)
    else:
        print('AI review: no issues found.')


if __name__ == '__main__':
    main()
