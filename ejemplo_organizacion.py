#!/usr/bin/env python3
"""
Ejemplo de organización automática de PDFs
==========================================
Este script muestra cómo usar el clasificador para organizar
automáticamente los PDFs en carpetas por tema.
"""

from pdf_classifier import PDFClassifier
from pathlib import Path

def ejemplo_organizacion_automatica():
    """Ejemplo de clasificación y organización automática."""
    print("🗂️  EJEMPLO: CLASIFICACIÓN Y ORGANIZACIÓN AUTOMÁTICA")
    print("=" * 60)

    # Configurar rutas
    carpeta_pdfs = "/home/federico/prg/duply_v6_clipy/pdf"  # Ajusta esta ruta
    carpeta_organizada = "/home/federico/prg/duply_v6_clipy/pdf_organizados"

    if not Path(carpeta_pdfs).exists():
        print(f"❌ La carpeta {carpeta_pdfs} no existe.")
        print("   Ajusta la variable 'carpeta_pdfs' con la ruta correcta.")
        return

    try:
        # Crear clasificador
        classifier = PDFClassifier(batch_size=3)

        print(f"📁 Procesando PDFs de: {carpeta_pdfs}")
        print(f"🎯 Organizando en: {carpeta_organizada}")
        print()

        # Clasificar y organizar automáticamente
        stats = classifier.classify_and_organize(
            folder_path=carpeta_pdfs,
            output_dir="resultados_organizacion",
            organize_files=True,
            organized_folder=carpeta_organizada
        )

        # Mostrar resultados
        print("\n✅ PROCESO COMPLETADO!")
        print("-" * 40)
        print(f"📊 Archivos procesados: {stats['processed']}/{stats['total_files']}")

        if 'organization' in stats:
            org = stats['organization']
            print(f"🗂️  Organizados por tema: {org['successfully_organized']}")
            print(f"❓ Movidos a 'no_clasificados': {org['moved_to_unclassified']}")
            print(f"📁 Carpetas creadas: {org['folders_created']}")

        print(f"\n📂 Revisa la carpeta: {carpeta_organizada}")

        # Mostrar estructura creada
        mostrar_estructura_creada(Path(carpeta_organizada))

    except Exception as e:
        print(f"❌ Error: {e}")

def mostrar_estructura_creada(carpeta_organizada: Path):
    """Muestra la estructura de carpetas creada."""
    if not carpeta_organizada.exists():
        return

    print(f"\n🌳 ESTRUCTURA CREADA EN {carpeta_organizada.name}:")
    print("-" * 40)

    def mostrar_carpeta(carpeta, nivel=0):
        indent = "  " * nivel
        items = sorted(carpeta.iterdir())

        for item in items:
            if item.is_dir():
                print(f"{indent}📁 {item.name}/")
                # Mostrar archivos en la carpeta
                archivos = list(item.glob("*.pdf"))
                if archivos:
                    for archivo in sorted(archivos):
                        print(f"{indent}  📄 {archivo.name}")
                # Mostrar subcarpetas
                subcarpetas = [x for x in item.iterdir() if x.is_dir()]
                if subcarpetas:
                    mostrar_carpeta(item, nivel + 1)

    mostrar_carpeta(carpeta_organizada)

def ejemplo_solo_organizacion():
    """Ejemplo de organización usando resultados existentes."""
    print("\n🔄 EJEMPLO: ORGANIZAR ARCHIVOS YA CLASIFICADOS")
    print("=" * 60)

    carpeta_pdfs = "/home/federico/prg/duply_v6_clipy/pdf"
    resultados_json = "results/clasificacion_20250918_141611.json"  # Usar tu archivo de resultados

    if not Path(carpeta_pdfs).exists():
        print(f"❌ La carpeta {carpeta_pdfs} no existe.")
        return

    if not Path(resultados_json).exists():
        print(f"❌ Archivo de resultados no encontrado: {resultados_json}")
        print("   Ejecuta primero una clasificación.")
        return

    try:
        import json

        # Cargar resultados existentes
        with open(resultados_json, 'r', encoding='utf-8') as f:
            resultados = json.load(f)

        # Crear clasificador y organizar
        classifier = PDFClassifier()

        stats = classifier.organize_files_by_classification(
            results=resultados,
            source_folder=Path(carpeta_pdfs),
            organized_folder=Path("pdf_organizados_manual")
        )

        print("✅ Organización completada!")
        print(f"🗂️  Archivos organizados: {stats['successfully_organized']}")
        print(f"❓ Movidos a no_clasificados: {stats['moved_to_unclassified']}")

    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Función principal."""
    print("🚀 EJEMPLOS DE ORGANIZACIÓN DE PDFs")
    print("=" * 50)

    # Verificar API key
    import os
    if not os.getenv('DEEPSEEK_API_KEY'):
        print("❌ API key de DeepSeek no encontrada en .env")
        return

    print("✅ API key de DeepSeek configurada")
    print()

    # Ejecutar ejemplos
    ejemplo_organizacion_automatica()
    #ejemplo_solo_organizacion()  # Descomenta para probar

    print("\n" + "=" * 50)
    print("📋 COMANDOS ÚTILES:")
    print("=" * 50)
    print("# Clasificar y organizar automáticamente:")
    print("python pdf_classifier.py /ruta/pdfs --organize")
    print()
    print("# Solo clasificar (sin organizar):")
    print("python pdf_classifier.py /ruta/pdfs --no-organize")
    print()
    print("# Organizar en carpeta personalizada:")
    print("python pdf_classifier.py /ruta/pdfs --organize --organized-folder /ruta/destino")

if __name__ == "__main__":
    main()
