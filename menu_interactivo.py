#!/usr/bin/env python3
"""
MENÚ INTERACTIVO PARA CLASIFICADOR DE PDFs
==========================================
Interfaz colorida y atractiva para el clasificador de PDFs con DeepSeek.
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import json

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

# Importar nuestro clasificador
from pdf_classifier import PDFClassifier

class MenuColorido:
    def __init__(self):
        self.console = Console()
        self.classifier = None
        self.carpeta_actual = None

    def limpiar_pantalla(self):
        """Limpia la pantalla del terminal."""
        os.system('clear' if os.name == 'posix' else 'cls')

    def mostrar_banner(self):
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
                Text("\n🤖 Clasificador Inteligente de PDFs con DeepSeek", style="bold yellow") +
                Text("\n📚 Organiza automáticamente tus documentos por tema", style="italic green")
            ),
            box=box.DOUBLE,
            border_style="bright_blue",
            title="[bold red]🚀 BIENVENIDO 🚀[/bold red]",
            title_align="center"
        )

        self.console.print(panel)
        self.console.print()

    def mostrar_menu_principal(self):
        """Menú principal con Rich."""
        self.console.rule(Text("MENÚ PRINCIPAL", style="bold bright_blue"), style="bright_black")

        api_status = "API key configurada" if os.getenv('DEEPSEEK_API_KEY') else "API key pendiente"
        carpeta_status = f"Ruta seleccionada: {self.carpeta_actual}" if self.carpeta_actual else "Ruta no seleccionada"

        # Indicadores de requisitos para las opciones
        req_clasificacion = "⚠️ Requiere API key DeepSeek" if not os.getenv('DEEPSEEK_API_KEY') else ""

        opciones = [
            ("1", "Seleccionar carpeta de PDFs", carpeta_status, "cyan"),
            ("2", "Consolidar PDFs recursivamente", "No requiere API", "magenta"),
            ("3", "Clasificar PDFs únicamente", req_clasificacion, "yellow" if req_clasificacion else ""),
            ("4", "Clasificar y organizar automáticamente", req_clasificacion or "Recomendado", "yellow" if req_clasificacion else "green"),
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

        self.console.rule(style="bright_black")

        return Prompt.ask(
            "\n[bold yellow]Selecciona una opción[/bold yellow]",
            choices=["0", "1", "2", "3", "4", "5", "6", "7", "8"],
            default="4"
        )

    def seleccionar_carpeta(self):
        """Permite al usuario seleccionar una carpeta de PDFs."""
        self.console.print("\n[bold blue]📁 SELECCIÓN DE CARPETA[/bold blue]")
        while True:
            carpeta = Prompt.ask("\n[yellow]Introduce la ruta de la carpeta con PDFs[/yellow]")
            if not carpeta:
                continue

            path = Path(carpeta).expanduser()

            if not path.exists():
                self.console.print(f"[red]❌ La carpeta no existe: {path}[/red]")
                continue

            if not path.is_dir():
                self.console.print(f"[red]❌ No es una carpeta válida: {path}[/red]")
                continue

            # Contar PDFs
            pdfs = list(path.glob("*.pdf"))

            if not pdfs:
                self.console.print(f"[red]❌ No se encontraron archivos PDF en: {path}[/red]")
                continue

            self.carpeta_actual = str(path)

            self.console.print(f"\n[green]✅ Carpeta seleccionada: {path}[/green]")
            self.console.print(f"[blue]📊 Se encontraron {len(pdfs)} archivos PDF[/blue]")
            input("\nPresiona Enter para continuar...")
            break

    def mostrar_progreso_clasificacion(self, total_archivos, batch_size):
        """Muestra una barra de progreso durante la clasificación."""
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
            self.console.print("[red]❌ Primero debes seleccionar una carpeta de PDFs[/red]")
            input("Presiona Enter para continuar...")
            return

        if not os.getenv('DEEPSEEK_API_KEY'):
            self.console.print("[red]❌ API Key de DeepSeek no configurada[/red]")
            input("Presiona Enter para continuar...")
            return

        try:
            # Crear clasificador
            batch_size = int(Prompt.ask("\n[yellow]Tamaño del lote[/yellow]", default="5"))
            self.classifier = PDFClassifier(batch_size=batch_size)

            # Mostrar configuración
            config_table = Table(show_header=False, box=box.SIMPLE)
            config_table.add_column("Setting", style="cyan")
            config_table.add_column("Value", style="white")
            config_table.add_row("📁 Carpeta", self.carpeta_actual)
            config_table.add_row("🔄 Modo", "Clasificar y Organizar" if organizar else "Solo Clasificar")
            config_table.add_row("📦 Lote", str(batch_size))

            self.console.print(Panel(config_table, title="[bold green]⚙️ CONFIGURACIÓN[/bold green]"))

            if not Confirm.ask("\n[yellow]¿Continuar con la clasificación?[/yellow]", default=True):
                return
            # Ejecutar clasificación
            self.console.print("\n[bold green]🚀 INICIANDO CLASIFICACIÓN...[/bold green]")
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
            self.console.print(f"[red]❌ Error durante la clasificación: {e}[/red]")
        input("\nPresiona Enter para continuar...")

    def mostrar_resultados(self, stats):
        """Muestra los resultados de la clasificación de forma visual."""
        self._mostrar_resultados_rich(stats)
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

    def mostrar_ayuda(self):
        """Muestra la ayuda del programa."""
        help_text = """
[bold cyan]🔍 CÓMO USAR EL CLASIFICADOR[/bold cyan]

[bold yellow]1. Preparación:[/bold yellow]
   • Coloca tus archivos PDF en una carpeta
   • Asegúrate de tener conexión a internet
   • Verifica que tu API Key de DeepSeek esté configurada

[bold yellow]2. Proceso de clasificación:[/bold yellow]
   • El sistema analiza las primeras 20 páginas de cada PDF
   • Utiliza la API de DeepSeek para clasificar el contenido
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

        input("\nPresiona Enter para continuar...")

    def consolidar_pdfs_recursivamente(self):
        """Consolida PDFs de múltiples carpetas en una sola."""
        self.console.print("\n[bold blue]📦 CONSOLIDACIÓN RECURSIVA DE PDFs[/bold blue]")

        # Usar carpeta actual si existe, o pedir una nueva
        if self.carpeta_actual:
            self.console.print(f"\n[cyan]📁 Carpeta seleccionada: {self.carpeta_actual}[/cyan]")
            usar_actual = Confirm.ask(
                "[yellow]¿Usar esta carpeta para consolidación?[/yellow]",
                default=True
            )
            if usar_actual:
                carpeta_origen = self.carpeta_actual
            else:
                carpeta_origen = Prompt.ask("\n[yellow]Carpeta raíz para buscar PDFs recursivamente[/yellow]")
        else:
            carpeta_origen = Prompt.ask("\n[yellow]Carpeta raíz para buscar PDFs recursivamente[/yellow]")

        if not carpeta_origen:
            return

        carpeta_origen_path = Path(carpeta_origen).expanduser()

        if not carpeta_origen_path.exists():
            self.console.print(f"[red]❌ La carpeta no existe: {carpeta_origen_path}[/red]")
            input("Presiona Enter para continuar...")
            return

        # Previsualizar archivos encontrados
        pdf_files = list(carpeta_origen_path.rglob("*.pdf"))

        if not pdf_files:
            self.console.print(f"[yellow]⚠️  No se encontraron archivos PDF en: {carpeta_origen_path}[/yellow]")
            input("Presiona Enter para continuar...")
            return

        # Mostrar previsualización
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
        try:
            # Ejecutar consolidación
            self.console.print("\n[bold green]🚀 INICIANDO CONSOLIDACIÓN...[/bold green]")
            classifier = PDFClassifier()

            stats = classifier.consolidate_pdfs_recursively(
                source_folder=str(carpeta_origen_path),
                consolidated_folder=carpeta_destino if carpeta_destino else None
            )

            # Mostrar resultados
            self.mostrar_resultados_consolidacion(stats)

            # Actualizar carpeta actual con la carpeta consolidada
            # para que las opciones siguientes (3 y 4) puedan usarla
            self.carpeta_actual = stats['consolidated_folder']
            self.console.print(f"\n[bold green]✅ La carpeta consolidada se ha establecido como carpeta actual[/bold green]")
            self.console.print(f"[cyan]💡 Ahora puedes usar las opciones 3 o 4 para clasificar estos PDFs[/cyan]")

        except Exception as e:
            self.console.print(f"[red]❌ Error durante la consolidación: {e}[/red]")
        input("\nPresiona Enter para continuar...")

    def restaurar_consolidacion(self):
        """Restaura archivos desde una consolidación."""
        self.console.print("\n[bold blue]🔄 RESTAURAR DESDE CONSOLIDACIÓN[/bold blue]")

        # Usar carpeta actual si existe, o pedir una nueva
        if self.carpeta_actual:
            self.console.print(f"\n[cyan]📁 Carpeta seleccionada: {self.carpeta_actual}[/cyan]")
            usar_actual = Confirm.ask(
                "[yellow]¿Restaurar desde esta carpeta consolidada?[/yellow]",
                default=True
            )
            if usar_actual:
                carpeta_consolidada = self.carpeta_actual
            else:
                carpeta_consolidada = Prompt.ask("\n[yellow]Carpeta con archivos consolidados[/yellow]")
        else:
            carpeta_consolidada = Prompt.ask("\n[yellow]Carpeta con archivos consolidados[/yellow]")

        if not carpeta_consolidada:
            return

        carpeta_path = Path(carpeta_consolidada).expanduser()

        if not carpeta_path.exists():
            self.console.print(f"[red]❌ La carpeta no existe: {carpeta_path}[/red]")
            input("Presiona Enter para continuar...")
            return

        # Verificar archivo de registro
        registry_file = carpeta_path / "registry_origenes.json"

        if not registry_file.exists():
            self.console.print(f"[red]❌ No se encontró archivo de registro en: {registry_file}[/red]")
            input("Presiona Enter para continuar...")
            return

        try:
            # Leer información de consolidación
            with open(registry_file, 'r', encoding='utf-8') as f:
                registry_data = json.load(f)

            consolidation_info = registry_data.get("consolidation_info", {})
            file_origins = registry_data.get("file_origins", {})

            # Mostrar información
            info_table = Table(show_header=False, box=box.SIMPLE)
            info_table.add_column("Info", style="cyan")
            info_table.add_column("Valor", style="white")

            info_table.add_row("📁 Carpeta original", consolidation_info.get("source_folder", "N/A"))
            info_table.add_row("📦 Fecha consolidación", consolidation_info.get("consolidation_date", "N/A"))
            info_table.add_row("📄 Total archivos", str(len(file_origins)))

            self.console.print(Panel(info_table, title="[bold yellow]📋 Información de Consolidación[/bold yellow]"))

            if not Confirm.ask("\n[yellow]¿Confirmar restauración?[/yellow]", default=False):
                return
            # Ejecutar restauración
            self.console.print("\n[bold green]🔄 INICIANDO RESTAURACIÓN...[/bold green]")
            classifier = PDFClassifier()
            stats = classifier.restore_from_consolidation(str(carpeta_path))

            # Mostrar resultados
            self.console.print(f"\n[green]✅ Restauración completada: {stats['successfully_restored']}/{stats['total_to_restore']}[/green]")
        except Exception as e:
            self.console.print(f"[red]❌ Error durante la restauración: {e}[/red]")
        input("\nPresiona Enter para continuar...")

    def mostrar_resultados_consolidacion(self, stats):
        """Muestra los resultados de la consolidación."""
        self.console.print("\n" + "="*60)
        self.console.print("[bold green]RESULTADOS DE LA CONSOLIDACIÓN[/bold green]")
        self.console.print("="*60)

        self.console.print(f"[cyan]Archivos encontrados:[/cyan]        [white]{stats['total_found']}[/white]")
        self.console.print(f"[green]Archivos movidos:[/green]           [white]{stats['successfully_moved']}[/white]")
        self.console.print(f"[yellow]Duplicados manejados:[/yellow]       [white]{stats['duplicates_handled']}[/white]")
        self.console.print(f"[blue]Carpetas procesadas:[/blue]         [white]{stats['folders_processed']}[/white]")
        self.console.print(f"[magenta]Carpetas vacías eliminadas:[/magenta] [white]{stats.get('empty_folders_removed', 0)}[/white]")

        errores = stats['errors']
        error_color = "red" if errores > 0 else "green"
        self.console.print(f"[{error_color}]Errores:[/{error_color}]                      [white]{errores}[/white]")

        self.console.print("="*60)
        self.console.print(f"[bold blue]Archivos consolidados en:[/bold blue] [white]{stats['consolidated_folder']}[/white]")

    def ejecutar(self):
        """Ejecuta el menú principal del programa."""
        while True:
            self.limpiar_pantalla()
            self.mostrar_banner()

            opcion = self.mostrar_menu_principal()

            if opcion == "0":
                self.console.print("\n[bold blue]👋 ¡Gracias por usar el Clasificador de PDFs![/bold blue]")
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
            self.console.print("[yellow]📭 No se encontraron resultados anteriores[/yellow]")
            input("Presiona Enter para continuar...")
            return

        json_files = list(results_dir.glob("clasificacion_*.json"))

        if not json_files:
            self.console.print("[yellow]📭 No se encontraron archivos de clasificación[/yellow]")
            input("Presiona Enter para continuar...")
            return

        # Mostrar archivos disponibles
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
        input("\nPresiona Enter para continuar...")

    def configuracion_avanzada(self):
        """Muestra opciones de configuración avanzada."""
        self.console.print("\n[bold blue]⚙️ CONFIGURACIÓN AVANZADA[/bold blue]")

        config_table = Table(show_header=False, box=box.SIMPLE)
        config_table.add_column("Setting", style="cyan")
        config_table.add_column("Value", style="white")

        api_key = os.getenv('DEEPSEEK_API_KEY', 'No configurada')
        api_status = "✅ Configurada" if api_key != 'No configurada' else "❌ No configurada"

        config_table.add_row("🔑 API Key", api_status)
        config_table.add_row("📁 Carpeta actual", self.carpeta_actual or "No seleccionada")
        config_table.add_row("📂 Directorio de resultados", "results/")

        self.console.print(config_table)
        input("\nPresiona Enter para continuar...")


def main():
    """Función principal del menú interactivo."""
    try:
        menu = MenuColorido()
        menu.ejecutar()
    except KeyboardInterrupt:
        console = Console()
        console.print("\n\n[bold blue]👋 ¡Hasta luego![/bold blue]")
    except Exception as e:
        console = Console()
        console.print(f"\n[red]❌ Error inesperado: {e}[/red]" )


if __name__ == "__main__":
    main()
