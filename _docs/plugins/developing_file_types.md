# Developing File Type Plugins

This document explains how to develop new file type plugins for the PDF Downloader application.

## Overview

The PDF Downloader application supports different file types through a modular plugin system. Each file type plugin is responsible for validating and extracting metadata from a specific type of file. The application provides a base validator class that all file type plugins must inherit from, and a plugin system for loading and managing file type plugins.

## Creating a New File Type Plugin

To create a new file type plugin, you need to create a Python module that defines a class inheriting from `FileTypeValidator`. The module should be placed in the `src/plugins/file_types` directory.

### Basic Structure

```python
from src.plugins.file_types import FileTypeValidator

class MyFileTypeValidator(FileTypeValidator):
    # File type identifier
    FILE_TYPE = "my_file_type"
    
    # File extensions supported by this validator
    EXTENSIONS = [".myext", ".myotherext"]
    
    def validate(self, file_path):
        # Implementation...
```

### Required Attributes and Methods

All file type plugins must define the following attributes and methods:

#### `FILE_TYPE`

A string identifier for the file type (e.g., "pdf", "epub", "txt").

#### `EXTENSIONS`

A list of file extensions supported by this validator (e.g., [".pdf"], [".epub"], [".txt", ".text"]).

#### `validate(file_path)`

This method should validate the given file and return a dictionary containing validation results. The dictionary should have the following keys:

- `valid`: Boolean indicating whether the file is valid
- `file_path`: Path to the file
- `file_type`: Type of the file
- `error`: Error message if the file is invalid, or `None` if the file is valid
- `metadata`: Dictionary containing metadata extracted from the file

### Example

Here's a simple example of a file type plugin that validates Markdown files:

```python
import os
from src.plugins.file_types import FileTypeValidator

class MarkdownValidator(FileTypeValidator):
    FILE_TYPE = "markdown"
    EXTENSIONS = [".md", ".markdown"]
    
    def validate(self, file_path):
        result = {
            "valid": False,
            "file_path": file_path,
            "file_type": self.FILE_TYPE,
            "error": None,
            "metadata": {}
        }
        
        try:
            # Try to open the file to check if it's readable
            with open(file_path, "r", encoding="utf-8") as f:
                # Read the first few lines to extract metadata
                lines = [f.readline().strip() for _ in range(10) if f.readline()]
                
                # Look for a title (# Title)
                title = None
                for line in lines:
                    if line.startswith("# "):
                        title = line[2:].strip()
                        break
                
                # Count the number of headers
                header_count = 0
                with open(file_path, "r", encoding="utf-8") as f2:
                    for line in f2:
                        if line.strip().startswith("#"):
                            header_count += 1
                
                # Add metadata to the result
                result["metadata"] = {
                    "title": title,
                    "header_count": header_count,
                    "size": os.path.getsize(file_path)
                }
                
                # Mark the file as valid
                result["valid"] = True
        except Exception as e:
            result["error"] = str(e)
        
        return result
```

## Testing Your File Type Plugin

You should test your file type plugin to ensure it works correctly. You can create a test file and use your validator to validate it.

```python
import unittest
import os
from src.plugins.file_types.my_file_type_validator import MyFileTypeValidator

class TestMyFileTypeValidator(unittest.TestCase):
    def setUp(self):
        self.validator = MyFileTypeValidator()
        self.test_file = "test_file.myext"
        
        # Create a test file
        with open(self.test_file, "w", encoding="utf-8") as f:
            f.write("Test content")
    
    def tearDown(self):
        # Remove the test file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
    
    def test_validate(self):
        # Validate the test file
        result = self.validator.validate(self.test_file)
        
        # Check the results
        self.assertTrue(result["valid"])
        self.assertEqual(result["file_type"], "my_file_type")
        self.assertIsNone(result["error"])
        self.assertIn("size", result["metadata"])

if __name__ == "__main__":
    unittest.main()
```

## Registering Your File Type Plugin

The application will automatically discover and register your file type plugin when it's placed in the `src/plugins/file_types` directory. You don't need to do anything else to register it.

## Best Practices

- Handle errors gracefully and log them using the `logging` module.
- Use meaningful names for your validator class and methods.
- Document your validator with docstrings.
- Write tests for your validator to ensure it works correctly.
- Follow the PEP8 style guide for Python code.

## Troubleshooting

- If your file type plugin isn't being discovered, make sure it's in the correct directory and inherits from `FileTypeValidator`.
- If you're getting errors when validating files, check the file path and make sure it's accessible.
- If you're having trouble extracting metadata, try using different libraries or techniques.