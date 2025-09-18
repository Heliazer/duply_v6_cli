#!/usr/bin/env python3
"""
CLASIFICADOR DE PDFs - PUNTO DE ENTRADA PRINCIPAL
================================================
Ejecuta el menú interactivo o comandos directos del clasificador.
"""

import sys
import os
from pathlib import Path

def main():
    """Función principal que determina qué interfaz usar."""

    # Si hay argumentos de línea de comandos, usar interfaz CLI
    if len(sys.argv) > 1:
        # Importar y ejecutar el clasificador original
        from pdf_classifier import main as classifier_main
        return classifier_main()

    # Si no hay argumentos, mostrar menú interactivo
    else:
        try:
            # Verificar si las dependencias están instaladas
            try:
                import rich
                import colorama
            except ImportError:
                print("⚠️  Las dependencias para el menú colorido no están instaladas.")
                print("Ejecuta: pip install -r requirements.txt")
                print("\nUsando interfaz básica...")

                # Fallback a interfaz CLI básica
                print("\n🔍 USO BÁSICO:")
                print("python main.py /ruta/a/carpeta/pdfs")
                print("python main.py /ruta/a/carpeta/pdfs --organize")
                return 1

            # Ejecutar menú interactivo
            from menu_interactivo import main as menu_main
            return menu_main()

        except Exception as e:
            print(f"❌ Error al iniciar el menú: {e}")
            print("\n🔍 USO ALTERNATIVO:")
            print("python pdf_classifier.py /ruta/a/carpeta/pdfs")
            return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code or 0)
    except KeyboardInterrupt:
        print("\n\n👋 ¡Proceso interrumpido por el usuario!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error crítico: {e}")
        sys.exit(1)