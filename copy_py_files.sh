#!/bin/bash
# Dieses Script muss im Hauptverzeichnis Ihres Projekts abgelegt werden.
# Es löscht zunächst die Zwischenablage und kopiert dann den Inhalt aller relevanten .py-Dateien
# aus dem Basisverzeichnis eines _app-Ordners (gezielt: models.py, urls.py, views.py, serializers.py, permissions.py, tests.py)
# sowie aller .py-Dateien aus den Unterordnern "api" und "tests" in die Zwischenablage.
# Für Dateien in den Unterordnern wird ein individueller Datei‑Header eingefügt.

# Schritt 1: Zwischenablage leeren
pbcopy < /dev/null

# Funktion: Sammle die relevanten Dateien aus dem Basisverzeichnis eines _app-Ordners
collect_base_files() {
    local base_dir="$1"
    # Definierte relevante Dateien
    local relevant_files=("models.py" "urls.py" "views.py" "serializers.py" "permissions.py" "tests.py")
    for file in "${relevant_files[@]}"; do
        if [ -f "$base_dir/$file" ]; then
            echo "----- Inhalt aus: $base_dir/$file -----"
            cat "$base_dir/$file"
            echo ""
        fi
    done
}

# Funktion: Sammle den Inhalt aller .py-Dateien aus einem Unterordner und füge einen Datei-Header hinzu
collect_subfolder_content() {
    local base_dir="$1"
    local subdir="$2"
    if [ -d "$base_dir/$subdir" ]; then
        echo "----- Inhalte aus: $base_dir/$subdir -----"
        # Rekursive Suche nach .py-Dateien im Unterordner; für jede gefundene Datei wird ein Header eingefügt
        find "$base_dir/$subdir" -type f -name "*.py" | while IFS= read -r file; do
            echo "----- Datei: $file -----"
            cat "$file"
            echo ""
        done
    fi
}

# Initialisierung der Ausgabe, die später in die Zwischenablage gepiped wird
output=""

if [ "$#" -eq 0 ]; then
    echo "Verarbeite alle Verzeichnisse, deren Name auf '_app' endet..."
    # Ohne Parameter: Alle Verzeichnisse, die auf _app enden, werden verarbeitet
    for app_folder in *_app; do
        if [ -d "$app_folder" ]; then
            output+="===== Ordner: $app_folder ====="$'\n'
            # Inhalt aus den relevanten Basisdateien
            output+="$(collect_base_files "$app_folder")"$'\n'
            # Inhalt aus den Unterordnern "api" und "tests" inklusive Datei-Header
            output+="$(collect_subfolder_content "$app_folder" "api")"$'\n'
            output+="$(collect_subfolder_content "$app_folder" "tests")"$'\n'
        fi
    done
else
    # Mit Parameter: Nur das angegebene _app-Verzeichnis wird verarbeitet
    APP_DIR="$1"
    if [ -d "$APP_DIR" ]; then
        echo "Verarbeite spezifisches Verzeichnis: $APP_DIR"
        output+="===== Ordner: $APP_DIR ====="$'\n'
        output+="$(collect_base_files "$APP_DIR")"$'\n'
        output+="$(collect_subfolder_content "$APP_DIR" "api")"$'\n'
        output+="$(collect_subfolder_content "$APP_DIR" "tests")"$'\n'
    else
        echo "Fehler: Das Verzeichnis '$APP_DIR' existiert nicht. Bitte überprüfen Sie den Pfad."
        exit 1
    fi
fi

# Schritt 2: Den gesammelten Inhalt in die Zwischenablage kopieren (alle Inhalte werden gepiped)
printf "%s" "$output" | pbcopy

echo "Fertig: Der Inhalt aller relevanten .py-Dateien wurde in die Zwischenablage kopiert."
