#!/usr/bin/env python3
import os
import sys

def main():
    # Get labels and formats from config file
    labels = []
    branch_formats = []
    with open(".github/labels_config.txt") as f:
        for line in f:
            label, branch_format = line.strip().split()
            labels.append(label)
            branch_formats.append(branch_format)

    # Get pull request details
    pr_head_ref = os.getenv("GITHUB_HEAD_REF") or os.getenv("BRANCH_NAME") or ""
    pr_title = os.getenv("GITHUB_PULL_REQUEST_TITLE") or os.getenv("PR_TITLE") or ""
    pr_title = pr_title.lower()

    matching_labels = ""
    for i in range(len(labels)):
        label = labels[i]
        branch_format = branch_formats[i] + "/"

        if pr_head_ref.startswith(branch_format) or label in pr_title:
            matching_labels.append(label)

    if len(matching_labels) > 0:
        result = '\n'.join(matching_labels)
        with open("labels.txt", "w") as f:
            f.write(result)
        sys.exit(0)

    sys.exit(1)

if __name__ == "__main__":
    main()
