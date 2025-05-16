import os
import re
import argparse


def argparse_args():
    parser = argparse.ArgumentParser(description="Replace strings in files within a directory.")
    parser.add_argument("--directory", type=str, help="Directory to search for files.", default="scripts")
    parser.add_argument("--your_url", type=str, help="String to replace with.")
    return parser.parse_args()


def replace_in_file(file_path, your_url):
    print(file_path)
    if "__pycache__" in file_path or ".git" in file_path or "png" in file_path or ".xlsx" in file_path or "pkl" in file_path or ".jsonl" in file_path:
        print("skip")
        return None
    with open(file_path, 'r', encoding='utf-8') as file:
        file_contents = file.read()
    file_contents = file_contents.replace("<your_base_url>", your_url)

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(file_contents)


def replace_in_directory(directory, your_url):
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            replace_in_file(file_path, your_url)


def main(args):
    replace_in_directory(args.directory, args.your_url)


if __name__ == "__main__":
    args = argparse_args()
    if args.your_url is None:
        print("Please provide a replacement string.")
        exit(1)
    main(args)
