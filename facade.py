"""
ESP32 Build and Flash Utility (Facade)
--------------------------------------------------------------------------------
AUTHOR: Grzegorz Maletka "FRYGA" for yoRadio Community

DESCRIPTION:
This Python script provides an automated workflow for compiling, merging, and
flashing firmware (including SPIFFS data) onto ESP32, ESP32-S3, and ESP32-C3
microcontrollers using the Arduino CLI and esptool.

It automatically detects the connected COM port and reads configuration
directives from comments within your Arduino (.ino) sketch file.

PREREQUISITES:
1. Python installed.
2. Arduino CLI installed and configured.
3. ESP32 platform package installed in Arduino (required for esptool and
   mkspiffs paths).
4. Required Python libraries: 'colorama' and 'pyserial' (serial.tools.list_ports).
   Install them with: pip install colorama pyserial

USAGE:
1. Place this script in the root directory of your Arduino project (where the
   .ino file is located).
2. Ensure the PATH variables (ARDUINO_CLI, ESPTOOL, etc.) at the top of the
   script are correctly set to your local installation paths.
3. Define configuration parameters inside your main .ino sketch file using
   special comments (directives).
4. Run the script from the project directory: python fasada_with_instructions.py

CONFIGURATION DIRECTIVES (in your .ino file):
You must include these directives as comments in the following format:
//DIRECTIVE=VALUE

* //PART=VALUE
    Sets the Partition Scheme.
    - AUTO (Default): Automatically selects a scheme based on the size of the 'data'
      directory (prefers 'min_spiffs' if data fits, otherwise 'huge_app', or 'default').
    - MS: Alias for 'min_spiffs'.
    - HA: Alias for 'huge_app'.
    - DEFAULT: Alias for 'default'.
    - RAW_NAME: You can provide any custom partition name (e.g., 'default_8MB').

* //FLASH-SIZE=VALUE or //FLASH=VALUE
    Sets the flash size for esptool/merge-bin.
    Accepted values: 2MB, 4MB (Default), 8MB, 16MB, 32MB.

* //PSRAM=VALUE
    Configures PSRAM option for the FQBN (Board Fully Qualified Name).
    - For ESP32-S3: OPI, QPI, DISABLED.
    - For ESP32: ENABLED, DISABLED.

* //ERASE=TRUE
    If set to TRUE, the script performs a full flash erase before compilation/flashing.

* //CUST=TRUE
    If set to TRUE, the script uses the 'mkspiffs' tool to manually create and
    flash a SPIFFS image from the 'data/' directory. If not set, SPIFFS is skipped.

* //COM=NUMBER
    Specifies the COM port number (e.g., //COM=5 for COM5). If omitted, the script
    will attempt to auto-detect the port.

* //PLATFORM=VALUE
    Defines the target chip architecture.
    Accepted values: ESP32 (Default), ESP32S3, ESP32C3.
    (You can also use single-line directives like //ESP32S3 or //ESP32C3)

Example .ino Directives:
//PART=HA
//FLASH=16MB
//CUST=TRUE
//PLATFORM=ESP32S3
"""
import os
import sys
import shutil
import subprocess
import time
from datetime import datetime

from colorama import init, Fore, Back, Style
import serial.tools.list_ports

init(autoreset=True)

# PATHS – adjust if something has changed
ARDUINO_CLI = r"C:\Program Files\Arduino CLI\arduino-cli.exe"
ESPTOOL     = r"C:\Users\Grzeg\AppData\Local\Arduino15\packages\esp32\tools\esptool_py\5.1.0\esptool.exe"
MK_SPIFFS   = r"C:\Users\Grzeg\AppData\Local\Arduino15\packages\esp32\tools\mkspiffs\0.2.3\mkspiffs.exe"
BOOT_APP0   = r"C:\Users\Grzeg\AppData\Local\Arduino15\packages\esp32\hardware\esp32\3.3.3\tools\partitions\boot_app0.bin"

BUILD_BASE  = r"D:\arduino-builds"
BAUD        = 921600
LOGFILE     = "bf_mkspiffs.log"


# ---------------- LOG + MEASUREMENT ----------------

def log(msg: str):
    with open(LOGFILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {msg}\n")


def run(cmd: str):
    print(Fore.CYAN + "\n[CMD] " + cmd + "\n")
    log(cmd)
    r = subprocess.run(cmd, shell=True)
    if r.returncode != 0:
        print(Fore.RED + "❌ Command finished with an error.")
        log("ERROR")
        sys.exit(1)


def print_step_time(label: str, step_start: float, global_start: float):
    step_duration = time.time() - step_start
    total_duration = time.time() - global_start
    txt = f"⏱ {label}: step {step_duration:.2f}s | since start {total_duration:.2f}s"
    print(Back.WHITE + Fore.BLACK + Style.BRIGHT + txt + Style.RESET_ALL)
    log(txt)


# ---------------- UTILITY FUNCTIONS ----------------

def detect_port() -> str:
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        if any(x in p.description for x in ["CP210", "CH340", "USB-SERIAL", "Silicon", "JTAG"]):
            print(Fore.GREEN + f"🔌 ESP detected: {p.device}")
            return p.device
    if ports:
        # Fallback to the first available port if no typical description is found
        print(Fore.YELLOW + f"⚠ No typical one – using {ports[0].device}")
        return ports[0].device
    print(Fore.RED + "❌ No COM ports found")
    sys.exit(1)


def find_ino(path: str) -> str:
    for f in os.listdir(path):
        if f.endswith(".ino"):
            print(Fore.GREEN + f"INO found: {f}")
            return os.path.join(path, f)
    print(Fore.RED + "❌ No .ino file found")
    sys.exit(1)


def calc_dir_size(path: str) -> int:
    """Recursively calculates the directory size in bytes."""
    total = 0
    for root, dirs, files in os.walk(path):
        for f in files:
            fp = os.path.join(root, f)
            if os.path.isfile(fp):
                total += os.path.getsize(fp)
    return total


# ---------------- .INO DIRECTIVES PARSING ----------------

def parse_directives(ino: str) -> dict:
    cfg = {
        "PART": "AUTO",   # AUTO/MS/HA/DEFAULT or raw name (default, min_spiffs, huge_app, etc.)
        "FLASH": "4MB",
        "PSRAM": None,
        "ERASE": False,
        "CUST": None,
        "PLATFORM": "esp32",  # esp32 / esp32s3 / esp32c3
        "COM": None
    }

    def norm_flash(val: str) -> str:
        v = val.upper().replace(" ", "")
        v = v.replace("MB", "").replace("M", "")
        if v not in ("2", "4", "8", "16", "32"):
            return "4MB"
        return f"{v}MB"

    def norm_part_alias(val: str) -> str:
        if not val:
            return "AUTO"
        u = val.strip().upper().replace("-", "_")
        if u in ("MS", "MINIMAL_SPIFFS", "MIN_SPIFFS", "MIN_SPIPFS", "MIN_SPIFS"):
            return "MS"
        if u in ("HA", "HUGE_APP", "HUGEAPP", "HUGE"):
            return "HA"
        if u in ("DEF", "DEFAULT"):
            return "DEFAULT"
        if u in ("AUTO", "AUT"):
            return "AUTO"
        # raw name – leave as is (e.g., default_8MB, mf_large, no_ota)
        return val.strip()

    with open(ino, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()

            # disabled directives – //-SOMETHING
            if line.startswith("//-"):
                continue

            if line.startswith("//PART="):
                val = line.split("=", 1)[1].strip()
                cfg["PART"] = norm_part_alias(val)

            elif line.startswith("//FLASH-SIZE=") or line.startswith("//FLASH="):
                val = line.split("=", 1)[1].strip()
                cfg["FLASH"] = norm_flash(val)

            elif line.startswith("//PSRAM="):
                cfg["PSRAM"] = line.split("=", 1)[1].strip()

            elif line.startswith("//ERASE="):
                cfg["ERASE"] = (line.split("=", 1)[1].strip().upper() == "TRUE")

            elif line.startswith("//CUST="):
                cfg["CUST"] = line.split("=", 1)[1].strip()

            elif line.startswith("//COM="):
                # Ensure the format is COMx
                cfg["COM"] = "COM" + line.split("=", 1)[1].strip().upper().replace("COM", "")

            elif line.startswith("//PLATFORM="):
                plat = line.split("=", 1)[1].strip().upper()
                if plat in ("ESP32S3", "ESP32_S3"):
                    cfg["PLATFORM"] = "esp32s3"
                elif plat in ("ESP32C3", "ESP32_C3"):
                    cfg["PLATFORM"] = "esp32c3"
                else:
                    cfg["PLATFORM"] = "esp32"

            elif line.startswith("//ESP32S3"):
                cfg["PLATFORM"] = "esp32s3"
            elif line.startswith("//ESP32C3"):
                cfg["PLATFORM"] = "esp32c3"
            elif line.startswith("//ESP32"):
                cfg["PLATFORM"] = "esp32"

    return cfg


# ---------------- PARTITION CSV / SPIFFS ----------------

def get_partitions_dir() -> str:
    # BOOT_APP0 sits in ...\tools\partitions\
    return os.path.dirname(BOOT_APP0)


def find_partition_csv(part_name: str) -> str | None:
    part_dir = get_partitions_dir()
    if not os.path.isdir(part_dir):
        print(Fore.RED + f"❌ Missing partitions directory: {part_dir}")
        return None

    exact = os.path.join(part_dir, f"{part_name}.csv")
    if os.path.exists(exact):
        return exact

    candidates = [
        f for f in os.listdir(part_dir)
        if f.lower().startswith(part_name.lower()) and f.endswith(".csv")
    ]
    if not candidates:
        return None
    candidates.sort(key=len)
    return os.path.join(part_dir, candidates[0])


def get_spiffs_region(part_name: str) -> tuple[int | None, int | None]:
    """
    Returns (size_bytes, offset) for the SPIFFS partition in the given scheme.
    """
    csv_path = find_partition_csv(part_name)
    if not csv_path:
        print(Fore.YELLOW + f"ℹ CSV file not found for partition '{part_name}'.")
        return None, None

    print(Fore.CYAN + f"📄 Using partition table: {csv_path}")

    with open(csv_path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            cols = [c.strip() for c in line.split(",")]
            if len(cols) < 5:
                continue

            name, ptype, subtype, offset, size = cols[:5]

            # if it's SPIFFS
            if ptype.lower() == "data" and (subtype.lower() == "spiffs" or name.lower() == "spiffs"):
                try:
                    off_val = int(offset, 0)
                    size_val = int(size, 0)
                    print(Fore.MAGENTA + f"📦 SPIFFS from CSV: offset=0x{off_val:06X}, size=0x{size_val:06X}")
                    return size_val, off_val
                except ValueError:
                    continue

    print(Fore.YELLOW + f"ℹ Partition '{part_name}' does not contain SPIFFS.")
    return None, None


def auto_choose_partition(cfg: dict, data_bytes: int | None) -> None:
    """
    Sets cfg["PART"] to a specific PartitionScheme (default / min_spiffs / huge_app / custom),
    considering aliases (AUTO/MS/HA/DEFAULT) and the size of the 'data' directory.
    """
    part = cfg["PART"]
    plat = cfg["PLATFORM"]

    if isinstance(part, str):
        u = part.strip().upper().replace("-", "_")
    else:
        u = "AUTO"

    # explicit aliases -> specific schemes
    if u in ("MS", "MINIMAL_SPIFFS", "MIN_SPIFFS"):
        cfg["PART"] = "min_spiffs"
        print(Fore.CYAN + "ℹ PART=MS → PartitionScheme=min_spiffs")
        return

    if u in ("HA", "HUGE_APP", "HUGEAPP", "HUGE"):
        cfg["PART"] = "huge_app"
        print(Fore.CYAN + "ℹ PART=HA → PartitionScheme=huge_app")
        return

    if u in ("DEF", "DEFAULT"):
        cfg["PART"] = "default"
        print(Fore.CYAN + "ℹ PART=DEFAULT → PartitionScheme=default")
        return

    if u not in ("", "AUTO", "AUT"):
        # user provided a specific name (e.g., default_8MB, mf_large, no_ota, etc.)
        print(Fore.CYAN + f"ℹ PART={part} → using name without changes.")
        return

    # AUTO:
    if data_bytes is None:
        print(Fore.CYAN + "ℹ PART=AUTO, missing data directory – using 'default'.")
        cfg["PART"] = "default"
        return

    print(Fore.CYAN + f"ℹ PART=AUTO, data size = {data_bytes} B – attempting to select min_spiffs / huge_app.")

    # get SPIFFS sizes for min_spiffs and huge_app
    size_min, _ = get_spiffs_region("min_spiffs")
    size_ha, _ = get_spiffs_region("huge_app")

    margin = 4096  # some buffer for SPIFFS structures

    # prefer min_spiffs if there is enough space
    if size_min and data_bytes < (size_min - margin):
        cfg["PART"] = "min_spiffs"
        print(Fore.GREEN + f"✅ Selected PartitionScheme=min_spiffs (SPIFFS ~0x{size_min:X} B)")
        return

    # otherwise try huge_app
    if size_ha and data_bytes < (size_ha - margin):
        cfg["PART"] = "huge_app"
        print(Fore.GREEN + f"✅ Selected PartitionScheme=huge_app (SPIFFS ~0x{size_ha:X} B)")
        return

    # no sensible SPIFFS (e.g., custom scheme without spiffs) – fallback to default
    print(Fore.YELLOW + "⚠ Could not match min_spiffs/huge_app – using 'default'.")
    cfg["PART"] = "default"


def make_spiffs_image(data_dir: str, out_path: str, size_bytes: int) -> bool:
    if not os.path.isdir(data_dir):
        print(Fore.YELLOW + "⚠ Missing data/ directory – not creating SPIFFS.")
        return False

    file_count = 0
    dir_count = 0
    for root, dirs, files in os.walk(data_dir):
        if root == data_dir:
            dir_count += len(dirs)
        else:
            dir_count += 1
        file_count += len(files)

    payload_size = calc_dir_size(data_dir)
    print(Fore.CYAN + f"📁 data/: {dir_count} directories, {file_count} files, {payload_size} B of data")

    if payload_size > size_bytes - 4096:
        print(Fore.RED + f"❌ Data ({payload_size} B) does not fit in SPIFFS partition ({size_bytes} B).")
        print(Fore.RED + "   Reduce data/ content or select a larger partition scheme (e.g., HA/huge_app).")
        return False

    print(Fore.CYAN + f"🔧 Building SPIFFS image of size {size_bytes} B ...")

    cmd = f'"{MK_SPIFFS}" -c "{data_dir}" -b 4096 -p 256 -s {size_bytes} "{out_path}"'
    run(cmd)

    if os.path.exists(out_path):
        sz = os.path.getsize(out_path)
        print(Fore.GREEN + f"✅ SPIFFS generated: {out_path} ({sz} B)")
        return True
    else:
        print(Fore.RED + "❌ mkspiffs failed to create the file!")
        return False


# ---------------- MERGE + FQBN ----------------

def merge_bin(bin_dir: str, ino_name: str, flash_size: str, chip: str) -> str:
    base = os.path.splitext(ino_name)[0]
    boot = os.path.join(bin_dir, f"{base}.ino.bootloader.bin")
    part = os.path.join(bin_dir, f"{base}.ino.partitions.bin")
    app  = os.path.join(bin_dir, f"{base}.ino.bin")
    merged = os.path.join(bin_dir, f"{base}_merged.bin")

    for f in [boot, part, app, BOOT_APP0]:
        if not os.path.exists(f):
            print(Fore.RED + f"❌ Missing file: {f}")
            sys.exit(1)

    # --- Layout dependent on chip type ---
    if chip == "esp32":
        # classic ESP32 – bootloader at 0x1000
        layout = [
            (0x1000,  boot),
            (0x8000,  part),
            (0xE000,  BOOT_APP0),
            (0x10000, app),
        ]
    elif chip in ("esp32s3", "esp32c3"):
        # ESP32-S3 / C3 – bootloader at 0x0000
        layout = [
            (0x0000,  boot),
            (0x8000,  part),
            (0xE000,  BOOT_APP0),
            (0x10000, app),
        ]
    else:
        # fallback – treat as classic ESP32
        layout = [
            (0x1000,  boot),
            (0x8000,  part),
            (0xE000,  BOOT_APP0),
            (0x10000, app),
        ]

    # build string for esptool merge-bin
    segs = []
    for off, path in layout:
        segs.append(f"0x{off:X} \"{path}\"")
    segs_str = " ".join(segs)

    cmd = (
        f'"{ESPTOOL}" --chip {chip} merge-bin '
        f'--flash-size {flash_size} '
        f'-o "{merged}" '
        f'{segs_str}'
    )
    run(cmd)
    return merged


def build_fqbn(cfg: dict) -> str:
    plat = cfg["PLATFORM"]
    if plat == "esp32":
        base = "esp32:esp32:esp32"
    elif plat == "esp32s3":
        base = "esp32:esp32:esp32s3"
    elif plat == "esp32c3":
        base = "esp32:esp32:esp32c3"
    else:
        base = "esp32:esp32:esp32"

    # --- PSRAM (only what the core understands) ---
    psram_opt = ""
    if cfg["PSRAM"]:
        ps_up = cfg["PSRAM"].upper().replace(" ", "")
        if plat == "esp32s3":
            if ps_up in ("OPI", "ON", "EN", "ENABLED", "QIO_OPI", "OCTAL"):
                ps_val = "opi"
            elif ps_up in ("QPI", "QSPI"):
                ps_val = "qspi"
            elif ps_up in ("OFF", "NONE", "DIS", "DISABLED"):
                ps_val = "disabled"
            else:
                ps_val = cfg["PSRAM"]
        elif plat == "esp32":
            if ps_up in ("ON", "EN", "ENABLED"):
                ps_val = "enabled"
            elif ps_up in ("OFF", "NONE", "DIS", "DISABLED"):
                ps_val = "disabled"
            else:
                ps_val = cfg["PSRAM"]
        else:
            ps_val = cfg["PSRAM"]

        psram_opt = f",PSRAM={ps_val}"

    # Note: NO FlashMode/FlashFreq/FlashSize in FQBN,
    # as different core versions have different menus and Arduino CLI complains.
    fqbn = f'{base}:PartitionScheme={cfg["PART"]}{psram_opt}'
    print(Fore.CYAN + f"FQBN: {fqbn}")
    return fqbn




# ---------------- MAIN ----------------

def main():
    global_start = time.time()
    print(Fore.GREEN + "🚀 BF_mkspiffs START")
    project = os.getcwd()
    ino = find_ino(project)
    ino_name = os.path.basename(ino)
    cfg = parse_directives(ino)

    # Detected chip (esp32, esp32s3, esp32c3)
    target_chip = cfg["PLATFORM"]

    build_path = os.path.join(BUILD_BASE, os.path.splitext(ino_name)[0])
    os.makedirs(build_path, exist_ok=True)

    data_src = os.path.join(project, "data")
    data_dst = os.path.join(build_path, "data")

    # calculate data size in project (before copying)
    data_bytes = None
    if os.path.isdir(data_src):
        data_bytes = calc_dir_size(data_src)
        print(Fore.CYAN + f"📏 Size of data/ directory: {data_bytes} B")
    else:
        print(Fore.YELLOW + "⚠ Missing data/ in the project.")
        data_bytes = None

    # select PartitionScheme based on PART + data size
    auto_choose_partition(cfg, data_bytes)

    # copy data to build_path
    if os.path.isdir(data_src):
        if os.path.exists(data_dst):
            shutil.rmtree(data_dst)
        shutil.copytree(data_src, data_dst)
        print(Fore.GREEN + f"📂 data/ copied → {data_dst}")

    port = cfg["COM"] or detect_port()

    # ERASE FLASH
    if cfg["ERASE"]:
        step_start = time.time()
        run(f'"{ESPTOOL}" --chip {target_chip} --port {port} erase-flash')
        print_step_time("ERASE FLASH", step_start, global_start)

    fqbn = build_fqbn(cfg)

    # COMPILATION
    step_start = time.time()
    run(f'"{ARDUINO_CLI}" compile --fqbn "{fqbn}" --build-path "{build_path}" "{project}"')
    print_step_time("COMPILATION", step_start, global_start)

    # Copy bins to bin_out
    bin_out = os.path.join(project, "bin_out")
    os.makedirs(bin_out, exist_ok=True)

    base = os.path.splitext(ino_name)[0]
    for name in [f"{base}.ino.bootloader.bin", f"{base}.ino.partitions.bin", f"{base}.ino.bin"]:
        src = os.path.join(build_path, name)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(bin_out, name))
            print("→", name)

    # --- SPIFFS via mkspiffs with CUST ---
    spiffs_bin_path = None
    spiffs_offset = None

    if cfg["CUST"]:
        size_bytes, off = get_spiffs_region(cfg["PART"])
        if size_bytes and off is not None:
            spiffs_bin_path = os.path.join(bin_out, f"{base}.spiffs.bin")
            step_start = time.time()
            if make_spiffs_image(data_src, spiffs_bin_path, size_bytes):
                print_step_time("MK_SPIFFS", step_start, global_start)
                spiffs_offset = off
        else:
            print(Fore.RED + "❌ Selected partition has no SPIFFS – mkspiffs has nowhere to write.")
    else:
        print(Fore.YELLOW + "ℹ Missing CUST – mkspiffs unused, skipping SPIFFS.")

    # MERGE BIN
    step_start = time.time()
    merged = merge_bin(bin_out, ino_name, cfg["FLASH"], target_chip)
    print_step_time("MERGE BIN", step_start, global_start)

    # FLASH FIRMWARE
    step_start = time.time()
    run(f'"{ESPTOOL}" --chip {target_chip} --port {port} --baud {BAUD} write-flash 0x0 "{merged}"')
    print_step_time("FLASH FIRMWARE", step_start, global_start)

    # FLASH SPIFFS
    if spiffs_bin_path and spiffs_offset is not None and os.path.exists(spiffs_bin_path):
        print(Fore.CYAN + f"💾 Flashing SPIFFS to offset 0x{spiffs_offset:06X} ...")
        step_start = time.time()
        run(
            f'"{ESPTOOL}" --chip {target_chip} --port {port} --baud {BAUD} '
            f'write-flash 0x{spiffs_offset:x} "{spiffs_bin_path}"'
        )
        print_step_time("FLASH SPIFFS", step_start, global_start)
    else:
        print(Fore.YELLOW + "⚠ Missing SPIFFS image – SPIFFS step skipped.")

    total = time.time() - global_start
    print(Fore.GREEN + f"✅ Done. Total: {total:.2f}s")
    log(f"TOTAL {total:.2f}s")


if __name__ == "__main__":
    main()
