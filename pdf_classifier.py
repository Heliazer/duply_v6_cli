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
        self.existing_folders_cache = set()  # Cache de carpetas ya creadas

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

    def _initialize_folders_cache(self, organized_folder: Path):
        """
        Inicializa el cache con carpetas existentes para evitar verificaciones repetitivas.

        Args:
            organized_folder: Carpeta base de organización
        """
        self.existing_folders_cache.clear()

        if organized_folder.exists():
            # Recorrer todas las carpetas existentes y agregarlas al cache
            for root, dirs, files in os.walk(organized_folder):
                root_path = Path(root)
                self.existing_folders_cache.add(str(root_path))

                # Agregar también las subcarpetas
                for dir_name in dirs:
                    subfolder_path = root_path / dir_name
                    self.existing_folders_cache.add(str(subfolder_path))

        self.logger.info(f"Cache inicializado con {len(self.existing_folders_cache)} carpetas existentes")

    def _create_folder_if_needed(self, folder_path: Path) -> bool:
        """
        Crea una carpeta solo si no existe, usando cache para optimizar.

        Args:
            folder_path: Ruta de la carpeta a crear

        Returns:
            bool: True si la carpeta se creó o ya existía, False si hubo error
        """
        folder_str = str(folder_path)

        # Verificar cache primero
        if folder_str in self.existing_folders_cache:
            return True

        # Si no está en cache, verificar si existe físicamente
        if folder_path.exists():
            # Agregar al cache para futuras verificaciones
            self.existing_folders_cache.add(folder_str)
            return True

        # Crear la carpeta y sus padres si es necesario
        try:
            folder_path.mkdir(parents=True, exist_ok=True)

            # Agregar al cache la carpeta y todas sus carpetas padre
            current_path = folder_path
            while current_path != current_path.parent:
                self.existing_folders_cache.add(str(current_path))
                current_path = current_path.parent

            self.logger.debug(f"Carpeta creada: {folder_path}")
            return True

        except Exception as e:
            self.logger.error(f"Error creando carpeta {folder_path}: {e}")
            return False

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

    def organize_files_by_classification(self, results: List[Dict], source_folder: Path,
                                       organized_folder: Path = None) -> Dict[str, int]:
        """
        Organiza los archivos PDF en carpetas basadas en su clasificación.
        Optimizado para evitar duplicación de carpetas y usar cache.

        Args:
            results: Lista de resultados de clasificación
            source_folder: Carpeta origen con los PDFs
            organized_folder: Carpeta destino para la organización

        Returns:
            Diccionario con estadísticas de organización
        """
        if organized_folder is None:
            organized_folder = source_folder.parent / f"{source_folder.name}_clasificado"

        # Crear carpeta principal usando método optimizado
        self._create_folder_if_needed(organized_folder)

        # Inicializar cache de carpetas existentes
        self._initialize_folders_cache(organized_folder)

        # Crear carpeta de no clasificados
        no_clasificados_folder = organized_folder / "no_clasificados"
        self._create_folder_if_needed(no_clasificados_folder)

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
                    # Crear estructura de carpetas usando método optimizado
                    tema_folder = self._sanitize_folder_name(tema_general)
                    subtema_folder = self._sanitize_folder_name(subtema) if subtema else None

                    if subtema_folder and subtema_folder != "Sin_Clasificar":
                        dest_folder = organized_folder / tema_folder / subtema_folder
                    else:
                        dest_folder = organized_folder / tema_folder

                    # Usar método optimizado para crear carpeta
                    if self._create_folder_if_needed(dest_folder):
                        stats["folders_created"].add(str(dest_folder))

                        dest_file = dest_folder / archivo
                        shutil.copy2(source_file, dest_file)
                        stats["successfully_organized"] += 1

                        # Log más informativo
                        relative_path = dest_folder.relative_to(organized_folder)
                        self.logger.info(f"Organizado: {archivo} → {relative_path}")
                    else:
                        self.logger.error(f"No se pudo crear carpeta para {archivo}")
                        stats["errors"] += 1

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

        # Preparar estadísticas finales
        unique_folders = stats["folders_created"]
        total_folders_created = len(unique_folders)
        cached_folders_used = len(self.existing_folders_cache) - total_folders_created

        # Convertir set a count para el reporte
        stats["folders_created"] = total_folders_created
        stats["folders_reused"] = max(0, cached_folders_used)

        # Log detallado de resultados
        self.logger.info(f"Organización completada:")
        self.logger.info(f"  - Archivos organizados: {stats['successfully_organized']}")
        self.logger.info(f"  - Movidos a no_clasificados: {stats['moved_to_unclassified']}")
        self.logger.info(f"  - Carpetas nuevas creadas: {stats['folders_created']}")
        self.logger.info(f"  - Carpetas existentes reutilizadas: {stats['folders_reused']}")
        self.logger.info(f"  - Total en cache: {len(self.existing_folders_cache)}")
        self.logger.info(f"  - Errores: {stats['errors']}")

        # Log de carpetas únicas creadas (solo si son pocas)
        if total_folders_created <= 10:
            self.logger.info("Nuevas carpetas creadas:")
            for folder_path in sorted(unique_folders):
                relative_path = Path(folder_path).relative_to(organized_folder)
                self.logger.info(f"  → {relative_path}")

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

    def consolidate_pdfs_recursively(self, source_folder: str, consolidated_folder: str = None) -> Dict:
        """
        Consolida todos los PDFs de una estructura de carpetas recursiva en una sola carpeta.
        Los archivos se MUEVEN (no copian) para optimizar espacio y evitar duplicados.

        Args:
            source_folder: Carpeta raíz para buscar PDFs recursivamente
            consolidated_folder: Carpeta destino para consolidación

        Returns:
            Diccionario con estadísticas y registro de orígenes
        """
        source_path = Path(source_folder)

        if not source_path.exists() or not source_path.is_dir():
            raise ValueError(f"La carpeta origen no existe o no es válida: {source_folder}")

        # Crear carpeta de consolidación
        if consolidated_folder is None:
            consolidated_folder = source_path.parent / f"{source_path.name}_consolidado"
        else:
            consolidated_folder = Path(consolidated_folder)

        self._create_folder_if_needed(consolidated_folder)

        # Estadísticas y registro
        stats = {
            "total_found": 0,
            "successfully_moved": 0,
            "errors": 0,
            "duplicates_handled": 0,
            "folders_processed": 0,
            "origin_registry": {},  # archivo -> ruta_original
            "consolidated_folder": str(consolidated_folder)
        }

        # Archivo de registro de orígenes
        registry_file = consolidated_folder / "registry_origenes.json"

        self.logger.info(f"Iniciando consolidación recursiva desde: {source_path}")
        self.logger.info(f"Consolidando en: {consolidated_folder}")

        # Buscar todos los PDFs recursivamente
        pdf_files = list(source_path.rglob("*.pdf"))
        stats["total_found"] = len(pdf_files)

        if not pdf_files:
            self.logger.warning(f"No se encontraron archivos PDF en: {source_path}")
            return stats

        self.logger.info(f"Encontrados {len(pdf_files)} archivos PDF para consolidar")

        # Procesar cada PDF
        folders_seen = set()

        for pdf_file in pdf_files:
            try:
                # Registrar carpeta procesada
                folder_path = pdf_file.parent
                if folder_path not in folders_seen:
                    folders_seen.add(folder_path)
                    stats["folders_processed"] += 1

                # Determinar nombre destino (manejar duplicados)
                dest_filename = self._get_unique_filename(
                    consolidated_folder,
                    pdf_file.name,
                    pdf_file.parent
                )

                dest_file = consolidated_folder / dest_filename

                # Registrar origen
                relative_origin = pdf_file.relative_to(source_path)
                stats["origin_registry"][dest_filename] = {
                    "original_path": str(pdf_file),
                    "relative_path": str(relative_origin),
                    "original_folder": str(pdf_file.parent),
                    "moved_timestamp": datetime.now().isoformat(),
                    "file_size": pdf_file.stat().st_size
                }

                # Mover archivo (no copiar)
                shutil.move(str(pdf_file), str(dest_file))
                stats["successfully_moved"] += 1

                self.logger.info(f"Movido: {relative_origin} → {dest_filename}")

                # Si el nombre cambió por duplicado
                if dest_filename != pdf_file.name:
                    stats["duplicates_handled"] += 1
                    self.logger.info(f"  → Renombrado por duplicado: {pdf_file.name} → {dest_filename}")

            except Exception as e:
                self.logger.error(f"Error moviendo {pdf_file}: {e}")
                stats["errors"] += 1

        # Guardar registro de orígenes
        try:
            with open(registry_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "consolidation_info": {
                        "source_folder": str(source_path),
                        "consolidated_folder": str(consolidated_folder),
                        "consolidation_date": datetime.now().isoformat(),
                        "total_files": stats["successfully_moved"]
                    },
                    "file_origins": stats["origin_registry"]
                }, f, indent=2, ensure_ascii=False)

            self.logger.info(f"Registro de orígenes guardado en: {registry_file}")

        except Exception as e:
            self.logger.error(f"Error guardando registro de orígenes: {e}")

        # Limpiar carpetas vacías (opcional)
        self._cleanup_empty_folders(source_path, stats)

        # Log final
        self.logger.info(f"Consolidación completada:")
        self.logger.info(f"  - Archivos encontrados: {stats['total_found']}")
        self.logger.info(f"  - Archivos movidos: {stats['successfully_moved']}")
        self.logger.info(f"  - Duplicados manejados: {stats['duplicates_handled']}")
        self.logger.info(f"  - Carpetas procesadas: {stats['folders_processed']}")
        self.logger.info(f"  - Errores: {stats['errors']}")

        return stats

    def _get_unique_filename(self, dest_folder: Path, filename: str, original_folder: Path) -> str:
        """
        Genera un nombre único para evitar sobrescribir archivos con el mismo nombre.

        Args:
            dest_folder: Carpeta destino
            filename: Nombre original del archivo
            original_folder: Carpeta original del archivo

        Returns:
            Nombre único para el archivo
        """
        base_name = filename
        dest_file = dest_folder / base_name

        # Si no hay conflicto, usar nombre original
        if not dest_file.exists():
            return base_name

        # Si hay conflicto, agregar prefijo de carpeta original
        name_without_ext = Path(filename).stem
        extension = Path(filename).suffix
        folder_name = original_folder.name

        # Crear nombre con prefijo de carpeta
        new_name = f"{folder_name}_{name_without_ext}{extension}"
        dest_file = dest_folder / new_name

        # Si aún hay conflicto, agregar contador
        counter = 1
        while dest_file.exists():
            counter_name = f"{folder_name}_{name_without_ext}_{counter:03d}{extension}"
            dest_file = dest_folder / counter_name
            counter += 1
            if counter > 999:  # Límite de seguridad
                # Usar timestamp como último recurso
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                counter_name = f"{folder_name}_{name_without_ext}_{timestamp}{extension}"
                break

        return dest_file.name

    def _cleanup_empty_folders(self, source_path: Path, stats: Dict):
        """
        Limpia carpetas vacías después de la consolidación.

        Args:
            source_path: Carpeta raíz
            stats: Diccionario de estadísticas para actualizar
        """
        empty_folders_removed = 0

        try:
            # Recorrer desde las carpetas más profundas hacia arriba
            for root, dirs, files in os.walk(source_path, topdown=False):
                root_path = Path(root)

                # Saltar la carpeta raíz
                if root_path == source_path:
                    continue

                # Verificar si la carpeta está vacía
                if not any(root_path.iterdir()):
                    try:
                        root_path.rmdir()
                        empty_folders_removed += 1
                        self.logger.info(f"Carpeta vacía eliminada: {root_path.relative_to(source_path)}")
                    except Exception as e:
                        self.logger.warning(f"No se pudo eliminar carpeta vacía {root_path}: {e}")

        except Exception as e:
            self.logger.error(f"Error durante limpieza de carpetas vacías: {e}")

        stats["empty_folders_removed"] = empty_folders_removed
        if empty_folders_removed > 0:
            self.logger.info(f"Carpetas vacías eliminadas: {empty_folders_removed}")

    def restore_from_consolidation(self, consolidated_folder: str) -> Dict:
        """
        Restaura archivos a sus ubicaciones originales usando el registro.

        Args:
            consolidated_folder: Carpeta con archivos consolidados

        Returns:
            Estadísticas de la restauración
        """
        consolidated_path = Path(consolidated_folder)
        registry_file = consolidated_path / "registry_origenes.json"

        if not registry_file.exists():
            raise ValueError(f"No se encontró archivo de registro en: {registry_file}")

        stats = {
            "total_to_restore": 0,
            "successfully_restored": 0,
            "errors": 0
        }

        try:
            with open(registry_file, 'r', encoding='utf-8') as f:
                registry_data = json.load(f)

            file_origins = registry_data.get("file_origins", {})
            stats["total_to_restore"] = len(file_origins)

            self.logger.info(f"Iniciando restauración de {len(file_origins)} archivos")

            for consolidated_filename, origin_info in file_origins.items():
                try:
                    consolidated_file = consolidated_path / consolidated_filename
                    original_path = Path(origin_info["original_path"])

                    # Crear carpeta original si no existe
                    original_path.parent.mkdir(parents=True, exist_ok=True)

                    # Mover archivo de vuelta
                    shutil.move(str(consolidated_file), str(original_path))
                    stats["successfully_restored"] += 1

                    self.logger.info(f"Restaurado: {consolidated_filename} → {origin_info['relative_path']}")

                except Exception as e:
                    self.logger.error(f"Error restaurando {consolidated_filename}: {e}")
                    stats["errors"] += 1

        except Exception as e:
            self.logger.error(f"Error leyendo registro: {e}")
            stats["errors"] += 1

        self.logger.info(f"Restauración completada: {stats['successfully_restored']}/{stats['total_to_restore']}")
        return stats


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