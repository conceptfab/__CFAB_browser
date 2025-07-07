Kategoria 1: Zasady Hierarchii i Pierwszeństwa (Kaskadowość)
Te reguły decydują o tym, który styl zostanie zastosowany, gdy zdefiniowano ich kilka.
Reguła Specyficzności: Styl bardziej szczegółowy zawsze nadpisuje styl ogólny.
Wyjaśnienie: Styl zdefiniowany dla konkretnego przycisku za pomocą jego ID (#mojPrzycisk) jest ważniejszy i wygra ze stylem zdefiniowanym dla wszystkich przycisków danego typu (QPushButton).
Kolejność od najsłabszego do najsilniejszego: Typ widżetu -> Klasa -> ID obiektu.
Reguła Dziedziczenia: Widżety nie dziedziczą większości stylów wizualnych.
Wyjaśnienie: Ustawienie background-color dla okna głównego (QMainWindow) nie sprawi, że wszystkie przyciski w tym oknie automatycznie staną się tego koloru. Styl musisz zdefiniować bezpośrednio dla QPushButton. Dziedziczone są głównie właściwości dotyczące czcionek i kolorów tekstu.
Reguła Kolejności: Jeśli reguły mają tę samą specyficzność, ostatnia zdefiniowana reguła wygrywa.
Wyjaśnienie: Jeżeli w jednym arkuszu stylów zdefiniujesz dwa razy styl dla QPushButton, właściwości z drugiej definicji nadpiszą te z pierwszej.
Kategoria 2: Zasady Interaktywności i Stanu (Feedback dla Użytkownika)
Te reguły zapewniają, że przycisk komunikuje swój stan użytkownikowi, co jest kluczowe dla dobrego UX (User Experience).
Reguła Stanu Podstawowego: Każdy przycisk musi mieć zdefiniowany wygląd domyślny.
Wyjaśnienie: To jest jego wygląd, gdy nic się z nim nie dzieje. Musi być czytelny i jasno wskazywać na swoją funkcję (np. poprzez tekst lub ikonę).
Reguła Reakcji na Kursor (:hover): Zawsze definiuj styl dla stanu najechania myszką.
Wyjaśnienie: Użytkownik musi otrzymać natychmiastową informację zwrotną, że element, nad którym ma kursor, jest interaktywny. Zmiana może być subtelna (np. lekkie rozjaśnienie tła, zmiana koloru ramki), ale musi być zauważalna.
Reguła Reakcji na Wciśnięcie (:pressed): Zawsze definiuj styl dla stanu wciśnięcia.
Wyjaśnienie: Użytkownik musi widzieć, że jego akcja (kliknięcie) została zarejestrowana. Styl ten powinien wyraźnie różnić się od stanu podstawowego i :hover (np. ciemniejsze tło, efekt "wciśnięcia" do środka).
Reguła Stanu Nieaktywnego (:disabled): Zawsze definiuj styl dla przycisku wyłączonego.
Wyjaśnienie: Nieaktywny przycisk musi wizualnie komunikować, że nie można go użyć. Najczęściej osiąga się to przez wyszarzenie, obniżenie kontrastu lub usunięcie cieni. Musi wyglądać na "płaski" i nie reagować na najechanie kursorem.
Reguła Fokusu (:focus): Zdefiniuj styl dla stanu fokusu, aby wspierać nawigację klawiaturą.
Wyjaśnienie: To jest kluczowe dla dostępności. Użytkownik poruszający się po interfejsie za pomocą klawisza Tab musi widzieć, który element jest aktualnie aktywny. Zazwyczaj jest to dodatkowa ramka (outline) wokół przycisku.
Kategoria 3: Zasady Projektowania Wizualnego i Spójności
Te reguły dotyczą estetyki, czytelności i utrzymania porządku w interfejsie.
Reguła Spójności Funkcjonalnej: Używaj spójnych stylów dla przycisków o podobnej funkcji.
Wyjaśnienie: Wszystkie przyciski "akceptujące" (OK, Zapisz, Zastosuj) powinny wyglądać podobnie (np. zielone tło). Wszystkie przyciski "anulujące" (Anuluj, Zamknij) również powinny tworzyć spójną grupę (np. szare lub czerwone). To buduje intuicyjność interfejsu.
Reguła Kontrastu: Zapewnij wysoki kontrast między tekstem przycisku a jego tłem.
Wyjaśnienie: Tekst musi być bezwzględnie czytelny. Biały tekst na jasnożółtym tle jest złym pomysłem. Stosuj się do wytycznych WCAG (Web Content Accessibility Guidelines) dotyczących kontrastu.
Reguła "Oddechu" (padding): Zawsze dodawaj wewnętrzny margines (padding).
Wyjaśnienie: Tekst nie może stykać się z krawędziami przycisku. Padding tworzy przestrzeń, która poprawia czytelność i sprawia, że przycisk wygląda profesjonalnie.
Reguła Prostoty: Nie przesadzaj z liczbą różnych stylów.
Wyjaśnienie: Interfejs z dziesięcioma różnymi rodzajami przycisków jest chaotyczny i męczący dla użytkownika. Zdefiniuj 2-3 główne warianty (np. główny, drugorzędny, tekstowy) i trzymaj się ich w całej aplikacji.
Kategoria 4: Zasady Organizacji i Utrzymania Kodu
Te reguły pomagają pisać czyste i łatwe w zarządzaniu arkusze stylów.
Reguła Separacji: Oddzielaj style (QSS) od logiki (Python).
Wyjaśnienie: Trzymaj definicje stylów w osobnym pliku .qss i wczytuj go w aplikacji. Unikaj umieszczania długich, wieloliniowych stringów QSS bezpośrednio w kodzie Pythona. To radykalnie poprawia czytelność i ułatwia modyfikacje.
Reguła Komentowania: Komentuj złożone lub nieoczywiste fragmenty arkusza stylów.
Wyjaśnienie: Jeśli tworzysz skomplikowany selektor lub używasz koloru, którego znaczenie nie jest oczywiste, dodaj komentarz (/* komentarz */). Pomoże to Tobie i innym w przyszłości.