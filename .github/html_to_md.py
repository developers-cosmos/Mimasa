import argparse
import html2text

# create argument parser
parser = argparse.ArgumentParser(description="Convert HTML file to Markdown")
parser.add_argument("-i", "--input", type=str, help="input HTML file path", required=True)
parser.add_argument("-o", "--output", type=str, help="output Markdown file path", required=True)

# parse arguments
args = parser.parse_args()

# read input HTML file
with open(args.input, "r") as file:
    html = file.read()

# convert HTML to Markdown
md = html2text.html2text(html)

# save Markdown file
with open(args.output, "w") as file:
    file.write(md)

print("Conversion completed!")
