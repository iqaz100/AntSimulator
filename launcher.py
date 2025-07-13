#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Launcher dla Symulatora Mrówek
Umożliwia łatwe uruchamianie symulatora z różnymi konfiguracjami
"""

import os
import sys
import subprocess
from example_configs import load_config

def print_banner():
    """Wyświetla banner launcher'a"""
    print("=" * 60)
    print("🐜 SYMULATOR MRÓWEK - LAUNCHER 🐜")
    print("=" * 60)
    print()

def print_configs():
    """Wyświetla dostępne konfiguracje"""
    configs = {
        '1': ('basic', 'Podstawowy symulator'),
        '2': ('obstacles', 'Z przeszkodami'),
        '3': ('advanced', 'Zaawansowana nawigacja'),
        '4': ('specialization', 'Ze specjalizacją mrówek'),
        '5': ('experimental', 'Eksperymentalna'),
        '6': ('slow', 'Wolny symulator'),
        '7': ('fast', 'Szybki symulator'),
        '8': ('large', 'Duża kolonia'),
        '9': ('small', 'Mała kolonia'),
        '10': ('maze', 'Labirynt'),
    }
    
    print("Dostępne konfiguracje:")
    print("-" * 40)
    for key, (config_name, description) in configs.items():
        print(f"{key:2}. {config_name:15} - {description}")
    print()

def get_user_choice():
    """Pobiera wybór użytkownika"""
    while True:
        try:
            choice = input("Wybierz konfigurację (1-10) lub 'q' aby wyjść: ").strip()
            if choice.lower() == 'q':
                return None
            
            choice_num = int(choice)
            if 1 <= choice_num <= 10:
                configs = {
                    1: 'basic', 2: 'obstacles', 3: 'advanced', 4: 'specialization',
                    5: 'experimental', 6: 'slow', 7: 'fast', 8: 'large', 9: 'small', 10: 'maze'
                }
                return configs[choice_num]
            else:
                print("❌ Nieprawidłowy wybór. Wybierz liczbę od 1 do 10.")
        except ValueError:
            print("❌ Nieprawidłowy wybór. Wybierz liczbę od 1 do 10.")

def apply_config(config_name):
    """Stosuje wybraną konfigurację"""
    print(f"🔧 Stosowanie konfiguracji: {config_name}")
    
    # Załaduj konfigurację
    config = load_config(config_name)
    
    # Stwórz tymczasowy plik config.py z wybraną konfiguracją
    config_content = "# Tymczasowa konfiguracja wygenerowana przez launcher\n"
    config_content += "# Oryginalny config.py został zachowany jako config_backup.py\n\n"
    
    for key, value in config.items():
        config_content += f"{key} = {value}\n"
    
    # Zachowaj oryginalny config.py
    if os.path.exists('config.py'):
        if not os.path.exists('config_backup.py'):
            os.rename('config.py', 'config_backup.py')
            print("💾 Zachowano oryginalny config.py jako config_backup.py")
    
    # Zapisz nową konfigurację
    with open('config.py', 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print(f"✅ Konfiguracja '{config_name}' została zastosowana")
    print()

def restore_original_config():
    """Przywraca oryginalną konfigurację"""
    if os.path.exists('config_backup.py'):
        if os.path.exists('config.py'):
            os.remove('config.py')
        os.rename('config_backup.py', 'config.py')
        print("🔄 Przywrócono oryginalną konfigurację")

def run_simulator():
    """Uruchamia symulator"""
    print("🚀 Uruchamianie symulatora...")
    print("💡 Wskazówki:")
    print("   - ESC: Wyjście")
    print("   - SPACJA: Dodaj mrówki")
    print("   - F: Dodaj jedzenie")
    print("   - O: Dodaj przeszkodę")
    print("   - R: Resetuj przeszkody")
    print()
    
    try:
        # Uruchom symulator
        subprocess.run([sys.executable, 'ant_simulator.py'])
    except KeyboardInterrupt:
        print("\n⏹️  Symulator zatrzymany przez użytkownika")
    except Exception as e:
        print(f"❌ Błąd podczas uruchamiania symulatora: {e}")

def main():
    """Główna funkcja launcher'a"""
    print_banner()
    
    while True:
        print_configs()
        choice = get_user_choice()
        
        if choice is None:
            print("👋 Do widzenia!")
            break
        
        apply_config(choice)
        
        # Pytaj czy uruchomić symulator
        run_choice = input("Czy uruchomić symulator? (t/n): ").strip().lower()
        if run_choice in ['t', 'tak', 'y', 'yes']:
            run_simulator()
        
        # Pytaj czy przywrócić oryginalną konfigurację
        restore_choice = input("Czy przywrócić oryginalną konfigurację? (t/n): ").strip().lower()
        if restore_choice in ['t', 'tak', 'y', 'yes']:
            restore_original_config()
        
        print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Do widzenia!")
        restore_original_config() 