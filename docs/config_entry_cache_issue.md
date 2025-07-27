# Analiza problemu z cache'em konfiguracji Home Assistant

## Problem z Config Entry Cache

### Co się dzieje podczas restartu HA:
1. HA wczytuje config entries z bazy danych
2. Stara konfiguracja (ze starym IP) jest przywracana
3. Nowa konfiguracja z YAML/UI nie jest uwzględniana

### Co się dzieje podczas usuwania i dodawania integracji:
1. Usunięcie = kasowanie config entry z bazy HA
2. Dodanie = utworzenie nowego config entry z aktualnymi danymi
3. Nowa konfiguracja jest zapisana w bazie

## Rozwiązania na przyszłość:

### Opcja 1: Edycja istniejącej integracji
- Settings → Devices & Services 
- Znajdź integrację "Tuya 8-in-1"
- Kliknij "Configure" lub "Options"
- Zmień IP address

### Opcja 2: Reload integration (jeśli obsługiwane)
- Settings → Devices & Services
- Kliknij na integrację 
- "Reload" (jeśli dostępne)

### Opcja 3: Development reload
- Developer Tools → YAML → Reload: All YAML configurations
- Ale to nie zawsze działa z custom components

### Opcja 4: Core restart (nie zwykły restart)
- Settings → System → Hardware → Restart
- "Restart Home Assistant Core" (nie "Restart System")

## Najlepsze praktyki:

1. **Zawsze używaj opcji "Configure"** w UI zamiast usuwania całej integracji
2. **Sprawdź czy integracja ma opcję reload**
3. **Dla custom components** - czasem usunięcie/dodanie jest jedyną opcją

## Dodatkowa diagnostyka:

Możemy dodać do naszej integracji opcję reload i konfiguracji przez UI.
