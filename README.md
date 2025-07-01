# PDF Downloader

A PyQt-based desktop application for managing and downloading categorized files from websites. It scans user-specified sites for downloadable files, compares them to a local directory structure, and downloads missing files into mirrored category subdirectories.

## Features

- **Site Management**: Add, edit, and remove sites with their scraping configurations
- **Local Directory Scanning**: Scan local directories for existing files and metadata
- **Remote Site Scanning**: Scrape websites for available files and categories
- **File Comparison**: Compare local and remote files to identify missing content
- **Download Management**: Queue, download, and validate files with progress tracking
- **Categorization**: Organize files into categories matching the remote structure
- **Search & Filter**: Search and filter both local and remote file libraries
- **File Validation**: Validate downloaded files (PDF, EPUB, TXT) for integrity
- **Modular Design**: Extensible architecture for adding new scrapers and file types

## Requirements

- Python 3.8+
- PyQt5 for the GUI
- SQLite for the database
- Various libraries for HTTP, parsing, and file handling (see requirements.txt)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/JoshRDFI/pdf-downloader.git
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

## Usage

### Quick Start

The easiest way to run the application is to use the provided launcher script:

```bash
# On Windows
PDF-Downloader.py

# On macOS/Linux
./PDF-Downloader.py
```

This script will:
1. Create a virtual environment if it doesn't exist
2. Install or update all required dependencies
3. Launch the PDF Downloader application

### Manual Launch

If you prefer to manually manage the environment, you can run:

```bash
python src/main.py
```

### Basic Workflow

1. Add sites to monitor in the Site Management tab
2. Configure your local library directory
3. Scan your local directory to catalog existing files
4. Scan remote sites to discover available files
5. Use the Comparison tab to see what files are missing
6. Queue files for download and monitor progress
7. View your download history and manage your library

## Project Structure

- `src/` — All source code
  - `gui/` — PyQt UI components
  - `core/` — Scraping, comparison, download, and file operations
  - `db/` — Database models and helpers
  - `utils/` — Utility functions
  - `scrapers/` — Modular site scrapers
  - `plugins/` — Extension points for new file types and scrapers
- `tests/` — Unit and integration tests
- `database/` — Database schema and migrations
- `_docs/` — Documentation
- `log/` — Application logs
- `resources/` — Application resources (icons, images, etc.)

For more details about the project structure, see [project-layout.md](project-layout.md).

## Testing

The project includes a comprehensive test suite. To run all tests:

```bash
./run_tests.py
```

To run specific test categories:

```bash
./run_tests.py --category=utils    # Run only utility tests
./run_tests.py --category=db       # Run only database model tests
./run_tests.py --category=core     # Run only core functionality tests
./run_tests.py --category=scrapers # Run only scraper tests
./run_tests.py --category=gui      # Run only GUI tests
```

For more information about testing, see [tests/README.md](tests/README.md).

## Development

### Adding New Scrapers

To add support for a new website, create a new scraper module in `src/scrapers/` that extends the `BaseScraper` class. See the documentation in `_docs/plugins/developing_scrapers.md` for details.

### Adding New File Types

To add support for a new file type, create a new file type handler in `src/plugins/file_types/` that implements the required validation methods. See the documentation in `_docs/plugins/developing_file_types.md` for details.

### Application Icon

The application uses an icon file located in the `resources/` directory:
- Windows: `resources/icon.ico`
- macOS/Linux: `resources/icon.png`

Replace the placeholder files with your own icons to customize the application's appearance.

## License

This project is in the public domain within the United States, and copyright and related rights in the work worldwide are waived as far as they can be. See <https://unlicense.org/> or the included LICENSE file for more information.