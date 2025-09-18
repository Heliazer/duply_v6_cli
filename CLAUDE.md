# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a PDF classification tool that uses Google Gemini AI to automatically categorize PDF documents by their content. The tool provides both interactive and command-line interfaces for processing PDFs in batches.

## Development Commands

### Installation
```bash
# Full installation with rich UI
pip install -r requisitos.txt

# Minimal installation (CLI only)
pip install -r requirements-minimal.txt
```

### Running the Application
```bash
# Interactive menu (recommended)
python main.py

# Command line interface
python pdf_classifier.py /path/to/pdf/folder
python pdf_classifier.py /path/to/pdf/folder --batch-size 3
python pdf_classifier.py /path/to/pdf/folder --output results

# Main entry point with organization
python main.py /path/to/pdf/folder --organize
```

### Development Tools
```bash
# Check dependencies
python verificar_dependencias.py

# Run examples
python ejemplo_uso.py
python ejemplo_organizacion.py
```

## Architecture Overview

### Core Components

- **`pdf_classifier.py`**: Main classification engine containing the `PDFClassifier` class
  - Handles PDF text extraction using PyMuPDF
  - Manages batch processing with Google Gemini API
  - Exports results to JSON and CSV formats
  - Implements robust error handling and logging

- **`main.py`**: Entry point that routes between interactive and CLI modes
  - Detects command-line arguments to choose interface
  - Falls back gracefully when rich dependencies are missing

- **`menu_interactivo.py`**: Rich interactive interface (`MenuColorido` class)
  - Colorful terminal UI using rich library
  - Progress bars and visual feedback
  - Guided configuration and help system

### Key Features

- **Batch Processing**: Optimizes API calls by processing multiple PDFs together (default batch size: 5)
- **Hierarchical Classification**: 3-level topic classification (general → subtopic → specific)
- **Multiple Output Formats**: JSON and CSV export with timestamps and confidence levels
- **Robust Error Handling**: Continues processing even when individual files fail
- **Flexible Configuration**: Adjustable batch sizes, page limits, and character limits

### Configuration

The application uses environment variables via `.env` file:
- `GOOGLE_API_KEY`: Required Google Gemini API key
- See `.env.example` for configuration template

### Dependencies

**Core Dependencies** (requirements-minimal.txt):
- `google-generativeai>=0.3.0`: Google Gemini API client
- `PyMuPDF>=1.23.0`: PDF text extraction
- `python-dotenv>=1.0.0`: Environment variable management

**UI Dependencies** (requisitos.txt):
- `colorama>=0.4.6`: Cross-platform terminal colors
- `rich>=13.0.0`: Advanced terminal UI components

### File Organization

- **Entry Points**: `main.py` (dual interface), `pdf_classifier.py` (CLI only)
- **Examples**: `ejemplo_uso.py`, `ejemplo_organizacion.py`
- **Utilities**: `verificar_dependencias.py`
- **Documentation**: `README.md`, `codigo_ejemplo.txt`
- **Configuration**: `.env.example`, `requisitos.txt`, `requirements-minimal.txt`

### Output Structure

Results are saved in two formats:
- **JSON**: Structured data with metadata, confidence scores, and timestamps
- **CSV**: Tabular format for spreadsheet analysis
- **Logging**: Detailed processing logs in `pdf_classifier.log`

### Development Notes

- The codebase supports graceful degradation (rich UI → basic CLI)
- API rate limiting is handled with automatic delays between batches
- Text extraction is limited to first 5 pages and 10,000 characters per PDF for efficiency
- All user-facing text is in Spanish