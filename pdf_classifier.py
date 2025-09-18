#!/usr/bin/env python3
"""
CLASIFICADOR TEMÁTICO DE LIBROS PDF POR LOTES CON GOOGLE GEMINI
================================================================
Este script analiza una carpeta de PDFs en lotes, extrae el texto inicial
de cada uno y utiliza la API de Google Gemini para clasificarlos eficientemente.

Características:
- Procesamiento en lotes para optimizar llamadas a la API
- Extracción inteligente de texto de PDFs
- Clasificación jerárquica de 3 niveles
- Manejo de errores robusto
- Exportación de resultados a JSON y CSV
- Configuración flexible via variables de entorno
"""

import os
import json
import time
import csv
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import fitz  # PyMuPDF
import google.generativeai as genai
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class PDFClassifier:
    def __init__(self, api_key: str = None, batch_size: int = 5):
        """
        Inicializa el clasificador de PDFs.

        Args:
            api_key: Clave de API de Google Gemini
            batch_size: Tamaño del lote para procesamiento
        """
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        self.batch_size = batch_size
        self.model = None
        self.results = []

        # Configurar logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('pdf_classifier.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

        self._configure_gemini()

    def _configure_gemini(self):
        """Configura la API de Google Gemini."""
        if not self.api_key:
            raise ValueError("API key de Google Gemini no encontrada. Verificar .env")

        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.logger.info("API de Gemini configurada correctamente")
        except Exception as e:
            self.logger.error(f"Error al configurar la API de Gemini: {e}")
            raise

    def extract_text_from_pdf(self, pdf_path: Path, num_pages: int = 20, max_chars: int = 15000) -> Optional[str]:
        """
        Extrae texto de las primeras páginas de un PDF.

        Args:
            pdf_path: Ruta al archivo PDF
            num_pages: Número de páginas a procesar
            max_chars: Máximo número de caracteres a extraer

        Returns:
            Texto extraído o None si hay error
        """
        try:
            with fitz.open(pdf_path) as documento:
                texto_completo = ""
                for i in range(min(num_pages, documento.page_count)):
                    page_text = documento.load_page(i).get_text()
                    texto_completo += page_text

                # Limitar caracteres para optimizar API calls
                texto_final = texto_completo[:max_chars]

                if len(texto_final.strip()) < 100:
                    self.logger.warning(f"Texto muy corto extraído de {pdf_path.name}")

                return texto_final

        except Exception as e:
            self.logger.error(f"Error al leer PDF '{pdf_path.name}': {e}")
            return None

    def classify_batch_with_ai(self, texts_and_files: List[Tuple[str, str]]) -> Optional[List[Dict]]:
        """
        Clasifica un lote de textos usando la API de Gemini.

        Args:
            texts_and_files: Lista de tuplas (texto, nombre_archivo)

        Returns:
            Lista de clasificaciones o None si hay error
        """
        if not texts_and_files:
            return []

        # Construir prompt para el lote
        prompt_documents = ""
        for i, (texto, filename) in enumerate(texts_and_files):
            prompt_documents += f"--- DOCUMENTO {i+1} (Archivo: {filename}) ---\n{texto}\n\n"

        prompt = f"""
        Analiza los {len(texts_and_files)} textos de documentos PDF que te proporciono a continuación.
        Para cada uno, clasifícalo en una jerarquía temática de 3 niveles, considerando que son libros o documentos académicos/técnicos.

        {prompt_documents}

        Responde ÚNICAMENTE con un array JSON válido, uno por cada documento en el mismo orden.
        La estructura debe ser exactamente esta:
        [
            {{
                "documento": 1,
                "archivo": "nombre_del_archivo.pdf",
                "tema_general": "Categoría principal (ej: Ciencias, Tecnología, Historia, etc.)",
                "subtema": "Subcategoría específica",
                "tema_especifico": "Tema muy específico del contenido",
                "confianza": "alta|media|baja",
                "palabras_clave": ["palabra1", "palabra2", "palabra3"]
            }}
        ]

        Asegúrate de que el JSON sea válido y sin texto adicional.
        """

        try:
            response = self.model.generate_content(prompt)

            # Limpiar respuesta
            json_text = response.text.strip()
            if json_text.startswith("```json"):
                json_text = json_text[7:]
            if json_text.endswith("```"):
                json_text = json_text[:-3]
            json_text = json_text.strip()

            # Parsear JSON
            classifications = json.loads(json_text)

            # Validar estructura
            if not isinstance(classifications, list):
                raise ValueError("La respuesta no es una lista válida")

            return classifications

        except json.JSONDecodeError as e:
            self.logger.error(f"Error al parsear JSON de la API: {e}")
            self.logger.debug(f"Respuesta recibida: {response.text}")
            return None
        except Exception as e:
            self.logger.error(f"Error en llamada a la API: {e}")
            return None

    def process_batch(self, pdf_files: List[Path], folder_path: Path) -> List[Dict]:
        """
        Procesa un lote de archivos PDF.

        Args:
            pdf_files: Lista de archivos PDF a procesar
            folder_path: Ruta base de la carpeta

        Returns:
            Lista de resultados de clasificación
        """
        self.logger.info(f"Procesando lote de {len(pdf_files)} archivos")

        texts_and_files = []

        # Extraer texto de cada PDF
        for pdf_file in pdf_files:
            full_path = folder_path / pdf_file
            texto = self.extract_text_from_pdf(full_path)

            if texto and len(texto.strip()) > 50:
                texts_and_files.append((texto, pdf_file.name))
            else:
                self.logger.warning(f"Saltando archivo '{pdf_file.name}' (texto insuficiente)")

        if not texts_and_files:
            self.logger.warning("Lote vacío, no hay texto válido para clasificar")
            return []

        # Clasificar con IA
        classifications = self.classify_batch_with_ai(texts_and_files)

        if not classifications:
            self.logger.error("No se recibieron clasificaciones válidas")
            return []

        # Procesar resultados
        batch_results = []
        for i, (_, filename) in enumerate(texts_and_files):
            if i < len(classifications):
                result = classifications[i].copy()
                result['archivo'] = filename
                result['timestamp'] = datetime.now().isoformat()
                batch_results.append(result)

                # Log resultado
                self.logger.info(f"Clasificado: {filename}")
                self.logger.info(f"  General: {result.get('tema_general', 'N/A')}")
                self.logger.info(f"  Subtema: {result.get('subtema', 'N/A')}")
                self.logger.info(f"  Específico: {result.get('tema_especifico', 'N/A')}")
            else:
                self.logger.warning(f"Sin clasificación para {filename}")

        return batch_results

    def classify_pdfs_in_folder(self, folder_path: str, output_dir: str = "results") -> Dict:
        """
        Clasifica todos los PDFs en una carpeta.

        Args:
            folder_path: Ruta a la carpeta con PDFs
            output_dir: Directorio para guardar resultados

        Returns:
            Diccionario con estadísticas del procesamiento
        """
        folder_path = Path(folder_path)
        output_dir = Path(output_dir)

        if not folder_path.is_dir():
            raise ValueError(f"La carpeta no existe: {folder_path}")

        # Crear directorio de salida
        output_dir.mkdir(exist_ok=True)

        # Encontrar archivos PDF
        pdf_files = [f for f in folder_path.iterdir()
                    if f.suffix.lower() == '.pdf' and f.is_file()]

        if not pdf_files:
            self.logger.warning("No se encontraron archivos PDF en la carpeta")
            return {"total_files": 0, "processed": 0, "errors": 0}

        self.logger.info(f"Encontrados {len(pdf_files)} archivos PDF")
        self.logger.info(f"Procesando en lotes de {self.batch_size}")

        # Procesar en lotes
        all_results = []
        processed_count = 0
        error_count = 0

        for i in range(0, len(pdf_files), self.batch_size):
            batch = pdf_files[i:i + self.batch_size]

            try:
                batch_results = self.process_batch(batch, folder_path)
                all_results.extend(batch_results)
                processed_count += len(batch_results)

                # Pausa entre lotes para respetar rate limits
                if i + self.batch_size < len(pdf_files):
                    self.logger.info("Pausa de 2 segundos antes del siguiente lote...")
                    time.sleep(2)

            except Exception as e:
                self.logger.error(f"Error procesando lote {i//self.batch_size + 1}: {e}")
                error_count += len(batch)

        # Guardar resultados
        self._save_results(all_results, output_dir)

        stats = {
            "total_files": len(pdf_files),
            "processed": processed_count,
            "errors": error_count,
            "success_rate": processed_count / len(pdf_files) * 100 if pdf_files else 0
        }

        self.logger.info(f"Procesamiento completado: {processed_count}/{len(pdf_files)} archivos")
        self.logger.info(f"Tasa de éxito: {stats['success_rate']:.1f}%")

        return stats

    def _save_results(self, results: List[Dict], output_dir: Path):
        """Guarda los resultados en archivos JSON y CSV."""
        if not results:
            self.logger.warning("No hay resultados para guardar")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Guardar JSON
        json_file = output_dir / f"clasificacion_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        self.logger.info(f"Resultados guardados en JSON: {json_file}")

        # Guardar CSV
        csv_file = output_dir / f"clasificacion_{timestamp}.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            if results:
                fieldnames = ['documento', 'archivo', 'tema_general', 'subtema', 'tema_especifico',
                             'confianza', 'palabras_clave', 'timestamp']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

                for result in results:
                    # Convertir lista de palabras clave a string
                    result_copy = result.copy()
                    if 'palabras_clave' in result_copy and isinstance(result_copy['palabras_clave'], list):
                        result_copy['palabras_clave'] = ', '.join(result_copy['palabras_clave'])
                    # Filtrar solo los campos que están en fieldnames
                    filtered_result = {k: v for k, v in result_copy.items() if k in fieldnames}
                    writer.writerow(filtered_result)

        self.logger.info(f"Resultados guardados en CSV: {csv_file}")


def main():
    """Función principal del script."""
    import argparse

    parser = argparse.ArgumentParser(description="Clasificador temático de PDFs con Google Gemini")
    parser.add_argument("folder", help="Carpeta con archivos PDF a clasificar")
    parser.add_argument("--batch-size", type=int, default=5, help="Tamaño del lote (default: 5)")
    parser.add_argument("--output", default="results", help="Directorio de salida (default: results)")

    args = parser.parse_args()

    try:
        classifier = PDFClassifier(batch_size=args.batch_size)
        stats = classifier.classify_pdfs_in_folder(args.folder, args.output)

        print("\n" + "="*50)
        print("RESUMEN DE PROCESAMIENTO")
        print("="*50)
        print(f"Archivos totales: {stats['total_files']}")
        print(f"Procesados exitosamente: {stats['processed']}")
        print(f"Errores: {stats['errors']}")
        print(f"Tasa de éxito: {stats['success_rate']:.1f}%")
        print("="*50)

    except Exception as e:
        print(f"Error crítico: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())