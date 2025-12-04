# build_flash "FACADE"
Pyhton wrapper for compiling, linking, merging, flashing and spiffs writting automaticaly for Esp32dev / S3 / C3 / S3zero

[English version below]
a. Zero wprowadzania COMx
b. Zero wprowadzania nazw plików i katalogów wejściowych i wynikowych --> umieść skrypt w katalogu gdzie plik .ino
c. Zero kombinowania ze SPIFFS, masakra recznie wpychać pliki data i www --> zrobi to automatycznie
d. Zero kasowania flash - zrobi to za ciebie
e. Jak rakieta - odpalasz - idziesz na kawę, skompiluje, zlinkuje, wrzuci na flash, wrzuci spiffs, zresetuje UART. Robi to ok 2x szybciej niż IDE. Pewnie wolniej niż VS Platformio
f. Do zdefiniowania własne ścieżki lokalizacji w skrypcie w zależności od użytego pakietu board - tutaj 3.3.3

takie jak "\Grzeg\ wstawcie swoje:
ARDUINO_CLI = r"C:\Program Files\Arduino CLI\arduino-cli.exe"
ESPTOOL = r"C:\Users\Grzeg\AppData\Local\Arduino15\packages\esp32\tools\esptool_py\5.1.0\esptool.exe"
BOARD = "esp32:esp32:esp32"
DEFAULT_PARTITION = "minimal"
DEFAULT_FLASH_SIZE = "4MB"
BAUD = 921600
BOOT_APP0 = r"C:\Users\Grzeg\AppData\Local\Arduino15\packages\esp32\hardware\esp32\3.3.3\tools\partitions\boot_app0.bin"
LOG_FILE = "bf_log.txt"



Jak działa:
1. Uruchamianie: python facade.py
    W katalogu w którym jest plik .ino pobiera jego folder domowy (nazwę) oraz nazwę i na podstawie typowej struktury plików produkuje zgodnie z nazwą .ino wszystkie pliki.
W pliku .ino umieszczamy dyrektywy dla tego wrappera, jako zwykłe komentarze.

3. Jesli ustawiona będzie partycja ze SPIFFS, to skrypt automatycznie stworzy plik spiffs.bin i "wrzuci go do pamięci ESP32"
4. Sam wykrywa pod którym COM jest podłączony ESP, nie trzeba podawać
5. W przypadku posiadania w tym samym katalogu dwóch lub więcej plików ino. jako parametr należy podać który plik ma kompilować.
6. Nie trzeba za każdym razem zmieniać ustawien płytki pod ESP32 - są projekty z inną partycją - majace PSRAM czy podłączone kilka urządzeń pod COMy (np. środowisko OT) to w pliku .ino w pierwszych liniach można podać wg tabelki poniżej

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
//DIRECTIVE=VALUE                     - active
//-DIRECTIVE=VALUE                    - non-active / passive directive - to be ignored

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

   





