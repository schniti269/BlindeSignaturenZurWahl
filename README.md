# Blind Signature Wahlsystem - Demo

Eine Demonstrationsanwendung für ein Wahlsystem mit Blinden Signaturen für die Kurssprecherwahl an der DHBW Mannheim WWI 22 SEA.

## Überblick

Diese Demo zeigt, wie Blinde Signaturen für ein anonymes Wahlsystem eingesetzt werden können. Dabei werden kryptographische Prozesse Schritt für Schritt visualisiert und erklärt.

### Funktionen

- **Anonyme Stimmabgabe**: Wähler können anonym abstimmen, während die Wahlbehörde die Wahlberechtigung überprüft
- **Verifizierbarkeit**: Jede Stimme wird kryptographisch signiert und kann verifiziert werden
- **Transparenz**: Alle kryptographischen Schritte werden im Browser ausgeführt und angezeigt
- **Admin-Dashboard**: Wahlleiter können Wahlbeteiligung und Ergebnisse einsehen

## Voraussetzungen

- Python 3.8 oder höher
- Pip (Python-Paketmanager)

## Installation

1. Abhängigkeiten installieren:
   ```
   pip install -r requirements.txt
   ```

## Starten der Anwendung

1. Server starten:
   ```
   python -m app.main
   ```

2. Öffne im Browser die Adresse: `http://localhost:8000`

## Technische Details

### Blinde Signaturen

Die Anwendung verwendet einen vereinfachten RSA-basierten Blind-Signature-Algorithmus:

1. Der Wähler erstellt einen Stimmzettel
2. Der Stimmzettel wird mit einem zufälligen Faktor "geblendet"
3. Die Wahlbehörde signiert den geblendeten Stimmzettel, ohne seinen Inhalt zu kennen
4. Der Wähler entfernt den Blendungsfaktor und erhält eine gültige Signatur
5. Der Wähler gibt seinen Stimmzettel mit der Signatur anonym ab

### Verzeichnisstruktur

```
/app
  /static
    /js          - Frontend JavaScript für Blinding und Verifizierung
  /templates     - HTML-Vorlagen für die Benutzeroberfläche
  /utils         - Hilfsfunktionen, z.B. für Kryptographie
  main.py        - Hauptanwendung mit FastAPI-Routen
/data            - Gespeicherte Wahldaten (generiert zur Laufzeit)
requirements.txt - Python-Abhängigkeiten
```

### Sicherheitshinweise

Diese Demo verwendet aus Demonstrationszwecken vereinfachte kryptographische Verfahren:

- **Schlüssellänge**: Es werden kürzere RSA-Schlüssel verwendet als in einer Produktionsumgebung empfohlen
- **Zufallsgenerator**: Es wird ein einfacherer Zufallsgenerator verwendet als in einer echten Anwendung
- **Persistenz**: Die Daten werden in einfachen Dateien gespeichert, nicht in einer sicheren Datenbank

## Vortrag: Ian Schnitzke - Blinde Signaturen zur Wahl

Diese Demo ist Teil eines Vortrags über Blinde Signaturen und ihre Anwendung bei elektronischen Wahlen an der DHBW Mannheim im Kurs WWI 22 SEA. 