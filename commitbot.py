"""version control commit generation using an LLM."""

__version__ = "0.1"
import json
import os
import subprocess
from pathlib import Path

from google import genai

# with open("secrets/.gemini_api_key") as f:
#    gemini_api_key, *_ = f.readlines()

try:
    os.environ["GEMINI_API_KEY"]
except KeyError as e:
    raise KeyError("You have not set the GEMINI_API_KEY environment variable") from e

client = genai.Client()

history_list: list[genai.types.Content] = []

SYSTEM_INSTRUCTION = """You generate concise commit messages for
    commiting to the mercurial repository. Keep the commit message
    short. 

    <tools>
    You have the following tools at your disposal
    1. A tool to list files in the current directory
    2. A tool to read file contents
    3. A tool to run a hg diff command
    </tools>

    For each file that has changes, generate a summary of the
    changes. Ensure that the summary of changes for a single file don't
    exceed two sentences. Don't show me intermediate responses. 

    For generating the summary, use the tools available. Based on the contents
    of the files and the diff, arrive at the implication or intent of the changes.
    
    Here is the structure of a good commit message:
    <commit>
    feat: add gemini client for commit message generation

    - Added `.hgignore` to exclude the `secrets` directory.
    - Added `.python-version` file to specify the Python version as
    'gemini'.
    - Implemented `main.py` with Google Gemini client integration for
    generating commit messages.
    </commit>
    """


def list_current_directory_files():
    """List files in current directory. Lists only files, not directories."""
    return json.dumps([str(f) for f in Path(".").iterdir() if f.is_file()])


def read_file_contents(filename: str) -> str:
    """Read contents of the file. The contents may contain newline
    characters."""
    with open(filename) as f:
        return f.read()


def hgdiff():
    """Return the result of the hg diff command."""
    try:
        result = subprocess.run(
            ["hg", "diff", "--git"], capture_output=True, text=True, check=True
        )
        return result.stdout
    except FileNotFoundError:
        print("Error: 'hg' command not found. ")
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        print("Stderr:", e.stderr)


def call():
    config = genai.types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTION,
        tools=[
            genai.types.Tool(
                function_declarations=[
                    genai.types.FunctionDeclaration.from_callable(
                        client=client, callable=list_current_directory_files
                    ),
                    genai.types.FunctionDeclaration.from_callable(
                        client=client, callable=read_file_contents
                    ),
                    genai.types.FunctionDeclaration.from_callable(
                        client=client, callable=hgdiff
                    ),
                ]
            )
        ],
    )
    return client.models.generate_content(
        model="gemini-2.5-flash-lite", contents=history_list, config=config
    )


def process(line):
    history_list.append(
        genai.types.Content(parts=[genai.types.Part(line)], role="user")
    )
    response = call()
    history_list.append(response.candidates[0].content)
    if function_called := response.candidates[0].content.parts[0].function_call:
        if function_called.name == "list_current_directory_files":
            result = list_current_directory_files()
        if function_called.name == "read_file_contents":
            result = read_file_contents(**function_called.args)
        if function_called.name == "hgdiff":
            result = hgdiff()
        function_response_part = genai.types.Part.from_function_response(
            name=function_called.name, response={"result": result}
        )
        # For some reason, we need to add a 'empty' query after the func call
        history_list.append(
            genai.types.Content(
                parts=[
                    genai.types.Part(
                        "Here is the result of the function "
                        "call, "
                        "now please continue the "
                        "conversation based on this "
                        "information"
                    ),
                    function_response_part,
                ],
                role="user",
            ),
        )
        response = call()
        history_list.append(response.candidates[0].content)
    return response.text


def main2():
    while True:
        line = input("> ")
        result = process(line)
        print(f">>> {result}\n")


def main():
    print(process(""))


if __name__ == "__main__":
    main()
