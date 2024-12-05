#!/usr/bin/env python3
"""
Name:     regex_bulk_edits.py
Purpose:  Performs bulk regex-based edits on specified text files or all text files in a directory.
Usage:    python3 regex_bulk_edits.py [-h] [-rgx REGEX] [file_or_directory_path] [-t file_type] [--example]
Arguments:
    -h,           --help            Show this help message and exit.
    -rgx REGEX,   --regex REGEX     Path to the regex patterns YAML file.
    file_or_directory_path          Path to a text file or directory. Defaults to the current directory.
    -t file_type, --type file_type  File type to filter (e.g., .txt). Defaults to .txt and .md.
    --example                       Generate an example regex pattern YAML file.
Notes:
  + Ensure the regex patterns in the YAML file have properly escaped backslashes.
  + Added support for $SENT_CASE() function in replacement strings.
Versions:
  + 1.4.1 - Fix "consider-using-f-string" pylint error
  + 1.4.0 - Added support for $SENT_CASE() function in replacement strings
  + 1.3.1 - Added support for capturing groups and backreferences in replacement text
  + 1.2.1 - Improvements to handling of regex patterns file
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
import yaml  # pylint: disable=import-error

# Default configurations
DEFAULT_REGEX_FILE = "regex_patterns.yaml"
DEFAULT_LOG_FILE = "regex_bulk_edits.log"
DEFAULT_FILE_TYPES = [".txt", ".md"]


def install_libraries():
    """
    Installs missing libraries required for the script.

    :return: True if all required libraries are installed, otherwise False.
    """
    required_libraries = ["yaml"]
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
        print("\nPlease install the required libraries to run the script.")
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
            f"\n---\n"
            f"# {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Arguments: {' '.join(arguments)}\n"
            f"---\n"
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


def process_replacement_string(replacement):
    """
    Processes the replacement string to convert `$1` syntax to `\\g<1>` syntax.

    Example:
        Input: "Replace $1 with this"
        Output: "Replace \\g<1> with this"

    :param replacement: (str) The replacement string to process.
    :raises ValueError: If the input is not a string.
    :return: (str) The processed replacement string.
    """
    if not isinstance(replacement, str):
        raise ValueError("Input replacement must be a string.")

    try:
        processed_string = re.sub(
            r"\$(\d+)", lambda m: rf"\g<{m.group(1)}>", replacement
        )
        return processed_string
    except Exception as e:
        raise RuntimeError(
            f"An error occurred while processing the string: {e}"
        ) from e  # pylint: disable=broad-exception-caught


def sentence_case_converter(s):
    """
    Converts a string to sentence case.

    :param s: The input string.

    :return: The string converted to sentence case.
    """
    if not s:
        return ""
    return s[0].upper() + s[1:].lower()


def create_replacement_function(replacement_string):
    """
    Creates a replacement function for re.sub, handling $SENT_CASE() in the replacement string.

    :param replacement_string: The replacement string containing $SENT_CASE()

    :return: A function that can be used as the replacement in re.sub
    """
    # Tokenize the replacement string
    token_pattern = re.compile(r"(\$SENT_CASE\((.*?)\))|(\$\d+)|([^$]+)|(\$)")

    tokens = []
    pos = 0
    while pos < len(replacement_string):
        match = token_pattern.match(replacement_string, pos)
        if not match:
            break
        if match.group(1):  # $SENT_CASE(some_content)
            content = match.group(2)  # the content inside the parentheses
            tokens.append(("SENT_CASE", content))
        elif match.group(3):  # $n
            tokens.append(("GROUP", int(match.group(3)[1:])))
        elif match.group(4):  # Text
            tokens.append(("TEXT", match.group(4)))
        elif match.group(5):  # Single $
            tokens.append(("TEXT", "$"))
        pos = match.end()

    def replacement_function(match):
        # Build the replacement string
        result = ""
        for token in tokens:
            if token[0] == "TEXT":
                result += token[1]
            elif token[0] == "GROUP":
                group_num = token[1]
                group_text = match.group(group_num)
                result += group_text if group_text is not None else ""
            elif token[0] == "SENT_CASE":
                content = token[1]
                # Process the content, which may contain $n references
                content_result = ""
                content_pos = 0
                while content_pos < len(content):
                    content_match = re.match(
                        r"(\$\d+)|([^\$]+)|(\$)", content[content_pos:]
                    )
                    if not content_match:
                        break
                    if content_match.group(1):  # $n
                        group_num = int(content_match.group(1)[1:])
                        group_text = match.group(group_num)
                        content_result += group_text if group_text is not None else ""
                    elif content_match.group(2):  # Text
                        content_result += content_match.group(2)
                    elif content_match.group(3):  # Single $
                        content_result += "$"
                    content_pos += content_match.end()
                # Apply sentence case to content_result
                result += sentence_case_converter(content_result)
        return result

    return replacement_function


def load_regex_patterns(file_path):
    """
    Loads and compiles regex patterns from a YAML file.

    :param file_path: The path to the YAML file containing regex patterns.

    :return: A list of regex patterns with compiled patterns.
    """
    e_flag_message = (
        "Generate an example regex pattern YAML file by using the --example flag:\n"
        "  python3 regex_bulk_edits.py --example"
    )
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
                try:
                    pattern["compiled_pattern"] = re.compile(pattern["pattern"])
                    if "$SENT_CASE(" in pattern["replacement"]:
                        pattern["use_function"] = True
                        pattern["replacement_function"] = create_replacement_function(
                            pattern["replacement"]
                        )
                    else:
                        pattern["use_function"] = False
                        pattern["processed_replacement"] = process_replacement_string(
                            pattern["replacement"]
                        )
                except re.error as e:
                    terminal_output(f"Error compiling pattern '{pattern['name']}': {e}")
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
                    if pattern.get("use_function", False):
                        line = pattern["compiled_pattern"].sub(
                            pattern["replacement_function"], line
                        )
                    else:
                        line = pattern["compiled_pattern"].sub(
                            pattern["processed_replacement"], line
                        )
                if original_line != line:
                    changes.append((i, original_line.strip(), line.strip()))
                file.write(line)

        if changes:
            log_changes(DEFAULT_LOG_FILE, file_path, changes)
    except Exception as e:  # pylint: disable=broad-exception-caught
        terminal_output(f"Error editing file '{file_path}': {e}")


def find_files(path, file_types, regex_patterns):
    """
    Finds files in a directory that match the specified file types.

    :param path: The path to search (file or directory).
    :param file_types: The file types to filter.
    :param regex_patterns: The compiled regex patterns.
    """
    path = Path(path)
    if path.is_file():
        edit_file(path, regex_patterns)
        edit_file(path, regex_patterns)
    elif path.is_dir():
        for file_path in path.rglob("*"):
            if file_path.suffix in file_types:
                edit_file(file_path, regex_patterns)
                edit_file(path, regex_patterns)
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
        "-t",
        "--type",
        type=str,
        help="File type to filter (e.g., .txt)",
        default=None,
    )
    parser.add_argument(
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
    valid_file_types = [
        ".txt",
        ".md",
        ".rtf",
        ".html",
        ".json",
        ".csv",
        ".tsv",
    ]
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
        sys.exit(1)

    args = parse_arguments()
    validate_arguments(args)

    if args.example:
        create_example_regex_pattern_file()
        sys.exit(0)

    regex_patterns = load_regex_patterns(args.regex)
    log_start(DEFAULT_LOG_FILE, sys.argv)

    find_files(
        args.path, [args.type] if args.type else DEFAULT_FILE_TYPES, regex_patterns
    )

    log_end(DEFAULT_LOG_FILE)


if __name__ == "__main__":
    main()
