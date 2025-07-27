# Tuya 8-in-1 Device Troubleshooting Guide

## Najczęstsze problemy i rozwiązania

### 1. "Python was not found"

**Problem:** Brak zainstalowanego Python lub nieprawidłowa ścieżka.

**Rozwiązanie:**
- Zainstaluj Python z [python.org](https://python.org) lub Microsoft Store
- Upewnij się, że Python jest w PATH
- Uruchom: `python --version` w PowerShell

### 2. "No base python found"

**Problem:** VS Code nie może znaleźć interpretera Python.

**Rozwiązanie:**
1. Otwórz Command Palette (Ctrl+Shift+P)
2. Wpisz "Python: Select Interpreter"
3. Wybierz odpowiedni interpreter Python
4. Lub zainstaluj Python extension dla VS Code

### 3. Błąd importu bibliotek Tuya

**Problem:** `ImportError: No module named 'tinytuya'`

**Rozwiązanie:**
```powershell
pip install tinytuya tuya-connector-python
# lub jeśli masz problemy z pip:
python -m pip install tinytuya tuya-connector-python
```

### 4. Urządzenie nie odpowiada

**Problem:** Timeout lub brak odpowiedzi z urządzenia.

**Sprawdź:**
- Czy urządzenie jest podłączone do WiFi
- Czy adres IP jest poprawny: `ping 192.168.1.XXX`
- Czy Local Key jest prawidłowy
- Czy urządzenie jest w tej samej sieci co komputer

### 5. Nieprawidłowe dane z czujników

**Problem:** Wartości są zbyt wysokie/niskie lub nierealne.

**Rozwiązanie:**
1. Sprawdź `scale` w `const.py`
2. Uruchom `discover_sensors.py` ponownie
3. Porównaj z wartościami w aplikacji Tuya
4. Dostosuj skalowanie w konfiguracji

### 6. Integracja nie pojawia się w Home Assistant

**Problem:** Brak integracji w liście dostępnych.

**Sprawdź:**
- Czy folder `custom_components/tuya_8in1` jest w odpowiednim miejscu
- Czy wszystkie pliki zostały skopiowane
- Czy zrestartowałeś Home Assistant
- Sprawdź logi Home Assistant

### 7. Czujniki pokazują "unknown" lub "unavailable"

**Problem:** Brak danych z czujników.

**Debugowanie:**
1. Włącz logi debug w Home Assistant
2. Sprawdź czy DPS ID są poprawne
3. Uruchom ponownie analizator urządzenia
4. Sprawdź czy urządzenie jest online

## Przydatne komendy

### Testowanie połączenia z urządzeniem
```python
import tinytuya

device = tinytuya.Device(
    dev_id="TWOJ_DEVICE_ID",
    address="192.168.1.XXX", 
    local_key="TWOJ_LOCAL_KEY",
    version=3.3
)

print(device.status())
```

### Skanowanie sieci w poszukiwaniu urządzeń Tuya
```powershell
python -m tinytuya scan
```

### Sprawdzanie logów Home Assistant
```bash
# Logi ogólne
tail -f home-assistant.log

# Logi tylko z naszej integracji
tail -f home-assistant.log | grep tuya_8in1
```

## Diagnostyka kroków

### Krok 1: Sprawdź połączenie sieciowe
```powershell
ping 192.168.1.XXX
telnet 192.168.1.XXX 6668
```

### Krok 2: Testuj Tuya API
```python
import tinytuya
device = tinytuya.Device("ID", "IP", "KEY", 3.3)
print(device.detect_available_dps())
```

### Krok 3: Sprawdź Home Assistant
- Przejdź do **Developer Tools** > **States**
- Sprawdź czy encje `sensor.tuya_8in1_*` istnieją
- Sprawdź atrybuty encji

### Krok 4: Analiza logów
W `configuration.yaml`:
```yaml
logger:
  default: warning
  logs:
    custom_components.tuya_8in1: debug
    homeassistant.components.sensor: debug
```

## Kontakt i wsparcie

Jeśli problemy nadal występują:
1. Sprawdź issues na GitHub
2. Utwórz nowy issue z:
   - Opisem problemu
   - Logami z Home Assistant
   - Konfiguracją (bez wrażliwych danych)
   - Wynikami z `discover_sensors.py`
