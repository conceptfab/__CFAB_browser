# 🛡️ Raport Bandit (Bezpieczeństwo)

**Data generowania:** 2025-07-05 01:19:01

---

## Wyniki analizy bezpieczeństwa folderu `core`

```text
Run started:2025-07-04 23:19:03.127358

Test results:
>> Issue: [B110:try_except_pass] Try, Except, Pass detected.
   Severity: Low   Confidence: High
   CWE: CWE-703 (https://cwe.mitre.org/data/definitions/703.html)
   More Info: https://bandit.readthedocs.io/en/1.8.5/plugins/b110_try_except_pass.html
   Location: core\amv_views\asset_tile_view.py:593:12
592	                self.model.data_changed.disconnect(self.update_ui)
593	            except Exception:
594	                pass
595	        self.model = None

--------------------------------------------------
>> Issue: [B404:blacklist] Consider possible security implications associated with the subprocess module.
   Severity: Low   Confidence: High
   CWE: CWE-78 (https://cwe.mitre.org/data/definitions/78.html)
   More Info: https://bandit.readthedocs.io/en/1.8.5/blacklists/blacklist_imports.html#b404-import-subprocess
   Location: core\file_utils.py:8:0
7	import os
8	import subprocess
9	import sys

--------------------------------------------------
>> Issue: [B607:start_process_with_partial_path] Starting a process with a partial executable path
   Severity: Low   Confidence: High
   CWE: CWE-78 (https://cwe.mitre.org/data/definitions/78.html)
   More Info: https://bandit.readthedocs.io/en/1.8.5/plugins/b607_start_process_with_partial_path.html
   Location: core\file_utils.py:40:12
39	            )
40	            subprocess.run(["explorer", normalized_path])
41	        elif sys.platform == "darwin":  # macOS

--------------------------------------------------
>> Issue: [B603:subprocess_without_shell_equals_true] subprocess call - check for execution of untrusted input.
   Severity: Low   Confidence: High
   CWE: CWE-78 (https://cwe.mitre.org/data/definitions/78.html)
   More Info: https://bandit.readthedocs.io/en/1.8.5/plugins/b603_subprocess_without_shell_equals_true.html
   Location: core\file_utils.py:40:12
39	            )
40	            subprocess.run(["explorer", normalized_path])
41	        elif sys.platform == "darwin":  # macOS

--------------------------------------------------
>> Issue: [B607:start_process_with_partial_path] Starting a process with a partial executable path
   Severity: Low   Confidence: High
   CWE: CWE-78 (https://cwe.mitre.org/data/definitions/78.html)
   More Info: https://bandit.readthedocs.io/en/1.8.5/plugins/b607_start_process_with_partial_path.html
   Location: core\file_utils.py:42:12
41	        elif sys.platform == "darwin":  # macOS
42	            subprocess.run(["open", normalized_path])
43	        else:  # Linux

--------------------------------------------------
>> Issue: [B603:subprocess_without_shell_equals_true] subprocess call - check for execution of untrusted input.
   Severity: Low   Confidence: High
   CWE: CWE-78 (https://cwe.mitre.org/data/definitions/78.html)
   More Info: https://bandit.readthedocs.io/en/1.8.5/plugins/b603_subprocess_without_shell_equals_true.html
   Location: core\file_utils.py:42:12
41	        elif sys.platform == "darwin":  # macOS
42	            subprocess.run(["open", normalized_path])
43	        else:  # Linux

--------------------------------------------------
>> Issue: [B607:start_process_with_partial_path] Starting a process with a partial executable path
   Severity: Low   Confidence: High
   CWE: CWE-78 (https://cwe.mitre.org/data/definitions/78.html)
   More Info: https://bandit.readthedocs.io/en/1.8.5/plugins/b607_start_process_with_partial_path.html
   Location: core\file_utils.py:44:12
43	        else:  # Linux
44	            subprocess.run(["xdg-open", normalized_path])
45	        logger.info(f"Otworzono ścieżkę w eksploratorze: {normalized_path}")

--------------------------------------------------
>> Issue: [B603:subprocess_without_shell_equals_true] subprocess call - check for execution of untrusted input.
   Severity: Low   Confidence: High
   CWE: CWE-78 (https://cwe.mitre.org/data/definitions/78.html)
   More Info: https://bandit.readthedocs.io/en/1.8.5/plugins/b603_subprocess_without_shell_equals_true.html
   Location: core\file_utils.py:44:12
43	        else:  # Linux
44	            subprocess.run(["xdg-open", normalized_path])
45	        logger.info(f"Otworzono ścieżkę w eksploratorze: {normalized_path}")

--------------------------------------------------
>> Issue: [B606:start_process_with_no_shell] Starting a process without a shell.
   Severity: Low   Confidence: Medium
   CWE: CWE-78 (https://cwe.mitre.org/data/definitions/78.html)
   More Info: https://bandit.readthedocs.io/en/1.8.5/plugins/b606_start_process_with_no_shell.html
   Location: core\file_utils.py:69:12
68	        if sys.platform == "win32":
69	            os.startfile(path)
70	        elif sys.platform == "darwin":  # macOS

--------------------------------------------------
>> Issue: [B607:start_process_with_partial_path] Starting a process with a partial executable path
   Severity: Low   Confidence: High
   CWE: CWE-78 (https://cwe.mitre.org/data/definitions/78.html)
   More Info: https://bandit.readthedocs.io/en/1.8.5/plugins/b607_start_process_with_partial_path.html
   Location: core\file_utils.py:71:12
70	        elif sys.platform == "darwin":  # macOS
71	            subprocess.run(["open", path])
72	        else:  # Linux

--------------------------------------------------
>> Issue: [B603:subprocess_without_shell_equals_true] subprocess call - check for execution of untrusted input.
   Severity: Low   Confidence: High
   CWE: CWE-78 (https://cwe.mitre.org/data/definitions/78.html)
   More Info: https://bandit.readthedocs.io/en/1.8.5/plugins/b603_subprocess_without_shell_equals_true.html
   Location: core\file_utils.py:71:12
70	        elif sys.platform == "darwin":  # macOS
71	            subprocess.run(["open", path])
72	        else:  # Linux

--------------------------------------------------
>> Issue: [B607:start_process_with_partial_path] Starting a process with a partial executable path
   Severity: Low   Confidence: High
   CWE: CWE-78 (https://cwe.mitre.org/data/definitions/78.html)
   More Info: https://bandit.readthedocs.io/en/1.8.5/plugins/b607_start_process_with_partial_path.html
   Location: core\file_utils.py:73:12
72	        else:  # Linux
73	            subprocess.run(["xdg-open", path])
74	        logger.info(f"Otworzono plik w domyślnej aplikacji: {path}")

--------------------------------------------------
>> Issue: [B603:subprocess_without_shell_equals_true] subprocess call - check for execution of untrusted input.
   Severity: Low   Confidence: High
   CWE: CWE-78 (https://cwe.mitre.org/data/definitions/78.html)
   More Info: https://bandit.readthedocs.io/en/1.8.5/plugins/b603_subprocess_without_shell_equals_true.html
   Location: core\file_utils.py:73:12
72	        else:  # Linux
73	            subprocess.run(["xdg-open", path])
74	        logger.info(f"Otworzono plik w domyślnej aplikacji: {path}")

--------------------------------------------------
>> Issue: [B110:try_except_pass] Try, Except, Pass detected.
   Severity: Low   Confidence: High
   CWE: CWE-703 (https://cwe.mitre.org/data/definitions/703.html)
   More Info: https://bandit.readthedocs.io/en/1.8.5/plugins/b110_try_except_pass.html
   Location: core\main_window.py:395:20
394	                            )
395	                    except Exception:
396	                        pass
397	

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
   Location: core\pairing_tab.py:250:12
249	        if sys.platform == "win32":
250	            os.startfile(full_path)
251	        elif sys.platform == "darwin":  # macOS

--------------------------------------------------
>> Issue: [B607:start_process_with_partial_path] Starting a process with a partial executable path
   Severity: Low   Confidence: High
   CWE: CWE-78 (https://cwe.mitre.org/data/definitions/78.html)
   More Info: https://bandit.readthedocs.io/en/1.8.5/plugins/b607_start_process_with_partial_path.html
   Location: core\pairing_tab.py:252:12
251	        elif sys.platform == "darwin":  # macOS
252	            subprocess.Popen(["open", full_path])
253	        else:  # linux

--------------------------------------------------
>> Issue: [B603:subprocess_without_shell_equals_true] subprocess call - check for execution of untrusted input.
   Severity: Low   Confidence: High
   CWE: CWE-78 (https://cwe.mitre.org/data/definitions/78.html)
   More Info: https://bandit.readthedocs.io/en/1.8.5/plugins/b603_subprocess_without_shell_equals_true.html
   Location: core\pairing_tab.py:252:12
251	        elif sys.platform == "darwin":  # macOS
252	            subprocess.Popen(["open", full_path])
253	        else:  # linux

--------------------------------------------------
>> Issue: [B607:start_process_with_partial_path] Starting a process with a partial executable path
   Severity: Low   Confidence: High
   CWE: CWE-78 (https://cwe.mitre.org/data/definitions/78.html)
   More Info: https://bandit.readthedocs.io/en/1.8.5/plugins/b607_start_process_with_partial_path.html
   Location: core\pairing_tab.py:254:12
253	        else:  # linux
254	            subprocess.Popen(["xdg-open", full_path])
255	        self.selected_preview = file_name if file_name else None

--------------------------------------------------
>> Issue: [B603:subprocess_without_shell_equals_true] subprocess call - check for execution of untrusted input.
   Severity: Low   Confidence: High
   CWE: CWE-78 (https://cwe.mitre.org/data/definitions/78.html)
   More Info: https://bandit.readthedocs.io/en/1.8.5/plugins/b603_subprocess_without_shell_equals_true.html
   Location: core\pairing_tab.py:254:12
253	        else:  # linux
254	            subprocess.Popen(["xdg-open", full_path])
255	        self.selected_preview = file_name if file_name else None

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
>> Issue: [B311:blacklist] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
   Severity: Low   Confidence: High
   CWE: CWE-330 (https://cwe.mitre.org/data/definitions/330.html)
   More Info: https://bandit.readthedocs.io/en/1.8.5/blacklists/blacklist_calls.html#b311-random
   Location: core\tools_tab.py:688:25
687	        # Generuj 8 cyfr i 8 liter
688	        digits = "".join(random.choices(string.digits, k=8))
689	        letters = "".join(random.choices(string.ascii_uppercase, k=8))

--------------------------------------------------
>> Issue: [B311:blacklist] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
   Severity: Low   Confidence: High
   CWE: CWE-330 (https://cwe.mitre.org/data/definitions/330.html)
   More Info: https://bandit.readthedocs.io/en/1.8.5/blacklists/blacklist_calls.html#b311-random
   Location: core\tools_tab.py:689:26
688	        digits = "".join(random.choices(string.digits, k=8))
689	        letters = "".join(random.choices(string.ascii_uppercase, k=8))
690	        # Połącz i wymieszaj

--------------------------------------------------
>> Issue: [B311:blacklist] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
   Severity: Low   Confidence: High
   CWE: CWE-330 (https://cwe.mitre.org/data/definitions/330.html)
   More Info: https://bandit.readthedocs.io/en/1.8.5/blacklists/blacklist_calls.html#b311-random
   Location: core\tools_tab.py:692:27
691	        combined = digits + letters
692	        shuffled = "".join(random.sample(combined, len(combined)))
693	        return shuffled

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
1243	                    subprocess.Popen(["open", full_path])
1244	                else:  # Linux

--------------------------------------------------
>> Issue: [B603:subprocess_without_shell_equals_true] subprocess call - check for execution of untrusted input.
   Severity: Low   Confidence: High
   CWE: CWE-78 (https://cwe.mitre.org/data/definitions/78.html)
   More Info: https://bandit.readthedocs.io/en/1.8.5/plugins/b603_subprocess_without_shell_equals_true.html
   Location: core\tools_tab.py:1243:20
1242	                elif sys.platform == "darwin":  # macOS
1243	                    subprocess.Popen(["open", full_path])
1244	                else:  # Linux

--------------------------------------------------
>> Issue: [B607:start_process_with_partial_path] Starting a process with a partial executable path
   Severity: Low   Confidence: High
   CWE: CWE-78 (https://cwe.mitre.org/data/definitions/78.html)
   More Info: https://bandit.readthedocs.io/en/1.8.5/plugins/b607_start_process_with_partial_path.html
   Location: core\tools_tab.py:1245:20
1244	                else:  # Linux
1245	                    subprocess.Popen(["xdg-open", full_path])
1246	                logger.info(f"Otworzono archiwum: {full_path}")

--------------------------------------------------
>> Issue: [B603:subprocess_without_shell_equals_true] subprocess call - check for execution of untrusted input.
   Severity: Low   Confidence: High
   CWE: CWE-78 (https://cwe.mitre.org/data/definitions/78.html)
   More Info: https://bandit.readthedocs.io/en/1.8.5/plugins/b603_subprocess_without_shell_equals_true.html
   Location: core\tools_tab.py:1245:20
1244	                else:  # Linux
1245	                    subprocess.Popen(["xdg-open", full_path])
1246	                logger.info(f"Otworzono archiwum: {full_path}")

--------------------------------------------------
>> Issue: [B110:try_except_pass] Try, Except, Pass detected.
   Severity: Low   Confidence: High
   CWE: CWE-703 (https://cwe.mitre.org/data/definitions/703.html)
   More Info: https://bandit.readthedocs.io/en/1.8.5/plugins/b110_try_except_pass.html
   Location: core\utilities.py:42:4
41	                break
42	    except Exception:
43	        pass

--------------------------------------------------

Code scanned:
	Total lines of code: 8259
	Total lines skipped (#nosec): 0
	Total potential issues skipped due to specifically being disabled (e.g., #nosec BXXX): 0

Run metrics:
	Total issues (by severity):
		Undefined: 0
		Low: 30
		Medium: 0
		High: 0
	Total issues (by confidence):
		Undefined: 0
		Low: 0
		Medium: 3
		High: 27
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
