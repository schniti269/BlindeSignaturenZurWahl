# Blinde Signaturen zur Wahl - Demo

![Docker](https://img.shields.io/badge/Docker-Ready-blue)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![License](https://img.shields.io/badge/License-Educational-green)
![Status](https://img.shields.io/badge/Status-Demo-orange)

Ein Demonstrationsprojekt für blinde Signaturen in einem elektronischen Wahlsystem für Bildungszwecke.

## 📋 Projektübersicht

Dieses Projekt demonstriert die Verwendung von blinden Signaturen für sichere und anonyme elektronische Wahlen:

* **Anonymität**: Wähler können anonym abstimmen
* **Nicht-Fälschbarkeit**: Nur berechtigte Wähler können gültige Stimmen abgeben
* **Transparenz**: Der gesamte kryptografische Prozess ist einsehbar
* **Lernumgebung**: Schritt-für-Schritt-Erklärungen des Wahlprozesses

## 🖼️ Screenshots

### Nutzeroberfläche
<img width="257" alt="image" src="https://github.com/user-attachments/assets/1573ef5e-20b2-4936-8c47-14be3746ba62" />


### Schritt-für-Schritt-Prozessvisualisierung
<img width="664" alt="image" src="https://github.com/user-attachments/assets/40e98bbb-b9e4-4fb1-b1cb-20bccd72034e" />



### Wahlleiter-Dashboard mit Live-Ergebnissen
<img width="416" alt="image" src="https://github.com/user-attachments/assets/08cba942-b2a3-4934-bbb9-070ddfee060a" />


### Eigenschaften des Wahlsystems
<img width="407" alt="image" src="https://github.com/user-attachments/assets/23dba158-0abb-4c9b-9091-6360956ecde0" />


## 🚀 Einrichtung und Konfiguration

### Methode 1: Mit Python direkt

1. **Voraussetzungen**
   * Python 3.9+ installieren

2. **Installation**
   ```powershell
   # Repository klonen
   git clone https://github.com/username/BlindeSignaturenZurWahlDEMO.git
   cd BlindeSignaturenZurWahlDEMO
   
   # Abhängigkeiten installieren
   pip install -r requirements.txt
   
   # .env-Datei konfigurieren (siehe unten)
   
   # Anwendung starten
   python run.py
   ```

3. **Zugriff**
   * Browser öffnen: http://localhost:8000

### Methode 2: Mit Docker Compose

1. **Voraussetzungen**
   * Docker und Docker Compose installieren

2. **Installation**
   ```powershell
   # Repository klonen
   git clone https://github.com/username/BlindeSignaturenZurWahlDEMO.git
   cd BlindeSignaturenZurWahlDEMO
   
   # .env-Datei konfigurieren (siehe unten)
   
   # Container starten
   docker-compose up -d
   ```

3. **Zugriff**
   * Browser öffnen: http://localhost:8000

### Methode 3: Mit Docker-Image

```powershell
# Docker-Container direkt starten
docker run -e COURSE_NAME="Kursname" -e VOTING_STUDENTS="Student1,Student2,Student3" -e CANDIDATES="Kandidat1,Kandidat2" -p 8000:8000 ianschn/blindewahl:latest
```

## ⚙️ Konfiguration mit .env

Die Anwendung verwendet eine `.env`-Datei für Umgebungsvariablen:

```
COURSE_NAME="DHBW WWI22SEA"
VOTING_STUDENTS="x,y,z"
CANDIDATES="a,b,c"
```

### Parameter

| Parameter | Beschreibung |
|-----------|-------------|
| `COURSE_NAME` | Name des Kurses/der Veranstaltung (wird auf der Webseite angezeigt) |
| `VOTING_STUDENTS` | Komma-getrennte Liste aller wahlberechtigten Personen (ohne Leerzeichen zwischen Kommas) |
| `CANDIDATES` | Komma-getrennte Liste aller Kandidaten (ohne Leerzeichen zwischen Kommas) |

## 🔍 Systemübersicht

Das System besteht aus drei Hauptkomponenten:

1. **Wahlleiter-Dashboard** 
   * Überwacht den Wahlprozess
   * Verwaltet die Wählerliste
   * Generiert kryptografische Schlüssel

2. **Wähler-Interface**
   * Authentifizierung der Wähler
   * Erstellung der blinden Stimmzettel
   * Abgabe der signierten Stimmen

3. **Ergebnis-Anzeige**
   * Anzeige der Wahlergebnisse in Echtzeit
   * Verifizierung der Stimmgültigkeit

## 💡 Konzept: Blinde Signaturen

Blinde Signaturen ermöglichen es einem Signierer, ein Dokument zu signieren, ohne den Inhalt zu sehen:

1. Der Wähler "blendet" seine Stimmabgabe mit einem Zufallsfaktor
2. Der Wahlleiter signiert die geblendete Nachricht
3. Der Wähler "entblendet" die Signatur und erhält eine gültige Signatur für seine ursprüngliche Stimme
4. Die Stimme kann mit der Signatur anonym abgegeben werden

Dies gewährleistet:
* **Anonymität**: Der Wahlleiter weiß nicht, für wen der Wähler stimmt
* **Nicht-Fälschbarkeit**: Nur berechtigte Wähler können gültige Stimmen abgeben


## 🐳 Docker-Nutzung

### Mit Docker ausführen

```powershell
# Docker-Image bauen
docker build -t blindewahl .

# Container starten
docker run -p 8000:8000 -v ./data:/app/data blindewahl
```

### Mit Docker Compose ausführen

```powershell
# Anwendung bauen und starten
docker-compose up -d

# Anwendung stoppen
docker-compose down
```
## ⚠️ Einschränkungen und Warnungen

**Dieses Projekt ist nur für Bildungszwecke konzipiert und nicht für reale Wahlen geeignet!**

Einschränkungen:
* Verwendet kleine Primzahlen (p < 10.000)
* Enthält Approximationen bei der Entblendung
* Bietet keinen Schutz gegen Replay-Angriffe
* Implementiert keine Zero-Knowledge-Beweise
* Verwendet keine ausreichende Anonymisierung

## 📚 Weiterführende Literatur

* [Blind Signatures for Untraceable Payments - David Chaum](https://www.chaum.com/publications/Chaum-blind-signatures.PDF)
* [Secure Electronic Voting](https://link.springer.com/book/10.1007/978-1-4615-0239-5)
* [Applied Cryptography - Bruce Schneier](https://www.schneier.com/books/applied-cryptography/) 
