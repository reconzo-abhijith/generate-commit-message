# Gemini Commit Generator

Automates the generation of concise Mercurial commit messages using the Google Gemini API. Analyzes code changes and provides file-specific summaries.

## Features

*   Automated commit message generation.
*   Code change summarization via `hg diff`.
*   Google Gemini API integration.
*   File system and diff interaction tools.

## Setup

1.  **Prerequisites:** Python 3.x, Mercurial (hg), Gemini API key.
2.  **Clone:**
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```
3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    # (Ensure requirements.txt lists google-generativeai, etc.)
    ```
4.  **Configure API Key:**
    *   Create `secrets/.gemini_api_key`.
    *   Paste your Gemini API key into the file.

## Usage

1.  Run the tool:
    ```bash
    python main.py
    ```
2.  Interact with the prompt to generate commit messages for your changes.

## How it Works

The script uses the Gemini API with defined tools (`list_current_directory_files`, `read_file_contents`, `hgdiff`) to gather context. It then generates commit messages based on the provided system instructions and code diffs.

## License

MIT License
