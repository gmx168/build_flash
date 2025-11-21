# build_flash
Pyhton wrapper for compiling, linking, merging, flashing and spiffs writting automaticaly for Esp32dev 
Zero wprowadzania COMx
Zero wprowadzania nazw plików i katalogów wejściowych i wynikowych --> umieść skrypt w katalogu gdzie plik .ino
Zero kombinowania ze SPIFFS, masakra recznie wpychać pliki data i www --> zrobi to automatycznie
Zero kasowania flash - zrobi to za ciebie
Jak rakieta - odpalasz - idziesz na kawę, skompiluje, zlinkuje, wrzuci na flash, wrzuci spiffs, zresetuje UART.
Do zdefiniowania własne ścieżki lokalizacji w pliku w zależności od użytego pakietu board - tutaj 3.3.3

ARDUINO_CLI = r"C:\Program Files\Arduino CLI\arduino-cli.exe"
ESPTOOL = r"C:\Users\Grzeg\AppData\Local\Arduino15\packages\esp32\tools\esptool_py\5.1.0\esptool.exe"
BOARD = "esp32:esp32:esp32"
DEFAULT_PARTITION = "minimal"
DEFAULT_FLASH_SIZE = "4MB"
BAUD = 921600
BOOT_APP0 = r"C:\Users\Grzeg\AppData\Local\Arduino15\packages\esp32\hardware\esp32\3.3.3\tools\partitions\boot_app0.bin"
LOG_FILE = "bf_log.txt"



Jak działa:
1. Uruchamianie: python bf4.py
    W katalogu w którym jest plik .ino pobiera jego folder domowy (nazwę) oraz nazwę i na podstawie typowej struktury plików produkuje zgodnie z nazwą .ino wszystkie pliki.

2. Jesli ustawiona będzie partycja ze SPIFFS, to skrypt automatycznie stworzy plik spiffs.bin i "wrzuci go do pamięci ESP32"

3. Sam wykrywa pod którym COM jest podłączony ESP, nie trzeba podawać
4. W przypadku posiadania w tym samym katalogu dwóch lub więcej plików ino. jako parametr należy podać który plik ma kompilować.
5. Nie trzeba za każdym razem zmieniać ustawien płytki pod ESP32 - są projekty z inną partycją - majace PSRAM czy podłączone kilka urządzeń pod COMy (np. środowisko OT) to w pliku .ino w pierwszych liniach można podać wg tabelki poniżej

6. Poprawne wartości dla opcji PSRAM w ESP32 (core 3.3.3)
Co wpisujesz w .ino	Co faktycznie zostanie użyte w kompilacji (arduino-cli)	Opis
//PSRAM=QPI	--> PSRAM=qio	klasyczny tryb QIO (większość ESP32-WROVER)
//PSRAM=OPI	--> PSRAM=opi	nowszy tryb OPI (ESP32-S3, ESP32-WROVER-E)
//PSRAM=None --> lub brak	nie dodaje się opcji PSRAM do FQBN → działa jak „disabled”	PSRAM wyłącz


Dostępne wartości //PART= dla ESP32 (Arduino core 3.3.3)
Nazwa (//PART=...)	Opis	Rozmiar aplikacji	Rozmiar SPIFFS
default	Domyślna partycja Arduino	ok. 1.2 MB	1.5 MB
minimal	Mała aplikacja + duży SPIFFS	1 MB	2.8 MB
no_ota	Jedna duża partycja bez OTA	3 MB	1 MB
huge_app	Największa możliwa partycja dla jednej aplikacji	3 MB	0.5 MB
minimal_spiffs	Minimalny SPIFFS (250 kB) – używany gdy kod ledwo się mieści	3.5 MB	0.25 MB
app3M_fat9M_16MB	Dla układów z flash 16MB – ogromny FAT zamiast SPIFFS	3 MB	9 MB (FAT)
16M_fat_12MB	Dla 16MB flash – duży FAT	12 MB	4 MB (FAT)
8M_fat	Dla 8MB flash – duży FAT	3 MB	4.6 MB (FAT)
app3M_fat12M_16MB	Dla 16MB flash – największa app + FAT	3 MB	12 MB (FAT)
factory	Jedna partycja factory bez OTA	1.3 MB	1.5 MB
no_ota_large_spiffs	Brak OTA, ale duży SPIFFS	1.9 MB	2 MB
