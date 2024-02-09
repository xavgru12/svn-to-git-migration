import subprocess
import sys
import argparse

parser = argparse.ArgumentParser(description='get commit hash from revision')
parser.add_argument('--revision', "-r", required=True, type=int, help='Create a .gitignore file.')
parser.add_argument("path", nargs="?")

args = parser.parse_args()
revision = args.revision

revision = f"r{revision}"

print(f"revision: {revision}")
print(f"path: {args.path}")

output = subprocess.check_output(["git", "svn", "log", "--show-commit", "--oneline"], cwd=args.path).decode(
    sys.stdout.encoding)

found = False
for line in output.splitlines():
    if revision in line:
        found = True
        print(line.split("|")[1].strip())

if found is False:
    print("revision not found in git, please check if the necessary branch was fetched by git")
