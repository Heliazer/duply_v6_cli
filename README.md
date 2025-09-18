# Clasificador de PDFs con Google Gemini

Herramienta eficiente para clasificar automáticamente archivos PDF por temas utilizando la API de Google Gemini.

## 🚀 Características

- **Procesamiento por lotes**: Optimiza las llamadas a la API procesando múltiples PDFs juntos
- **Clasificación jerárquica**: 3 niveles de clasificación temática
- **Múltiples formatos de salida**: JSON y CSV
- **Logging completo**: Registro detallado del procesamiento
- **Configuración flexible**: Tamaño de lotes ajustable
- **Manejo de errores robusto**: Continúa procesando aunque falle algún archivo

## 📦 Instalación

1. **Clonar o descargar** los archivos del proyecto

2. **Instalar dependencias**:

   **Opción A: Instalación completa (recomendada)**
   ```bash
   pip install -r requirements.txt
   ```
   Incluye interfaz colorida, menús interactivos y todas las funcionalidades.

   **Opción B: Instalación mínima**
   ```bash
   pip install -r requirements-minimal.txt
   ```
   Solo funcionalidades básicas por línea de comandos.

3. **Configurar API key**:
   - Obtén tu clave de API de Google Gemini en: https://makersuite.google.com/app/apikey
   - El archivo `.env` ya está configurado con tu API key

### 🔧 Dependencias incluidas

#### Principales:
- `google-generativeai` - API de Google Gemini para clasificación IA
- `PyMuPDF` - Extracción de texto de archivos PDF
- `python-dotenv` - Manejo de variables de entorno

#### Interfaz visual:
- `colorama` - Colores en terminal (multiplataforma)
- `rich` - Interfaz rica con tablas, barras de progreso y menús

## 💻 Uso

### 🎨 Menú Interactivo Colorido (Recomendado)

```bash
# Lanzar menú interactivo
python main.py
```

El menú interactivo incluye:
- 🎨 **Interfaz colorida y atractiva**
- 📋 **Menú de opciones intuitivo**
- 🔄 **Barras de progreso en tiempo real**
- 📊 **Resultados visuales**
- ⚙️ **Configuración guiada**
- ❓ **Ayuda integrada**

### 💻 Línea de Comandos (Uso Avanzado)

```bash
# Clasificar PDFs en una carpeta
python pdf_classifier.py /ruta/a/carpeta/con/pdfs

# Con tamaño de lote personalizado
python pdf_classifier.py /ruta/a/carpeta/con/pdfs --batch-size 3

# Especificar directorio de salida
python pdf_classifier.py /ruta/a/carpeta/con/pdfs --output mis_resultados

# O usar el punto de entrada principal
python main.py /ruta/a/carpeta/con/pdfs --organize
```

### Uso programático

```python
from pdf_classifier import PDFClassifier

# Crear clasificador
classifier = PDFClassifier(batch_size=5)

# Clasificar PDFs en carpeta
stats = classifier.classify_pdfs_in_folder(
    folder_path="/ruta/a/pdfs",
    output_dir="resultados"
)

print(f"Procesados: {stats['processed']}/{stats['total_files']}")
```

### Ejecutar ejemplo

```bash
python ejemplo_uso.py
```

## 📁 Estructura de salida

Los resultados se guardan en dos formatos:

### JSON
```json
[
  {
    "documento": 1,
    "archivo": "libro_historia.pdf",
    "tema_general": "Historia",
    "subtema": "Historia Medieval",
    "tema_especifico": "Caballería y Feudalismo",
    "confianza": "alta",
    "palabras_clave": ["medieval", "caballeros", "feudal"],
    "timestamp": "2024-01-15T10:30:00"
  }
]
```

### CSV
| archivo | tema_general | subtema | tema_especifico | confianza | palabras_clave |
|---------|-------------|---------|----------------|-----------|----------------|
| libro_historia.pdf | Historia | Historia Medieval | Caballería y Feudalismo | alta | medieval, caballeros, feudal |

## ⚙️ Configuración

### Variables de entorno (.env)
```
GOOGLE_API_KEY=tu_api_key_aqui
```

### Parámetros ajustables

- **batch_size**: Número de PDFs por lote (default: 5)
- **num_pages**: Páginas a analizar por PDF (default: 5)
- **max_chars**: Caracteres máximos por PDF (default: 10000)

## 📊 Logging

El sistema genera logs detallados en `pdf_classifier.log`:
- Archivos procesados exitosamente
- Errores encontrados
- Estadísticas de procesamiento
- Tiempos de ejecución

## 🛠️ Solución de problemas

### Error de API key
```
ValueError: API key de Google Gemini no encontrada
```
**Solución**: Verificar que el archivo `.env` contiene la clave correcta.

### PDFs no se procesan
- Verificar que los archivos son PDFs válidos
- Algunos PDFs escaneados pueden no tener texto extraíble
- Verificar permisos de lectura de archivos

### Rate limits de la API
El sistema incluye pausas automáticas entre lotes. Si experimentas límites:
- Reducir `batch_size`
- Aumentar el tiempo de pausa en `time.sleep()`

## 📈 Optimizaciones para grandes volúmenes

Para procesar muchos PDFs eficientemente:

1. **Ajustar tamaño de lote**: Prueba diferentes valores (3-7)
2. **Limitar páginas analizadas**: Reducir `num_pages` a 3
3. **Procesar en horarios de menor uso**: Para evitar rate limits
4. **Monitorear logs**: Para identificar archivos problemáticos

## 🤝 Contribuir

Para mejorar el clasificador:
1. Fork del proyecto
2. Crear rama para tu feature
3. Commit de cambios
4. Push y crear Pull Request