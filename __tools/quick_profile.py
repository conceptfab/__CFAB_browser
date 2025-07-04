#!/usr/bin/env python3
"""
Szybkie profilowanie konkretnych funkcji CFAB Browser
Autor: CFAB Browser Team
Data: 2025-01-05
"""

import cProfile
import pstats
import time
from pathlib import Path


def quick_profile_function(func, *args, iterations=1000, **kwargs):
    """
    Szybko profiluje funkcję przez określoną liczbę iteracji

    Args:
        func: Funkcja do sprofilowania
        *args: Argumenty funkcji
        iterations: Liczba iteracji
        **kwargs: Dodatkowe argumenty funkcji
    """
    print(f"🔍 Szybkie profilowanie: {func.__name__}")
    print(f"📊 Iteracje: {iterations}")

    # Profilowanie
    profiler = cProfile.Profile()
    profiler.enable()

    start_time = time.time()

    for _ in range(iterations):
        result = func(*args, **kwargs)

    end_time = time.time()
    profiler.disable()

    # Statystyki
    total_time = end_time - start_time
    avg_time = total_time / iterations

    print(f"⏱️  Całkowity czas: {total_time:.4f}s")
    print(f"📈 Średni czas: {avg_time:.6f}s")
    print(f"🚀 Operacje/s: {iterations/total_time:.0f}")

    # Generuj raport
    stats = pstats.Stats(profiler)
    stats.sort_stats("cumulative")

    print("\n🏆 TOP 10 FUNKCJI:")
    print("-" * 50)
    stats.print_stats(10)

    return result


def profile_import_time(module_name):
    """
    Profiluje czas importowania modułu

    Args:
        module_name: Nazwa modułu do zaimportowania
    """
    print(f"📦 Profilowanie importu: {module_name}")

    profiler = cProfile.Profile()
    profiler.enable()

    start_time = time.time()

    try:
        __import__(module_name)
        import_time = time.time() - start_time

        profiler.disable()

        print(f"⏱️  Czas importu: {import_time:.4f}s")

        # Generuj raport
        stats = pstats.Stats(profiler)
        stats.sort_stats("cumulative")

        print("\n🏆 TOP 10 OPERACJI IMPORTU:")
        print("-" * 50)
        stats.print_stats(10)

    except ImportError as e:
        print(f"❌ Błąd importu: {e}")
        return False

    return True


def profile_file_operations(file_path, operation="read"):
    """
    Profiluje operacje na plikach

    Args:
        file_path: Ścieżka do pliku
        operation: Typ operacji ('read', 'write', 'exists')
    """
    print(f"📁 Profilowanie operacji na pliku: {file_path}")
    print(f"🔧 Operacja: {operation}")

    profiler = cProfile.Profile()
    profiler.enable()

    if operation == "read":
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            print(f"✅ Wczytano {len(content)} znaków")
        except Exception as e:
            print(f"❌ Błąd odczytu: {e}")
            return False

    elif operation == "write":
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("Test content for profiling")
            print("✅ Zapisano plik")
        except Exception as e:
            print(f"❌ Błąd zapisu: {e}")
            return False

    elif operation == "exists":
        exists = Path(file_path).exists()
        print(f"✅ Plik istnieje: {exists}")

    profiler.disable()

    # Generuj raport
    stats = pstats.Stats(profiler)
    stats.sort_stats("cumulative")

    print("\n🏆 TOP 10 OPERACJI NA PLIKACH:")
    print("-" * 50)
    stats.print_stats(10)

    return True


def profile_memory_usage(func, *args, **kwargs):
    """
    Profiluje użycie pamięci przez funkcję

    Args:
        func: Funkcja do sprofilowania
        *args, **kwargs: Argumenty funkcji
    """
    print(f"🧠 Profilowanie pamięci: {func.__name__}")

    try:
        import os

        import psutil

        process = psutil.Process(os.getpid())
        memory_before = process.memory_info().rss / 1024 / 1024  # MB

        profiler = cProfile.Profile()
        profiler.enable()

        result = func(*args, **kwargs)

        profiler.disable()

        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        memory_diff = memory_after - memory_before

        print(f"📊 Pamięć przed: {memory_before:.2f} MB")
        print(f"📊 Pamięć po: {memory_after:.2f} MB")
        print(f"📈 Różnica: {memory_diff:.2f} MB")

        # Generuj raport
        stats = pstats.Stats(profiler)
        stats.sort_stats("cumulative")

        print("\n🏆 TOP 10 OPERACJI:")
        print("-" * 50)
        stats.print_stats(10)

        return result

    except ImportError:
        print("❌ psutil nie jest zainstalowany")
        print("   Zainstaluj: pip install psutil")
        return None


def main():
    """Główna funkcja z przykładami użycia"""
    print("🚀 SZYBKIE PROFILOWANIE CFAB BROWSER")
    print("=" * 50)

    # Przykład 1: Profilowanie funkcji matematycznej
    print("\n1️⃣ Profilowanie funkcji matematycznej:")

    def fibonacci(n):
        if n <= 1:
            return n
        return fibonacci(n - 1) + fibonacci(n - 2)

    quick_profile_function(fibonacci, 20, iterations=100)

    # Przykład 2: Profilowanie importu
    print("\n2️⃣ Profilowanie importu modułu:")
    profile_import_time("pathlib")

    # Przykład 3: Profilowanie operacji na plikach
    print("\n3️⃣ Profilowanie operacji na plikach:")
    test_file = "test_profile.txt"
    profile_file_operations(test_file, "write")
    profile_file_operations(test_file, "read")

    # Usuń plik testowy
    try:
        Path(test_file).unlink()
    except FileNotFoundError:
        pass

    # Przykład 4: Profilowanie pamięci
    print("\n4️⃣ Profilowanie pamięci:")

    def create_large_list():
        return list(range(100000))

    profile_memory_usage(create_large_list)

    print("\n✅ Szybkie profilowanie zakończone!")


if __name__ == "__main__":
    main()
