import subprocess
import time
import os

# Procesos a detener
PROCESSES = [
    "chrome",
    "chromium",
    "chromedriver",
    "firefox",
    "geckodriver"
]

def kill_processes(process_name, force=False):
    """
    Mata procesos por nombre.
    Usa SIGTERM por defecto, SIGKILL si force=True
    """
    signal = "-9" if force else ""
    try:
        subprocess.run(
            ["pkill", signal, "-f", process_name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False
        )
    except Exception:
        pass


def clear_memory():
    """
    Libera caché de memoria (requiere root)
    """
    try:
        subprocess.run(
            ["sync"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        subprocess.run(
            ["bash", "-c", "echo 3 > /proc/sys/vm/drop_caches"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception:
        pass


def main():
    print("🔴 Deteniendo navegadores y drivers (SIGTERM)...")
    for proc in PROCESSES:
        kill_processes(proc, force=False)

    time.sleep(3)

    print("🔥 Forzando cierre de procesos restantes (SIGKILL)...")
    for proc in PROCESSES:
        kill_processes(proc, force=True)

    print("🧹 Liberando memoria...")
    clear_memory()

    print("✅ Limpieza completada")


if __name__ == "__main__":
    main()
