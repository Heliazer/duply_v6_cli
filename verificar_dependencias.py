#!/usr/bin/env python3
"""
VERIFICADOR DE DEPENDENCIAS
===========================
Script para verificar que todas las dependencias están correctamente instaladas.
"""

import sys
import importlib.util
from pathlib import Path

def verificar_modulo(nombre_modulo, nombre_paquete=None, requerido=True):
    """
    Verifica si un módulo está instalado.

    Args:
        nombre_modulo: Nombre del módulo a importar
        nombre_paquete: Nombre del paquete para instalación (si es diferente)
        requerido: Si el módulo es requerido o opcional

    Returns:
        bool: True si está instalado, False si no
    """
    try:
        spec = importlib.util.find_spec(nombre_modulo)
        if spec is not None:
            print(f"✅ {nombre_modulo:<20} - Instalado")
            return True
        else:
            status = "❌ REQUERIDO" if requerido else "⚠️  Opcional"
            paquete = nombre_paquete or nombre_modulo
            print(f"{status} {nombre_modulo:<15} - pip install {paquete}")
            return False
    except Exception as e:
        status = "❌ ERROR" if requerido else "⚠️  Error"
        print(f"{status} {nombre_modulo:<18} - Error: {e}")
        return False

def main():
    """Función principal de verificación."""
    print("🔍 VERIFICANDO DEPENDENCIAS DEL CLASIFICADOR DE PDFs")
    print("=" * 60)

    # Dependencias principales (requeridas)
    print("\n📦 DEPENDENCIAS PRINCIPALES:")
    dependencias_principales = [
        ("requests", "requests"),
        ("fitz", "PyMuPDF"),
        ("dotenv", "python-dotenv"),
    ]

    principales_ok = True
    for modulo, paquete in dependencias_principales:
        if not verificar_modulo(modulo, paquete, requerido=True):
            principales_ok = False

    # Dependencias para interfaz visual (opcionales)
    print("\n🎨 DEPENDENCIAS PARA INTERFAZ VISUAL:")
    dependencias_visuales = [
        ("colorama", "colorama"),
        ("rich", "rich"),
    ]

    visuales_ok = True
    for modulo, paquete in dependencias_visuales:
        if not verificar_modulo(modulo, paquete, requerido=False):
            visuales_ok = False

    # Dependencias estándar de Python
    print("\n🐍 MÓDULOS ESTÁNDAR DE PYTHON:")
    modulos_estandar = [
        "os", "sys", "json", "time", "csv", "logging",
        "shutil", "re", "pathlib", "datetime", "argparse"
    ]

    for modulo in modulos_estandar:
        verificar_modulo(modulo, requerido=True)

    # Resumen
    print("\n" + "=" * 60)
    print("📋 RESUMEN:")

    if principales_ok:
        print("✅ Dependencias principales: TODAS INSTALADAS")
        print("   → El clasificador básico funcionará correctamente")
    else:
        print("❌ Dependencias principales: FALTAN ALGUNAS")
        print("   → Ejecuta: pip install -r requirements-minimal.txt")

    if visuales_ok:
        print("✅ Dependencias visuales: TODAS INSTALADAS")
        print("   → El menú interactivo colorido estará disponible")
    else:
        print("⚠️  Dependencias visuales: FALTAN ALGUNAS")
        print("   → Para interfaz completa: pip install -r requirements.txt")
        print("   → El programa funcionará en modo básico")

    # Verificar archivos de configuración
    print("\n🔧 CONFIGURACIÓN:")
    env_file = Path(".env")
    if env_file.exists():
        print("✅ Archivo .env encontrado")

        # Verificar API key
        try:
            with open(env_file, 'r') as f:
                content = f.read()
                if "DEEPSEEK_API_KEY=" in content and len(content.split("DEEPSEEK_API_KEY=")[1].split()[0]) > 10:
                    print("✅ API Key configurada en .env")
                else:
                    print("⚠️  API Key en .env parece incompleta")
        except:
            print("⚠️  No se pudo verificar API Key en .env")
    else:
        print("❌ Archivo .env no encontrado")
        print("   → Crea un archivo .env con tu DEEPSEEK_API_KEY")

    # Recomendaciones
    print("\n💡 RECOMENDACIONES:")
    if not principales_ok:
        print("1. Instala las dependencias principales primero")
        print("2. Configura tu API Key de DeepSeek")
        print("3. Prueba el clasificador básico")
    elif not visuales_ok:
        print("1. Considera instalar las dependencias visuales para mejor experiencia")
        print("2. Usa 'python main.py' para menú interactivo")
    else:
        print("1. ¡Todo está listo! Usa 'python main.py' para empezar")
        print("2. El menú interactivo estará disponible con todas las funciones")

    return 0 if principales_ok else 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n👋 Verificación interrumpida")
        sys.exit(0)
