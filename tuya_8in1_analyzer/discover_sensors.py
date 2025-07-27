#!/usr/bin/env python3
"""
Tuya 8-in-1 Water Quality Tester - Device Analyzer
Skrypt do odkrywania wszystkich dostępnych czujników i punktów danych.
"""

import asyncio
import json
import logging
import os
from typing import Dict, Any, List
from datetime import datetime

try:
    import tinytuya
    from tuya_connector import TuyaOpenAPI, TUYA_LOGGER
except ImportError as e:
    print("Błąd importu bibliotek Tuya:")
    print("Uruchom: pip install tinytuya tuya-connector-python")
    print(f"Szczegóły błędu: {e}")
    exit(1)

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TuyaDeviceAnalyzer:
    """Analizator urządzenia Tuya 8-in-1"""
    
    def __init__(self, config_file: str = "tuya_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        self.device = None
        self.api = None
        
    def load_config(self) -> Dict[str, Any]:
        """Wczytuje konfigurację z pliku JSON"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Tworzy przykładowy plik konfiguracji
            sample_config = {
                "device_id": "YOUR_DEVICE_ID",
                "local_key": "YOUR_LOCAL_KEY", 
                "ip_address": "192.168.1.XXX",
                "tuya_cloud": {
                    "access_id": "YOUR_ACCESS_ID",
                    "access_secret": "YOUR_ACCESS_SECRET",
                    "endpoint": "https://openapi.tuyaeu.com"
                }
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(sample_config, f, indent=2, ensure_ascii=False)
            
            logger.error(f"Utworzono przykładowy plik {self.config_file}")
            logger.error("Wypełnij go swoimi danymi Tuya i uruchom ponownie")
            return sample_config
    
    def setup_local_connection(self, version=None):
        """Konfiguruje połączenie lokalne z urządzeniem"""
        try:
            # Używa wersji z konfiguracji lub domyślnej
            if version is None:
                version = self.config.get("protocol_version", 3.5)
                
            self.device = tinytuya.Device(
                dev_id=self.config["device_id"],
                address=self.config["ip_address"],
                local_key=self.config["local_key"],
                version=version
            )
            self.device.set_socketTimeout(5)  # Timeout 5 sekund
            logger.info(f"Połączenie lokalne skonfigurowane (wersja {version})")
        except Exception as e:
            logger.error(f"Błąd konfiguracji połączenia lokalnego: {e}")
    
    def setup_cloud_connection(self):
        """Konfiguruje połączenie z Tuya Cloud API"""
        try:
            cloud_config = self.config.get("tuya_cloud", {})
            self.api = TuyaOpenAPI(
                endpoint=cloud_config["endpoint"],
                access_id=cloud_config["access_id"],
                access_secret=cloud_config["access_secret"]
            )
            self.api.connect()
            logger.info("Połączenie z Tuya Cloud skonfigurowane")
        except Exception as e:
            logger.error(f"Błąd konfiguracji Tuya Cloud: {e}")
    
    def scan_local_device(self) -> Dict[str, Any]:
        """Skanuje urządzenie lokalnie"""
        results = {}
        
        # Używa wersji 3.5 która działa
        logger.info("Skanowanie z wersją protokołu 3.5...")
        try:
            self.setup_local_connection(3.5)
            
            # Podstawowy test połączenia
            logger.info("Testowanie połączenia...")
            heartbeat = self.device.heartbeat()
            logger.info(f"Heartbeat: {heartbeat}")
            
            # Pobiera status urządzenia
            logger.info("Pobieranie statusu urządzenia...")
            status = self.device.status()
            logger.info(f"Status: {status}")
            
            if status and isinstance(status, dict) and "dps" in status:
                results["version_3.5"] = {
                    "status": status,
                    "heartbeat": heartbeat,
                    "success": True,
                    "dps_count": len(status["dps"])
                }
                logger.info(f"✅ Sukces! Znaleziono {len(status['dps'])} punktów DPS")
                
                # Dodatkowo próbuj pobrać więcej danych
                try:
                    logger.info("Próba wykrycia dodatkowych DPS...")
                    dps_data = self.device.detect_available_dps()
                    results["available_dps"] = dps_data
                    logger.info(f"Dodatkowe DPS: {dps_data}")
                except Exception as e:
                    logger.warning(f"Nie udało się wykryć dodatkowych DPS: {e}")
                    
            else:
                results["version_3.5"] = {
                    "status": status,
                    "heartbeat": heartbeat,
                    "success": False,
                    "note": "Brak danych DPS lub błąd odpowiedzi"
                }
                    
        except Exception as e:
            logger.error(f"Błąd skanowania lokalnego: {e}")
            results["error"] = str(e)
        
        return results
    
    def scan_cloud_device(self) -> Dict[str, Any]:
        """Skanuje urządzenie przez Tuya Cloud API"""
        if not self.api:
            self.setup_cloud_connection()
        
        results = {}
        device_id = self.config["device_id"]
        
        try:
            # Informacje o urządzeniu
            logger.info("Pobieranie informacji o urządzeniu z chmury...")
            device_info = self.api.get(f"/v1.0/devices/{device_id}")
            results["device_info"] = device_info
            
            # Status urządzenia
            logger.info("Pobieranie statusu z chmury...")
            device_status = self.api.get(f"/v1.0/devices/{device_id}/status")
            results["device_status"] = device_status
            
            # Specyfikacja urządzenia
            logger.info("Pobieranie specyfikacji urządzenia...")
            device_spec = self.api.get(f"/v1.0/devices/{device_id}/specifications")
            results["device_specifications"] = device_spec
            
            # Funkcje urządzenia
            logger.info("Pobieranie funkcji urządzenia...")
            device_functions = self.api.get(f"/v1.0/devices/{device_id}/functions")
            results["device_functions"] = device_functions
            
        except Exception as e:
            logger.error(f"Błąd skanowania chmury: {e}")
            results["error"] = str(e)
        
        return results
    
    def analyze_sensor_mappings(self, local_data: Dict, cloud_data: Dict) -> Dict[str, Any]:
        """Analizuje mapowania czujników"""
        mappings = {
            "timestamp": datetime.now().isoformat(),
            "sensor_mappings": {},
            "analysis": {}
        }
        
        # Analiza danych lokalnych
        logger.info("Analizuję dane lokalne...")
        for version_key, version_data in local_data.items():
            if version_key.startswith("version_") and version_data.get("success"):
                status = version_data.get("status", {})
                if isinstance(status, dict) and "dps" in status:
                    logger.info(f"Znaleziono dane DPS w {version_key}")
                    for key, value in status["dps"].items():
                        mappings["sensor_mappings"][f"dps_{key}"] = {
                            "value": value,
                            "type": type(value).__name__,
                            "source": f"local_{version_key}"
                        }
        
        # Analiza danych z chmury
        logger.info("Analizuję dane z chmury...")
        if "device_status" in cloud_data and cloud_data["device_status"].get("success"):
            for item in cloud_data["device_status"]["result"]:
                code = item.get("code")
                value = item.get("value")
                if code:
                    mappings["sensor_mappings"][code] = {
                        "value": value,
                        "type": type(value).__name__,
                        "source": "cloud"
                    }
        
        # Potencjalne mapowania czujników
        potential_sensors = {
            "temp": ["temperature", "temperatura"],
            "ph": ["ph", "pH"],
            "orp": ["orp", "redox"],
            "tds": ["tds", "dissolved_solids"],
            "salinity": ["salinity", "zasolenie"],
            "ec": ["ec", "conductivity"],
            "do": ["do", "dissolved_oxygen"],
            "turbidity": ["turbidity", "mętność"]
        }
        
        mappings["analysis"]["potential_sensors"] = potential_sensors
        
        return mappings
    
    def save_results(self, results: Dict[str, Any], filename: str = None):
        """Zapisuje wyniki do pliku JSON"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"tuya_analysis_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"Wyniki zapisane do: {filename}")
    
    async def run_full_analysis(self):
        """Uruchamia pełną analizę urządzenia"""
        logger.info("=== Rozpoczęcie analizy urządzenia Tuya 8-in-1 ===")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "device_id": self.config["device_id"],
            "local_scan": {},
            "cloud_scan": {},
            "analysis": {}
        }
        
        # Skanowanie lokalne
        logger.info("\n--- Skanowanie lokalne ---")
        results["local_scan"] = self.scan_local_device()
        
        # Skanowanie przez chmurę
        logger.info("\n--- Skanowanie przez Tuya Cloud ---")
        results["cloud_scan"] = self.scan_cloud_device()
        
        # Analiza mapowań
        logger.info("\n--- Analiza mapowań czujników ---")
        results["analysis"] = self.analyze_sensor_mappings(
            results["local_scan"], 
            results["cloud_scan"]
        )
        
        # Zapisanie wyników
        self.save_results(results)
        
        logger.info("=== Analiza zakończona ===")
        return results

def main():
    """Główna funkcja programu"""
    print("🔍 Tuya 8-in-1 Water Quality Tester - Analyzer")
    print("=" * 50)
    
    analyzer = TuyaDeviceAnalyzer()
    
    # Sprawdza konfigurację
    if analyzer.config["device_id"] == "YOUR_DEVICE_ID":
        print("❌ Najpierw skonfiguruj plik tuya_config.json")
        print("   Wypełnij Device ID, Local Key i adres IP urządzenia")
        return
    
    # Uruchamia analizę
    try:
        results = asyncio.run(analyzer.run_full_analysis())
        
        print("\n✅ Analiza zakończona pomyślnie!")
        print("\nWażne informacje:")
        
        if "sensor_mappings" in results["analysis"]:
            print(f"📊 Znaleziono {len(results['analysis']['sensor_mappings'])} punktów danych")
            
            print("\n🔗 Mapowania czujników:")
            for key, data in results["analysis"]["sensor_mappings"].items():
                print(f"  {key}: {data['value']} ({data['type']})")
        
        print("\n📋 Następne kroki:")
        print("1. Sprawdź plik wyników JSON")
        print("2. Zidentyfikuj czujniki pH i ORP")
        print("3. Przejdź do konfiguracji custom_components")
        
    except Exception as e:
        logger.error(f"Błąd podczas analizy: {e}")
        print("❌ Analiza nie powiodła się. Sprawdź logi powyżej.")

if __name__ == "__main__":
    main()
