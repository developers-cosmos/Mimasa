#!/usr/bin/env python3
import os
import sys
import requests

BRANCH_FORMATS = ["feature", "bug", "chore", "release", "documentation", "ci/cd"]

# pull request details
PR_HEAD_REF = os.getenv("BRANCH_NAME") or os.getenv("GITHUB_HEAD_REF")
PR_TITLE = os.getenv("GITHUB_PULL_REQUEST_TITLE") or os.getenv("PR_TITLE") or ""
PR_BODY = os.getenv("GITHUB_PULL_REQUEST_BODY") or os.getenv("PR_BODY")
OWNER = os.getenv("GITHUB_REPOSITORY_OWNER") or os.getenv("OWNER") or "developers-cosmos"
REPO = os.getenv("GITHUB_REPOSITORY") or os.getenv("REPO")
PULL_REQUEST_NUMBER = os.getenv("GITHUB_PULL_REQUEST_NUMBER") or os.getenv("PR_NUMBER")
ACCESS_TOKEN = os.environ.get("MIMASA_ADD_LABELS") or os.environ.get("GITHUB_ACCESS_TOKEN")

OWNER = OWNER.split("/")[0]
PR_TITLE = PR_TITLE.lower()

OWNER = "developers-cosmos"
REPO = "Mimasa"

def check_environment():
    health_check = (
        PR_HEAD_REF is not None
        and PR_TITLE is not None
        and OWNER is not None
        and REPO is not None
        and PULL_REQUEST_NUMBER is not None
    )
    return health_check


def get_labels_to_add():
    """Determine labels to add based on branch format, PR title, and PR body"""
    labels_to_add = []
    for label in BRANCH_FORMATS:
        branch_format = label + "/"
        if PR_HEAD_REF.startswith(branch_format) or " {label} " in PR_TITLE:
            labels_to_add.append(label)

    if " workflow " in PR_TITLE:
        labels_to_add.append("ci/cd")

    return list(set(labels_to_add))


def add_labels(labels_to_add):
    """Make API request to add labels to pull request"""
    # Define the API endpoint for adding labels to a pull request
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/issues/{PULL_REQUEST_NUMBER}/labels"

    # Set up the headers for the API request
    headers = {
        "Authorization": f"Token {ACCESS_TOKEN}",
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json",
    }

    # Make the API request to add labels to the pull request
    labels_data = {"labels": labels_to_add}

    print(f"Adding labels: {labels_data} with url: {url}")
    try:
        response = requests.post(url, headers=headers, json=labels_data)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while making the API request: {e}")
        return

    # Check if the request was successful
    if response.status_code == 200:
        print("Labels added successfully!")
    else:
        print(f"Failed to add labels. Response code: {response.status_code}. Response text: {response.text}")


def main():
    final_labels = get_labels_to_add()
    add_labels(final_labels)


if __name__ == "__main__":
    if not check_environment():
        sys.exit(0)

    main()
