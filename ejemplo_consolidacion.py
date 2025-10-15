#!/usr/bin/env python3
"""
EJEMPLO DE CONSOLIDACIÓN RECURSIVA DE PDFs
==========================================
Este script demuestra cómo consolidar PDFs de múltiples carpetas
en una sola ubicación para procesamiento eficiente.
"""

from pdf_classifier import PDFClassifier
from pathlib import Path
import tempfile
import json

def crear_estructura_test():
    """Crea una estructura de carpetas de prueba con PDFs."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Crear estructura de carpetas con PDFs
        estructura = {
            "Documentos": ["doc1.pdf", "doc2.pdf"],
            "Documentos/Científicos": ["ciencia1.pdf", "ciencia2.pdf"],
            "Documentos/Científicos/Física": ["fisica1.pdf"],
            "Libros": ["libro1.pdf", "libro2.pdf"],
            "Libros/Historia": ["historia1.pdf"],
            "Libros/Técnicos": ["tecnico1.pdf", "tecnico2.pdf"],
            "Descargadas": ["descarga1.pdf", "descarga2.pdf"]
        }

        # Crear carpetas y archivos
        for carpeta, archivos in estructura.items():
            carpeta_path = temp_path / carpeta
            carpeta_path.mkdir(parents=True, exist_ok=True)

            for archivo in archivos:
                archivo_path = carpeta_path / archivo
                archivo_path.write_text(f"Contenido de {archivo}")

        return temp_path, estructura

def ejemplo_consolidacion_basica():
    """Ejemplo básico de consolidación."""
    print("📦 EJEMPLO: CONSOLIDACIÓN BÁSICA")
    print("=" * 50)

    # Nota: Para usar este ejemplo, necesitas una carpeta real con PDFs
    print("⚠️  Este ejemplo requiere una carpeta real con PDFs.")
    print("   Modifica la variable 'carpeta_origen' para probar.")
    print()

    # Ejemplo con carpeta real (modifica esta ruta)
    carpeta_origen = "/ruta/a/tu/carpeta/con/subcarpetas/y/pdfs"

    if not Path(carpeta_origen).exists():
        print(f"❌ Carpeta no encontrada: {carpeta_origen}")
        print("   Modifica la ruta en el script para probar.")
        return

    try:
        classifier = PDFClassifier()

        print(f"🔍 Buscando PDFs en: {carpeta_origen}")

        # Consolidar PDFs
        stats = classifier.consolidate_pdfs_recursively(
            source_folder=carpeta_origen,
            consolidated_folder=None  # Usar nombre automático
        )

        # Mostrar resultados
        print("\n✅ CONSOLIDACIÓN COMPLETADA!")
        print("-" * 40)
        print(f"📁 Archivos encontrados: {stats['total_found']}")
        print(f"✅ Archivos movidos: {stats['successfully_moved']}")
        print(f"🔄 Duplicados manejados: {stats['duplicates_handled']}")
        print(f"📂 Carpetas procesadas: {stats['folders_processed']}")
        print(f"🗑️ Carpetas vacías eliminadas: {stats.get('empty_folders_removed', 0)}")
        print(f"❌ Errores: {stats['errors']}")
        print(f"\n📂 Consolidado en: {stats['consolidated_folder']}")

        # Mostrar registro
        registry_file = Path(stats['consolidated_folder']) / "registry_origenes.json"
        if registry_file.exists():
            print(f"\n📋 Registro de orígenes guardado en: {registry_file}")

            with open(registry_file, 'r', encoding='utf-8') as f:
                registry_data = json.load(f)

            print(f"📄 Total archivos registrados: {len(registry_data['file_origins'])}")

    except Exception as e:
        print(f"❌ Error: {e}")

def ejemplo_workflow_completo():
    """Ejemplo de workflow completo: consolidar -> clasificar -> organizar."""
    print("\n🔄 EJEMPLO: WORKFLOW COMPLETO")
    print("=" * 50)
    print("Este ejemplo muestra el workflow completo:")
    print("1. Consolidar PDFs de múltiples carpetas")
    print("2. Clasificar PDFs consolidados")
    print("3. Organizar en estructura final")
    print()

    # Este es un ejemplo teórico - necesitarías una API key y carpeta real
    carpeta_origen = "/ruta/a/carpeta/con/subcarpetas"

    if not Path(carpeta_origen).exists():
        print(f"❌ Para probar este ejemplo, modifica 'carpeta_origen' con una ruta real.")
        print("   Workflow teórico:")
        print("   1. 📦 Consolidar: /mi/carpeta/compleja -> /mi/carpeta/compleja_consolidado")
        print("   2. 🔍 Clasificar: /mi/carpeta/compleja_consolidado -> results/")
        print("   3. 🗂️  Organizar: archivos copiados a carpetas por tema")
        print("   4. 🔄 Restaurar: opcional, devolver archivos a ubicaciones originales")
        return

    try:
        classifier = PDFClassifier()

        # Paso 1: Consolidar
        print("📦 PASO 1: Consolidando PDFs...")
        consolidation_stats = classifier.consolidate_pdfs_recursively(
            source_folder=carpeta_origen
        )
        consolidated_folder = consolidation_stats['consolidated_folder']
        print(f"✅ Consolidados {consolidation_stats['successfully_moved']} archivos")

        # Paso 2 y 3: Clasificar y organizar
        print("\n🔍 PASO 2-3: Clasificando y organizando...")
        classification_stats = classifier.classify_and_organize(
            folder_path=consolidated_folder,
            organize_files=True
        )

        print(f"✅ Clasificados {classification_stats['processed']} archivos")
        if 'organization' in classification_stats:
            org_stats = classification_stats['organization']
            print(f"🗂️  Organizados {org_stats['successfully_organized']} archivos")

        # Paso 4: Opcional - Restaurar
        print("\n🔄 PASO 4: Para restaurar archivos originales, usar:")
        print(f"   classifier.restore_from_consolidation('{consolidated_folder}')")

        print(f"\n📂 Resultado final en: {classification_stats.get('organized_folder', 'N/A')}")

    except Exception as e:
        print(f"❌ Error: {e}")

def mostrar_comandos_utiles():
    """Muestra comandos útiles para consolidación."""
    print("\n💻 COMANDOS ÚTILES")
    print("=" * 50)
    print("# Consolidar usando línea de comandos:")
    print("python -c \"")
    print("from pdf_classifier import PDFClassifier")
    print("c = PDFClassifier()")
    print("stats = c.consolidate_pdfs_recursively('/ruta/origen', '/ruta/destino')")
    print("print(f'Movidos: {stats[\\\"successfully_moved\\\"]} archivos')")
    print("\"")
    print()
    print("# Restaurar consolidación:")
    print("python -c \"")
    print("from pdf_classifier import PDFClassifier")
    print("c = PDFClassifier()")
    print("stats = c.restore_from_consolidation('/ruta/consolidada')")
    print("print(f'Restaurados: {stats[\\\"successfully_restored\\\"]} archivos')")
    print("\"")
    print()
    print("# Workflow completo con menú interactivo:")
    print("python main.py")
    print("# Luego seleccionar opción 2: Consolidar PDFs recursivamente")

def main():
    """Función principal."""
    print("🚀 EJEMPLOS DE CONSOLIDACIÓN DE PDFs")
    print("=" * 60)
    print("La consolidación permite:")
    print("• 📦 Unificar PDFs de múltiples carpetas en una sola")
    print("• 🔄 Mover (no copiar) archivos para optimizar espacio")
    print("• 📋 Mantener registro detallado de orígenes")
    print("• 🔄 Restaurar a ubicaciones originales si es necesario")
    print("• ⚡ Procesar lotes más eficientemente")
    print()

    # Ejecutar ejemplos
    ejemplo_consolidacion_basica()
    ejemplo_workflow_completo()
    mostrar_comandos_utiles()

    print("\n" + "=" * 60)
    print("📋 PARA USAR:")
    print("1. Modifica las rutas en este script con carpetas reales")
    print("2. O usa el menú interactivo: python main.py")
    print("3. Selecciona opción 2: 'Consolidar PDFs recursivamente'")
    print("4. Luego opción 4: 'Clasificar y organizar automáticamente'")

if __name__ == "__main__":
    main()