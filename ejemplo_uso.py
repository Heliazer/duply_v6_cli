#!/usr/bin/env python3
"""
Ejemplo de uso del clasificador de PDFs
======================================
Este script muestra diferentes formas de usar el clasificador.
"""

from pdf_classifier import PDFClassifier
from pathlib import Path
import os

def ejemplo_basico():
    """Ejemplo básico de uso del clasificador."""
    print("=== EJEMPLO BÁSICO ===")

    # Crear instancia del clasificador
    classifier = PDFClassifier(batch_size=3)

    # Carpeta con PDFs (ajusta esta ruta)
    carpeta_pdfs = "/ruta/a/tu/carpeta/de/pdfs"

    # Verificar que la carpeta existe
    if not Path(carpeta_pdfs).exists():
        print(f"⚠️  La carpeta {carpeta_pdfs} no existe.")
        print("   Ajusta la variable 'carpeta_pdfs' con la ruta correcta.")
        return

    try:
        # Procesar PDFs
        stats = classifier.classify_pdfs_in_folder(
            folder_path=carpeta_pdfs,
            output_dir="resultados_ejemplo"
        )

        print(f"✅ Procesados: {stats['processed']}/{stats['total_files']} archivos")
        print(f"📊 Tasa de éxito: {stats['success_rate']:.1f}%")

    except Exception as e:
        print(f"❌ Error: {e}")

def ejemplo_configuracion_personalizada():
    """Ejemplo con configuración personalizada."""
    print("\n=== EJEMPLO CON CONFIGURACIÓN PERSONALIZADA ===")

    # Configuración personalizada
    classifier = PDFClassifier(
        api_key=os.getenv('GOOGLE_API_KEY'),  # API key específica
        batch_size=2  # Lotes más pequeños
    )

    carpeta_pdfs = "/ruta/a/tu/carpeta/de/pdfs"

    if not Path(carpeta_pdfs).exists():
        print(f"⚠️  La carpeta {carpeta_pdfs} no existe.")
        return

    try:
        # Procesar con configuración personalizada
        stats = classifier.classify_pdfs_in_folder(
            folder_path=carpeta_pdfs,
            output_dir="resultados_personalizados"
        )

        print(f"✅ Procesamiento completado")
        print(f"📁 Resultados guardados en: resultados_personalizados/")

    except Exception as e:
        print(f"❌ Error: {e}")

def ejemplo_procesamiento_individual():
    """Ejemplo de procesamiento de archivos individuales."""
    print("\n=== EJEMPLO DE PROCESAMIENTO INDIVIDUAL ===")

    classifier = PDFClassifier()

    # Archivo específico (ajusta esta ruta)
    archivo_pdf = "/ruta/a/un/archivo.pdf"

    if not Path(archivo_pdf).exists():
        print(f"⚠️  El archivo {archivo_pdf} no existe.")
        return

    try:
        # Extraer texto del PDF
        texto = classifier.extract_text_from_pdf(Path(archivo_pdf))

        if texto:
            print(f"📄 Texto extraído de {Path(archivo_pdf).name}:")
            print(f"   Primeros 200 caracteres: {texto[:200]}...")

            # Clasificar un solo documento
            resultado = classifier.classify_batch_with_ai([(texto, Path(archivo_pdf).name)])

            if resultado:
                print(f"🏷️  Clasificación:")
                print(f"   General: {resultado[0].get('tema_general')}")
                print(f"   Subtema: {resultado[0].get('subtema')}")
                print(f"   Específico: {resultado[0].get('tema_especifico')}")
        else:
            print("❌ No se pudo extraer texto del PDF")

    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Función principal que ejecuta todos los ejemplos."""
    print("🚀 EJEMPLOS DE USO DEL CLASIFICADOR DE PDFs")
    print("=" * 50)

    # Verificar que tenemos API key
    if not os.getenv('GOOGLE_API_KEY'):
        print("❌ API key de Google Gemini no encontrada.")
        print("   Asegúrate de tener un archivo .env con GOOGLE_API_KEY")
        return

    print("✅ API key encontrada")

    # Ejecutar ejemplos
    ejemplo_basico()
    ejemplo_configuracion_personalizada()
    ejemplo_procesamiento_individual()

    print("\n" + "=" * 50)
    print("📚 INSTRUCCIONES:")
    print("1. Ajusta las rutas de carpetas en los ejemplos")
    print("2. Asegúrate de tener PDFs en las carpetas especificadas")
    print("3. Los resultados se guardarán en formato JSON y CSV")
    print("4. Revisa los logs en pdf_classifier.log para más detalles")

if __name__ == "__main__":
    main()