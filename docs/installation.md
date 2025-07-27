# Instrukcja instalacji i konfiguracji

## Krok 1: Przygotowanie danych Tuya

### Opcja A: Tuya IoT Platform (Zalecane)
1. Przejdź na [Tuya IoT Platform](https://iot.tuya.com/)
2. Utwórz konto lub zaloguj się
3. Utwórz nowy projekt Cloud
4. Zanotuj `Access ID` i `Access Secret`
5. Dodaj swoje urządzenie do projektu
6. Znajdź `Device ID` swojego urządzenia

### Opcja B: Lokalny klucz (Alternatywa)
1. Użyj aplikacji mobilnej Tuya Smart/Smart Life
2. Wyciągnij lokalny klucz używając narzędzi takich jak:
   - [tuya-cloudcutter](https://github.com/tuya-cloudcutter/tuya-cloudcutter)
   - [tinytuya wizard](https://github.com/jasonacox/tinytuya)

## Krok 2: Odnalezienie adresu IP urządzenia

1. Sprawdź router/DHCP dla adresu IP urządzenia
2. Lub użyj skanera sieci: `nmap -sn 192.168.1.0/24`
3. Możesz też użyć aplikacji Tuya dla identyfikacji

## Krok 3: Analiza czujników

1. Skopiuj plik `tuya_config.json.example` jako `tuya_config.json`
2. Wypełnij dane urządzenia:
```json
{
  "device_id": "bf1234567890abcdef",
  "local_key": "1234567890abcdef", 
  "ip_address": "192.168.1.100",
  "tuya_cloud": {
    "access_id": "twoje_access_id",
    "access_secret": "twój_access_secret",
    "endpoint": "https://openapi.tuyaeu.com"
  }
}
```

3. Uruchom analizator:
```bash
cd tuya_8in1_analyzer
python discover_sensors.py
```

4. Sprawdź plik wyników JSON
5. Zidentyfikuj które DPS odpowiadają którym czujnikom

## Krok 4: Konfiguracja integracji

1. Otwórz `custom_components/tuya_8in1/const.py`
2. Zaktualizuj `SENSOR_TYPES` z prawidłowymi ID DPS:

```python
SENSOR_TYPES = {
    "temperature": {
        "name": "Temperatura",
        "dps_id": 1,  # Zmień na prawdziwe DPS ID
        # reszta konfiguracji...
    },
    "ph": {
        "name": "pH", 
        "dps_id": 2,  # Zmień na prawdziwe DPS ID
        # reszta konfiguracji...
    },
    # itd...
}
```

## Krok 5: Instalacja w Home Assistant

1. Skopiuj folder `custom_components/tuya_8in1` do:
   - `<home_assistant_config>/custom_components/tuya_8in1`

2. Zrestartuj Home Assistant

3. Przejdź do: **Konfiguracja** > **Integracje** > **Dodaj integrację**

4. Wyszukaj "Tuya 8-in-1 Water Quality Tester"

5. Wprowadź dane:
   - Device ID
   - Local Key  
   - Adres IP urządzenia
   - Nazwę (opcjonalnie)

## Krok 6: Weryfikacja

Po dodaniu integracji powinieneś zobaczyć wszystkie czujniki:
- `sensor.tuya_8in1_tester_temperatura`
- `sensor.tuya_8in1_tester_ph`
- `sensor.tuya_8in1_tester_orp`
- `sensor.tuya_8in1_tester_tds`
- i inne...

## Rozwiązywanie problemów

### Brak połączenia z urządzeniem
- Sprawdź adres IP urządzenia
- Upewnij się, że Local Key jest poprawny
- Sprawdź czy urządzenie jest w tej samej sieci

### Brak danych z czujników
- Uruchom ponownie analizator
- Sprawdź mapowania DPS w `const.py`
- Włącz logi debug w Home Assistant

### Nieprawidłowe wartości
- Sprawdź `scale` w konfiguracji czujnika
- Niektóre urządzenia przesyłają wartości przeskalowane

## Logi debug

Dodaj do `configuration.yaml`:
```yaml
logger:
  default: info
  logs:
    custom_components.tuya_8in1: debug
```
