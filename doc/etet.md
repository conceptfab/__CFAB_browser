jak użytkownik kliknie w folder mają być zrealizowane następujące warunki:
- jeśli folder zawiera pliki archiwum i podglądy i nie ma plików asset - scanner zaczyna pracę i po sukcesie galeria wyświetla assety z tego folderu
- jeśli folder zawiera pliki archiwum, podglądy i pliki assett to sprawdzane sa kolejne warunki:
- jeśli w folderze nie ma folderu .cache - scanner zaczyna pracę i po sukcesie galeria wyświetla assety z tego folderu
- jeśli w folderze jest folder .cache ale zawiera on inna licznę plików thumb niż folder roboczy plików asset (brak miniaturek) - scanner zaczyna pracę i po sukcesie galeria wyświetla assety z tego folderu
- jeśli w folderze w folderze .cache jest identyczna liczna plików i co plików asset to galeria wyświetla pliki asset z tego folderu. Decyzja o uruchomieniu scannera zostaje do decyzji użytkownika - do tego musi być osobne polecenie