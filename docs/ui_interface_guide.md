# Interfejs użytkownika dla integracji Tuya 8-in-1

## Co zostało dodane:

### 1. Config Flow z pełnym UI
- ✅ **Formularz konfiguracji** w Settings → Devices & Services
- ✅ **Walidacja połączenia** w czasie rzeczywistym  
- ✅ **Opcje edycji** konfiguracji bez usuwania integracji
- ✅ **Obsługa błędów** z jasnymi komunikatami
- ✅ **Tłumaczenia** polskie i angielskie

### 2. Funkcje interfejsu:

#### Podczas dodawania integracji:
- **Device ID**: Pole na identyfikator urządzenia z Tuya IoT
- **Local Key**: Pole na klucz lokalny z Tuya IoT  
- **IP Address**: Pole na adres IP urządzenia w sieci lokalnej
- **Protocol Version**: Wybór wersji protokołu (domyślnie 3.5)
- **Scan Interval**: Interwał pobierania danych (domyślnie 30s)

#### Test połączenia:
- Automatyczny test podczas konfiguracji
- Sprawdzenie czy urządzenie odpowiada
- Walidacja czy zwraca dane DPS
- Jasne komunikaty błędów

#### Edycja konfiguracji:
- Opcja "Configure" przy integracji w Devices & Services  
- Możliwość zmiany IP gdy urządzenie zmieni adres
- Aktualizacja innych parametrów bez usuwania integracji

## Jak używać:

### Krok 1: Restart Home Assistant
```bash
# Restart wymagany dla nowych plików
Developer Tools → YAML → Restart Home Assistant
```

### Krok 2: Dodaj integrację przez UI  
1. **Settings** → **Devices & Services**
2. **Add Integration** (prawy dolny róg)
3. Wyszukaj **"Tuya 8-in-1"**
4. Wypełnij formularz:
   - Device ID: `bf70d7388a31ac0421bfyi`
   - Local Key: `(!9xO2G6myyUEz.&`
   - IP Address: `192.168.20.161`  
   - Protocol Version: `3.5`
   - Scan Interval: `30`

### Krok 3: Test i konfiguracja
- Kliknij **Submit**
- System automatycznie sprawdzi połączenie
- Jeśli OK → integracja zostanie dodana
- Jeśli błąd → popraw dane i spróbuj ponownie

### Krok 4: Edycja w przyszłości
1. **Settings** → **Devices & Services** 
2. Znajdź **"Tuya 8-in-1 Tester"**
3. Kliknij **"Configure"**
4. Zmień parametry (np. nowy IP)
5. **Submit** → automatyczny restart integracji

## Zalety nowego UI:

✅ **Bez YAML** - wszystko przez interfejs graficzny  
✅ **Walidacja** - test połączenia przed zapisem  
✅ **Łatwa edycja** - zmiana IP bez usuwania integracji  
✅ **Jasne błędy** - komunikaty pomagają znaleźć problem  
✅ **Dwujęzyczne** - polski i angielski interfejs  

## Rozwiązywanie problemów:

### "Cannot connect to device"
- Sprawdź czy IP jest poprawne  
- Sprawdź czy Device ID i Local Key się zgadzają
- Sprawdź czy urządzenie jest online

### "Invalid data" 
- Zmień Protocol Version na 3.3 lub 3.1
- Sprawdź czy to rzeczywiście urządzenie Tuya 8-in-1

### "Already configured"
- Urządzenie o tym Device ID już istnieje
- Użyj opcji "Configure" zamiast dodawania nowego

## Migracja z YAML:

Jeśli masz konfigurację w `configuration.yaml`:
1. Usuń sekcję `tuya_8in1:` z YAML
2. Restart HA
3. Dodaj integrację przez UI z tymi samymi danymi
