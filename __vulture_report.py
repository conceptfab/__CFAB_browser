import datetime
import subprocess


def run_vulture_report_md(output_file="__raports/vulture_report.md"):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header = f"# 🦉 Raport Vulture\n\n**Data generowania:** {now}\n\n---\n\n"
    section = "## Wyniki analizy folderu `core`\n\n"
    cmd = ["vulture", "core", "--min-confidence", "80"]  # tylko folder core

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(header)
            f.write(section)
            if result.stdout.strip():
                f.write("```text\n")
                f.write(result.stdout)
                f.write("```\n")
            else:
                f.write("> ✅ Brak nieużywanego kodu wykrytego przez vulture.\n")
            if result.stderr.strip():
                f.write("\n## Błędy\n")
                f.write("```text\n")
                f.write(result.stderr)
                f.write("```\n")
        print(f"✅ Raport zapisany do: {output_file}")
    except Exception as e:
        print(f"❌ Błąd podczas generowania raportu: {e}")


if __name__ == "__main__":
    run_vulture_report_md()
