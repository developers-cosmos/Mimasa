#!/usr/bin/env python3
import sys


def main(target_release):
    # Open the input file and the output file
    with open("CHANGELOG.md", "r") as input_file, open("release_notes.md", "w", encoding="utf-8") as output_file:
        in_target_release = False

        # Read each line of the input file
        for line in input_file:
            # Check if we're at the start of the target release section
            if line.strip() == f"## {target_release} release":
                in_target_release = True
            # Check if we've moved past the target release section
            elif line.startswith("## "):
                in_target_release = False

            # If we're in the target release section, write the line to the output file
            if in_target_release:
                output_file.write(line)


if __name__ == "__main__":
    target_release = sys.argv[1]
    main(target_release)
