#!/usr/bin/env python3
"""
MENÚ INTERACTIVO PARA CLASIFICADOR DE PDFs
==========================================
Interfaz colorida y atractiva para el clasificador de PDFs con Google Gemini.
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import json

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
    from rich.prompt import Prompt, Confirm
    from rich.layout import Layout
    from rich.align import Align
    from rich.live import Live
    from rich import box
    from colorama import init, Fore, Back, Style
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    from colorama import init, Fore, Back, Style

# Inicializar colorama
init(autoreset=True)

# Importar nuestro clasificador
from pdf_classifier import PDFClassifier

class MenuColorido:
    def __init__(self):
        self.console = Console() if RICH_AVAILABLE else None
        self.classifier = None
        self.carpeta_actual = None

    def limpiar_pantalla(self):
        """Limpia la pantalla del terminal."""
        os.system('clear' if os.name == 'posix' else 'cls')

    def mostrar_banner(self):
        """Muestra el banner principal del programa."""
        if RICH_AVAILABLE:
            self._mostrar_banner_rich()
        else:
            self._mostrar_banner_simple()

    def _mostrar_banner_rich(self):
        """Banner con Rich (colorido y estilizado)."""
        banner_text = """
    ██████╗ ██████╗ ███████╗     ██████╗██╗      █████╗ ███████╗███████╗██╗███████╗██╗███████╗██████╗
    ██╔══██╗██╔══██╗██╔════╝    ██╔════╝██║     ██╔══██╗██╔════╝██╔════╝██║██╔════╝██║██╔════╝██╔══██╗
    ██████╔╝██║  ██║█████╗      ██║     ██║     ███████║███████╗███████╗██║█████╗  ██║█████╗  ██████╔╝
    ██╔═══╝ ██║  ██║██╔══╝      ██║     ██║     ██╔══██║╚════██║╚════██║██║██╔══╝  ██║██╔══╝  ██╔══██╗
    ██║     ██████╔╝██║         ╚██████╗███████╗██║  ██║███████║███████║██║██║     ██║███████╗██║  ██║
    ╚═╝     ╚═════╝ ╚═╝          ╚═════╝╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝╚═╝╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝
        """

        panel = Panel(
            Align.center(
                Text(banner_text, style="bold cyan") +
                Text("\n🤖 Clasificador Inteligente de PDFs con Google Gemini", style="bold yellow") +
                Text("\n📚 Organiza automáticamente tus documentos por tema", style="italic green")
            ),
            box=box.DOUBLE,
            border_style="bright_blue",
            title="[bold red]🚀 BIENVENIDO 🚀[/bold red]",
            title_align="center"
        )

        self.console.print(panel)
        self.console.print()

    def _mostrar_banner_simple(self):
        """Banner simple sin Rich."""
        print(Fore.CYAN + Style.BRIGHT + "=" * 70)
        print(Fore.YELLOW + Style.BRIGHT + "🚀   CLASIFICADOR INTELIGENTE DE PDFs   🚀")
        print(Fore.GREEN + "📚   Organiza automáticamente tus documentos por tema")
        print(Fore.BLUE + "🤖   Powered by Google Gemini AI")
        print(Fore.CYAN + Style.BRIGHT + "=" * 70)
        print()

    def mostrar_menu_principal(self):
        """Muestra el menú principal de opciones."""
        if RICH_AVAILABLE:
            return self._mostrar_menu_rich()
        else:
            return self._mostrar_menu_simple()

    def _mostrar_menu_rich(self):
        """Menú principal con Rich."""
        self.console.print(Text("MENÚ PRINCIPAL", style="bold bright_blue"))
        self.console.print(Text("─" * 64, style="bright_black"))

        api_status = "API key configurada" if os.getenv('GOOGLE_API_KEY') else "API key pendiente"
        carpeta_status = f"Ruta seleccionada: {self.carpeta_actual}" if self.carpeta_actual else "Ruta no seleccionada"

        opciones = [
            ("1", "Seleccionar carpeta de PDFs", carpeta_status, "cyan"),
            ("2", "Consolidar PDFs recursivamente", "Nuevo", "magenta"),
            ("3", "Clasificar PDFs únicamente", "", ""),
            ("4", "Clasificar y organizar automáticamente", "Recomendado", "green"),
            ("5", "Restaurar desde consolidación", "", ""),
            ("6", "Ver resultados anteriores", "", ""),
            ("7", "Configuración avanzada", api_status, "yellow"),
            ("8", "Ayuda y ejemplos", "", ""),
            ("0", "Salir", "", ""),
        ]

        for numero, descripcion, estado, estado_color in opciones:
            linea = Text()
            linea.append(f"{numero}. ", style="bold bright_white")
            linea.append(descripcion, style="bold white" if numero == "4" else "white")
            if estado:
                linea.append("  ")
                linea.append(estado, style=f"bold {estado_color}" if estado_color else "bold bright_black")
            self.console.print(linea)

        self.console.print(Text("─" * 64, style="bright_black"))

        return Prompt.ask(
            "\n[bold yellow]Selecciona una opción[/bold yellow]",
            choices=["0", "1", "2", "3", "4", "5", "6", "7", "8"],
            default="4"
        )

    def _mostrar_menu_simple(self):
        """Menú principal simple."""
        print(Fore.CYAN + Style.BRIGHT + "MENÚ PRINCIPAL")
        print(Fore.BLUE + "─" * 50)

        api_status = "API key configurada" if os.getenv('GOOGLE_API_KEY') else "API key pendiente"
        carpeta_status = f"Ruta seleccionada: {self.carpeta_actual}" if self.carpeta_actual else "Ruta no seleccionada"

        print(Fore.WHITE + f"1. Seleccionar carpeta de PDFs              {carpeta_status}")
        print(Fore.WHITE + "2. Consolidar PDFs recursivamente           Nuevo")
        print(Fore.WHITE + "3. Clasificar PDFs únicamente")
        print(Fore.WHITE + Style.BRIGHT + "4. Clasificar y organizar automáticamente   Recomendado")
        print(Fore.WHITE + "5. Restaurar desde consolidación")
        print(Fore.WHITE + "6. Ver resultados anteriores")
        print(Fore.WHITE + f"7. Configuración avanzada                   {api_status}")
        print(Fore.WHITE + "8. Ayuda y ejemplos")
        print(Fore.WHITE + "0. Salir")
        print(Fore.BLUE + "─" * 50)

        while True:
            opcion = input(Fore.YELLOW + "Selecciona una opción (0-8, default=4): ").strip()
            if not opcion:
                return "4"
            if opcion in ["0", "1", "2", "3", "4", "5", "6", "7", "8"]:
                return opcion
            print(Fore.RED + "Opción inválida. Intenta de nuevo.")

    def seleccionar_carpeta(self):
        """Permite al usuario seleccionar una carpeta de PDFs."""
        if RICH_AVAILABLE:
            self.console.print("\n[bold blue]📁 SELECCIÓN DE CARPETA[/bold blue]")
        else:
            print(Fore.BLUE + Style.BRIGHT + "\n📁 SELECCIÓN DE CARPETA")

        while True:
            if RICH_AVAILABLE:
                carpeta = Prompt.ask("\n[yellow]Introduce la ruta de la carpeta con PDFs[/yellow]")
            else:
                carpeta = input(Fore.YELLOW + "\nIntroduce la ruta de la carpeta con PDFs: ")

            if not carpeta:
                continue

            path = Path(carpeta).expanduser()

            if not path.exists():
                if RICH_AVAILABLE:
                    self.console.print(f"[red]❌ La carpeta no existe: {path}[/red]")
                else:
                    print(Fore.RED + f"❌ La carpeta no existe: {path}")
                continue

            if not path.is_dir():
                if RICH_AVAILABLE:
                    self.console.print(f"[red]❌ No es una carpeta válida: {path}[/red]")
                else:
                    print(Fore.RED + f"❌ No es una carpeta válida: {path}")
                continue

            # Contar PDFs
            pdfs = list(path.glob("*.pdf"))

            if not pdfs:
                if RICH_AVAILABLE:
                    self.console.print(f"[red]❌ No se encontraron archivos PDF en: {path}[/red]")
                else:
                    print(Fore.RED + f"❌ No se encontraron archivos PDF en: {path}")
                continue

            self.carpeta_actual = str(path)

            if RICH_AVAILABLE:
                self.console.print(f"\n[green]✅ Carpeta seleccionada: {path}[/green]")
                self.console.print(f"[blue]📊 Se encontraron {len(pdfs)} archivos PDF[/blue]")
            else:
                print(Fore.GREEN + f"\n✅ Carpeta seleccionada: {path}")
                print(Fore.BLUE + f"📊 Se encontraron {len(pdfs)} archivos PDF")

            input("\nPresiona Enter para continuar...")
            break

    def mostrar_progreso_clasificacion(self, total_archivos, batch_size):
        """Muestra una barra de progreso durante la clasificación."""
        if not RICH_AVAILABLE:
            print(Fore.YELLOW + f"🔄 Procesando {total_archivos} archivos en lotes de {batch_size}...")
            return None

        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=self.console
        )

        return progress

    def ejecutar_clasificacion(self, organizar=True):
        """Ejecuta el proceso de clasificación con interfaz visual."""
        if not self.carpeta_actual:
            if RICH_AVAILABLE:
                self.console.print("[red]❌ Primero debes seleccionar una carpeta de PDFs[/red]")
            else:
                print(Fore.RED + "❌ Primero debes seleccionar una carpeta de PDFs")
            input("Presiona Enter para continuar...")
            return

        if not os.getenv('GOOGLE_API_KEY'):
            if RICH_AVAILABLE:
                self.console.print("[red]❌ API Key de Google Gemini no configurada[/red]")
            else:
                print(Fore.RED + "❌ API Key de Google Gemini no configurada")
            input("Presiona Enter para continuar...")
            return

        try:
            # Crear clasificador
            if RICH_AVAILABLE:
                batch_size = int(Prompt.ask("\n[yellow]Tamaño del lote[/yellow]", default="5"))
            else:
                batch_size_input = input(Fore.YELLOW + "\nTamaño del lote (default=5): ")
                batch_size = int(batch_size_input) if batch_size_input else 5

            self.classifier = PDFClassifier(batch_size=batch_size)

            # Mostrar configuración
            if RICH_AVAILABLE:
                config_table = Table(show_header=False, box=box.SIMPLE)
                config_table.add_column("Setting", style="cyan")
                config_table.add_column("Value", style="white")
                config_table.add_row("📁 Carpeta", self.carpeta_actual)
                config_table.add_row("🔄 Modo", "Clasificar y Organizar" if organizar else "Solo Clasificar")
                config_table.add_row("📦 Lote", str(batch_size))

                self.console.print(Panel(config_table, title="[bold green]⚙️ CONFIGURACIÓN[/bold green]"))

                if not Confirm.ask("\n[yellow]¿Continuar con la clasificación?[/yellow]", default=True):
                    return
            else:
                print(Fore.GREEN + "\n⚙️ CONFIGURACIÓN:")
                print(f"📁 Carpeta: {self.carpeta_actual}")
                print(f"🔄 Modo: {'Clasificar y Organizar' if organizar else 'Solo Clasificar'}")
                print(f"📦 Lote: {batch_size}")

                continuar = input("\n¿Continuar? (s/N): ").lower()
                if continuar not in ['s', 'si', 'sí', 'y', 'yes']:
                    return

            # Ejecutar clasificación
            if RICH_AVAILABLE:
                self.console.print("\n[bold green]🚀 INICIANDO CLASIFICACIÓN...[/bold green]")
            else:
                print(Fore.GREEN + Style.BRIGHT + "\n🚀 INICIANDO CLASIFICACIÓN...")

            if organizar:
                stats = self.classifier.classify_and_organize(
                    folder_path=self.carpeta_actual,
                    output_dir="results",
                    organize_files=True
                )
            else:
                stats = self.classifier.classify_pdfs_in_folder(
                    folder_path=self.carpeta_actual,
                    output_dir="results"
                )

            # Mostrar resultados
            self.mostrar_resultados(stats)

        except Exception as e:
            if RICH_AVAILABLE:
                self.console.print(f"[red]❌ Error durante la clasificación: {e}[/red]")
            else:
                print(Fore.RED + f"❌ Error durante la clasificación: {e}")

        input("\nPresiona Enter para continuar...")

    def mostrar_resultados(self, stats):
        """Muestra los resultados de la clasificación de forma visual."""
        if RICH_AVAILABLE:
            self._mostrar_resultados_rich(stats)
        else:
            self._mostrar_resultados_simple(stats)

    def _mostrar_resultados_rich(self, stats):
        """Muestra resultados con Rich."""
        # Tabla de estadísticas
        results_table = Table(show_header=False, box=box.ROUNDED, border_style="green")
        results_table.add_column("Métrica", style="bold cyan")
        results_table.add_column("Valor", style="bold white")

        results_table.add_row("📁 Archivos totales", str(stats['total_files']))
        results_table.add_row("✅ Procesados exitosamente", str(stats['processed']))
        results_table.add_row("❌ Errores", str(stats['errors']))
        results_table.add_row("📊 Tasa de éxito", f"{stats['success_rate']:.1f}%")

        if 'organization' in stats:
            org_stats = stats['organization']
            results_table.add_row("", "")  # Separador
            results_table.add_row("🗂️ Organizados por tema", str(org_stats['successfully_organized']))
            results_table.add_row("❓ Movidos a 'no_clasificados'", str(org_stats['moved_to_unclassified']))
            results_table.add_row("📁 Carpetas nuevas creadas", str(org_stats['folders_created']))
            if 'folders_reused' in org_stats:
                results_table.add_row("♻️ Carpetas reutilizadas", str(org_stats['folders_reused']))

        panel = Panel(
            results_table,
            title="[bold green]🎉 RESULTADOS DE LA CLASIFICACIÓN[/bold green]",
            border_style="bright_green"
        )

        self.console.print("\n" + "="*60)
        self.console.print(panel)

        if 'organized_folder' in stats:
            self.console.print(f"\n[bold blue]📂 Archivos organizados en: {stats['organized_folder']}[/bold blue]")

    def _mostrar_resultados_simple(self, stats):
        """Muestra resultados simples."""
        print(Fore.GREEN + Style.BRIGHT + "\n🎉 RESULTADOS DE LA CLASIFICACIÓN")
        print(Fore.CYAN + "=" * 60)
        print(f"📁 Archivos totales: {stats['total_files']}")
        print(f"✅ Procesados exitosamente: {stats['processed']}")
        print(f"❌ Errores: {stats['errors']}")
        print(f"📊 Tasa de éxito: {stats['success_rate']:.1f}%")

        if 'organization' in stats:
            org_stats = stats['organization']
            print(Fore.YELLOW + "\n--- ORGANIZACIÓN DE ARCHIVOS ---")
            print(f"🗂️ Organizados por tema: {org_stats['successfully_organized']}")
            print(f"❓ Movidos a 'no_clasificados': {org_stats['moved_to_unclassified']}")
            print(f"📁 Carpetas nuevas creadas: {org_stats['folders_created']}")
            if 'folders_reused' in org_stats:
                print(f"♻️ Carpetas reutilizadas: {org_stats['folders_reused']}")

        if 'organized_folder' in stats:
            print(Fore.BLUE + f"\n📂 Archivos organizados en: {stats['organized_folder']}")

    def mostrar_ayuda(self):
        """Muestra la ayuda del programa."""
        if RICH_AVAILABLE:
            help_text = """
[bold cyan]🔍 CÓMO USAR EL CLASIFICADOR[/bold cyan]

[bold yellow]1. Preparación:[/bold yellow]
   • Coloca tus archivos PDF en una carpeta
   • Asegúrate de tener conexión a internet
   • Verifica que tu API Key esté configurada

[bold yellow]2. Proceso de clasificación:[/bold yellow]
   • El sistema analiza las primeras 20 páginas de cada PDF
   • Utiliza Google Gemini AI para clasificar el contenido
   • Genera una jerarquía de 3 niveles: General > Subtema > Específico

[bold yellow]3. Organización automática:[/bold yellow]
   • Crea carpetas por tema automáticamente
   • Copia los PDFs a sus carpetas correspondientes
   • Los archivos problemáticos van a 'no_clasificados'

[bold yellow]4. Resultados:[/bold yellow]
   • Archivos JSON y CSV con la clasificación
   • Logs detallados del proceso
   • Estructura de carpetas organizada

[bold red]💡 CONSEJOS:[/bold red]
   • Usa lotes de 3-7 archivos para mejor rendimiento
   • Los PDFs deben tener texto extraíble (no solo imágenes)
   • La clasificación mejora con PDFs de contenido claro y específico
            """

            panel = Panel(
                help_text,
                title="[bold blue]❓ AYUDA Y GUÍA DE USO[/bold blue]",
                border_style="yellow"
            )

            self.console.print(panel)
        else:
            print(Fore.BLUE + Style.BRIGHT + "\n❓ AYUDA Y GUÍA DE USO")
            print(Fore.CYAN + "=" * 50)
            print("🔍 CÓMO USAR EL CLASIFICADOR")
            print("\n1. Preparación:")
            print("   • Coloca tus archivos PDF en una carpeta")
            print("   • Asegúrate de tener conexión a internet")
            print("   • Verifica que tu API Key esté configurada")
            print("\n2. Proceso de clasificación:")
            print("   • Analiza las primeras 20 páginas de cada PDF")
            print("   • Utiliza Google Gemini AI para clasificar")
            print("   • Genera jerarquía de 3 niveles")
            print("\n3. Organización automática:")
            print("   • Crea carpetas por tema automáticamente")
            print("   • Copia PDFs a carpetas correspondientes")
            print("   • Archivos problemáticos van a 'no_clasificados'")

        input("\nPresiona Enter para continuar...")

    def consolidar_pdfs_recursivamente(self):
        """Consolida PDFs de múltiples carpetas en una sola."""
        if RICH_AVAILABLE:
            self.console.print("\n[bold blue]📦 CONSOLIDACIÓN RECURSIVA DE PDFs[/bold blue]")
        else:
            print(Fore.BLUE + Style.BRIGHT + "\n📦 CONSOLIDACIÓN RECURSIVA DE PDFs")

        if RICH_AVAILABLE:
            carpeta_origen = Prompt.ask("\n[yellow]Carpeta raíz para buscar PDFs recursivamente[/yellow]")
        else:
            carpeta_origen = input(Fore.YELLOW + "\nCarpeta raíz para buscar PDFs recursivamente: ")

        if not carpeta_origen:
            return

        carpeta_origen_path = Path(carpeta_origen).expanduser()

        if not carpeta_origen_path.exists():
            if RICH_AVAILABLE:
                self.console.print(f"[red]❌ La carpeta no existe: {carpeta_origen_path}[/red]")
            else:
                print(Fore.RED + f"❌ La carpeta no existe: {carpeta_origen_path}")
            input("Presiona Enter para continuar...")
            return

        # Previsualizar archivos encontrados
        pdf_files = list(carpeta_origen_path.rglob("*.pdf"))

        if not pdf_files:
            if RICH_AVAILABLE:
                self.console.print(f"[yellow]⚠️  No se encontraron archivos PDF en: {carpeta_origen_path}[/yellow]")
            else:
                print(Fore.YELLOW + f"⚠️  No se encontraron archivos PDF en: {carpeta_origen_path}")
            input("Presiona Enter para continuar...")
            return

        # Mostrar previsualización
        if RICH_AVAILABLE:
            self.console.print(f"\n[green]📊 Se encontraron {len(pdf_files)} archivos PDF[/green]")

            if len(pdf_files) <= 10:
                self.console.print("\n[cyan]Archivos encontrados:[/cyan]")
                for pdf_file in pdf_files[:10]:
                    relative_path = pdf_file.relative_to(carpeta_origen_path)
                    self.console.print(f"  📄 {relative_path}")
            else:
                self.console.print(f"\n[cyan]Mostrando primeros 10 de {len(pdf_files)} archivos:[/cyan]")
                for pdf_file in pdf_files[:10]:
                    relative_path = pdf_file.relative_to(carpeta_origen_path)
                    self.console.print(f"  📄 {relative_path}")
                self.console.print(f"  ... y {len(pdf_files) - 10} más")

            carpeta_destino = Prompt.ask(
                "\n[yellow]Carpeta destino para consolidación (Enter para automática)[/yellow]",
                default=""
            )

            if not Confirm.ask("\n[yellow]¿Confirmar consolidación? Los archivos se MOVERÁN[/yellow]", default=False):
                return
        else:
            print(Fore.GREEN + f"\n📊 Se encontraron {len(pdf_files)} archivos PDF")

            if len(pdf_files) <= 10:
                print(Fore.CYAN + "\nArchivos encontrados:")
                for pdf_file in pdf_files[:10]:
                    relative_path = pdf_file.relative_to(carpeta_origen_path)
                    print(f"  📄 {relative_path}")
            else:
                print(Fore.CYAN + f"\nMostrando primeros 10 de {len(pdf_files)} archivos:")
                for pdf_file in pdf_files[:10]:
                    relative_path = pdf_file.relative_to(carpeta_origen_path)
                    print(f"  📄 {relative_path}")
                print(f"  ... y {len(pdf_files) - 10} más")

            carpeta_destino = input(Fore.YELLOW + "\nCarpeta destino para consolidación (Enter para automática): ")

            confirmacion = input(Fore.YELLOW + "\n¿Confirmar consolidación? Los archivos se MOVERÁN (s/N): ").lower()
            if confirmacion not in ['s', 'si', 'sí', 'y', 'yes']:
                return

        try:
            # Ejecutar consolidación
            if RICH_AVAILABLE:
                self.console.print("\n[bold green]🚀 INICIANDO CONSOLIDACIÓN...[/bold green]")
            else:
                print(Fore.GREEN + Style.BRIGHT + "\n🚀 INICIANDO CONSOLIDACIÓN...")

            classifier = PDFClassifier()

            stats = classifier.consolidate_pdfs_recursively(
                source_folder=str(carpeta_origen_path),
                consolidated_folder=carpeta_destino if carpeta_destino else None
            )

            # Mostrar resultados
            self.mostrar_resultados_consolidacion(stats)

        except Exception as e:
            if RICH_AVAILABLE:
                self.console.print(f"[red]❌ Error durante la consolidación: {e}[/red]")
            else:
                print(Fore.RED + f"❌ Error durante la consolidación: {e}")

        input("\nPresiona Enter para continuar...")

    def restaurar_consolidacion(self):
        """Restaura archivos desde una consolidación."""
        if RICH_AVAILABLE:
            self.console.print("\n[bold blue]🔄 RESTAURAR DESDE CONSOLIDACIÓN[/bold blue]")
        else:
            print(Fore.BLUE + Style.BRIGHT + "\n🔄 RESTAURAR DESDE CONSOLIDACIÓN")

        if RICH_AVAILABLE:
            carpeta_consolidada = Prompt.ask("\n[yellow]Carpeta con archivos consolidados[/yellow]")
        else:
            carpeta_consolidada = input(Fore.YELLOW + "\nCarpeta con archivos consolidados: ")

        if not carpeta_consolidada:
            return

        carpeta_path = Path(carpeta_consolidada).expanduser()

        if not carpeta_path.exists():
            if RICH_AVAILABLE:
                self.console.print(f"[red]❌ La carpeta no existe: {carpeta_path}[/red]")
            else:
                print(Fore.RED + f"❌ La carpeta no existe: {carpeta_path}")
            input("Presiona Enter para continuar...")
            return

        # Verificar archivo de registro
        registry_file = carpeta_path / "registry_origenes.json"

        if not registry_file.exists():
            if RICH_AVAILABLE:
                self.console.print(f"[red]❌ No se encontró archivo de registro en: {registry_file}[/red]")
            else:
                print(Fore.RED + f"❌ No se encontró archivo de registro en: {registry_file}")
            input("Presiona Enter para continuar...")
            return

        try:
            # Leer información de consolidación
            with open(registry_file, 'r', encoding='utf-8') as f:
                registry_data = json.load(f)

            consolidation_info = registry_data.get("consolidation_info", {})
            file_origins = registry_data.get("file_origins", {})

            # Mostrar información
            if RICH_AVAILABLE:
                info_table = Table(show_header=False, box=box.SIMPLE)
                info_table.add_column("Info", style="cyan")
                info_table.add_column("Valor", style="white")

                info_table.add_row("📁 Carpeta original", consolidation_info.get("source_folder", "N/A"))
                info_table.add_row("📦 Fecha consolidación", consolidation_info.get("consolidation_date", "N/A"))
                info_table.add_row("📄 Total archivos", str(len(file_origins)))

                self.console.print(Panel(info_table, title="[bold yellow]📋 Información de Consolidación[/bold yellow]"))

                if not Confirm.ask("\n[yellow]¿Confirmar restauración?[/yellow]", default=False):
                    return
            else:
                print(Fore.YELLOW + "\n📋 Información de Consolidación:")
                print(f"📁 Carpeta original: {consolidation_info.get('source_folder', 'N/A')}")
                print(f"📦 Fecha consolidación: {consolidation_info.get('consolidation_date', 'N/A')}")
                print(f"📄 Total archivos: {len(file_origins)}")

                confirmacion = input(Fore.YELLOW + "\n¿Confirmar restauración? (s/N): ").lower()
                if confirmacion not in ['s', 'si', 'sí', 'y', 'yes']:
                    return

            # Ejecutar restauración
            if RICH_AVAILABLE:
                self.console.print("\n[bold green]🔄 INICIANDO RESTAURACIÓN...[/bold green]")
            else:
                print(Fore.GREEN + Style.BRIGHT + "\n🔄 INICIANDO RESTAURACIÓN...")

            classifier = PDFClassifier()
            stats = classifier.restore_from_consolidation(str(carpeta_path))

            # Mostrar resultados
            if RICH_AVAILABLE:
                self.console.print(f"\n[green]✅ Restauración completada: {stats['successfully_restored']}/{stats['total_to_restore']}[/green]")
            else:
                print(Fore.GREEN + f"\n✅ Restauración completada: {stats['successfully_restored']}/{stats['total_to_restore']}")

        except Exception as e:
            if RICH_AVAILABLE:
                self.console.print(f"[red]❌ Error durante la restauración: {e}[/red]")
            else:
                print(Fore.RED + f"❌ Error durante la restauración: {e}")

        input("\nPresiona Enter para continuar...")

    def mostrar_resultados_consolidacion(self, stats):
        """Muestra los resultados de la consolidación."""
        if RICH_AVAILABLE:
            results_table = Table(show_header=False, box=box.ROUNDED, border_style="green")
            results_table.add_column("Métrica", style="bold cyan")
            results_table.add_column("Valor", style="bold white")

            results_table.add_row("📁 Archivos encontrados", str(stats['total_found']))
            results_table.add_row("✅ Archivos movidos", str(stats['successfully_moved']))
            results_table.add_row("🔄 Duplicados manejados", str(stats['duplicates_handled']))
            results_table.add_row("📂 Carpetas procesadas", str(stats['folders_processed']))
            results_table.add_row("🗑️ Carpetas vacías eliminadas", str(stats.get('empty_folders_removed', 0)))
            results_table.add_row("❌ Errores", str(stats['errors']))

            panel = Panel(
                results_table,
                title="[bold green]📦 RESULTADOS DE LA CONSOLIDACIÓN[/bold green]",
                border_style="bright_green"
            )

            self.console.print("\n" + "="*60)
            self.console.print(panel)
            self.console.print(f"\n[bold blue]📂 Archivos consolidados en: {stats['consolidated_folder']}[/bold blue]")

        else:
            print(Fore.GREEN + Style.BRIGHT + "\n📦 RESULTADOS DE LA CONSOLIDACIÓN")
            print(Fore.CYAN + "=" * 60)
            print(f"📁 Archivos encontrados: {stats['total_found']}")
            print(f"✅ Archivos movidos: {stats['successfully_moved']}")
            print(f"🔄 Duplicados manejados: {stats['duplicates_handled']}")
            print(f"📂 Carpetas procesadas: {stats['folders_processed']}")
            print(f"🗑️ Carpetas vacías eliminadas: {stats.get('empty_folders_removed', 0)}")
            print(f"❌ Errores: {stats['errors']}")
            print(Fore.BLUE + f"\n📂 Archivos consolidados en: {stats['consolidated_folder']}")

    def ejecutar(self):
        """Ejecuta el menú principal del programa."""
        while True:
            self.limpiar_pantalla()
            self.mostrar_banner()

            opcion = self.mostrar_menu_principal()

            if opcion == "0":
                if RICH_AVAILABLE:
                    self.console.print("\n[bold blue]👋 ¡Gracias por usar el Clasificador de PDFs![/bold blue]")
                else:
                    print(Fore.BLUE + "\n👋 ¡Gracias por usar el Clasificador de PDFs!")
                break

            elif opcion == "1":
                self.seleccionar_carpeta()

            elif opcion == "2":
                self.consolidar_pdfs_recursivamente()

            elif opcion == "3":
                self.ejecutar_clasificacion(organizar=False)

            elif opcion == "4":
                self.ejecutar_clasificacion(organizar=True)

            elif opcion == "5":
                self.restaurar_consolidacion()

            elif opcion == "6":
                self.ver_resultados_anteriores()

            elif opcion == "7":
                self.configuracion_avanzada()

            elif opcion == "8":
                self.mostrar_ayuda()

    def ver_resultados_anteriores(self):
        """Muestra resultados de clasificaciones anteriores."""
        results_dir = Path("results")

        if not results_dir.exists():
            if RICH_AVAILABLE:
                self.console.print("[yellow]📭 No se encontraron resultados anteriores[/yellow]")
            else:
                print(Fore.YELLOW + "📭 No se encontraron resultados anteriores")
            input("Presiona Enter para continuar...")
            return

        json_files = list(results_dir.glob("clasificacion_*.json"))

        if not json_files:
            if RICH_AVAILABLE:
                self.console.print("[yellow]📭 No se encontraron archivos de clasificación[/yellow]")
            else:
                print(Fore.YELLOW + "📭 No se encontraron archivos de clasificación")
            input("Presiona Enter para continuar...")
            return

        # Mostrar archivos disponibles
        if RICH_AVAILABLE:
            self.console.print("\n[bold blue]📊 RESULTADOS ANTERIORES[/bold blue]")

            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Archivo", style="cyan")
            table.add_column("Fecha", style="yellow")
            table.add_column("Archivos", style="green")

            for json_file in sorted(json_files, key=lambda x: x.stat().st_mtime, reverse=True):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    fecha = datetime.fromtimestamp(json_file.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                    table.add_row(json_file.name, fecha, str(len(data)))
                except:
                    continue

            self.console.print(table)
        else:
            print(Fore.BLUE + "\n📊 RESULTADOS ANTERIORES")
            print(Fore.CYAN + "=" * 50)

            for i, json_file in enumerate(sorted(json_files, key=lambda x: x.stat().st_mtime, reverse=True)[:5]):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    fecha = datetime.fromtimestamp(json_file.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                    print(f"{i+1}. {json_file.name} - {fecha} ({len(data)} archivos)")
                except:
                    continue

        input("\nPresiona Enter para continuar...")

    def configuracion_avanzada(self):
        """Muestra opciones de configuración avanzada."""
        if RICH_AVAILABLE:
            self.console.print("\n[bold blue]⚙️ CONFIGURACIÓN AVANZADA[/bold blue]")

            config_table = Table(show_header=False, box=box.SIMPLE)
            config_table.add_column("Setting", style="cyan")
            config_table.add_column("Value", style="white")

            api_key = os.getenv('GOOGLE_API_KEY', 'No configurada')
            api_status = "✅ Configurada" if api_key != 'No configurada' else "❌ No configurada"

            config_table.add_row("🔑 API Key", api_status)
            config_table.add_row("📁 Carpeta actual", self.carpeta_actual or "No seleccionada")
            config_table.add_row("📂 Directorio de resultados", "results/")

            self.console.print(config_table)
        else:
            print(Fore.BLUE + "\n⚙️ CONFIGURACIÓN AVANZADA")
            print(Fore.CYAN + "=" * 40)

            api_key = os.getenv('GOOGLE_API_KEY', 'No configurada')
            api_status = "✅ Configurada" if api_key != 'No configurada' else "❌ No configurada"

            print(f"🔑 API Key: {api_status}")
            print(f"📁 Carpeta actual: {self.carpeta_actual or 'No seleccionada'}")
            print(f"📂 Directorio de resultados: results/")

        input("\nPresiona Enter para continuar...")


def main():
    """Función principal del menú interactivo."""
    try:
        menu = MenuColorido()
        menu.ejecutar()
    except KeyboardInterrupt:
        print("\n\n👋 ¡Hasta luego!")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")


if __name__ == "__main__":
    main()
