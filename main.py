#!/usr/bin/env python3
"""
CLASIFICADOR DE PDFs - PUNTO DE ENTRADA PRINCIPAL
================================================
Ejecuta el menú interactivo o comandos directos del clasificador.
"""

import sys
from rich.console import Console

def main():
    """Función principal que determina qué interfaz usar."""

    # Si hay argumentos de línea de comandos, usar interfaz CLI
    if len(sys.argv) > 1:
        # Importar y ejecutar el clasificador original
        from pdf_classifier import main as classifier_main
        return classifier_main()

    console = Console()

    try:
        from menu_interactivo import main as menu_main
    except ImportError as exc:
        console.print("[red]❌ No se pudo importar la interfaz Rich.[/red]")
        console.print("Instala dependencias con `pip install -r requirements.txt` y vuelve a intentarlo.")
        return 1

    try:
        return menu_main()
    except Exception as e:
        console.print(f"[red]❌ Error al iniciar el menú interactivo: {e}[/red]")
        console.print("Como alternativa puedes ejecutar `python pdf_classifier.py /ruta/a/carpeta/pdfs`.")
        return 1

if __name__ == "__main__":
    console = Console()
    try:
        exit_code = main()
        sys.exit(exit_code or 0)
    except KeyboardInterrupt:
        console.print("\n\n[bold blue]👋 Proceso interrumpido por el usuario[/bold blue]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]❌ Error crítico: {e}[/red]")
        sys.exit(1)
