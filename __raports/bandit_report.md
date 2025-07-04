# 🛡️ Raport Bandit (Bezpieczeństwo)

**Data generowania:** 2025-07-05 01:25:45

---

## Wyniki analizy bezpieczeństwa folderu `core`

```text
Run started:2025-07-04 23:25:47.354455

Test results:
>> Issue: [B404:blacklist] Consider possible security implications associated with the subprocess module.
   Severity: Low   Confidence: High
   CWE: CWE-78 (https://cwe.mitre.org/data/definitions/78.html)
   More Info: https://bandit.readthedocs.io/en/1.8.5/blacklists/blacklist_imports.html#b404-import-subprocess
   Location: core\file_utils.py:8:0
7	import os
8	import subprocess
9	import sys

--------------------------------------------------
>> Issue: [B603:subprocess_without_shell_equals_true] subprocess call - check for execution of untrusted input.
   Severity: Low   Confidence: High
   CWE: CWE-78 (https://cwe.mitre.org/data/definitions/78.html)
   More Info: https://bandit.readthedocs.io/en/1.8.5/plugins/b603_subprocess_without_shell_equals_true.html
   Location: core\file_utils.py:27:8
26	    try:
27	        subprocess.run(
28	            [command, "--version"], capture_output=True, timeout=5, check=False
29	        )
30	        return True

--------------------------------------------------
>> Issue: [B607:start_process_with_partial_path] Starting a process with a partial executable path
   Severity: Low   Confidence: High
   CWE: CWE-78 (https://cwe.mitre.org/data/definitions/78.html)
   More Info: https://bandit.readthedocs.io/en/1.8.5/plugins/b607_start_process_with_partial_path.html
   Location: core\file_utils.py:78:12
77	                return False
78	            subprocess.run(["explorer", normalized_path], check=True, timeout=10)
79	        elif sys.platform == "darwin":  # macOS

--------------------------------------------------
>> Issue: [B603:subprocess_without_shell_equals_true] subprocess call - check for execution of untrusted input.
   Severity: Low   Confidence: High
   CWE: CWE-78 (https://cwe.mitre.org/data/definitions/78.html)
   More Info: https://bandit.readthedocs.io/en/1.8.5/plugins/b603_subprocess_without_shell_equals_true.html
   Location: core\file_utils.py:78:12
77	                return False
78	            subprocess.run(["explorer", normalized_path], check=True, timeout=10)
79	        elif sys.platform == "darwin":  # macOS

--------------------------------------------------
>> Issue: [B607:start_process_with_partial_path] Starting a process with a partial executable path
   Severity: Low   Confidence: High
   CWE: CWE-78 (https://cwe.mitre.org/data/definitions/78.html)
   More Info: https://bandit.readthedocs.io/en/1.8.5/plugins/b607_start_process_with_partial_path.html
   Location: core\file_utils.py:83:12
82	                return False
83	            subprocess.run(["open", normalized_path], check=True, timeout=10)
84	        else:  # Linux

--------------------------------------------------
>> Issue: [B603:subprocess_without_shell_equals_true] subprocess call - check for execution of untrusted input.
   Severity: Low   Confidence: High
   CWE: CWE-78 (https://cwe.mitre.org/data/definitions/78.html)
   More Info: https://bandit.readthedocs.io/en/1.8.5/plugins/b603_subprocess_without_shell_equals_true.html
   Location: core\file_utils.py:83:12
82	                return False
83	            subprocess.run(["open", normalized_path], check=True, timeout=10)
84	        else:  # Linux

--------------------------------------------------
>> Issue: [B607:start_process_with_partial_path] Starting a process with a partial executable path
   Severity: Low   Confidence: High
   CWE: CWE-78 (https://cwe.mitre.org/data/definitions/78.html)
   More Info: https://bandit.readthedocs.io/en/1.8.5/plugins/b607_start_process_with_partial_path.html
   Location: core\file_utils.py:88:12
87	                return False
88	            subprocess.run(["xdg-open", normalized_path], check=True, timeout=10)
89	        logger.info(f"Otworzono ścieżkę w eksploratorze: {normalized_path}")

--------------------------------------------------
>> Issue: [B603:subprocess_without_shell_equals_true] subprocess call - check for execution of untrusted input.
   Severity: Low   Confidence: High
   CWE: CWE-78 (https://cwe.mitre.org/data/definitions/78.html)
   More Info: https://bandit.readthedocs.io/en/1.8.5/plugins/b603_subprocess_without_shell_equals_true.html
   Location: core\file_utils.py:88:12
87	                return False
88	            subprocess.run(["xdg-open", normalized_path], check=True, timeout=10)
89	        logger.info(f"Otworzono ścieżkę w eksploratorze: {normalized_path}")

--------------------------------------------------
>> Issue: [B606:start_process_with_no_shell] Starting a process without a shell.
   Severity: Low   Confidence: Medium
   CWE: CWE-78 (https://cwe.mitre.org/data/definitions/78.html)
   More Info: https://bandit.readthedocs.io/en/1.8.5/plugins/b606_start_process_with_no_shell.html
   Location: core\file_utils.py:139:12
138	        if sys.platform == "win32":
139	            os.startfile(path)
140	        elif sys.platform == "darwin":  # macOS

--------------------------------------------------
>> Issue: [B607:start_process_with_partial_path] Starting a process with a partial executable path
   Severity: Low   Confidence: High
   CWE: CWE-78 (https://cwe.mitre.org/data/definitions/78.html)
   More Info: https://bandit.readthedocs.io/en/1.8.5/plugins/b607_start_process_with_partial_path.html
   Location: core\file_utils.py:144:12
143	                return False
144	            subprocess.run(["open", path], check=True, timeout=10)
145	        else:  # Linux

--------------------------------------------------
>> Issue: [B603:subprocess_without_shell_equals_true] subprocess call - check for execution of untrusted input.
   Severity: Low   Confidence: High
   CWE: CWE-78 (https://cwe.mitre.org/data/definitions/78.html)
   More Info: https://bandit.readthedocs.io/en/1.8.5/plugins/b603_subprocess_without_shell_equals_true.html
   Location: core\file_utils.py:144:12
143	                return False
144	            subprocess.run(["open", path], check=True, timeout=10)
145	        else:  # Linux

--------------------------------------------------
>> Issue: [B607:start_process_with_partial_path] Starting a process with a partial executable path
   Severity: Low   Confidence: High
   CWE: CWE-78 (https://cwe.mitre.org/data/definitions/78.html)
   More Info: https://bandit.readthedocs.io/en/1.8.5/plugins/b607_start_process_with_partial_path.html
   Location: core\file_utils.py:149:12
148	                return False
149	            subprocess.run(["xdg-open", path], check=True, timeout=10)
150	        logger.info(f"Otworzono plik w domyślnej aplikacji: {path}")

--------------------------------------------------
>> Issue: [B603:subprocess_without_shell_equals_true] subprocess call - check for execution of untrusted input.
   Severity: Low   Confidence: High
   CWE: CWE-78 (https://cwe.mitre.org/data/definitions/78.html)
   More Info: https://bandit.readthedocs.io/en/1.8.5/plugins/b603_subprocess_without_shell_equals_true.html
   Location: core\file_utils.py:149:12
148	                return False
149	            subprocess.run(["xdg-open", path], check=True, timeout=10)
150	        logger.info(f"Otworzono plik w domyślnej aplikacji: {path}")

--------------------------------------------------
>> Issue: [B404:blacklist] Consider possible security implications associated with the subprocess module.
   Severity: Low   Confidence: High
   CWE: CWE-78 (https://cwe.mitre.org/data/definitions/78.html)
   More Info: https://bandit.readthedocs.io/en/1.8.5/blacklists/blacklist_imports.html#b404-import-subprocess
   Location: core\pairing_tab.py:3:0
2	import os
3	import subprocess
4	import sys

--------------------------------------------------
>> Issue: [B606:start_process_with_no_shell] Starting a process without a shell.
   Severity: Low   Confidence: Medium
   CWE: CWE-78 (https://cwe.mitre.org/data/definitions/78.html)
   More Info: https://bandit.readthedocs.io/en/1.8.5/plugins/b606_start_process_with_no_shell.html
   Location: core\pairing_tab.py:257:16
256	            if sys.platform == "win32":
257	                os.startfile(full_path)
258	            elif sys.platform == "darwin":  # macOS

--------------------------------------------------
>> Issue: [B607:start_process_with_partial_path] Starting a process with a partial executable path
   Severity: Low   Confidence: High
   CWE: CWE-78 (https://cwe.mitre.org/data/definitions/78.html)
   More Info: https://bandit.readthedocs.io/en/1.8.5/plugins/b607_start_process_with_partial_path.html
   Location: core\pairing_tab.py:259:16
258	            elif sys.platform == "darwin":  # macOS
259	                subprocess.run(["open", full_path], check=True, timeout=10)
260	            else:  # linux

--------------------------------------------------
>> Issue: [B603:subprocess_without_shell_equals_true] subprocess call - check for execution of untrusted input.
   Severity: Low   Confidence: High
   CWE: CWE-78 (https://cwe.mitre.org/data/definitions/78.html)
   More Info: https://bandit.readthedocs.io/en/1.8.5/plugins/b603_subprocess_without_shell_equals_true.html
   Location: core\pairing_tab.py:259:16
258	            elif sys.platform == "darwin":  # macOS
259	                subprocess.run(["open", full_path], check=True, timeout=10)
260	            else:  # linux

--------------------------------------------------
>> Issue: [B607:start_process_with_partial_path] Starting a process with a partial executable path
   Severity: Low   Confidence: High
   CWE: CWE-78 (https://cwe.mitre.org/data/definitions/78.html)
   More Info: https://bandit.readthedocs.io/en/1.8.5/plugins/b607_start_process_with_partial_path.html
   Location: core\pairing_tab.py:261:16
260	            else:  # linux
261	                subprocess.run(["xdg-open", full_path], check=True, timeout=10)
262	        except subprocess.TimeoutExpired:

--------------------------------------------------
>> Issue: [B603:subprocess_without_shell_equals_true] subprocess call - check for execution of untrusted input.
   Severity: Low   Confidence: High
   CWE: CWE-78 (https://cwe.mitre.org/data/definitions/78.html)
   More Info: https://bandit.readthedocs.io/en/1.8.5/plugins/b603_subprocess_without_shell_equals_true.html
   Location: core\pairing_tab.py:261:16
260	            else:  # linux
261	                subprocess.run(["xdg-open", full_path], check=True, timeout=10)
262	        except subprocess.TimeoutExpired:

--------------------------------------------------
>> Issue: [B404:blacklist] Consider possible security implications associated with the subprocess module.
   Severity: Low   Confidence: High
   CWE: CWE-78 (https://cwe.mitre.org/data/definitions/78.html)
   More Info: https://bandit.readthedocs.io/en/1.8.5/blacklists/blacklist_imports.html#b404-import-subprocess
   Location: core\tools_tab.py:5:0
4	import string
5	import subprocess
6	import sys

--------------------------------------------------
>> Issue: [B606:start_process_with_no_shell] Starting a process without a shell.
   Severity: Low   Confidence: Medium
   CWE: CWE-78 (https://cwe.mitre.org/data/definitions/78.html)
   More Info: https://bandit.readthedocs.io/en/1.8.5/plugins/b606_start_process_with_no_shell.html
   Location: core\tools_tab.py:1241:20
1240	                if sys.platform == "win32":
1241	                    os.startfile(full_path)
1242	                elif sys.platform == "darwin":  # macOS

--------------------------------------------------
>> Issue: [B607:start_process_with_partial_path] Starting a process with a partial executable path
   Severity: Low   Confidence: High
   CWE: CWE-78 (https://cwe.mitre.org/data/definitions/78.html)
   More Info: https://bandit.readthedocs.io/en/1.8.5/plugins/b607_start_process_with_partial_path.html
   Location: core\tools_tab.py:1243:20
1242	                elif sys.platform == "darwin":  # macOS
1243	                    subprocess.run(["open", full_path], check=True, timeout=10)
1244	                else:  # Linux

--------------------------------------------------
>> Issue: [B603:subprocess_without_shell_equals_true] subprocess call - check for execution of untrusted input.
   Severity: Low   Confidence: High
   CWE: CWE-78 (https://cwe.mitre.org/data/definitions/78.html)
   More Info: https://bandit.readthedocs.io/en/1.8.5/plugins/b603_subprocess_without_shell_equals_true.html
   Location: core\tools_tab.py:1243:20
1242	                elif sys.platform == "darwin":  # macOS
1243	                    subprocess.run(["open", full_path], check=True, timeout=10)
1244	                else:  # Linux

--------------------------------------------------
>> Issue: [B607:start_process_with_partial_path] Starting a process with a partial executable path
   Severity: Low   Confidence: High
   CWE: CWE-78 (https://cwe.mitre.org/data/definitions/78.html)
   More Info: https://bandit.readthedocs.io/en/1.8.5/plugins/b607_start_process_with_partial_path.html
   Location: core\tools_tab.py:1245:20
1244	                else:  # Linux
1245	                    subprocess.run(["xdg-open", full_path], check=True, timeout=10)
1246	                logger.info(f"Otworzono archiwum: {full_path}")

--------------------------------------------------
>> Issue: [B603:subprocess_without_shell_equals_true] subprocess call - check for execution of untrusted input.
   Severity: Low   Confidence: High
   CWE: CWE-78 (https://cwe.mitre.org/data/definitions/78.html)
   More Info: https://bandit.readthedocs.io/en/1.8.5/plugins/b603_subprocess_without_shell_equals_true.html
   Location: core\tools_tab.py:1245:20
1244	                else:  # Linux
1245	                    subprocess.run(["xdg-open", full_path], check=True, timeout=10)
1246	                logger.info(f"Otworzono archiwum: {full_path}")

--------------------------------------------------

Code scanned:
	Total lines of code: 8357
	Total lines skipped (#nosec): 0
	Total potential issues skipped due to specifically being disabled (e.g., #nosec BXXX): 0

Run metrics:
	Total issues (by severity):
		Undefined: 0
		Low: 25
		Medium: 0
		High: 0
	Total issues (by confidence):
		Undefined: 0
		Low: 0
		Medium: 3
		High: 22
Files skipped (0):
```

## Błędy
```text
[main]	INFO	profile include tests: None
[main]	INFO	profile exclude tests: None
[main]	INFO	cli include tests: None
[main]	INFO	cli exclude tests: None
[main]	INFO	running on Python 3.13.3
```
