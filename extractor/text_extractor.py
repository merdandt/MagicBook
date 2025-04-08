import PyPDF2
from flask import logging


def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file with no length constraints."""
    logging.debug("Starting PDF text extraction from file: %s", pdf_path)
    text = ""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_path)
        logging.debug("Opened PDF file successfully. Total pages: %d", len(pdf_reader.pages))
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            page_text = page.extract_text()
            # Log the first 100 characters from the page's text for debugging
            logging.debug("Page %d extracted text (first 100 chars): %s", page_num + 1, (page_text or "")[:100])
            if page_text:
                text += page_text + "\n"
            else:
                logging.debug("No text found on page %d", page_num + 1)
    except Exception as e:
        error_msg = f"Error extracting text from PDF: {str(e)}"
        logging.error(error_msg)
        return error_msg

    logging.debug("Completed PDF text extraction. Total extracted text length: %d characters", len(text))
    # write text to txtfile
    with open("potter7book.txt", "w") as f:
        f.write(text)

    return text