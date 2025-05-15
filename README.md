# PDF to Text Transcription Tool

This Python tool transcribes text from PDF files using OpenAI's GPT-4.1 model. It processes each page of a PDF by converting it into an image, sending the image to the OpenAI API for OCR, and then saving the transcribed text to a file.

## Features

*   Processes multi-page PDF files.
*   Converts PDF pages to PNG images for OCR.
*   Utilizes OpenAI's GPT-4.1 model for high-quality text transcription.
*   Saves transcriptions in the `data/output` directory, with one text file per input PDF.
*   Manages dependencies using `uv`.
*   Handles API keys securely using `python-dotenv`.

## Directory Structure

```
pdf-to-text/
├── data/
│   ├── input/      # Place your PDF files here
│   └── output/     # Transcribed text files will be saved here
├── src/
│   └── main.py     # Main application script
├── .env            # For storing your OpenAI API key (create this manually)
├── .gitignore
└── pyproject.toml  # Project metadata and dependencies
```

## Prerequisites

*   Python 3.8+ (or as specified in `pyproject.toml`)
*   [uv](https://github.com/astral-sh/uv) (Python package installer and virtual environment manager)
*   An OpenAI API key

## Setup

1.  **Clone the repository (or set up the project files):**
    Ensure you have all the project files in your local directory.

2.  **Create and activate a virtual environment using `uv`:**
    ```bash
    uv venv
    source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    uv pip sync pyproject.toml
    ```
    (If a `uv.lock` file is present and up-to-date, you can also use `uv sync`)

4.  **Set up your OpenAI API Key:**
    Create a file named `.env` in the root directory of the project and add your OpenAI API key to it:
    ```
    OPENAI_API_KEY="your_openai_api_key_here"
    ```
    Make sure `.env` is listed in your `.gitignore` file (which it should be).

## Usage

1.  **Place PDF files:**
    Copy the PDF files you want to transcribe into the `data/input` directory.

2.  **Run the transcription script:**
    Execute the script using the alias defined in `pyproject.toml`:
    ```bash
    uv run transcribe
    ```

3.  **Find the output:**
    The transcribed text files (with a `.txt` extension) will be saved in the `data/output` directory. Each input PDF will have a corresponding text file.

## Key Dependencies

*   `openai`: For interacting with the OpenAI API.
*   `python-dotenv`: For managing environment variables (like the API key).
*   `PyMuPDF` (fitz): For reading PDF files and converting pages to images.

## Current AI Model

This tool currently uses the `gpt-4.1` model for transcription tasks.
