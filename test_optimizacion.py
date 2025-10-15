#!/usr/bin/env python3
"""
TEST DE OPTIMIZACIÓN DE CARPETAS
================================
Script para demostrar que no se duplican carpetas en procesamiento por lotes.
"""

from pdf_classifier import PDFClassifier
from pathlib import Path
import tempfile
import shutil
import json

def crear_datos_test():
    """Crea datos de prueba simulando clasificaciones repetitivas."""
    return [
        # Lote 1 - Crear carpetas iniciales
        {
            "archivo": "libro1.pdf",
            "tema_general": "Ciencias",
            "subtema": "Física",
            "tema_especifico": "Mecánica Cuántica"
        },
        {
            "archivo": "libro2.pdf",
            "tema_general": "Tecnología",
            "subtema": "Programación",
            "tema_especifico": "Python"
        },
        # Lote 2 - Reutilizar carpetas del Lote 1
        {
            "archivo": "libro3.pdf",
            "tema_general": "Ciencias",  # Carpeta ya existe
            "subtema": "Física",         # Subcarpeta ya existe
            "tema_especifico": "Física Nuclear"
        },
        {
            "archivo": "libro4.pdf",
            "tema_general": "Tecnología", # Carpeta ya existe
            "subtema": "Programación",    # Subcarpeta ya existe
            "tema_especifico": "JavaScript"
        },
        # Lote 3 - Mix de nuevas y existentes
        {
            "archivo": "libro5.pdf",
            "tema_general": "Ciencias",   # Carpeta ya existe
            "subtema": "Química",         # Nueva subcarpeta
            "tema_especifico": "Química Orgánica"
        },
        {
            "archivo": "libro6.pdf",
            "tema_general": "Historia",   # Nueva carpeta
            "subtema": "Historia Antigua",
            "tema_especifico": "Roma"
        }
    ]

def test_optimizacion_carpetas():
    """Prueba la optimización de creación de carpetas."""
    print("🧪 TESTING: Optimización de carpetas")
    print("=" * 50)

    # Crear directorio temporal para la prueba
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Crear archivos PDF falsos para el test
        pdf_folder = temp_path / "pdfs_test"
        pdf_folder.mkdir()

        datos_test = crear_datos_test()

        # Crear archivos PDF vacíos para la prueba
        for dato in datos_test:
            archivo_pdf = pdf_folder / dato["archivo"]
            archivo_pdf.write_text("PDF de prueba")

        # Crear carpeta de organización
        organized_folder = temp_path / "pdfs_organizados"

        print(f"📁 Carpeta de prueba: {pdf_folder}")
        print(f"🎯 Carpeta organizada: {organized_folder}")
        print()

        # Crear clasificador
        classifier = PDFClassifier()

        # Simular procesamiento por lotes
        print("🔄 SIMULANDO PROCESAMIENTO POR LOTES:")
        print()

        lotes = [
            datos_test[0:2],  # Lote 1: Crear carpetas iniciales
            datos_test[2:4],  # Lote 2: Reutilizar carpetas
            datos_test[4:6]   # Lote 3: Mix de nuevas y existentes
        ]

        total_stats = {
            "folders_created": 0,
            "folders_reused": 0,
            "files_organized": 0
        }

        for i, lote in enumerate(lotes, 1):
            print(f"📦 LOTE {i}: Procesando {len(lote)} archivos")

            # Procesar lote
            stats = classifier.organize_files_by_classification(
                results=lote,
                source_folder=pdf_folder,
                organized_folder=organized_folder
            )

            # Acumular estadísticas
            total_stats["folders_created"] += stats["folders_created"]
            total_stats["folders_reused"] += stats.get("folders_reused", 0)
            total_stats["files_organized"] += stats["successfully_organized"]

            print(f"  ✅ Archivos organizados: {stats['successfully_organized']}")
            print(f"  📁 Carpetas nuevas: {stats['folders_created']}")
            print(f"  ♻️  Carpetas reutilizadas: {stats.get('folders_reused', 0)}")
            print(f"  💾 Cache size: {len(classifier.existing_folders_cache)}")
            print()

        # Mostrar estructura final
        print("🌳 ESTRUCTURA FINAL CREADA:")
        mostrar_estructura(organized_folder)

        # Resumen final
        print("\n📊 RESUMEN DE OPTIMIZACIÓN:")
        print("=" * 40)
        print(f"📁 Total carpetas creadas: {total_stats['folders_created']}")
        print(f"♻️  Total carpetas reutilizadas: {total_stats['folders_reused']}")
        print(f"🗂️  Total archivos organizados: {total_stats['files_organized']}")

        eficiencia = (total_stats['folders_reused'] /
                     (total_stats['folders_created'] + total_stats['folders_reused']) * 100
                     if (total_stats['folders_created'] + total_stats['folders_reused']) > 0 else 0)
        print(f"⚡ Eficiencia de reutilización: {eficiencia:.1f}%")

        # Verificar que no hay duplicaciones
        verificar_no_duplicacion(organized_folder)

def mostrar_estructura(carpeta, nivel=0):
    """Muestra la estructura de carpetas creada."""
    if not carpeta.exists():
        return

    indent = "  " * nivel

    for item in sorted(carpeta.iterdir()):
        if item.is_dir():
            print(f"{indent}📁 {item.name}/")
            # Mostrar archivos en la carpeta
            archivos = list(item.glob("*.pdf")) + list(item.glob("*.txt"))
            for archivo in sorted(archivos):
                print(f"{indent}  📄 {archivo.name}")
            # Mostrar subcarpetas
            mostrar_estructura(item, nivel + 1)

def verificar_no_duplicacion(organized_folder):
    """Verifica que no hay carpetas duplicadas."""
    print("\n🔍 VERIFICACIÓN DE NO DUPLICACIÓN:")

    todas_las_carpetas = []
    for root, dirs, files in organized_folder.rglob("*"):
        if Path(root).is_dir():
            todas_las_carpetas.append(str(Path(root).relative_to(organized_folder)))

    # Contar carpetas únicas
    carpetas_unicas = set(todas_las_carpetas)

    if len(todas_las_carpetas) == len(carpetas_unicas):
        print("✅ NO se encontraron carpetas duplicadas")
        print(f"📊 Total carpetas: {len(carpetas_unicas)}")
    else:
        print("❌ Se encontraron posibles duplicaciones:")
        duplicadas = set([x for x in todas_las_carpetas if todas_las_carpetas.count(x) > 1])
        for carpeta in duplicadas:
            print(f"  ⚠️  {carpeta}")

def main():
    """Función principal del test."""
    print("🚀 TEST DE OPTIMIZACIÓN DEL CLASIFICADOR DE PDFs")
    print("Este test verifica que no se crean carpetas duplicadas")
    print("durante el procesamiento por lotes.")
    print()

    try:
        test_optimizacion_carpetas()
        print("\n✅ Test completado exitosamente!")

    except Exception as e:
        print(f"\n❌ Error durante el test: {e}")
        return 1

    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())