import datetime
import subprocess


def run_radon_report_md(output_file="__raports/radon_report.md"):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header = f"# 📊 Raport Radon (Złożoność)\n\n**Data generowania:** {now}\n\n---\n\n"

    # Analiza złożoności cyklomatycznej
    cc_cmd = ["radon", "cc", "core", "-a"]
    # Analiza maintainability index
    mi_cmd = ["radon", "mi", "core", "-a"]

    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(header)

            # Złożoność cyklomatyczna
            f.write("## Złożoność Cyklomatyczna (CC)\n\n")
            cc_result = subprocess.run(
                cc_cmd, capture_output=True, text=True, check=False
            )
            if cc_result.stdout.strip():
                f.write("```text\n")
                f.write(cc_result.stdout)
                f.write("```\n")
            else:
                f.write("> Brak danych o złożoności cyklomatycznej.\n")

            f.write("\n---\n\n")

            # Maintainability Index
            f.write("## Maintainability Index (MI)\n\n")
            mi_result = subprocess.run(
                mi_cmd, capture_output=True, text=True, check=False
            )
            if mi_result.stdout.strip():
                f.write("```text\n")
                f.write(mi_result.stdout)
                f.write("```\n")
            else:
                f.write("> Brak danych o maintainability index.\n")

            # Błędy
            if cc_result.stderr.strip() or mi_result.stderr.strip():
                f.write("\n## Błędy\n")
                f.write("```text\n")
                if cc_result.stderr.strip():
                    f.write("CC Errors:\n")
                    f.write(cc_result.stderr)
                if mi_result.stderr.strip():
                    f.write("MI Errors:\n")
                    f.write(mi_result.stderr)
                f.write("```\n")

        print(f"✅ Raport radon zapisany do: {output_file}")
    except Exception as e:
        print(f"❌ Błąd podczas generowania raportu radon: {e}")


if __name__ == "__main__":
    run_radon_report_md()
