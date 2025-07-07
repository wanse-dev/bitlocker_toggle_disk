import subprocess
import os
import re
import ctypes

LETRA_UNIDAD = "E:"

def clear_console():
    """Limpia la consola en Windows."""
    os.system('cls')

def estado_disco():
    """
    Verifica el estado actual de BitLocker para la unidad especificada.
    Devuelve "bloqueado", "desbloqueado" o None si no se puede determinar el estado.
    """
    comando = f'manage-bde -status {LETRA_UNIDAD}'
    try:
        resultado = subprocess.run(comando, shell=True, capture_output=True, text=True, encoding='cp850', errors='replace')

        if resultado.returncode != 0:
            print(f"Error al consultar el estado del disco {LETRA_UNIDAD}:")
            print(resultado.stderr or resultado.stdout)
            return None

        salida = resultado.stdout.lower()
        salida_normalizada = re.sub(r'\s+', ' ', salida).strip()

        if "estado de bloqueo: bloqueado" in salida_normalizada:
            return "bloqueado"
        elif "estado de bloqueo: desbloqueado" in salida_normalizada:
            return "desbloqueado"
        elif "estado de conversión: sin cifrar" in salida_normalizada or "protección desactivada" in salida_normalizada:
            print(f"La unidad {LETRA_UNIDAD} no está cifrada con BitLocker.")
            return None
        else:
            print("No se pudo determinar el estado del disco (no se encontró 'bloqueado' ni 'desbloqueado' en la salida).")
            return None

    except subprocess.SubprocessError as e:
        print(f"Error al ejecutar el comando manage-bde: {str(e)}")
        return None
    except Exception as e:
        print(f"Excepción inesperada: {str(e)}")
        return None

def bloquear_disco():
    """Bloquea la unidad BitLocker especificada."""
    comando = f'manage-bde -lock {LETRA_UNIDAD} -forcedismount'
    try:
        resultado = subprocess.run(comando, shell=True, capture_output=True, text=True, encoding='cp850', errors='replace')
        if resultado.returncode == 0:
            print(f"\n✅ Disco {LETRA_UNIDAD} bloqueado correctamente.")
        else:
            print(f"\n❌ Error al bloquear el disco:\n{resultado.stderr}")
    except Exception as e:
        print(f"\n⚠️ Excepción al bloquear el disco: {str(e)}")

def desbloquear_disco():
    """
    Desbloquea la unidad BitLocker especificada en modo interactivo.
    Si la contraseña es incorrecta, permite reintentar.
    """
    while True:
        print(f"\n🔓 Se solicitará la contraseña de BitLocker para desbloquear la unidad {LETRA_UNIDAD}...")
        comando = f'manage-bde -unlock {LETRA_UNIDAD} -password'
        try:
            subprocess.run(comando, shell=True)
        except Exception as e:
            print(f"⚠️ Error al ejecutar el comando de desbloqueo: {str(e)}")
            break

        # Verificar si se desbloqueó con éxito
        estado = estado_disco()
        if estado == "desbloqueado":
            print(f"\n✅ El disco {LETRA_UNIDAD} se ha desbloqueado correctamente.")
            break
        else:
            print("\n❌ Contraseña incorrecta o desbloqueo fallido.")
            opcion = input("¿Querés intentar de nuevo? (s/n): ").lower()
            clear_console()
            if opcion != 's':
                break

def main():
    """Función principal del script."""
    try:
        if ctypes.windll.shell32.IsUserAnAdmin() == 0:
            print("⚠️ Este script debe ejecutarse como administrador.")
            input("Presiona Enter para salir...")
            clear_console()
            return
    except Exception:
        print("⚠️ No se pudo verificar si el script se ejecuta como administrador.")

    estado = estado_disco()
    if estado is None:
        print(f"\nNo se pudo determinar el estado del disco {LETRA_UNIDAD}.")
        input("Presiona Enter para salir...")
        clear_console()
        return

    print(f"\n📦 El disco {LETRA_UNIDAD} está actualmente: {estado.upper()}")

    if estado == "desbloqueado":
        opcion = input("¿Querés bloquearlo? (s/n): ").lower()
        clear_console()
        if opcion == 's':
            bloquear_disco()
    elif estado == "bloqueado":
        opcion = input("¿Querés desbloquearlo? (s/n): ").lower()
        clear_console()
        if opcion == 's':
            desbloquear_disco()

    input("\nPresiona Enter para salir...")
    clear_console()

if __name__ == "__main__":
    main()
