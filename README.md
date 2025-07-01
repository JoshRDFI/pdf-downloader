# PDF Downloader

A simple command-line tool to download PDF files from specified URLs.

## Features
- Downloads PDF files and saves them in a dedicated folder
- Supports error handling for invalid URLs
- Uses the `requests` library for HTTP operations

## Requirements
- Python 3.8+
- `requests` library (install via requirements.txt)

## Setup and Usage
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/pdf-downloader.git
   cd pdf-downloader
   ```

2. Set up a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the PDF downloader:
   ```bash
   python src/main.py
   ```

5. Enter a URL when prompted.

## Project Layout
Refer to [project-layout.md](project-layout.md) for details about folder structure and organization.

## License
This project is in the public domain within the United States, and copyright and related rights in the work worldwide are waived as far as they can be. See <https://unlicense.org/> or the included LICENSE file for more information.