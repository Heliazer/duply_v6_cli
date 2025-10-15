# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`duply_v6_clipy` is a Python-based PDF classification and organization tool that uses the DeepSeek API to automatically categorize PDF documents into hierarchical topics. The system processes PDFs in batches, extracts text content, classifies them using AI, and organizes them into folder structures.

## Development Commands

### Setup & Dependencies
```bash
# Install all dependencies (includes rich UI)
pip install -r requirements.txt

# Install minimal dependencies (basic CLI only)
pip install -r requirements-minimal.txt

# Verify dependencies and configuration
python verificar_dependencias.py
```

### Running the Application
```bash
# Interactive menu (recommended)
python main.py

# Direct CLI classification
python pdf_classifier.py /path/to/pdfs --batch-size 5 --output results

# Classify and organize automatically
python pdf_classifier.py /path/to/pdfs --organize

# Run examples
python ejemplo_uso.py
python ejemplo_consolidacion.py
```

### Testing
```bash
# Run optimization tests
python -m pytest test_optimizacion.py

# Run all tests
python -m pytest
```

## Architecture Overview

### Core Components

**`pdf_classifier.py`** - Main classification engine
- `PDFClassifier` class handles all core operations
- Text extraction via PyMuPDF (fitz)
- Batch processing to optimize API calls
- Three-level hierarchical classification: General → Subtema → Específico
- Folder organization with caching to avoid duplicate folder creation
- Consolidation/restoration workflow for managing complex PDF structures

**`main.py`** - Application entry point
- Routes between CLI (`pdf_classifier.py`) and interactive menu (`menu_interactivo.py`)
- Handles argument parsing and delegates execution

**`menu_interactivo.py`** - Rich terminal UI
- `MenuColorido` class provides interactive menu system
- Uses `rich` library for colored tables, progress bars, panels
- Workflow options: select folder → consolidate → classify → organize → restore

### Key Workflows

1. **Simple Classification**: Extract text → Classify with DeepSeek → Save JSON/CSV results
2. **Classification + Organization**: Classify → Create folder hierarchy → Copy files to topic folders
3. **Consolidation Workflow**:
   - Recursively find PDFs in nested folders
   - MOVE (not copy) to single consolidated folder
   - Maintain `registry_origenes.json` for restoration
   - Optional: Classify consolidated PDFs → Organize by topic
   - Optional: Restore files to original locations

### Data Flow

```
PDFs → Text Extraction (PyMuPDF) → Batch Prompt (n PDFs) → DeepSeek API →
JSON Response → Results Storage (JSON/CSV) → Optional Organization (folder structure)
```

### File Organization

- **Input**: PDFs from specified folder or recursive search
- **Output**:
  - `results/clasificacion_TIMESTAMP.json` - Full classification results
  - `results/clasificacion_TIMESTAMP.csv` - Tabular export
  - `pdf_classifier.log` - Detailed execution logs
  - `{folder}_clasificado/` - Organized folder structure by topic
  - `{folder}_consolidado/` - Consolidated PDFs with registry

### Important Implementation Details

**Folder Caching**: `PDFClassifier` maintains `existing_folders_cache` to avoid redundant filesystem checks when organizing large batches. Always use `_create_folder_if_needed()` instead of direct `mkdir()`.

**Batch Processing**: Default batch size is 5 PDFs per API call. Larger batches reduce API calls but may hit token limits. Adjust via `--batch-size` parameter.

**Name Sanitization**: `_sanitize_folder_name()` ensures folder names are filesystem-safe by removing special characters, limiting length, and handling edge cases like "N/A".

**Duplicate Handling**: `_get_unique_filename()` prevents overwrites during consolidation by appending folder names or counters to duplicate filenames.

**Error Recovery**: Processing continues even if individual PDFs fail. Unprocessed files go to `no_clasificados/` folder.

## Configuration

### Environment Variables (.env)
```bash
DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

### Tunable Parameters

- `batch_size`: PDFs per API call (default: 5, recommended: 3-7)
- `num_pages`: Pages to analyze per PDF (default: 20)
- `max_chars`: Character limit per PDF (default: 15000)

## API Integration

**DeepSeek API**
- Model configurable via `DEEPSEEK_MODEL` (default `deepseek-chat`)
- Configurado en `_configure_deepseek()`
- Returns JSON array with classification for each document
- Includes retry logic and error handling for API failures

## Logging

All operations log to `pdf_classifier.log` with timestamps. Log levels:
- INFO: Normal operations (files processed, stats)
- WARNING: Non-critical issues (short text, missing files)
- ERROR: Processing failures (API errors, file errors)

## Code Style Conventions

- Follow PEP 8 with 4-space indentation
- Spanish docstrings and comments (project convention)
- Use `Path` from `pathlib` for all file operations
- Type hints via `typing` module
- Private methods prefixed with `_`
- Use `logging` instead of `print()` in core logic
- Rich library for user-facing output in interactive menu

## Testing Guidelines

See `test_optimizacion.py` for patterns:
- Use `pytest` with temporary directories
- Create minimal test PDFs with `fitz.open(..., filetype="pdf")`
- Verify folder caching and organization statistics
- Mock API calls when testing classification logic

## Common Development Tasks

### Adding a New Classification Level
1. Modify prompt in `classify_batch_with_ai()` to request additional field
2. Update JSON parsing to extract new field
3. Adjust `_save_results()` fieldnames for CSV export
4. Update folder organization logic in `organize_files_by_classification()`

### Changing Folder Structure
1. Modify `organize_files_by_classification()` path construction
2. Update `_sanitize_folder_name()` if new naming rules needed
3. Initialize folder cache with `_initialize_folders_cache()`

### Adding New Menu Options
1. Add option to `mostrar_menu_principal()` in `menu_interactivo.py`
2. Create handler method (e.g., `def ejecutar_nueva_opcion(self)`)
3. Add choice to prompt validation
4. Wire up in `ejecutar()` main loop

## Important Notes

- PDFs must contain extractable text (scanned images without OCR will fail)
- API rate limits: 2-second pause between batches is built in
- File operations use `shutil.copy2()` to preserve metadata
- Consolidation uses `shutil.move()` to save disk space
- The `pdf/` directory contains sample/test PDFs (not in repo)
- Git ignores results, logs, and virtual environments per `.gitignore`
