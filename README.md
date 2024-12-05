# Bulk Regex Editor

[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/pylint-dev/pylint)

This script allows you to apply multiple regex patterns to a text file or all text files in a directory.

Why? It's great for transcription editing or data cleaning involving similar patterns.

Create a YAML file with the regex patterns you want to apply. The script will apply the patterns to the text files and save the changes.

## Table of Contents <!-- omit in toc -->

* [Setup](#setup)
* [How to Add Regex Patterns?](#how-to-add-regex-patterns)
* [Usage - How to Run the Script?](#usage---how-to-run-the-script)
  * [Example Usage](#example-usage)
* [Script Options](#script-options)
* [Prompt Template to Generate a Regex Pattern](#prompt-template-to-generate-a-regex-pattern)
* [Sentence Case](#sentence-case)
* [Dev Notes - Feature Status](#dev-notes---feature-status)

## Setup

1. Install Python 3 (method of your choice):
    * Simplest way: [Download Python](https://www.python.org/downloads/)
    * Homebrew: `brew install python`
    * Recommended for developers: Use [pyenv](https://github.com/pyenv/pyenv#getting-pyenv)
2. Install the required packages:

    ```bash
    pip install -r ./scripts/required_libraries.txt
    ```

3. Generate an example `regex_patterns.yaml` file by running the script with the `--example` option:

    ```bash
    python3 script/regex_bulk_edits.py --example
    ```

## How to Add Regex Patterns?

Add regex patterns to the [regex_patterns.yaml](./regex_patterns.yaml) file.

Example:

  ```yaml
  - name: Example
    pattern: "Example:|example:| ex\/| ex:|"
    replacement: "Example:"
  ```

## Usage - How to Run the Script?

1. Open the [terminal](https://support.apple.com/guide/terminal/get-started-pht23b129fed/).
2. Run the following command to apply the regex patterns to all text files in the current directory:

    ```bash
    python3 script/regex_bulk_edits.py
    ```

### Example Usage

Apply the regex patterns to a specific file (e.g., `output.txt` in the `example` directory):

  ```bash
  python3 regex_bulk_edits.py ./example/output.txt
  ```

Apply the regex patterns to all text files in the `example` directory with the file type `.txt`:

  ```bash
  python3 regex_bulk_edits.py -t .txt ./example
  ```

Apply a specific regex pattern file (e.g., `custom_regex_patterns.yaml`) to all markdown files:

  ```bash
  python3 regex_bulk_edits.py -rgx custom_regex_patterns.yaml -t .md
  ```

## Script Options

Usage: `regex_bulk_edits.py [-h] [-rgx REGEX] [-t TYPE] [--example] [path]`

* path: Path to a text file or directory
* `-rgx`, `--regex`: Path to the regex patterns YAML file
* `-t`, `--type`: File type to filter (e.g., `.txt`)
* `--example`: Generate an example regex pattern YAML file
* `-h`, `--help`: Show this help message and exit

## Prompt Template to Generate a Regex Pattern

Use this prompt template to generate a regex pattern for the `regex_patterns.yaml` file using ChatGPT:

  ```md
  Act like an experienced developer and help me create a regex pattern to find words for my YAML file.

  Template to follow:
      ```yaml
      - name: Name of the pattern
        pattern: "Pattern to match"
        replacement: "Replacement text"
      ```

  Ensure the following:
  * The pattern is case-insensitive
  * Word boundaries are used
  * Special characters are escaped for YAML

  Create a regex pattern to match the following words:
  * example1
  * example2
  * example3

  I want to replace the matched words with "example".
  ```

## Sentence Case

If you want to convert the first letter of each sentence to uppercase, you can use the `$SENT_CASE()` function within the replacement regex pattern.

Example:

  ```yaml
  # Sentence Case
  - name: Use sentence case for all lines
    pattern: "^(\\w)"
    replacement: "$SENT_CASE($1)"
  ```

## Dev Notes - Feature Status

* [x] Apply regex patterns to a text file (version 1.0.0)
* [x] Apply regex patterns to all text files in a directory (version 1.0.1)
* [x] Support a specific regex pattern file (version 1.1.0)
* [x] Generate an example regex pattern YAML file (version 1.1.1)
* [ ] Add a feature to ignore .gitignore files from the bulk edit by default
* [x] Support regex capturing groups and backreferences in replacement text
* [x] Sentence case feature that can be specified in the YAML file (version 1.4.0)
* [ ] Title case feature that can be specified in the YAML file
* [ ] Lowercase feature that can be specified in the YAML file
* [ ] Uppercase feature that can be specified in the YAML file
* [ ] Make the Python script into a Mac App - [Reference](https://medium.com/@jackhuang.wz/in-just-two-steps-you-can-turn-a-python-script-into-a-macos-application-installer-6e21bce2ee71)
