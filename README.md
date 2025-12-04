# 🚀 build_flash "FACADE"

## Automatyczny Python Wrapper do Kompilacji i Flashowania ESP32 / S3 / C3

<p align="center">
  <img src="https://img.shields.io/badge/Platform-ESP32%20%7C%20S3%20%7C%20C3-blueviolet.svg" alt="Platform Badge">
  <img src="https://img.shields.io/badge/Language-Python-informational.svg" alt="Python Badge">
  <img src="https://img.shields.io/badge/Tool-Arduino%20CLI%20%2B%20esptool-red.svg" alt="Tool Badge">
</p>

**FACADE** to Twój nowy, ultraszybki asystent, który automatyzuje cały proces *compiling, linking, merging, flashing* oraz *SPIFFS writing* dla mikrokontrolerów **ESP32**, **ESP32-S3** i **ESP32-C3**.

**Pożegnaj się z ręcznym wprowadzaniem danych – ciesz się workflowem na autopilocie!**

---

## ⚡ Główne Zalety – Koniec z ręcznym konfigurowaniem!

| Funkcjonalność | FACADE | Standardowe IDE |
| :--- | :---: | :---: |
| **Wykrywanie portu COM** | ✅ Automatyczne | ❌ Wymaga ręcznego wyboru |
| **Nazwy plików/katalogów** | ✅ Automatyczne (z folderu) | ❌ Wymaga podawania |
| **Obsługa SPIFFS** | ✅ Automatyczna (tworzenie i flashowanie) | ❌ Często ręczny i skomplikowany |
| **Kasowanie Flash** | ✅ Automatyczne | ❌ Wymaga ręcznej akcji |
| **Szybkość** | **~2x szybszy niż IDE!** | Zwykle wolniejszy |

### ✨ **Kluczowe Usprawnienia**

* **Zero Wprowadzania Danych:** Skrypt sam znajduje plik `.ino`, jego folder domowy i wykrywa podłączony port **COM**.
* **SPIFFS bez Bólu Głowy:** Jeśli ustawisz partycję ze SPIFFS, skrypt **automatycznie** stworzy plik `spiffs.bin` i wgra go do pamięci.
* **"Jak Rakieta" 🚀:** Uruchom go i idź na kawę! Skompiluje, zlinkuje, wrzuci na flash, wgra SPIFFS i zresetuje UART.

> ⏱️ **Uwaga:** Choć jest ok. 2x szybszy niż standardowe IDE, może być wolniejszy niż VS PlatformIO.

---

## 🛠️ Jak To Działa?

1.  Umieść skrypt w **katalogu głównym** projektu Arduino (tam, gdzie znajduje się plik `.ino`).
2.  Skrypt odczytuje nazwę pliku i katalogu na podstawie typowej struktury Arduino.
3.  **Magia Dzieje Się w Komentarzach!** 🧙‍♂️ W pliku `.ino` umieść specjalne **dyrektywy** w formie zwykłych komentarzy, aby nadpisać domyślne ustawienia płytki.

### 📝 Dyrektywy Konfiguracyjne (w pliku `.ino`)

Dyrektywy są umieszczane jako komentarze w formacie: `//DYREKTYWA=WARTOŚĆ`. Nieaktywne dyrektywy oznacz jako `//-DYREKTYWA=WARTOŚĆ`.

| Dyrektywa | Opis | Przykładowe Wartości |
| :--- | :--- | :--- |
| `//PART=VALUE` | Schemat partycji. | `AUTO` (Domyślnie), `MS` (min_spiffs), `HA` (huge_app), `DEFAULT`, lub nazwa surowa (`default_8MB`). |
| `//FLASH=VALUE` | Rozmiar pamięci Flash. | `2MB`, **`4MB` (Domyślnie)**, `8MB`, `16MB`, `32MB`. |
| `//PSRAM=VALUE` | Konfiguracja PSRAM dla FQBN (dla S3: OPI, QPI, DISABLED). | `ENABLED`, `DISABLED`. |
| `//ERASE=TRUE` | Całkowite kasowanie flash przed kompilacją/flashowaniem. | `TRUE`. |
| `//CUST=TRUE` | Użycie `mkspiffs` i flashowanie SPIFFS z katalogu `data/`. | `TRUE`. |
| `//COM=NUMBER` | Ręczne określenie portu COM (np. `//COM=5`). Jeśli pominięte, następuje auto-detekcja. | Liczba portu. |
| `//PLATFORM=VALUE` | Architektura chipa. Można też użyć `//ESP32S3` lub `//ESP32C3`. | **`ESP32` (Domyślnie)**, `ESP32S3`, `ESP32C3`. |

> **Przykład użycia w pliku `.ino`:**
>
> ```cpp
> //PART=HA
> //FLASH=16MB
> //CUST=TRUE
> //PLATFORM=ESP32S3
> //... reszta kodu ...
> ```

---

## ⚙️ Wymagania i Instalacja

### Wymagania Wstępne:

1.  Zainstalowany **Python**.
2.  Zainstalowany i skonfigurowany **Arduino CLI**.
3.  Zainstalowany pakiet platformy **ESP32** w Arduino (wymagany do ścieżek `esptool` i `mkspiffs`).
4.  Wymagane biblioteki Python:
    ```bash
    pip install colorama pyserial
    ```

### Ustawienie Ścieżek Lokalnych:

W skrypcie musisz zdefiniować **własne ścieżki** do narzędzi (wersja pakietu np. `3.3.3` może się różnić):

```python
ARDUINO_CLI = r"C:\Program Files\Arduino CLI\arduino-cli.exe"
ESPTOOL = r"C:\Users\Grzeg\AppData\Local\Arduino15\packages\esp32\tools\esptool_py\5.1.0\esptool.exe"

# Ustawienia Domyślne
BOARD = "esp32:esp32:esp32"
DEFAULT_PARTITION = "minimal"
DEFAULT_FLASH_SIZE = "4MB"
BAUD = 921600
BOOT_APP0 = r"C:\Users\Grzeg\AppData\Local\Arduino15\packages\esp32\hardware\esp32\3.3.3\tools\partitions\boot_app0.bin"
LOG_FILE = "bf_log.txt"

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

   
## 🌎 Global Access – Translations (Tłumaczenia)

### 🇬🇧 English

## ⚡ Main Advantages – No More Manual Configuration!

| Feature | FACADE | Standard IDE |
| :--- | :---: | :---: |
| **COM Port Detection** | ✅ Automatic | ❌ Requires manual selection |
| **File/Directory Names** | ✅ Automatic (from folder) | ❌ Requires input |
| **SPIFFS Handling** | ✅ Automatic (creation and flashing) | ❌ Often manual and complex |
| **Flash Erase** | ✅ Automatic | ❌ Requires manual action |
| **Speed** | **~2x faster than IDE!** | Generally slower |

### Key Improvements

* **Zero Data Input:** The script automatically finds the `.ino` file, its home folder, and detects the connected **COM** port.
* **SPIFFS Without Headache:** If a partition with SPIFFS is set, the script will **automatically** create the `spiffs.bin` file and upload it to the memory.
* **"Like a Rocket" 🚀:** Launch it and go for a coffee! It compiles, links, flashes, uploads SPIFFS, and resets the UART.

---

### 🇩🇪 Deutsch (Niemiecki)

## ⚡ Hauptvorteile – Schluss mit der manuellen Konfiguration!

| Funktion | FACADE | Standard IDE |
| :--- | :---: | :---: |
| **COM-Port-Erkennung** | ✅ Automatisch | ❌ Erfordert manuelle Auswahl |
| **Dateinamen/Verzeichnisse** | ✅ Automatisch (aus Ordner) | ❌ Erfordert Eingabe |
| **SPIFFS-Verwaltung** | ✅ Automatisch (Erstellung und Flash) | ❌ Oft manuell und kompliziert |
| **Flash Löschen** | ✅ Automatisch | ❌ Erfordert manuelle Aktion |
| **Geschwindigkeit** | **~2x schneller als IDE!** | Generell langsamer |

### Hauptverbesserungen

* **Keine Dateneingabe:** Das Skript findet automatisch die `.ino`-Datei und erkennt den angeschlossenen **COM**-Port.
* **SPIFFS ohne Kopfschmerzen:** Wenn eine Partition mit SPIFFS eingerichtet ist, erstellt das Skript **automatisch** die Datei `spiffs.bin` und lädt sie in den Speicher.
* **„Wie eine Rakete“ 🚀:** Starten Sie es und gehen Sie Kaffee trinken! Es kompiliert, verlinkt, flasht, lädt SPIFFS hoch und setzt den UART zurück.

---

### 🇳🇱 Nederlands (Holenderski)

## ⚡ Belangrijkste Voordelen – Geen handmatige configuratie meer!

| Functie | FACADE | Standaard IDE |
| :--- | :---: | :---: |
| **COM Poortdetectie** | ✅ Automatisch | ❌ Vereist handmatige selectie |
| **Bestands-/Maptitels** | ✅ Automatisch (van map) | ❌ Vereist invoer |
| **SPIFFS Afhandeling** | ✅ Automatisch (aanmaak en flash) | ❌ Vaak handmatig en complex |
| **Flash Wissen** | ✅ Automatisch | ❌ Vereist handmatige actie |
| **Snelheid** | **~2x sneller dan IDE!** | Over het algemeen langzamer |

### Belangrijkste Verbeteringen

* **Nul Invoer:** Het script vindt automatisch het `.ino`-bestand en detecteert de aangesloten **COM**-poort.
* **SPIFFS Zonder Hoofdpijn:** Als een partitie met SPIFFS is ingesteld, maakt het script **automatisch** het `spiffs.bin`-bestand aan en uploadt het naar het geheugen.
* **"Als een Raket" 🚀:** Start het op en ga koffie drinken! Het compileert, linkt, flasht, uploadt SPIFFS en reset de UART.

---

### 🇭🇺 Magyar (Węgierski)

## ⚡ Fő Előnyök – Nincs több kézi konfigurálás!

| Jellemző (Właściwość) | FACADE | Standard IDE |
| :--- | :---: | :---: |
| **COM Port észlelés** | ✅ Automatikus | ❌ Kézi választás |
| **Fájl-/Könyvtárnevek** | ✅ Automatikus (mappából) | ❌ Kézi bevitel |
| **SPIFFS kezelés** | ✅ Automatikus (készítés és flash) | ❌ Gyakran kézi és bonyolult |
| **Flash törlése** | ✅ Automatikus | ❌ Kézi műveletet igényel |
| **Sebesség** | **~2x gyorsabb, mint az IDE!** | Általában lassabb |

### Főbb Fejlesztések

* **Nulla adatbevitel:** A szkript automatikusan megtalálja a `.ino` fájlt, annak otthoni mappáját és észleli a csatlakoztatott **COM** portot.
* **SPIFFS Fejfájás Nélkül:** Ha SPIFFS-sel rendelkező partíció van beállítva, a szkript **automatikusan** létrehozza a `spiffs.bin` fájlt, és feltölti a memóriába.
* **„Mint egy Rakéta” 🚀:** Elindítod, elmész kávézni – lefordítja, flasheli, feltölti a SPIFFS-t és újraindítja az UART-ot.

---

### 🇺🇦 Українська (Ukraiński)

## ⚡ Головні Переваги – Більше ніяких ручних налаштувань!

| Особливість (Właściwość) | FACADE | Стандартне IDE |
| :--- | :---: | :---: |
| **Виявлення COM порту** | ✅ Автоматичне | ❌ Потрібен ручний вибір |
| **Імена файлів/каталогів** | ✅ Автоматично (з папки) | ❌ Потрібне введення |
| **Обробка SPIFFS** | ✅ Автоматична (створення та прошивка) | ❌ Часто ручна та складна |
| **Стирання Flash** | ✅ Автоматичне | ❌ Потрібна ручна дія |
| **Швидкість** | **~2x швидше, ніж IDE!** | Зазвичай повільніше |

### Ключові Покращення

* **Нульовий Ввід Даних:** Скрипт сам знаходить файл `.ino`, його домашню папку та виявляє підключений порт **COM**.
* **SPIFFS Без Головного Болю:** Якщо встановлено розділ зі SPIFFS, скрипт **автоматично** створить файл `spiffs.bin` і завантажить його в пам'ять.
* **«Як Ракета» 🚀:** Запускаєте – йдете на каву! Компілює, лінкує, прошиває, завантажує SPIFFS та перезавантажує UART.

---

### 🇷🇺 Русский (Российский)

## ⚡ Главные Преимущества – Больше никакой ручной настройки!

| Особенность (Właściwość) | FACADE | Стандартная IDE |
| :--- | :---: | :---: |
| **Обнаружение COM порта** | ✅ Автоматическое | ❌ Требуется ручной выбор |
| **Имена файлов/каталогов** | ✅ Автоматически (из папки) | ❌ Требуется ввод |
| **Работа с SPIFFS** | ✅ Автоматически (создание и прошивка) | ❌ Часто вручную и сложно |
| **Стирание Flash** | ✅ Автоматическое | ❌ Требуется ручное действие |
| **Скорость** | **~2x быстрее, чем IDE!** | Обычно медленнее |

### Ключевые Улучшения

* **Нулевой Ввод Данных:** Скрипт сам находит файл `.ino`, его домашнюю папку и обнаруживает подключенный порт **COM**.
* **SPIFFS Без Головной Боли:** Если установлен раздел со SPIFFS, скрипт **автоматически** создаст файл `spiffs.bin` и загрузит его в память.
* **«Как Ракета» 🚀:** Запускаете — идете пить кофе! Компилирует, линкует, прошивает, загружает SPIFFS и перезагружает UART.

---

### 🇨🇿 Čeština (Czeski)

## ⚡ Hlavní Výhody – Konec ruční konfiguraci!

| Vlastnost (Właściwość) | FACADE | Standardní IDE |
| :--- | :---: | :---: |
| **Detekce COM portu** | ✅ Automatická | ❌ Vyžaduje ruční výběr |
| **Názvy souborů/adresářů** | ✅ Automatické (z adresáře) | ❌ Vyžaduje zadání |
| **Zpracování SPIFFS** | ✅ Automatické (vytvoření a flash) | ❌ Často ruční a složité |
| **Vymazání Flash** | ✅ Automatické | ❌ Vyžaduje ruční akci |
| **Rychlost** | **~2x rychlejší než IDE!** | Obvykle pomalejší |

### Klíčové Zlepšení

* **Nulové Zadávání Dat:** Skript automaticky najde soubor `.ino`, jeho domovskou složku a detekuje připojený port **COM**.
* **SPIFFS Bez Bolesti Hlavy:** Pokud je nastavena partition se SPIFFS, skript **automaticky** vytvoří soubor `spiffs.bin` a nahraje jej do paměti.
* **"Jako Raketa" 🚀:** Spustíte, jdete na kávu! Zkompiluje, zalinkuje, nahraje na flash, nahraje SPIFFS a resetuje UART.



