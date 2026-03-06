import json
import os
import re
import subprocess
import sys
from pathlib import Path

import requests
from pydantic import Field

from dandy import BaseIntel, Bot, Prompt


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
        'Only reference lines that appear in the diff.',
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


def parse_diff_lines(diff: str) -> dict[str, set[int]]:
    diff_lines = {}
    current_file = None
    current_line = 0

    for line in diff.splitlines():
        file_match = re.match(r'^diff --git a/.+ b/(.+)$', line)
        if file_match:
            current_file = file_match.group(1)
            if current_file not in diff_lines:
                diff_lines[current_file] = set()
            continue

        hunk_match = re.match(r'^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@', line)
        if hunk_match:
            current_line = int(hunk_match.group(1))
            continue

        if current_file is None:
            continue

        if line.startswith('+') and not line.startswith('+++'):
            diff_lines[current_file].add(current_line)
            current_line += 1
        elif line.startswith('-') and not line.startswith('---'):
            pass
        else:
            current_line += 1

    return diff_lines


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

    if result.stderr:
        print(f'Ruff stderr: {result.stderr}')

    if not result.stdout.strip():
        return []

    return json.loads(result.stdout)


def ruff_results_to_comments(ruff_results: list[dict], diff_lines: dict[str, set[int]]) -> tuple[list[dict], list[str]]:
    inline_comments = []
    body_comments = []

    for violation in ruff_results:
        raw_path = violation.get('filename', '')
        line = violation.get('location', {}).get('row', 0)
        code = violation.get('code', '')
        message = violation.get('message', '')
        url = violation.get('url', '')

        relative_path = make_relative_path(raw_path)
        body = f'**Ruff [{code}]({url})**: {message}'

        file_diff_lines = diff_lines.get(relative_path, set())

        if line in file_diff_lines:
            inline_comments.append({
                'path': relative_path,
                'body': body,
                'line': line,
                'side': 'RIGHT',
            })
        else:
            body_comments.append(f'`{relative_path}:{line}` — {body}')

    return inline_comments, body_comments


def make_relative_path(raw_path: str) -> str:
    workspace = os.environ.get('GITHUB_WORKSPACE', '')

    if workspace and raw_path.startswith(workspace):
        return raw_path[len(workspace):].lstrip('/')

    return raw_path


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


def post_review(inline_comments: list[dict], body_lines: list[str]) -> None:
    if not inline_comments and not body_lines:
        return

    body = 'AI Code Review'

    if body_lines:
        body += '\n\n**Ruff issues outside of diff:**\n' + '\n'.join(f'- {line}' for line in body_lines)

    payload = {
        'body': body,
        'event': 'COMMENT',
    }

    if inline_comments:
        payload['comments'] = inline_comments

    response = requests.post(
        f'{GITHUB_API}/repos/{REPO_FULL_NAME}/pulls/{PR_NUMBER}/reviews',
        headers={
            'Authorization': f'Bearer {GH_TOKEN}',
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28',
        },
        json=payload,
        timeout=30,
    )
    response.raise_for_status()

    print(f'Posted review: {len(inline_comments)} inline comment(s), {len(body_lines)} body comment(s).')


def main() -> None:
    diff = get_diff()

    if not diff.strip():
        print('AI review: empty diff, skipping.')
        return

    diff_lines = parse_diff_lines(diff)

    changed_files = get_changed_files_from_diff(diff)
    print(f'Changed Python files: {changed_files}')

    ruff_results = run_ruff(changed_files)
    print(f'Ruff results: {len(ruff_results)} violation(s)')

    ruff_inline, ruff_body = ruff_results_to_comments(ruff_results, diff_lines)
    ruff_summary = ruff_results_to_summary(ruff_results)

    try:
        review_intel = CodeReviewBot().process(diff=diff, ruff_summary=ruff_summary)
    except Exception as e:
        print(f'AI review failed: {e}', file=sys.stderr)
        post_review(ruff_inline, ruff_body)
        sys.exit(1)

    ai_inline = []
    ai_body = []

    for comment in review_intel.comments:
        file_diff_lines = diff_lines.get(comment.path, set())

        if comment.line in file_diff_lines:
            ai_inline.append({
                'path': comment.path,
                'body': comment.body,
                'line': comment.line,
                'side': 'RIGHT',
            })
        else:
            ai_body.append(f'`{comment.path}:{comment.line}` — {comment.body}')

    all_inline = ruff_inline + ai_inline
    all_body = ruff_body + ai_body

    if all_inline or all_body:
        post_review(all_inline, all_body)
    else:
        print('AI review: no issues found.')


if __name__ == '__main__':
    main()
