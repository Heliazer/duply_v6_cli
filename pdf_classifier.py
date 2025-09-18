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
import shutil
import re
import tempfile
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
        self.temp_dir = None
        self.pdf_location_map = {}  # Mapeo de archivos temporales a ubicaciones originales

        # Generar timestamp para esta sesión
        self.session_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Crear carpeta para logs si no existe
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)

        self.general_log_file = f"logs/pdf_classifier_{self.session_timestamp}.log"
        self.api_log_file = f"logs/api_requests_{self.session_timestamp}.log"

        # Configurar logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.general_log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

        # Configurar logger específico para requests de API
        self.api_logger = logging.getLogger(f'api_requests_{self.session_timestamp}')
        self.api_logger.setLevel(logging.INFO)

        # Handler para el log de API (archivo separado)
        api_handler = logging.FileHandler(self.api_log_file, encoding='utf-8')
        api_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        api_handler.setFormatter(api_formatter)
        self.api_logger.addHandler(api_handler)
        self.api_logger.propagate = False  # Evitar duplicados en consola

        self._configure_gemini()

    def _sanitize_folder_name(self, name: str) -> str:
        """
        Limpia el nombre para crear carpetas válidas.

        Args:
            name: Nombre a limpiar

        Returns:
            Nombre válido para carpeta
        """
        if not name or name.lower() in ['n/a', 'na', 'none', 'null']:
            return "Sin_Clasificar"

        # Remover caracteres especiales y reemplazar espacios
        sanitized = re.sub(r'[<>:"/\\|?*]', '', name)
        sanitized = re.sub(r'\s+', '_', sanitized.strip())

        # Limitar longitud
        sanitized = sanitized[:50]

        # Capitalizar primera letra de cada palabra
        sanitized = '_'.join(word.capitalize() for word in sanitized.split('_') if word)

        return sanitized or "Sin_Clasificar"

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

    def collect_pdfs_recursively(self, root_folder: Path) -> Tuple[Path, Dict[str, str], int]:
        """
        Recolecta recursivamente todos los PDFs de una carpeta y subcarpetas,
        los copia a una carpeta temporal para análisis eficiente.

        Args:
            root_folder: Carpeta raíz donde buscar PDFs

        Returns:
            Tupla con (carpeta_temporal, mapeo_ubicaciones, total_archivos)
        """
        root_folder = Path(root_folder)
        if not root_folder.exists() or not root_folder.is_dir():
            raise ValueError(f"La carpeta no existe o no es válida: {root_folder}")

        # Crear carpeta temporal
        self.temp_dir = Path(tempfile.mkdtemp(prefix="pdf_classifier_"))
        self.pdf_location_map = {}

        total_files = 0
        copied_files = 0

        self.logger.info(f"🔍 Escaneando recursivamente la carpeta: {root_folder}")
        self.logger.info(f"📁 Carpeta temporal creada: {self.temp_dir}")

        # Buscar todos los PDFs recursivamente
        pdf_files = list(root_folder.rglob("*.pdf"))
        total_files = len(pdf_files)

        if total_files == 0:
            self.logger.warning(f"❌ No se encontraron archivos PDF en: {root_folder}")
            return self.temp_dir, self.pdf_location_map, 0

        self.logger.info(f"📊 Encontrados {total_files} archivos PDF")

        # Copiar cada PDF a la carpeta temporal
        for pdf_file in pdf_files:
            try:
                # Crear nombre único para evitar conflictos
                relative_path = pdf_file.relative_to(root_folder)
                safe_name = str(relative_path).replace(os.sep, "_")

                # Agregar timestamp si el nombre ya existe
                temp_pdf_name = f"{copied_files:04d}_{safe_name}"
                temp_pdf_path = self.temp_dir / temp_pdf_name

                # Copiar el archivo
                shutil.copy2(pdf_file, temp_pdf_path)

                # Guardar mapeo de ubicación original
                self.pdf_location_map[temp_pdf_name] = {
                    'original_path': str(pdf_file),
                    'relative_path': str(relative_path),
                    'parent_folder': str(pdf_file.parent),
                    'original_name': pdf_file.name
                }

                copied_files += 1

                if copied_files % 10 == 0:
                    self.logger.info(f"📋 Copiados {copied_files}/{total_files} archivos...")

            except Exception as e:
                self.logger.error(f"❌ Error copiando {pdf_file}: {e}")
                continue

        self.logger.info(f"✅ Proceso completado: {copied_files}/{total_files} archivos copiados")

        # Guardar mapeo en archivo JSON para referencia
        mapping_file = self.temp_dir / "ubicaciones_originales.json"
        with open(mapping_file, 'w', encoding='utf-8') as f:
            json.dump(self.pdf_location_map, f, indent=2, ensure_ascii=False)

        return self.temp_dir, self.pdf_location_map, copied_files

    def cleanup_temp_folder(self):
        """
        Limpia la carpeta temporal después del procesamiento.
        """
        if self.temp_dir and self.temp_dir.exists():
            try:
                shutil.rmtree(self.temp_dir)
                self.logger.info(f"🧹 Carpeta temporal eliminada: {self.temp_dir}")
                self.temp_dir = None
                self.pdf_location_map = {}
            except Exception as e:
                self.logger.error(f"❌ Error eliminando carpeta temporal: {e}")

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
            # Log del request
            filenames = [filename for _, filename in texts_and_files]
            self.api_logger.info(f"=== NUEVO REQUEST A LA API ===")
            self.api_logger.info(f"Archivos en el lote: {filenames}")
            self.api_logger.info(f"Cantidad de archivos: {len(texts_and_files)}")
            self.api_logger.info(f"Prompt enviado (primeros 500 chars): {prompt[:500]}...")

            # Hacer el request
            response = self.model.generate_content(prompt)

            # Log de la respuesta
            self.api_logger.info(f"✅ Respuesta recibida exitosamente")
            self.api_logger.info(f"Respuesta completa: {response.text}")

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

            # Log de éxito
            self.api_logger.info(f"✅ JSON parseado correctamente. {len(classifications)} clasificaciones obtenidas")

            # Log detallado de cada clasificación
            for i, classification in enumerate(classifications):
                filename = filenames[i] if i < len(filenames) else "archivo_desconocido"
                self.api_logger.info(f"  📁 {filename}: {classification.get('tema_general', 'N/A')} > {classification.get('subtema', 'N/A')} > {classification.get('tema_especifico', 'N/A')} (Confianza: {classification.get('confianza', 'N/A')})")

            self.api_logger.info(f"=== FIN REQUEST EXITOSO ===\n")

            return classifications

        except json.JSONDecodeError as e:
            # Log de error de JSON
            self.api_logger.error(f"❌ ERROR DE PARSEO JSON")
            self.api_logger.error(f"Error: {e}")
            self.api_logger.error(f"Respuesta que causó el error: {response.text}")
            self.api_logger.error(f"Archivos afectados: {filenames}")
            self.api_logger.error(f"=== FIN REQUEST CON ERROR JSON ===\n")

            self.logger.error(f"Error al parsear JSON de la API: {e}")
            self.logger.debug(f"Respuesta recibida: {response.text}")
            return None

        except Exception as e:
            # Log de error general
            self.api_logger.error(f"❌ ERROR EN LLAMADA A LA API")
            self.api_logger.error(f"Error: {str(e)}")
            self.api_logger.error(f"Tipo de error: {type(e).__name__}")
            self.api_logger.error(f"Archivos afectados: {filenames}")
            if 'response' in locals():
                self.api_logger.error(f"Respuesta (si existe): {getattr(response, 'text', 'Sin respuesta')}")
            self.api_logger.error(f"=== FIN REQUEST CON ERROR GENERAL ===\n")

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
                self.api_logger.info(f"📄 Texto extraído exitosamente de: {pdf_file.name} ({len(texto)} chars)")
            else:
                self.logger.warning(f"Saltando archivo '{pdf_file.name}' (texto insuficiente)")
                self.api_logger.warning(f"⚠️  Archivo saltado por texto insuficiente: {pdf_file.name} (chars: {len(texto) if texto else 0})")

        if not texts_and_files:
            self.logger.warning("Lote vacío, no hay texto válido para clasificar")
            self.api_logger.warning(f"⚠️  LOTE VACÍO: Ningún archivo del lote tuvo texto válido para clasificar")
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

        # Log de inicio de sesión en el archivo de API
        self.api_logger.info(f"🚀 NUEVA SESIÓN DE CLASIFICACIÓN INICIADA")
        self.api_logger.info(f"Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.api_logger.info(f"Carpeta de origen: {folder_path}")
        self.api_logger.info(f"Carpeta de salida: {output_dir}")
        self.api_logger.info(f"Total de archivos PDF encontrados: {len(pdf_files)}")
        self.api_logger.info(f"Tamaño de lote configurado: {self.batch_size}")
        self.api_logger.info(f"Archivos a procesar: {[f.name for f in pdf_files]}")
        self.api_logger.info(f"=" * 80)

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

        # Log de fin de sesión en el archivo de API
        self.api_logger.info(f"=" * 80)
        self.api_logger.info(f"🏁 SESIÓN DE CLASIFICACIÓN COMPLETADA")
        self.api_logger.info(f"Fecha y hora de finalización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.api_logger.info(f"📊 ESTADÍSTICAS FINALES:")
        self.api_logger.info(f"  Total de archivos: {len(pdf_files)}")
        self.api_logger.info(f"  Archivos procesados exitosamente: {processed_count}")
        self.api_logger.info(f"  Archivos con errores: {error_count}")
        self.api_logger.info(f"  Tasa de éxito: {stats['success_rate']:.1f}%")
        self.api_logger.info(f"  Resultados guardados en: {output_dir}")
        self.api_logger.info(f"  Log general: {self.general_log_file}")
        self.api_logger.info(f"  Log de API: {self.api_log_file}")
        self.api_logger.info(f"🎯 FIN DE SESIÓN")
        self.api_logger.info(f"=" * 100 + "\n")

        # Agregar información de logs a las estadísticas
        stats['log_files'] = {
            'general_log': self.general_log_file,
            'api_log': self.api_log_file,
            'session_timestamp': self.session_timestamp
        }

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

    def organize_files_by_classification(self, results: List[Dict], source_folder: Path,
                                       organized_folder: Path = None) -> Dict[str, int]:
        """
        Organiza los archivos PDF en carpetas basadas en su clasificación.

        Args:
            results: Lista de resultados de clasificación
            source_folder: Carpeta origen con los PDFs
            organized_folder: Carpeta destino para la organización

        Returns:
            Diccionario con estadísticas de organización
        """
        if organized_folder is None:
            organized_folder = source_folder.parent / f"{source_folder.name}_clasificado"

        organized_folder.mkdir(exist_ok=True)
        no_clasificados_folder = organized_folder / "no_clasificados"
        no_clasificados_folder.mkdir(exist_ok=True)

        stats = {
            "total_processed": 0,
            "successfully_organized": 0,
            "moved_to_unclassified": 0,
            "errors": 0,
            "folders_created": set()
        }

        self.logger.info(f"Organizando archivos en: {organized_folder}")

        # Organizar archivos clasificados
        for result in results:
            stats["total_processed"] += 1
            archivo = result.get('archivo', '')

            if not archivo:
                stats["errors"] += 1
                continue

            source_file = source_folder / archivo

            if not source_file.exists():
                self.logger.warning(f"Archivo no encontrado: {archivo}")
                stats["errors"] += 1
                continue

            try:
                # Determinar carpeta destino
                tema_general = result.get('tema_general', '')
                subtema = result.get('subtema', '')

                if not tema_general or tema_general.lower() in ['n/a', 'na', 'none']:
                    # Mover a no_clasificados
                    dest_file = no_clasificados_folder / archivo
                    shutil.copy2(source_file, dest_file)
                    stats["moved_to_unclassified"] += 1
                    self.logger.info(f"Movido a no_clasificados: {archivo}")
                else:
                    # Crear estructura de carpetas
                    tema_folder = self._sanitize_folder_name(tema_general)
                    subtema_folder = self._sanitize_folder_name(subtema) if subtema else None

                    if subtema_folder and subtema_folder != "Sin_Clasificar":
                        dest_folder = organized_folder / tema_folder / subtema_folder
                    else:
                        dest_folder = organized_folder / tema_folder

                    dest_folder.mkdir(parents=True, exist_ok=True)
                    stats["folders_created"].add(str(dest_folder))

                    dest_file = dest_folder / archivo
                    shutil.copy2(source_file, dest_file)
                    stats["successfully_organized"] += 1

                    self.logger.info(f"Organizado: {archivo} → {dest_folder.name}")

            except Exception as e:
                self.logger.error(f"Error organizando {archivo}: {e}")
                stats["errors"] += 1

        # Buscar archivos no clasificados (que no aparecen en results)
        classified_files = {result.get('archivo', '') for result in results}
        all_pdfs = list(source_folder.glob("*.pdf"))

        for pdf_file in all_pdfs:
            if pdf_file.name not in classified_files:
                try:
                    dest_file = no_clasificados_folder / pdf_file.name
                    shutil.copy2(pdf_file, dest_file)
                    stats["moved_to_unclassified"] += 1
                    self.logger.info(f"Archivo no clasificado movido: {pdf_file.name}")
                except Exception as e:
                    self.logger.error(f"Error moviendo archivo no clasificado {pdf_file.name}: {e}")
                    stats["errors"] += 1

        # Convertir set a count para el reporte
        stats["folders_created"] = len(stats["folders_created"])

        self.logger.info(f"Organización completada:")
        self.logger.info(f"  - Archivos organizados: {stats['successfully_organized']}")
        self.logger.info(f"  - Movidos a no_clasificados: {stats['moved_to_unclassified']}")
        self.logger.info(f"  - Carpetas creadas: {stats['folders_created']}")
        self.logger.info(f"  - Errores: {stats['errors']}")

        return stats

    def classify_and_organize(self, folder_path: str, output_dir: str = "results",
                            organize_files: bool = True, organized_folder: str = None) -> Dict:
        """
        Clasifica PDFs y opcionalmente los organiza en carpetas.

        Args:
            folder_path: Ruta a la carpeta con PDFs
            output_dir: Directorio para guardar resultados
            organize_files: Si True, organiza los archivos en carpetas
            organized_folder: Carpeta personalizada para organización

        Returns:
            Diccionario con estadísticas completas
        """
        # Primero clasificar
        classification_stats = self.classify_pdfs_in_folder(folder_path, output_dir)

        if not organize_files or classification_stats["processed"] == 0:
            return classification_stats

        # Cargar resultados de la clasificación más reciente
        output_dir_path = Path(output_dir)
        json_files = list(output_dir_path.glob("clasificacion_*.json"))

        if not json_files:
            self.logger.warning("No se encontraron archivos de clasificación para organizar")
            return classification_stats

        # Usar el archivo más reciente
        latest_json = max(json_files, key=lambda x: x.stat().st_mtime)

        with open(latest_json, 'r', encoding='utf-8') as f:
            results = json.load(f)

        # Organizar archivos
        folder_path = Path(folder_path)
        if organized_folder:
            organized_folder_path = Path(organized_folder)
        else:
            organized_folder_path = folder_path.parent / f"{folder_path.name}_clasificado"

        organization_stats = self.organize_files_by_classification(
            results, folder_path, organized_folder_path
        )

        # Combinar estadísticas
        combined_stats = {
            **classification_stats,
            "organization": organization_stats,
            "organized_folder": str(organized_folder_path)
        }

        return combined_stats


def main():
    """Función principal del script."""
    import argparse

    parser = argparse.ArgumentParser(description="Clasificador temático de PDFs con Google Gemini")
    parser.add_argument("folder", help="Carpeta con archivos PDF a clasificar")
    parser.add_argument("--batch-size", type=int, default=5, help="Tamaño del lote (default: 5)")
    parser.add_argument("--output", default="results", help="Directorio de salida (default: results)")
    parser.add_argument("--organize", action="store_true", help="Organizar archivos en carpetas por tema")
    parser.add_argument("--organized-folder", help="Carpeta personalizada para organización")
    parser.add_argument("--no-organize", action="store_true", help="Solo clasificar, no organizar archivos")

    args = parser.parse_args()

    try:
        classifier = PDFClassifier(batch_size=args.batch_size)

        # Determinar si organizar archivos
        organize_files = args.organize or (not args.no_organize)

        if organize_files:
            stats = classifier.classify_and_organize(
                folder_path=args.folder,
                output_dir=args.output,
                organize_files=True,
                organized_folder=args.organized_folder
            )
        else:
            stats = classifier.classify_pdfs_in_folder(args.folder, args.output)

        print("\n" + "="*50)
        print("RESUMEN DE PROCESAMIENTO")
        print("="*50)
        print(f"Archivos totales: {stats['total_files']}")
        print(f"Procesados exitosamente: {stats['processed']}")
        print(f"Errores: {stats['errors']}")
        print(f"Tasa de éxito: {stats['success_rate']:.1f}%")

        # Mostrar estadísticas de organización si están disponibles
        if 'organization' in stats:
            org_stats = stats['organization']
            print("\n--- ORGANIZACIÓN DE ARCHIVOS ---")
            print(f"Archivos organizados por tema: {org_stats['successfully_organized']}")
            print(f"Movidos a 'no_clasificados': {org_stats['moved_to_unclassified']}")
            print(f"Carpetas creadas: {org_stats['folders_created']}")
            print(f"Carpeta de organización: {stats.get('organized_folder', 'N/A')}")

        print("="*50)

    except Exception as e:
        print(f"Error crítico: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())