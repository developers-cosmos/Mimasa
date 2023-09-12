import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", type=str, required=True, help="The input HTML file path")
parser.add_argument("-o", "--output", type=str, required=True, help="The output markdown file path")
args = parser.parse_args()

import argparse
import re


# Define colors
class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


# Read input file
with open(args.input, "r") as f:
    content = f.read()

# Remove links
content = re.sub(r"\[([^]]*)\]\([^)]*\)", r"\1", content)

# Split content into lines
lines = content.split("\n")

# Parse lines and output colored text
with open(args.output, "w") as f:
    f.write(f"{bcolors.OKBLUE}Module | statements | missing | excluded | coverage{bcolors.ENDC}\n")
    f.write("-" * 80 + "\n")
    for line in lines:
        if line.startswith("|"):
            cols = line.split("|")[1:-1]
            if float(cols[-1].replace("\x1b[93m", "").replace("\x1b[0m", "")[:-1]) < 50:
                print(f"Coverage below 50%: {cols[-1]}")
            cols = [col.strip() for col in cols]
            cols = [col if col != "0" else f"{bcolors.WARNING}{col}{bcolors.ENDC}" for col in cols]
            if float(cols[-1].replace("\x1b[93m", "").replace("\x1b[0m", "")[:-1]) < 50:
                cols[-1] = f"{bcolors.FAIL}{cols[-1]}{bcolors.ENDC}"
            elif float(cols[-1][:-1]) < 80:
                cols[-1] = f"{bcolors.WARNING}{cols[-1]}{bcolors.ENDC}"
            else:
                cols[-1] = f"{bcolors.OKGREEN}{cols[-1]}{bcolors.ENDC}"
            f.write(f"| {cols[0]} | {cols[1]} | {cols[2]} | {cols[3]} | {cols[4]} |\n")
        else:
            f.write(line + "\n")
