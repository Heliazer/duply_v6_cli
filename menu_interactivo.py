#!/usr/bin/env python3
"""
MENÚ INTERACTIVO PARA CLASIFICADOR DE PDFs
==========================================
Interfaz colorida y atractiva para el clasificador de PDFs con Google Gemini.
"""

import os
import sys
import shutil
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
        # Banner principal con gradientes de colores
        banner_text = Text.from_markup("""
[bold bright_cyan]    ██████╗ ██████╗ ███████╗[/bold bright_cyan][bold magenta]     ██████╗██╗      █████╗ ███████╗███████╗██╗███████╗██╗███████╗██████╗[/bold magenta]
[bold bright_cyan]    ██╔══██╗██╔══██╗██╔════╝[/bold bright_cyan][bold magenta]    ██╔════╝██║     ██╔══██╗██╔════╝██╔════╝██║██╔════╝██║██╔════╝██╔══██╗[/bold magenta]
[bold bright_cyan]    ██████╔╝██║  ██║█████╗[/bold bright_cyan][bold magenta]      ██║     ██║     ███████║███████╗███████╗██║█████╗  ██║█████╗  ██████╔╝[/bold magenta]
[bold bright_cyan]    ██╔═══╝ ██║  ██║██╔══╝[/bold bright_cyan][bold magenta]      ██║     ██║     ██╔══██║╚════██║╚════██║██║██╔══╝  ██║██╔══╝  ██╔══██╗[/bold magenta]
[bold bright_cyan]    ██║     ██████╔╝██║[/bold bright_cyan][bold magenta]         ╚██████╗███████╗██║  ██║███████║███████║██║██║     ██║███████╗██║  ██║[/bold magenta]
[bold bright_cyan]    ╚═╝     ╚═════╝ ╚═╝[/bold bright_cyan][bold magenta]          ╚═════╝╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝╚═╝╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝[/bold magenta]
        """)

        # Subtítulos con efectos visuales
        subtitle = Text("\n🤖 Clasificador Inteligente de PDFs con Google Gemini", style="bold yellow on blue")
        description = Text("\n📚 Organiza automáticamente tus documentos por tema", style="italic bright_green")

        # Crear el contenido del panel
        content = Align.center(banner_text + subtitle + description)

        # Panel principal con bordes dobles y colores vibrantes
        panel = Panel(
            content,
            box=box.DOUBLE_EDGE,
            border_style="bright_magenta",
            title="[bold red on yellow] 🚀 BIENVENIDO 🚀 [/bold red on yellow]",
            title_align="center",
            padding=(1, 2)
        )

        self.console.print(panel)

        # Línea decorativa adicional
        decorative_line = "─" * 80
        self.console.print(f"[bright_blue]{decorative_line}[/bright_blue]")
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
        # Crear tabla con diseño más atractivo
        table = Table(
            show_header=False,
            box=box.HEAVY_EDGE,
            border_style="bright_magenta",
            title_style="bold bright_cyan on blue",
            padding=(0, 2)
        )

        table.add_column("", style="bold bright_cyan", width=3, justify="center")
        table.add_column("Opción", style="bold white", min_width=40)
        table.add_column("Estado", style="bold yellow", width=20, justify="center")

        # Estado de configuración con mejores visuales
        api_status = "[green]✅ Configurado[/green]" if os.getenv('GOOGLE_API_KEY') else "[red]❌ Falta API Key[/red]"
        carpeta_status = f"[green]📁 Seleccionada[/green]" if self.carpeta_actual else "[red]❌ No seleccionada[/red]"

        # Filas del menú con colores vibrantes
        table.add_row("[bold bright_cyan]1[/bold bright_cyan]", "[cyan]🗂️  Seleccionar carpeta de PDFs[/cyan]", carpeta_status)
        table.add_row("[bold bright_cyan]2[/bold bright_cyan]", "[blue]🔍 Clasificar PDFs únicamente[/blue]", "")
        table.add_row("[bold bright_cyan]3[/bold bright_cyan]", "[green]🗂️  Clasificar y organizar automáticamente[/green]", "[yellow]⭐ Recomendado[/yellow]")
        table.add_row("[bold bright_cyan]4[/bold bright_cyan]", "[bright_magenta]📂 Recolectar PDFs recursivamente[/bright_magenta]", "[bright_green]🚀 Nuevo[/bright_green]")
        table.add_row("[bold bright_cyan]5[/bold bright_cyan]", "[magenta]📊 Ver resultados anteriores[/magenta]", "")
        table.add_row("[bold bright_cyan]6[/bold bright_cyan]", "[yellow]⚙️  Configuración avanzada[/yellow]", api_status)
        table.add_row("[bold bright_cyan]7[/bold bright_cyan]", "[white]❓ Ayuda y ejemplos[/white]", "")
        table.add_row("", "", "")  # Separador
        table.add_row("[bold red]0[/bold red]", "[red]🚪 Salir[/red]", "")

        # Panel principal con gradientes
        panel = Panel(
            table,
            title="[bold white on bright_blue] 📋 MENÚ PRINCIPAL 📋 [/bold white on bright_blue]",
            border_style="bright_magenta",
            padding=(1, 1),
            expand=False
        )

        self.console.print(panel)

        # Prompt estilizado
        return Prompt.ask(
            "\n[bold bright_yellow on blue] Selecciona una opción (0-7) [/bold bright_yellow on blue]",
            choices=["0", "1", "2", "3", "4", "5", "6", "7"],
            default="3",
            show_default=True
        )

    def _mostrar_menu_simple(self):
        """Menú principal simple."""
        print(Fore.GREEN + Style.BRIGHT + "📋 MENÚ PRINCIPAL")
        print(Fore.CYAN + "=" * 50)

        # Estado
        api_status = "✅" if os.getenv('GOOGLE_API_KEY') else "❌"
        carpeta_status = f"📁 {self.carpeta_actual}" if self.carpeta_actual else "❌"

        print(f"1. 🗂️  Seleccionar carpeta de PDFs          {carpeta_status}")
        print(f"2. 🔍 Clasificar PDFs únicamente")
        print(f"3. 🗂️  Clasificar y organizar automáticamente  ⭐ Recomendado")
        print(f"4. 📂 Recolectar PDFs recursivamente      🚀 Nuevo")
        print(f"5. 📊 Ver resultados anteriores")
        print(f"6. ⚙️  Configuración avanzada              {api_status}")
        print(f"7. ❓ Ayuda y ejemplos")
        print(f"0. 🚪 Salir")
        print(Fore.CYAN + "=" * 50)

        while True:
            opcion = input(Fore.YELLOW + "Selecciona una opción (0-7, default=3): ").strip()
            if not opcion:
                return "3"
            if opcion in ["0", "1", "2", "3", "4", "5", "6", "7"]:
                return opcion
            print(Fore.RED + "❌ Opción inválida. Intenta de nuevo.")

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
        # Tabla de estadísticas con diseño mejorado
        results_table = Table(
            show_header=False,
            box=box.DOUBLE_EDGE,
            border_style="bright_green",
            padding=(0, 2)
        )
        results_table.add_column("Métrica", style="bold bright_cyan", width=35)
        results_table.add_column("Valor", style="bold bright_white", width=15, justify="center")

        # Datos principales con colores
        results_table.add_row("[cyan]📁 Archivos totales[/cyan]", f"[bright_white]{stats['total_files']}[/bright_white]")
        results_table.add_row("[green]✅ Procesados exitosamente[/green]", f"[bright_green]{stats['processed']}[/bright_green]")
        results_table.add_row("[red]❌ Errores[/red]", f"[bright_red]{stats['errors']}[/bright_red]")

        # Tasa de éxito con color condicional
        success_rate = stats['success_rate']
        success_color = "bright_green" if success_rate >= 90 else "yellow" if success_rate >= 70 else "red"
        results_table.add_row("[blue]📊 Tasa de éxito[/blue]", f"[{success_color}]{success_rate:.1f}%[/{success_color}]")

        if 'organization' in stats:
            org_stats = stats['organization']
            # Línea separadora visual
            results_table.add_row("[dim]" + "─" * 35 + "[/dim]", "[dim]" + "─" * 15 + "[/dim]")
            results_table.add_row("[magenta]🗂️ Organizados por tema[/magenta]", f"[bright_magenta]{org_stats['successfully_organized']}[/bright_magenta]")
            results_table.add_row("[yellow]❓ Movidos a 'no_clasificados'[/yellow]", f"[bright_yellow]{org_stats['moved_to_unclassified']}[/bright_yellow]")
            results_table.add_row("[blue]📁 Carpetas creadas[/blue]", f"[bright_blue]{org_stats['folders_created']}[/bright_blue]")

        # Panel de resultados con efectos visuales
        panel = Panel(
            results_table,
            title="[bold white on green] 🎉 RESULTADOS DE LA CLASIFICACIÓN 🎉 [/bold white on green]",
            border_style="bright_green",
            padding=(1, 2)
        )

        # Línea decorativa superior
        decorative_line = "▓" * 80
        self.console.print(f"\n[bright_green]{decorative_line}[/bright_green]")
        self.console.print(panel)

        if 'organized_folder' in stats:
            # Panel adicional para la carpeta de resultados
            folder_panel = Panel(
                f"[bold bright_blue]📂 Archivos organizados en: {stats['organized_folder']}[/bold bright_blue]",
                border_style="bright_blue",
                padding=(0, 1)
            )
            self.console.print(folder_panel)

        # Panel informativo sobre los logs de API
        if 'log_files' in stats:
            log_info = stats['log_files']
            log_content = (
                f"[bold cyan]📋 LOGS DETALLADOS GENERADOS:[/bold cyan]\n"
                f"[green]• {log_info['api_log']}[/green] - Log detallado de todos los requests a la API\n"
                f"[blue]• {log_info['general_log']}[/blue] - Log general del proceso de clasificación\n"
                f"[dim]• Sesión: {log_info['session_timestamp']}[/dim]\n\n"
                f"[yellow]💡 Revisa {log_info['api_log']} para ver qué archivos dieron error en las consultas a la API[/yellow]"
            )
        else:
            log_content = (
                "[bold cyan]📋 LOGS DETALLADOS GENERADOS:[/bold cyan]\n"
                "[green]• api_requests_YYYYMMDD_HHMMSS.log[/green] - Log detallado de todos los requests a la API\n"
                "[blue]• pdf_classifier_YYYYMMDD_HHMMSS.log[/blue] - Log general del proceso de clasificación\n\n"
                "[yellow]💡 Los logs se guardan con timestamp para diferenciar cada sesión[/yellow]"
            )

        log_panel = Panel(
            log_content,
            title="[bold magenta] 📝 INFORMACIÓN DE LOGS [/bold magenta]",
            border_style="bright_yellow",
            padding=(0, 1)
        )
        self.console.print(log_panel)

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
            print(f"📁 Carpetas creadas: {org_stats['folders_created']}")

        if 'organized_folder' in stats:
            print(Fore.BLUE + f"\n📂 Archivos organizados en: {stats['organized_folder']}")

        # Información sobre logs
        print(Fore.YELLOW + "\n📋 LOGS DETALLADOS GENERADOS:")
        if 'log_files' in stats:
            log_info = stats['log_files']
            print(Fore.GREEN + f"• {log_info['api_log']} - Log detallado de todos los requests a la API")
            print(Fore.BLUE + f"• {log_info['general_log']} - Log general del proceso de clasificación")
            print(Fore.CYAN + f"• Sesión: {log_info['session_timestamp']}")
            print(Fore.YELLOW + f"💡 Revisa {log_info['api_log']} para ver qué archivos dieron error en las consultas a la API")
        else:
            print(Fore.GREEN + "• api_requests_YYYYMMDD_HHMMSS.log - Log detallado de todos los requests a la API")
            print(Fore.BLUE + "• pdf_classifier_YYYYMMDD_HHMMSS.log - Log general del proceso de clasificación")
            print(Fore.YELLOW + "💡 Los logs se guardan con timestamp para diferenciar cada sesión")

    def mostrar_ayuda(self):
        """Muestra la ayuda del programa."""
        if RICH_AVAILABLE:
            # Crear múltiples paneles para mejor organización visual

            # Panel de preparación
            prep_panel = Panel(
                """[bold bright_cyan]1. Preparación:[/bold bright_cyan]
   [green]•[/green] Coloca tus archivos PDF en una carpeta
   [green]•[/green] Asegúrate de tener conexión a internet
   [green]•[/green] Verifica que tu API Key esté configurada""",
                title="[bold yellow on blue] 🛠️ PREPARACIÓN [/bold yellow on blue]",
                border_style="bright_cyan",
                padding=(0, 1)
            )

            # Panel de proceso
            process_panel = Panel(
                """[bold bright_magenta]2. Proceso de clasificación:[/bold bright_magenta]
   [yellow]•[/yellow] El sistema analiza las primeras 20 páginas de cada PDF
   [yellow]•[/yellow] Utiliza Google Gemini AI para clasificar el contenido
   [yellow]•[/yellow] Genera una jerarquía de 3 niveles: General > Subtema > Específico""",
                title="[bold white on magenta] 🤖 PROCESO IA [/bold white on magenta]",
                border_style="bright_magenta",
                padding=(0, 1)
            )

            # Panel de organización
            org_panel = Panel(
                """[bold bright_green]3. Organización automática:[/bold bright_green]
   [cyan]•[/cyan] Crea carpetas por tema automáticamente
   [cyan]•[/cyan] Copia los PDFs a sus carpetas correspondientes
   [cyan]•[/cyan] Los archivos problemáticos van a 'no_clasificados'""",
                title="[bold black on green] 📁 ORGANIZACIÓN [/bold black on green]",
                border_style="bright_green",
                padding=(0, 1)
            )

            # Panel de resultados
            results_panel = Panel(
                """[bold bright_blue]4. Resultados:[/bold bright_blue]
   [magenta]•[/magenta] Archivos JSON y CSV con la clasificación
   [magenta]•[/magenta] Logs detallados del proceso
   [magenta]•[/magenta] Estructura de carpetas organizada""",
                title="[bold white on blue] 📊 RESULTADOS [/bold white on blue]",
                border_style="bright_blue",
                padding=(0, 1)
            )

            # Panel de recolección recursiva
            recursive_panel = Panel(
                """[bold bright_yellow]📂 RECOLECCIÓN RECURSIVA (NUEVO):[/bold bright_yellow]
   [cyan]•[/cyan] Busca PDFs en TODAS las subcarpetas automáticamente
   [cyan]•[/cyan] Copia todos los PDFs a una carpeta única
   [cyan]•[/cyan] Mantiene registro completo de ubicaciones originales
   [cyan]•[/cyan] Ideal para preparar bibliotecas dispersas antes del análisis
   [cyan]•[/cyan] NO analiza automáticamente (solo recolecta y organiza)""",
                title="[bold white on bright_yellow] 🚀 RECOLECCIÓN RECURSIVA [/bold white on bright_yellow]",
                border_style="bright_yellow",
                padding=(0, 1)
            )

            # Panel de consejos
            tips_panel = Panel(
                """[bold bright_red]💡 CONSEJOS IMPORTANTES:[/bold bright_red]
   [bright_yellow]🎯[/bright_yellow] Usa lotes de 3-7 archivos para mejor rendimiento
   [bright_yellow]📄[/bright_yellow] Los PDFs deben tener texto extraíble (no solo imágenes)
   [bright_yellow]🎯[/bright_yellow] La clasificación mejora con PDFs de contenido claro y específico
   [bright_yellow]⚡[/bright_yellow] Procesa en horarios de menor tráfico para evitar límites de API
   [bright_yellow]📂[/bright_yellow] Usa recolección recursiva para carpetas con subcarpetas""",
                title="[bold white on red] 💡 CONSEJOS PRO [/bold white on red]",
                border_style="bright_red",
                padding=(0, 1)
            )

            # Panel principal que contiene todo
            main_help_panel = Panel(
                f"{prep_panel}\n{process_panel}\n{org_panel}\n{results_panel}\n{recursive_panel}\n{tips_panel}",
                title="[bold white on bright_blue] ❓ AYUDA Y GUÍA COMPLETA ❓ [/bold white on bright_blue]",
                border_style="bright_blue",
                padding=(1, 2)
            )

            self.console.print(main_help_panel)
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

    def recolectar_pdfs_recursivamente(self):
        """Recolecta PDFs de forma recursiva y los copia a una carpeta única."""
        try:
            # Solicitar carpeta raíz
            if RICH_AVAILABLE:
                self.console.print("\n[bold magenta]📂 RECOLECCIÓN RECURSIVA DE PDFs[/bold magenta]")
                self.console.print("[yellow]Esta opción busca PDFs en TODAS las subcarpetas y los copia a una carpeta única[/yellow]")
                carpeta_raiz = Prompt.ask("\n[cyan]Introduce la ruta de la carpeta raíz[/cyan]")
            else:
                print(Fore.MAGENTA + "\n📂 RECOLECCIÓN RECURSIVA DE PDFs")
                print(Fore.YELLOW + "Esta opción busca PDFs en TODAS las subcarpetas y los copia a una carpeta única")
                carpeta_raiz = input(Fore.CYAN + "\nIntroduce la ruta de la carpeta raíz: ")

            if not carpeta_raiz:
                return

            path = Path(carpeta_raiz).expanduser()
            if not path.exists() or not path.is_dir():
                if RICH_AVAILABLE:
                    self.console.print(f"[red]❌ La carpeta no existe: {path}[/red]")
                else:
                    print(Fore.RED + f"❌ La carpeta no existe: {path}")
                input("Presiona Enter para continuar...")
                return

            # Solicitar carpeta de destino
            if RICH_AVAILABLE:
                carpeta_destino = Prompt.ask("\n[green]Introduce la ruta de la carpeta destino[/green]", default="pdfs_recolectados")
            else:
                carpeta_destino = input(Fore.GREEN + "\nIntroduce la ruta de la carpeta destino (default=pdfs_recolectados): ") or "pdfs_recolectados"

            destino_path = Path(carpeta_destino).expanduser()

            # Crear carpeta destino si no existe
            destino_path.mkdir(parents=True, exist_ok=True)

            # Crear clasificador temporal solo para recolección
            temp_classifier = PDFClassifier()

            # Mostrar información del proceso
            if RICH_AVAILABLE:
                info_panel = Panel(
                    f"[cyan]📁 Carpeta raíz:[/cyan] {path}\n"
                    f"[green]📂 Carpeta destino:[/green] {destino_path}\n"
                    f"[yellow]🔍 Búsqueda:[/yellow] Recursiva en todas las subcarpetas\n"
                    f"[blue]💾 Acción:[/blue] Solo copia (sin análisis)",
                    title="[bold green]⚙️ CONFIGURACIÓN DE RECOLECCIÓN[/bold green]",
                    border_style="green"
                )
                self.console.print(info_panel)

                if not Confirm.ask("\n[yellow]¿Continuar con la recolección?[/yellow]", default=True):
                    return
            else:
                print(Fore.GREEN + "\n⚙️ CONFIGURACIÓN DE RECOLECCIÓN:")
                print(f"📁 Carpeta raíz: {path}")
                print(f"📂 Carpeta destino: {destino_path}")
                print("🔍 Búsqueda: Recursiva en todas las subcarpetas")
                print("💾 Acción: Solo copia (sin análisis)")

                continuar = input("\n¿Continuar? (S/n): ").lower()
                if continuar in ['n', 'no']:
                    return

            # Recolección de PDFs
            if RICH_AVAILABLE:
                self.console.print("\n[bold cyan]🔍 RECOLECTANDO PDFs RECURSIVAMENTE...[/bold cyan]")
            else:
                print(Fore.CYAN + Style.BRIGHT + "\n🔍 RECOLECTANDO PDFs RECURSIVAMENTE...")

            # Buscar todos los PDFs recursivamente
            pdf_files = list(path.rglob("*.pdf"))
            total_files = len(pdf_files)

            if total_files == 0:
                if RICH_AVAILABLE:
                    self.console.print("[yellow]📭 No se encontraron archivos PDF[/yellow]")
                else:
                    print(Fore.YELLOW + "📭 No se encontraron archivos PDF")
                input("Presiona Enter para continuar...")
                return

            if RICH_AVAILABLE:
                self.console.print(f"[green]📊 Encontrados {total_files} archivos PDF[/green]")
            else:
                print(Fore.GREEN + f"📊 Encontrados {total_files} archivos PDF")

            # Copiar archivos y crear mapeo
            copied_files = 0
            location_map = {}

            for pdf_file in pdf_files:
                try:
                    # Crear nombre único para evitar conflictos
                    relative_path = pdf_file.relative_to(path)
                    safe_name = str(relative_path).replace(os.sep, "_")

                    # Agregar numeración si el nombre ya existe
                    final_name = f"{copied_files:04d}_{safe_name}"
                    destino_file = destino_path / final_name

                    # Copiar el archivo
                    shutil.copy2(pdf_file, destino_file)

                    # Guardar mapeo de ubicación original
                    location_map[final_name] = {
                        'original_path': str(pdf_file),
                        'relative_path': str(relative_path),
                        'parent_folder': str(pdf_file.parent),
                        'original_name': pdf_file.name
                    }

                    copied_files += 1

                    if copied_files % 10 == 0:
                        if RICH_AVAILABLE:
                            self.console.print(f"[blue]📋 Copiados {copied_files}/{total_files} archivos...[/blue]")
                        else:
                            print(Fore.BLUE + f"📋 Copiados {copied_files}/{total_files} archivos...")

                except Exception as e:
                    if RICH_AVAILABLE:
                        self.console.print(f"[red]❌ Error copiando {pdf_file}: {e}[/red]")
                    else:
                        print(Fore.RED + f"❌ Error copiando {pdf_file}: {e}")
                    continue

            # Guardar mapeo en archivo JSON
            mapping_file = destino_path / "ubicaciones_originales.json"
            with open(mapping_file, 'w', encoding='utf-8') as f:
                json.dump(location_map, f, indent=2, ensure_ascii=False)

            # Mostrar resultados
            if RICH_AVAILABLE:
                results_panel = Panel(
                    f"[green]✅ Proceso completado exitosamente[/green]\n\n"
                    f"[cyan]📊 Archivos encontrados:[/cyan] {total_files}\n"
                    f"[green]📁 Archivos copiados:[/green] {copied_files}\n"
                    f"[blue]📂 Carpeta destino:[/blue] {destino_path}\n"
                    f"[yellow]🗺️  Mapeo guardado en:[/yellow] ubicaciones_originales.json\n\n"
                    f"[magenta]💡 Ahora puedes usar las opciones 2 o 3 del menú[/magenta]\n"
                    f"[magenta]   para clasificar los PDFs en: {destino_path}[/magenta]",
                    title="[bold green]🎉 RECOLECCIÓN COMPLETADA[/bold green]",
                    border_style="green"
                )
                self.console.print(results_panel)
            else:
                print(Fore.GREEN + Style.BRIGHT + "\n🎉 RECOLECCIÓN COMPLETADA")
                print(Fore.CYAN + "=" * 60)
                print(f"📊 Archivos encontrados: {total_files}")
                print(f"📁 Archivos copiados: {copied_files}")
                print(f"📂 Carpeta destino: {destino_path}")
                print(f"🗺️  Mapeo guardado en: ubicaciones_originales.json")
                print(Fore.MAGENTA + "\n💡 Ahora puedes usar las opciones 2 o 3 del menú")
                print(Fore.MAGENTA + f"   para clasificar los PDFs en: {destino_path}")

            # Actualizar carpeta actual para facilitar el siguiente paso
            self.carpeta_actual = str(destino_path)

        except Exception as e:
            if RICH_AVAILABLE:
                self.console.print(f"[red]❌ Error durante la recolección: {e}[/red]")
            else:
                print(Fore.RED + f"❌ Error durante la recolección: {e}")

        input("\nPresiona Enter para continuar...")

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
                self.ejecutar_clasificacion(organizar=False)

            elif opcion == "3":
                self.ejecutar_clasificacion(organizar=True)

            elif opcion == "4":
                self.recolectar_pdfs_recursivamente()

            elif opcion == "5":
                self.ver_resultados_anteriores()

            elif opcion == "6":
                self.configuracion_avanzada()

            elif opcion == "7":
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