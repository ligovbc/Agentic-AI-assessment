"""
PDF text extraction utility for the Agentic AI API
"""
import pdfplumber
import tempfile
import os


def extract_text_from_pdf(pdf_file) -> str:
    """
    Extract text content from a PDF file

    Args:
        pdf_file: File object or file-like object containing PDF data

    Returns:
        Extracted text as a string

    Raises:
        ValueError: If PDF extraction fails
    """
    tmp_path = None
    try:
        # Create a temporary file to store the uploaded PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            pdf_file.save(tmp_file.name)
            tmp_path = tmp_file.name

        # Extract text from the PDF
        text_content = []

        with pdfplumber.open(tmp_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text_content.append(f"--- Page {page_num} ---\n{page_text}")

        if not text_content:
            raise ValueError("No text could be extracted from the PDF")

        return "\n\n".join(text_content)

    except Exception as e:
        raise ValueError(f"Failed to extract text from PDF: {str(e)}")

    finally:
        # Clean up the temporary file
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except OSError:
                pass  # Ignore errors when cleaning up temporary file


def get_pdf_info(pdf_file) -> dict:
    """
    Get metadata about the PDF file

    Args:
        pdf_file: File object or file-like object containing PDF data

    Returns:
        Dictionary with PDF metadata (num_pages, metadata)
    """
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            pdf_file.save(tmp_file.name)
            tmp_path = tmp_file.name

        with pdfplumber.open(tmp_path) as pdf:
            info = {
                "num_pages": len(pdf.pages),
                "metadata": pdf.metadata or {}
            }

        return info

    except Exception as e:
        return {
            "num_pages": 0,
            "metadata": {},
            "error": str(e)
        }

    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except OSError:
                pass  # Ignore errors when cleaning up temporary file
