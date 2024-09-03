#!/usr/bin/env python3
"""
Script Name: regex-bulk-edits.py
Usage: python3 regex-bulk-edits.py [-h] [-rgx REGEX] [file_or_directory_path] [-t file_type] [-e]
Purpose: Performs bulk regex-based edits on specified text files or all text files in a directory.
Versions:
+ 1.2.0 - Fixing py
+ 1.1.1 - Fix example YAML file generator; changed regex patterns file to not be hidden
+ 1.0.0 - Initial version; replacement function working
"""

import argparse
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
import yaml # pylint: disable=import-error

# Default configurations
DEFAULT_REGEX_FILE = "regex_patterns.yaml"
DEFAULT_LOG_FILE = "regex_bulk_edits.log"
DEFAULT_FILE_TYPES = [".txt", ".md"]


def install_libraries():
    """
    Installs missing libraries required for the script.

    :return: True if all required libraries are installed, otherwise False.
    """
    required_libraries = ["yaml", "argparse"]
    missing_libraries = [
        lib for lib in required_libraries if not is_library_installed(lib)
    ]

    if not missing_libraries:
        return True

    print("Error - Required libraries are not installed:")
    for lib in missing_libraries:
        print(f"- {lib}")

    user_input = (
        input("\nDo you want to install the required libraries? (y/n): ")
        .strip()
        .lower()
    )
    if user_input == "y":
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", *missing_libraries]
            )
            print("\nLibraries installed successfully.")
            return True
        except subprocess.CalledProcessError:
            print("\nFailed to install the required libraries.")
    else:
        print("\nPlease install the required libraries to run the function.")
        print(f"Install manually by running: pip install {' '.join(missing_libraries)}")
    return False


def is_library_installed(library):
    """
    Checks if a Python library is installed.

    :param library: The name of the library to check.

    :return: True if the library is installed, otherwise False.
    """
    try:
        __import__(library)
        return True
    except ImportError:
        return False


def log_start(log_file, arguments):
    """
    Starts a logging session.

    :param log_file: The path to the log file.

    :param arguments: The arguments used for the script run.
    """
    with open(log_file, "a", encoding="utf-8") as log:
        log.write(
            f"\n---\n# {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Arguments: {' '.join(arguments)}\n---\n"
        )


def log_end(log_file):
    """
    Ends a logging session.

    :param log_file: The path to the log file.
    """
    with open(log_file, "a", encoding="utf-8") as log:
        log.write("---\n")
    terminal_output(f"Log file updated: {os.path.relpath(log_file)}")


def log_changes(log_file, file_path, changes):
    """
    Logs changes made to a file.

    :param log_file: The path to the log file.

    :param file_path: The path to the file that was edited.

    :param changes: A list of changes made to the file.
    """
    home = str(Path.home())
    short_path = str(file_path).replace(home, "~")
    with open(log_file, "a", encoding="utf-8") as log:
        log.write(f"* {short_path}\n")
        for line, original, replacement in changes:
            log.write(f'  * Line {line}: "{original}" -> "{replacement}"\n')


def load_regex_patterns(file_path):
    """
    Loads regex patterns from a YAML file.

    :param file_path: The path to the YAML file containing regex patterns.

    :return: A list of regex patterns.
    """
    e_flag_message = "Generate an example regex pattern YAML file by using the -e flag:\n  python3 regex-bulk-edits.py -e"
    if not Path(file_path).exists():
        terminal_output(
            f"Error: The regex patterns file '{file_path}' does not exist.\n{e_flag_message}"
        )
        sys.exit(1)
    if not file_path.endswith(".yaml"):
        terminal_output(
            f"Error: The regex patterns file '{file_path}' is not a YAML file.\n{e_flag_message}"
        )
        sys.exit(1)

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            patterns = yaml.safe_load(file)
            for pattern in patterns:
                if not all(
                    key in pattern for key in ("name", "pattern", "replacement")
                ):
                    terminal_output(
                        "Error: Missing required keys ('name', 'pattern', 'replacement') in regex patterns file."
                    )
                    sys.exit(1)
            return patterns
    except yaml.YAMLError as exc:
        terminal_output(f"Error parsing YAML file: {exc}")
        sys.exit(1)


def edit_file(file_path, regex_patterns):
    """
    Edits a file based on the given regex patterns.

    :param file_path: The path to the file to edit.

    :param regex_patterns: A list of regex patterns.
    """
    changes = []
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        with open(file_path, "w", encoding="utf-8") as file:
            for i, line in enumerate(lines, 1):
                original_line = line
                for pattern in regex_patterns:
                    line = re.sub(pattern["pattern"], pattern["replacement"], line)
                if original_line != line:
                    changes.append((i, original_line.strip(), line.strip()))
                file.write(line)

        if changes:
            log_changes(DEFAULT_LOG_FILE, file_path, changes)
    except Exception as e:  # pylint: disable=broad-exception-caught
        terminal_output(f"Error editing file '{file_path}': {e}")


def find_files(path, file_types):
    """
    Finds files in a directory that match the specified file types.

    :param path: The path to search (file or directory).

    :param file_types: The file types to filter.
    """
    path = Path(path)
    regex_patterns = load_regex_patterns(DEFAULT_REGEX_FILE)
    if path.is_file():
        edit_file(path, regex_patterns)
    elif path.is_dir():
        for file_path in path.rglob("*"):
            if file_path.suffix in file_types:
                edit_file(file_path, regex_patterns)
    else:
        terminal_output(f"Error: '{path}' is not a valid file or directory.")
        sys.exit(1)


def parse_arguments():
    """
    Parses command-line arguments.

    :return: Parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="Bulk regex-based text editing script."
    )
    parser.add_argument(
        "-rgx",
        "--regex",
        type=str,
        help="Path to the regex patterns YAML file",
        default=DEFAULT_REGEX_FILE,
    )
    parser.add_argument(
        "path",
        nargs="?",
        type=str,
        help="Path to a text file or directory",
        default=".",
    )
    parser.add_argument(
        "-t", "--type", type=str, help="File type to filter (e.g., .txt)", default=None
    )
    parser.add_argument(
        "-e",
        "--example",
        action="store_true",
        help="Generate an example regex pattern YAML file",
    )
    return parser.parse_args()


def validate_arguments(args):
    """
    Validates the script's arguments.

    :param args: Parsed arguments.
    """
    if args.regex and not args.regex.endswith(".yaml"):
        terminal_output("Error: The regex patterns file must be a YAML file.")
        sys.exit(1)

    if args.type:
        file_type_validator(args.type)


def file_type_validator(file_type):
    """
    Validates the file type.

    :param file_type: The file type to validate.
    """
    valid_file_types = [".txt", ".md", ".rtf", ".html", ".json", ".csv", ".tsv"]
    file_type = file_type if file_type.startswith(".") else f".{file_type}"
    if file_type not in valid_file_types:
        terminal_output(
            f"Error: Invalid file type '{file_type}'. Valid types are: {', '.join(valid_file_types)}."
        )
        sys.exit(1)


def terminal_output(message):
    """
    Outputs a message to the terminal.

    :param message: The message to output.
    """
    print(message)


def create_example_regex_pattern_file():
    """
    Creates an example regex pattern YAML file.

    :return: The path to the created file.
    """
    file_path = DEFAULT_REGEX_FILE
    yaml_content = """- name: input
  pattern: "regex pattern"
  replacement: "replacement"

- name: example
  pattern: "(?i)\\\\bexample\\\\b"
  replacement: "EXAMPLE"
"""
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(yaml_content)
    terminal_output(
        f"Example regex patterns YAML file generated at: {os.path.relpath(file_path)}"
    )
    return file_path


def main():
    """
    Main function to execute the script.
    """
    if not install_libraries():
        print("Failed to install libraries. Exiting the script.")
        sys.exit(1)

    args = parse_arguments()
    validate_arguments(args)

    log_start(DEFAULT_LOG_FILE, sys.argv)

    if args.example:
        create_example_regex_pattern_file()
        sys.exit(0)

    find_files(args.path, [args.type] if args.type else DEFAULT_FILE_TYPES)

    log_end(DEFAULT_LOG_FILE)


if __name__ == "__main__":
    main()
