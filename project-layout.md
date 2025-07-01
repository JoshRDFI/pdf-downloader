
# project-layout.md

## project-overview

This project is a PyQt-based desktop application for managing and downloading categorized PDF (and optionally EPUB, TXT, etc.) files from public library/archive websites. It scans user-specified sites for downloadable files, compares them to a local directory structure, and downloads missing files into mirrored category subdirectories. The program uses a modular scraper system for supporting multiple sites, stores metadata and progress in an SQLite database, and provides a user-friendly, searchable interface with notifications and network configuration options.

## user-flow

1. **Startup:**  
   User launches the application and is greeted with a landing screen to add/select library sites and set the local root directory.

2. **Site Management:**  
   User can add, edit, or remove sites. The app stores site info and scraping modules in a database for future use.

3. **Directory Scan:**  
   The app scans the local root directory (and subdirectories) for existing files and updates the database with their metadata.

4. **Site Scan:**  
   The app scrapes the selected site(s) for available files and categories, updating the database with remote file info.

5. **Comparison:**  
   The app compares local and remote files by category/folder and filename (and file size if available) to identify missing files.

6. **Download:**  
   User initiates download of missing files. The app downloads one file at a time, validates each file, and places it in the correct local subdirectory. Rate limiting and proxy/network settings are respected.

7. **Review & Search:**  
   User can search/filter both local and remote files, view download status, and receive notifications for completion/errors.

8. **Completion:**  
   User can view a summary of actions, errors, and download history.

## tech-stack

- **Python 3.12:** Core language for all logic and scripting.
- **PyQt:** GUI framework for a cross-platform, windowed desktop interface.
- **SQLite:** Local database for storing site info, file metadata, and download history.
- **requests:** HTTP library for downloading files and fetching web pages.
- **BeautifulSoup:** HTML parsing and scraping.
- **(Optional) lxml:** Faster HTML parsing if needed.
- **PyPDF2 or pdfminer:** For PDF validation and metadata extraction.
- **ebooklib, chardet:** For EPUB/TXT support and encoding detection.

## ui-rules

- Use PyQt’s Model/View architecture for scalable, responsive lists and tables.
- Tabs or sidebar for: Site Management, Local Library, Remote Library, Download Queue, Settings, and Logs.
- All long-running operations (scanning, downloading) must be threaded or run in background processes to keep the UI responsive.
- Search/filter bar for both local and remote file lists.
- Download status and notifications must be clearly visible (e.g., status bar, notification area).
- All destructive actions (deletion, overwrite) require confirmation.
- Progress and status indicators must be visible at all times.
- Save/resume progress is always available from the main menu.

## theme-rules

- **Colors:**  
  - Primary: #2D2D2D (dark gray), #4A90E2 (blue accent)  
  - Secondary: #F5F5F5 (light background), #E94E77 (error/red accent)
- **Typography:**  
  - Use a clean, sans-serif font (e.g., Segoe UI, Roboto, or system default).
  - Headings: Bold, 1.2x size of body text.
  - Body: Regular, 12-14pt.
- **Spacing:**  
  - Minimum 8px padding between elements.
  - Consistent margins for all containers.
- **Component Style:**  
  - Buttons: Rounded corners, clear hover/focus states.
  - Lists/Tables: Alternating row colors for readability.
  - Dialogs: Modal, with clear action buttons.

## project-rules

- **Folder Structure:**  
  - `src/` — All source code  
    - `gui/` — PyQt UI components  
    - `core/` — Scraping, comparison, download, and file operations  
    - `db/` — Database models and helpers  
    - `utils/` — Utility functions (file validation, threading, etc.)  
    - `scrapers/` — Modular site scrapers (one per supported site)
  - `tests/` — Unit and integration tests
  - `_docs/` — Documentation  
    - `phases/` — Project phases and feature/task breakdowns
  - `requirements.txt` — Python dependencies
  - `README.md` — Project introduction and quickstart
  - `project-layout.md` — This document

- **File Naming:**  
  - Use `snake_case` for Python files and folders.
  - Use `CamelCase` for class names, `snake_case` for functions and variables.
  - All modules must have a docstring at the top describing their purpose.

- **Code Style:**  
  - Follow PEP8 for Python code.
  - All public functions and classes must have type hints and docstrings.
  - Use logging for all non-UI errors and warnings.

## _docs/phases/

Each phase document should include:  
- **Phase Overview:** What this phase accomplishes  
- **Tasks:** List of tasks and features  
- **Dependencies:** What must be completed first  
- **Acceptance Criteria:** What defines “done” for this phase

**Example phase documents:**

- `phase_01_site_management.md`  
  - Adding/editing/removing sites, storing in SQLite, modular scraper loading

- `phase_02_local_scan.md`  
  - Scanning local directories, extracting file metadata, updating database

- `phase_03_remote_scan.md`  
  - Scraping remote site(s), extracting file/category info, updating database

- `phase_04_comparison_and_queue.md`  
  - Comparing local/remote, building download queue, rate limiting

- `phase_05_download_and_validation.md`  
  - Downloading files, validating PDFs, error handling, updating status

- `phase_06_ui_and_search.md`  
  - Building UI, search/filter, notifications, progress

- `phase_07_network_and_settings.md`  
  - Proxy/user-agent settings, saving/loading preferences

- `phase_08_modular_extensions.md`  
  - Adding new scrapers, supporting new file types
