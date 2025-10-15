# Repository Guidelines
Este repositorio implementa un clasificador por lotes de PDFs respaldado por la API de DeepSeek. Usa scripts de línea de comandos y un menú interactivo para organizar resultados y registrar métricas de ejecución.

## Project Structure & Module Organization
- `pdf_classifier.py` concentra la lógica principal: extracción con PyMuPDF, llamadas a DeepSeek y organización de carpetas usando `Path`.
- `main.py` y `menu_interactivo.py` exponen la interfaz interactiva; los scripts `ejemplo_uso.py`, `ejemplo_organizacion.py` y `ejemplo_consolidacion.py` demuestran flujos específicos.
- `results/`, `pdf_clasificado/` y `pdf/` guardan datos de entrada y salidas clasificadas; `pdf_classifier.log` registra trazas de ejecución.
- `test_optimizacion.py` valida la reutilización de carpetas y sirve de referencia para crear pruebas adicionales.

## Build, Test, and Development Commands
```bash
pip install -r requirements.txt              # dependencias completas, incluye interfaz rica
python main.py                               # lanza el menú interactivo
python pdf_classifier.py pdf/ --output results  # clasifica una carpeta de PDFs concreta
python -m pytest test_optimizacion.py        # ejecuta pruebas automatizadas
python verificar_dependencias.py             # comprueba versiones y prerequisitos locales
```

## Coding Style & Naming Conventions
- Seguir PEP 8 con indentación de 4 espacios y docstrings descriptivos en español.
- Preferir `Path` para rutas, `typing` para anotaciones y `logging` en lugar de `print`.
- Las funciones y métodos usan snake_case; clases como `PDFClassifier` emplean CamelCase. Reutilizar helpers privados existentes antes de añadir nuevos.

## Testing Guidelines
- Las pruebas viven en archivos `test_*.py` y se ejecutan con `pytest`; replicar el patrón de fixtures temporales de `test_optimizacion.py`.
- Incluir datasets simulados mínimos y verificar que no se crean carpetas duplicadas ni se pierden estadísticas de procesamiento.
- Ejecutar `python -m pytest` antes de abrir un PR y adjuntar la salida relevante.

## Commit & Pull Request Guidelines
- Los commits existentes usan mensajes cortos en español con contexto claro (p. ej. “Clasificacion por lotes y menu atractivo”). Mantener esta convención, capitalizando la primera palabra y describiendo la acción.
- Para PRs, describir propósito, impacto en la API pública y pasos de prueba; enlazar issues y añadir capturas de consola si afectan a la experiencia interactiva.

## Security & Configuration Tips
- Mantener el archivo `.env` fuera del control de versiones y definir `DEEPSEEK_API_KEY` antes de ejecutar ejemplos.
- Evitar volcar PDFs sensibles en el repositorio; usar carpetas temporales al escribir nuevas pruebas o ejemplos.
