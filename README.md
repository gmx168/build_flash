build_flash "FACADE"Automatyczny Python Wrapper do Kompilacji i Flashowania ESP32 / S3 / C3<p align="center"><img src="https://img.shields.io/badge/Platform-ESP32%20%7C%20S3%20%7C%20C3-blueviolet.svg" alt="Platform Badge"><img src="https://img.shields.io/badge/Language-Python-informational.svg" alt="Python Badge"><img src="https://img.shields.io/badge/Tool-Arduino%20CLI%20%2B%20esptool-red.svg" alt="Tool Badge"></p>FACADE to Twój nowy, ultraszybki asystent, który automatyzuje cały proces compiling, linking, merging, flashing oraz SPIFFS writing dla mikrokontrolerów ESP32, ESP32-S3 i ESP32-C3.Pożegnaj się z ręcznym wprowadzaniem danych – ciesz się workflowem na autopilocie!⚡ Główne Zalety – Koniec z ręcznym konfigurowaniem!FunkcjonalnośćFACADEStandardowe IDEWykrywanie portu COM✅ Automatyczne❌ Wymaga ręcznego wyboruNazwy plików/katalogów✅ Automatyczne (z folderu)❌ Wymaga podawaniaObsługa SPIFFS✅ Automatyczna (tworzenie i flashowanie)❌ Często ręczny i skomplikowanyKasowanie Flash✅ Automatyczne❌ Wymaga ręcznej akcjiSzybkość~2x szybszy niż IDE!Zwykle wolniejszy✨ Kluczowe UsprawnieniaZero Wprowadzania Danych: Skrypt sam znajduje plik .ino, jego folder domowy i wykrywa podłączony port COM.SPIFFS bez Bólu Głowy: Jeśli ustawisz partycję ze SPIFFS, skrypt automatycznie stworzy plik spiffs.bin i wgra go do pamięci."Jak Rakieta" 🚀: Uruchom go i idź na kawę! Skompiluje, zlinkuje, wrzuci na flash, wgra SPIFFS i zresetuje UART.⏱️ Uwaga: Choć jest ok. 2x szybszy niż standardowe IDE, może być wolniejszy niż VS PlatformIO.🛠️ Jak To Działa?Umieść skrypt w katalogu głównym projektu Arduino (tam, gdzie znajduje się plik .ino).Skrypt odczytuje nazwę pliku i katalogu na podstawie typowej struktury Arduino.Magia Dzieje Się w Komentarzach! 🧙‍♂️ W pliku .ino umieść specjalne dyrektywy w formie zwykłych komentarzy, aby nadpisać domyślne ustawienia płytki.📝 Dyrektywy Konfiguracyjne (w pliku .ino)Dyrektywy są umieszczane jako komentarze w formacie: //DYREKTYWA=WARTOŚĆ. Nieaktywne dyrektywy oznacz jako //-DYREKTYWA=WARTOŚĆ.DyrektywaOpisPrzykładowe Wartości//PART=VALUESchemat partycji.AUTO (Domyślnie), MS (min_spiffs), HA (huge_app), DEFAULT, lub nazwa surowa (default_8MB).//FLASH=VALUERozmiar pamięci Flash.2MB, 4MB (Domyślnie), 8MB, 16MB, 32MB.//PSRAM=VALUEKonfiguracja PSRAM dla FQBN (dla S3: OPI, QPI, DISABLED).ENABLED, DISABLED.//ERASE=TRUECałkowite kasowanie flash przed kompilacją/flashowaniem.TRUE.//CUST=TRUEUżycie mkspiffs i flashowanie SPIFFS z katalogu data/.TRUE.//COM=NUMBERRęczne określenie portu COM (np. //COM=5). Jeśli pominięte, następuje auto-detekcja.Liczba portu.//PLATFORM=VALUEArchitektura chipa. Można też użyć //ESP32S3 lub //ESP32C3.ESP32 (Domyślnie), ESP32S3, ESP32C3.Przykład użycia w pliku .ino:C++//PART=HA
//FLASH=16MB
//CUST=TRUE
//PLATFORM=ESP32S3
//... reszta kodu ...
⚙️ Wymagania i InstalacjaWymagania Wstępne:Zainstalowany Python.Zainstalowany i skonfigurowany Arduino CLI.Zainstalowany pakiet platformy ESP32 w Arduino (wymagany do ścieżek esptool i mkspiffs).Wymagane biblioteki Python:Bashpip install colorama pyserial
Ustawienie Ścieżek Lokalnych:W skrypcie musisz zdefiniować własne ścieżki do narzędzi (wersja pakietu np. 3.3.3 może się różnić):PythonARDUINO_CLI = r"C:\Program Files\Arduino CLI\arduino-cli.exe"
ESPTOOL = r"C:\Users\Grzeg\AppData\Local\Arduino15\packages\esp32\tools\esptool_py\5.1.0\esptool.exe"

# Ustawienia Domyślne
BOARD = "esp32:esp32:esp32"
DEFAULT_PARTITION = "minimal"
DEFAULT_FLASH_SIZE = "4MB"
BAUD = 921600
BOOT_APP0 = r"C:\Users\Grzeg\AppData\Local\Arduino15\packages\esp32\hardware\esp32\3.3.3\tools\partitions\boot_app0.bin"
LOG_FILE = "bf_log.txt"
▶️ UżycieUpewnij się, że Twoje dyrektywy w pliku .ino są ustawione.Uruchom skrypt w katalogu projektu:Bashpython facade.py
Jeśli w katalogu jest więcej niż jeden plik .ino, podaj jego nazwę jako parametr.👤 AutorGrzegorz Maletka "FRYGA" dla yoRadio Community[English version below]

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

   





