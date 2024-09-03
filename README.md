# Bulk Regex Editor

[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/pylint-dev/pylint)

This script allows you to apply multiple regex patterns to a text file or all text files in a directory.

Why? Great for transcription editing or data cleaning that have similar patterns.

Create a YAML file with the regex patterns you want to apply. The script will apply the patterns to the text files and save the changes.

## Setup

1. Install Python 3 (method of your choice):
    * Simplest way: [Download Python](https://www.python.org/downloads/)
    * Homebrew: `brew install python`
    * Recommend for devs: Use [pyenv](https://github.com/pyenv/pyenv#getting-pyenv)
1. Install the required packages:

    ```bash
    pip install -r ./scripts/required_libraries.txt
    ```

1. Generate an example `regex_patterns.yaml` file by running the script with the `-e` option:

    ```bash
    python3 script/regex-bulk-edits.py -e
    ```

## How to Add RegEx Patterns?

1. Open the `regex_patterns.yaml` file.
2. Add regex patterns and replacement text into the file.

Example:

```yaml
- name: Example
  pattern: "Example:|example:| ex\/| ex:|"
  replacement: "Example:"
```

## Usage - How to Run the Script?

1. Open the [terminal](https://support.apple.com/guide/terminal/get-started-pht23b129fed/).
1. Run the following command:

    ```bash
    python3 script/regex-bulk-edits.py
    ```

### Options

usage: `regex-bulk-edits.py [-h] [-rgx REGEX] [-t TYPE] [-e] [path]`

* path: Path to a text file or directory
* `-rgx`, `--regex`: Path to the regex patterns YAML file
* `-t`, `--type`: File type to filter (e.g., .txt)
* `-e`, `--example`: Generate an example regex pattern YAML file
* `-h`, `--help`: Show this help message and exit


## Prompt Template to Generate a Regex Pattern

Use this prompt template to generate a regex pattern for the `regex_patterns.yaml` file using ChatGPT.

````md
Act like an experienced developer and help me create a regex pattern to find words for my YAML file.

Template to follow:
```yaml
- name: Name of the pattern
  pattern: "Pattern to match"
  replacement: "Replacement text"
```

Ensure the following:
* the pattern is case-insensitive
* word boundaries are used
* the special characters are escaped for YAML

Create a regex pattern to match the following words:
* example1
* example2
* example3

I want to replace the matched words with "example".
````
