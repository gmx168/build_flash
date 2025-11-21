import os
import subprocess
import sys
import time
import serial.tools.list_ports
from colorama import init, Fore
from datetime import datetime

init(autoreset=True)

# ============================================
# KONFIGURACJA zmienic sciezki na takie jak na swojej instalacji, miejsce CLI, ESPTOOL, BOOT_APP0
# ============================================
ARDUINO_CLI = r"C:\Program Files\Arduino CLI\arduino-cli.exe"
ESPTOOL = r"C:\Users\Grzeg\AppData\Local\Arduino15\packages\esp32\tools\esptool_py\5.1.0\esptool.exe"
BOARD = "esp32:esp32:esp32"
DEFAULT_PARTITION = "minimal"
DEFAULT_FLASH_SIZE = "4MB"
BAUD = 921600
BOOT_APP0 = r"C:\Users\Grzeg\AppData\Local\Arduino15\packages\esp32\hardware\esp32\3.3.3\tools\partitions\boot_app0.bin"
LOG_FILE = "bf_log.txt"


# ============================================
# LOGOWANIE gdzie mamy zrzucic pliki z logiem
# ============================================
def log_to_file(message):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ")
    with open(LOG_FILE, "a", encoding="utf-8") as log:
        log.write(timestamp + message + "\n")


def run(cmd, cwd=None):
    """Uruchamia polecenie systemowe z logowaniem"""
    print(Fore.CYAN + f"\n[CMD] {cmd}\n")
    log_to_file(f"[CMD] {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd)
    if result.returncode != 0:
        log_to_file(f"❌ Błąd wykonania: {cmd}")
        print(Fore.RED + f"❌ Błąd wykonania: {cmd}")
        sys.exit(1)
    else:
        log_to_file("✅ Sukces.")


# ============================================
# FUNKCJE POMOCNICZE
# ============================================
def find_ino_file(path):
    for file in os.listdir(path):
        if file.endswith(".ino"):
            print(Fore.GREEN + f"✅ Znaleziono plik: {file}")
            return os.path.join(path, file)
    print(Fore.RED + "❌ Nie znaleziono pliku .ino!")
    sys.exit(1)


def parse_directives(ino_path):
    """Parsuje komentarze konfiguracyjne"""
    cfg = {
        "PART": DEFAULT_PARTITION,
        "COM": None,
        "ERASE": False,
        "PSRAM": None,
        "FLASH-SIZE": DEFAULT_FLASH_SIZE,
    }
    try:
        with open(ino_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("//PART="):
                    cfg["PART"] = line.split("=")[1].strip()
                elif line.startswith("//COM="):
                    cfg["COM"] = "COM" + line.split("=")[1].strip()
                elif line.startswith("//ERASE="):
                    cfg["ERASE"] = line.split("=")[1].strip().lower() == "true"
                elif line.startswith("//PSRAM="):
                    cfg["PSRAM"] = line.split("=")[1].strip().upper()
                elif line.startswith("//FLASH-SIZE="):
                    val = line.split("=")[1].strip()
                    if val.isdigit():
                        cfg["FLASH-SIZE"] = f"{val}MB"
    except Exception as e:
        print(Fore.YELLOW + f"⚠️ Nie udało się odczytać konfiguracji z .ino: {e}")
    return cfg


def detect_port():
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        if any(x in p.description for x in ["CP210", "CH340", "USB-SERIAL", "Silicon Labs"]):
            print(Fore.GREEN + f"✅ Wykryto port ESP32: {p.device}")
            return p.device
    if ports:
        print(Fore.YELLOW + f"⚠️ Używam pierwszego dostępnego portu: {ports[0].device}")
        return ports[0].device
    print(Fore.RED + "❌ Nie wykryto żadnego urządzenia ESP32!")
    sys.exit(1)


def find_build_dir():
    base = os.path.join(os.environ["LOCALAPPDATA"], "arduino", "sketches")
    dirs = [os.path.join(base, d) for d in os.listdir(base) if os.path.isdir(os.path.join(base, d))]
    newest = max(dirs, key=os.path.getmtime)
    print(Fore.CYAN + f"📁 Build folder: {newest}")
    return newest


# ============================================
# GŁÓWNE FUNKCJE
# ============================================
def compile_sketch(project_dir, part, psram):
    psram_flag = f":PSRAM={psram}" if psram else ""
    print(Fore.CYAN + f"🧱 Kompilacja szkicu... (partycja: {part}, PSRAM: {psram or 'AUTO'})")
# Naprawiony FQBN – Arduino CLI nie akceptuje samego PartitionScheme
    fqbn = f'{BOARD}:FlashMode=qio,FlashFreq=80,PartitionScheme={part}'
    if psram:
    	fqbn += f',PSRAM={psram}'
    cmd = f'"{ARDUINO_CLI}" compile --fqbn "{fqbn}" "{project_dir}"'
    run(cmd)


def merge_bin(build_dir, ino_name, flash_size="4MB"):
    """Tworzy merged.bin dynamicznie na podstawie nazwy pliku .ino (z rozszerzeniem w nazwach plików binarnych)."""
    print(Fore.CYAN + "🔗 Tworzenie merged.bin...")

    base_name = os.path.splitext(ino_name)[0]
    build_sub = os.path.join(build_dir, "build", "esp32.esp32.esp32")
    if not os.path.exists(build_sub):
        build_sub = build_dir

    # ✅ poprawka: uwzględnij .ino w nazwach
    boot = os.path.join(build_sub, f"{base_name}.ino.bootloader.bin")
    part = os.path.join(build_sub, f"{base_name}.ino.partitions.bin")
    app = os.path.join(build_sub, f"{base_name}.ino.bin")
    merged = os.path.join(build_dir, f"{base_name}_merged.bin")

    # 🧩 Sprawdzenie plików
    for f in [boot, part, app, BOOT_APP0]:
        if not os.path.exists(f):
            print(Fore.RED + f"❌ Brak pliku: {f}")
            sys.exit(1)

    # 🔨 Tworzenie merged.bin
    cmd = (
        f'"{ESPTOOL}" --chip esp32 merge-bin -o "{merged}" --flash-size {flash_size} '
        f'0x1000 "{boot}" 0x8000 "{part}" 0xe000 "{BOOT_APP0}" 0x10000 "{app}"'
    )
    run(cmd)

    if os.path.exists(merged):
        print(Fore.GREEN + f"✅ Utworzono plik: {merged}")
    else:
        print(Fore.RED + "❌ Nie udało się utworzyć merged.bin.")
        sys.exit(1)

    return merged





def erase_flash(port):
    print(Fore.YELLOW + f"🧨 Kasowanie flasha ({port})...")
    run(f'"{ESPTOOL}" --chip esp32 --port {port} erase_flash')


def flash_device(port, merged):
    print(Fore.CYAN + f"⚡ Flashowanie {port}...")
    run(f'"{ESPTOOL}" --chip esp32 --port {port} --baud {BAUD} write_flash 0x0 "{merged}"')


def flash_spiffs(port, build_dir, ino_name):
    base = os.path.splitext(ino_name)[0]
    spiffs = os.path.join(build_dir, f"{base}.spiffs.bin")

    if not os.path.exists(spiffs):
        print(Fore.YELLOW + "⚠️ Brak SPIFFS — pomijam.")
        return

    print(Fore.CYAN + "💾 Wgrywanie SPIFFS...")
    run(f'"{ESPTOOL}" --chip esp32 --port {port} --baud {BAUD} write_flash 0x290000 "{spiffs}"')
    print(Fore.GREEN + "✅ SPIFFS wgrane.")


# ============================================
# ENTRY POINT
# ============================================
def main():
    print(Fore.GREEN + "🚀 YO-RADIO WRAPPER START")
    log_to_file("\n================= NEW SESSION =================")

    start = time.time()
    project_dir = os.getcwd()
    ino_path = find_ino_file(project_dir)
    ino_name = os.path.basename(ino_path)
    cfg = parse_directives(ino_path)

    port = cfg["COM"] or detect_port()

    print(Fore.CYAN + f"🔧 Konfiguracja z pliku .ino:")
    for k, v in cfg.items():
        print(Fore.YELLOW + f"   {k}: {v}")
        log_to_file(f"{k}={v}")

    if cfg["ERASE"]:
        erase_flash(port)

    compile_sketch(project_dir, cfg["PART"], cfg["PSRAM"])
    build_dir = find_build_dir()
    merged = merge_bin(build_dir, ino_name, cfg["FLASH-SIZE"])
    flash_device(port, merged)
    flash_spiffs(port, build_dir, ino_name)

    elapsed = time.time() - start
    print(Fore.GREEN + f"\n✅ Zakończono pomyślnie w {elapsed:.1f}s")
    print(Fore.CYAN + f"💡 Port: {port}")
    print(Fore.CYAN + f"💡 Flash: {cfg['FLASH-SIZE']}")
    print(Fore.CYAN + f"💡 PSRAM: {cfg['PSRAM'] or 'AUTO'}")
    print(Fore.CYAN + f"💡 Partycja: {cfg['PART']}")
    log_to_file(f"✅ Zakończono w {elapsed:.1f}s")


if __name__ == "__main__":
    main()
