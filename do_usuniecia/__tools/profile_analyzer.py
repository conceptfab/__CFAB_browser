#!/usr/bin/env python3
"""
Skrypt do profilowania wydajności CFAB Browser z użyciem cProfile
Autor: CFAB Browser Team
Data: 2025-01-05
"""

import argparse
import cProfile
import io
import os
import pstats
import sys
import time
from datetime import datetime
from pathlib import Path


class ProfileAnalyzer:
    """Klasa do analizy profilowania wydajności aplikacji"""

    def __init__(self, output_dir="__raports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    def profile_application(self, script_path="cfab_browser.py", duration=30):
        """
        Profiluje aplikację przez określony czas

        Args:
            script_path (str): Ścieżka do głównego skryptu aplikacji
            duration (int): Czas profilowania w sekundach
        """
        print(f"🔍 Rozpoczynam profilowanie aplikacji: {script_path}")
        print(f"⏱️  Czas profilowania: {duration} sekund")
        print("💡 Aplikacja będzie działać normalnie - możesz ją testować!")
        print("   Profilowanie zakończy się automatycznie po określonym czasie.")
        print()

        # Sprawdź czy plik istnieje
        if not os.path.exists(script_path):
            print(f"❌ Błąd: Plik {script_path} nie istnieje!")
            return False

        # Utwórz nazwę pliku wynikowego
        stats_file = self.output_dir / f"profile_stats_{self.timestamp}.stats"
        report_file = self.output_dir / f"profile_report_{self.timestamp}.txt"

        try:
            # Profilowanie z cProfile
            profiler = cProfile.Profile()
            profiler.enable()

            print("🚀 Uruchamiam aplikację...")
            print("   Możesz teraz normalnie używać aplikacji!")
            print()

            # Uruchom aplikację bezpośrednio (nie w tle)
            import subprocess

            # Uruchom proces i czekaj na zakończenie lub timeout
            process = subprocess.Popen([sys.executable, script_path])

            # Timer do zatrzymania profilowania
            start_time = time.time()

            try:
                # Czekaj na zakończenie procesu lub timeout
                process.wait(timeout=duration)
                print("✅ Aplikacja zakończona przed upływem czasu profilowania")
            except subprocess.TimeoutExpired:
                print(
                    f"⏰ Czas profilowania ({duration}s) minął - zatrzymuję aplikację"
                )
                process.terminate()
                try:
                    process.wait(timeout=5)  # Daj 5 sekund na graceful shutdown
                except subprocess.TimeoutExpired:
                    print("⚠️  Aplikacja nie odpowiada - wymuszam zamknięcie")
                    process.kill()

            profiler.disable()

            print("✅ Profilowanie zakończone")

            # Zapisz statystyki
            profiler.dump_stats(str(stats_file))
            print(f"💾 Statystyki zapisane: {stats_file}")

            # Generuj raport
            self.generate_report(stats_file, report_file)

            return True

        except Exception as e:
            print(f"❌ Błąd podczas profilowania: {e}")
            return False

    def profile_function(self, function, *args, **kwargs):
        """
        Profiluje pojedynczą funkcję

        Args:
            function: Funkcja do sprofilowania
            *args, **kwargs: Argumenty funkcji
        """
        print(f"🔍 Profiluję funkcję: {function.__name__}")

        stats_file = (
            self.output_dir
            / f"function_profile_{function.__name__}_{self.timestamp}.stats"
        )
        report_file = (
            self.output_dir
            / f"function_report_{function.__name__}_{self.timestamp}.txt"
        )

        try:
            profiler = cProfile.Profile()
            profiler.enable()

            # Wywołaj funkcję
            result = function(*args, **kwargs)

            profiler.disable()

            # Zapisz statystyki
            profiler.dump_stats(str(stats_file))
            print(f"💾 Statystyki zapisane: {stats_file}")

            # Generuj raport
            self.generate_report(stats_file, report_file)

            return result

        except Exception as e:
            print(f"❌ Błąd podczas profilowania funkcji: {e}")
            return None

    def generate_report(self, stats_file, report_file, top_n=50):
        """
        Generuje czytelny raport z wyników profilowania

        Args:
            stats_file (Path): Plik ze statystykami
            report_file (Path): Plik raportu
            top_n (int): Liczba top funkcji do wyświetlenia
        """
        print(f"📊 Generuję raport: {report_file}")

        try:
            # Wczytaj statystyki
            stats = pstats.Stats(str(stats_file))

            # Przygotuj raport
            report = []
            report.append("=" * 80)
            report.append("📊 RAPORT PROFILOWANIA CFAB BROWSER")
            report.append("=" * 80)
            report.append(
                f"Data generowania: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            report.append(f"Plik statystyk: {stats_file.name}")
            report.append("")

            # Statystyki ogólne
            report.append("📈 STATYSTYKI OGÓLNE")
            report.append("-" * 40)

            # Pobierz statystyki ogólne
            stats_stream = io.StringIO()
            stats.stream = stats_stream
            stats.print_stats()
            stats_content = stats_stream.getvalue()

            # Wyciągnij pierwsze linie z ogólnymi statystykami
            lines = stats_content.split("\n")
            for line in lines[:10]:  # Pierwsze 10 linii
                if line.strip():
                    report.append(line)

            report.append("")

            # Top funkcje według czasu
            report.append("🏆 TOP FUNKCJE WEDŁUG CZASU WYKONANIA")
            report.append("-" * 50)

            stats_stream = io.StringIO()
            stats.stream = stats_stream
            stats.sort_stats("cumulative")
            stats.print_stats(top_n)
            stats_content = stats_stream.getvalue()

            # Wyciągnij funkcje z raportu
            lines = stats_content.split("\n")
            for line in lines[3 : top_n + 3]:  # Pomiń nagłówek
                if line.strip() and "function" in line:
                    report.append(line)

            report.append("")

            # Top funkcje według liczby wywołań
            report.append("📞 TOP FUNKCJE WEDŁUG LICZBY WYWOŁAŃ")
            report.append("-" * 50)

            stats_stream = io.StringIO()
            stats.stream = stats_stream
            stats.sort_stats("calls")
            stats.print_stats(top_n)
            stats_content = stats_stream.getvalue()

            lines = stats_content.split("\n")
            for line in lines[3 : top_n + 3]:
                if line.strip() and "function" in line:
                    report.append(line)

            report.append("")

            # Analiza wąskich gardeł
            report.append("🔍 ANALIZA WĄSKICH GARDEŁ")
            report.append("-" * 30)

            # Znajdź funkcje z największym czasem wykonania
            stats.sort_stats("cumulative")
            top_functions = []

            for func, (cc, nc, tt, ct, callers) in stats.stats.items():
                if ct > 0.1:  # Funkcje z czasem > 0.1s
                    top_functions.append((func, ct, nc))

            top_functions.sort(key=lambda x: x[1], reverse=True)

            if top_functions:
                report.append("Funkcje z największym czasem wykonania (>0.1s):")
                for func, ct, nc in top_functions[:10]:
                    report.append(f"  {func[2]} - {ct:.3f}s ({nc} wywołań)")
            else:
                report.append("Brak funkcji z czasem wykonania >0.1s")

            report.append("")

            # Rekomendacje
            report.append("💡 REKOMENDACJE OPTYMALIZACYJNE")
            report.append("-" * 40)

            if top_functions:
                report.append("1. Sprawdź funkcje z największym czasem wykonania")
                report.append("2. Rozważ cachowanie wyników kosztownych operacji")
                report.append("3. Zoptymalizuj pętle i operacje I/O")
                report.append("4. Użyj profilowania liniowego dla szczegółowej analizy")
            else:
                report.append("✅ Wydajność aplikacji wygląda dobrze!")
                report.append("   Brak oczywistych wąskich gardeł")

            report.append("")
            report.append("=" * 80)

            # Zapisz raport
            with open(report_file, "w", encoding="utf-8") as f:
                f.write("\n".join(report))

            print(f"✅ Raport zapisany: {report_file}")

            # Wyświetl podsumowanie
            print("\n📋 PODSUMOWANIE:")
            print(f"   📁 Statystyki: {stats_file}")
            print(f"   📄 Raport: {report_file}")
            print(f"   🏆 Przeanalizowano top {top_n} funkcji")

        except Exception as e:
            print(f"❌ Błąd podczas generowania raportu: {e}")

    def analyze_existing_stats(self, stats_file, top_n=50):
        """
        Analizuje istniejący plik statystyk

        Args:
            stats_file (str): Ścieżka do pliku .stats
            top_n (int): Liczba top funkcji do wyświetlenia
        """
        stats_path = Path(stats_file)
        if not stats_path.exists():
            print(f"❌ Plik {stats_file} nie istnieje!")
            return

        report_file = (
            self.output_dir / f"analysis_{stats_path.stem}_{self.timestamp}.txt"
        )
        self.generate_report(stats_path, report_file, top_n)


def main():
    """Główna funkcja skryptu"""
    parser = argparse.ArgumentParser(description="Profilowanie CFAB Browser")
    parser.add_argument(
        "--script",
        default="cfab_browser.py",
        help="Ścieżka do głównego skryptu aplikacji",
    )
    parser.add_argument(
        "--duration", type=int, default=30, help="Czas profilowania w sekundach"
    )
    parser.add_argument("--stats", help="Analizuj istniejący plik .stats")
    parser.add_argument(
        "--top", type=int, default=50, help="Liczba top funkcji do wyświetlenia"
    )

    args = parser.parse_args()

    analyzer = ProfileAnalyzer()

    if args.stats:
        print(f"📊 Analizuję istniejący plik: {args.stats}")
        analyzer.analyze_existing_stats(args.stats, args.top)
    else:
        print("🚀 Rozpoczynam profilowanie aplikacji...")
        success = analyzer.profile_application(args.script, args.duration)

        if success:
            print("✅ Profilowanie zakończone pomyślnie!")
        else:
            print("❌ Profilowanie nie powiodło się!")
            sys.exit(1)


if __name__ == "__main__":
    main()
