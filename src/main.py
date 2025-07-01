import os
import logging
from urllib.parse import urlparse
import requests

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
OUTPUT_DIR = "downloaded_pdfs/"

def validate_url(url):
    """Validate that the URL appears to be valid."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def download_pdf(url, save_path):
    """Downloads a PDF from a URL and saves it to the specified path."""
    logging.info(f"Preparing to download PDF from {url}")

    if not os.path.exists(save_path):
        os.makedirs(save_path)
        logging.info(f"Created output directory: {save_path}")

    try:
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()

        # Extract file name from URL
        filename = os.path.basename(urlparse(url).path)
        if not filename:
            logging.warning("Could not extract filename from URL, using 'downloaded.pdf'")
            filename = "downloaded.pdf"

        full_path = os.path.join(save_path, filename)

        with open(full_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:  # filter out keep-alive new chunks
                    file.write(chunk)
                    logging.debug(f"Wrote {len(chunk)} bytes to {full_path}")

        logging.info(f"Downloaded PDF to {full_path}")
        print(f"Successfully downloaded PDF to '{full_path}'")
    except requests.exceptions.RequestException as e:
        logging.error(f"Network-related error: {e}")
        print(f"Error downloading PDF due to network issues: {e.split(':')[0]}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        print(f"An unexpected error occurred: {str(e)}")

def main():
    # Get URL from user input
    pdf_url = input("Enter the PDF URL (or 'exit' to quit): ")

    if pdf_url.lower() == 'exit':
        logging.info("User chose to exit")
        print("Exiting PDF Downloader. Goodbye!")
        return

    # Validate URL before trying to download
    if not validate_url(pdf_url):
        logging.warning(f"Invalid URL provided: {pdf_url}")
        print("The URL you entered is invalid. Please make sure it's a complete, properly formatted URL.")
        return

    try:
        download_pdf(pdf_url, OUTPUT_DIR)
    except Exception as e:
        logging.error(f"Critical error in download process: {e}")

if __name__ == "__main__":
    print("Welcome to the PDF Downloader!")
    print("This tool will help you download PDF files from any URL.\n")
    main()
