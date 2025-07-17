#!/usr/bin/env python3
"""
GitHub Actions script to send Slack notifications for new pull requests.
Summarizes PR description or commit messages if no description is available.
"""

import os
import re
import subprocess
import sys
from typing import List

import httpx


def get_commit_messages(base_sha: str, head_sha: str) -> List[str]:
    """Get commit messages between base and head SHA."""
    try:
        # Get commit messages for the PR
        result = subprocess.run(
            ["git", "log", "--pretty=format:%s", f"{base_sha}..{head_sha}"],
            capture_output=True,
            text=True,
            check=True,
        )
        messages = [
            msg.strip() for msg in result.stdout.strip().split("\n") if msg.strip()
        ]
        return messages
    except subprocess.CalledProcessError as e:
        print(f"Error getting commit messages: {e}")
        return []


def clean_text(text: str) -> str:
    """Clean and normalize text for processing."""
    if not text:
        return ""

    # Remove excessive whitespace and newlines
    text = re.sub(r"\s+", " ", text.strip())

    # Remove markdown formatting
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)  # Bold
    text = re.sub(r"\*(.+?)\*", r"\1", text)  # Italic
    text = re.sub(r"`(.+?)`", r"\1", text)  # Code
    text = re.sub(r"#{1,6}\s*", "", text)  # Headers
    text = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", text)  # Links

    return text.strip()


def summarize_text(text: str, max_length: int = 100) -> str:
    """Create a one-sentence summary of the given text."""
    if not text:
        return "No description available"

    # Clean the text
    cleaned = clean_text(text)

    # Split into sentences
    sentences = re.split(r"[.!?]+", cleaned)
    sentences = [s.strip() for s in sentences if s.strip()]

    if not sentences:
        return "No description available"

    # Try to find the most informative sentence
    summary = sentences[0]

    # If first sentence is too short or generic, try to combine or find better one
    if len(summary) < 20:
        for sentence in sentences[1:]:
            if len(f"{summary} {sentence}") <= max_length:
                summary = f"{summary} {sentence}"
            else:
                break

    # Truncate if too long
    if len(summary) > max_length:
        summary = summary[: max_length - 3] + "..."

    return summary


def summarize_commits(commit_messages: List[str]) -> str:
    """Summarize commit messages into a single sentence."""
    if not commit_messages:
        return "No commits found"

    # Filter out merge commits and common patterns
    filtered_commits = []
    for msg in commit_messages:
        msg_lower = msg.lower()
        if not any(
            pattern in msg_lower
            for pattern in ["merge", "wip", "fixup", "squash", "revert"]
        ):
            filtered_commits.append(msg)

    if not filtered_commits:
        filtered_commits = commit_messages  # Fall back to all commits

    # Take up to 3 most relevant commits
    relevant_commits = filtered_commits[:3]

    if len(relevant_commits) == 1:
        return summarize_text(relevant_commits[0])
    else:
        # Combine multiple commits
        combined = " and ".join(relevant_commits)
        return summarize_text(combined)


def send_slack_message(token: str, channel: str, message: str) -> bool:
    """Send a message to Slack channel."""
    url = "https://slack.com/api/chat.postMessage"

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    data = {
        "channel": channel,
        "text": message,
        "unfurl_links": True,
        "unfurl_media": True,
    }

    with httpx.Client() as client:
        response = client.post(url, headers=headers, json=data)
        response.raise_for_status()

        result = response.text
        if "ok" in result:
            print("✅ Slack message sent successfully")
            return True
        else:
            print(f"❌ Slack API error: {result}")
            return False


def main():
    """Main function to process PR and send Slack notification."""
    # Get environment variables
    slack_token = os.getenv("SLACK_BOT_TOKEN")
    slack_channel = os.getenv("SLACK_CHANNEL")
    pr_number = os.getenv("PR_NUMBER")
    pr_title = os.getenv("PR_TITLE")
    pr_body = os.getenv("PR_BODY")
    pr_url = os.getenv("PR_URL")
    pr_author = os.getenv("PR_AUTHOR")
    repo_name = os.getenv("REPO_NAME")
    base_sha = os.getenv("BASE_SHA")
    head_sha = os.getenv("HEAD_SHA")

    # Validate required environment variables
    if not slack_token:
        print("❌ SLACK_BOT_TOKEN environment variable is required")
        sys.exit(1)

    if not slack_channel:
        print("❌ SLACK_CHANNEL environment variable is required")
        sys.exit(1)

    if not all([pr_number, pr_title, pr_url, pr_author, repo_name]):
        print("❌ Missing required PR information")
        sys.exit(1)

    print(f"Processing PR #{pr_number}: {pr_title}")

    # Determine summary source and create summary
    if pr_body and pr_body.strip():
        print("Using PR description for summary")
        summary = summarize_text(pr_body)
    else:
        print("No PR description found, using commit messages")
        if base_sha and head_sha:
            commit_messages = get_commit_messages(base_sha, head_sha)
            summary = summarize_commits(commit_messages)
        else:
            summary = "No description or commits available"

    # Create Slack message
    message = (
        f"Hello Team. Please, review this opened PR in {repo_name}\n"
        f"*{pr_title}* by @{pr_author}\n"
        f"Summary: {summary}\n"
        f":pr-opened: Link: {pr_url}"
    )

    print(f"Sending message to #{slack_channel}")
    print(f"Message: {message}")

    # Send to Slack
    success = send_slack_message(slack_token, slack_channel, message)

    if not success:
        sys.exit(1)

    print("✅ Process completed successfully")


if __name__ == "__main__":
    main()
