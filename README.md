# Blinde Signaturen zur Wahl - Demo

Ein Demonstrationsprojekt für Blind Signatures (blinde Signaturen) in einem elektronischen Wahlsystem.

## Einrichtung und Konfiguration

### Methode 1: Mit Python direkt

* Python 3.9+ installieren
* Repository klonen: `git clone https://github.com/username/BlindeSignaturenZurWahlDEMO.git`
* Abhängigkeiten installieren: `pip install -r requirements.txt`
* `.env`-Datei konfigurieren (siehe unten)
* Anwendung starten: `python run.py`
* Browser öffnen: http://localhost:8000

### Methode 2: Mit Docker

* Docker installieren
* Repository klonen: `git clone https://github.com/username/BlindeSignaturenZurWahlDEMO.git`
* `.env`-Datei konfigurieren (siehe unten)
* Container starten: `docker-compose up -d`
* Browser öffnen: http://localhost:8000

### Methode 3: Mit Docker-Image

* Docker installieren
* Container direkt starten:
```
docker run -e COURSE_NAME="Kursname" -e VOTING_STUDENTS="Student1,Student2,Student3" -e CANDIDATES="Kandidat1,Kandidat2" -p 8000:8000 ianschn/blindewahl:latest
```

## Konfiguration mit .env

Die Anwendung verwendet eine `.env`-Datei für Umgebungsvariablen:

```
COURSE_NAME="DHBW WWI22SEA"
VOTING_STUDENTS="valentin,ian,jared,samuel,svenja,marian,monika"
CANDIDATES="valentin,joel"
```

### Parameter

* `COURSE_NAME`: Name des Kurses/der Veranstaltung (wird auf der Webseite angezeigt)
* `VOTING_STUDENTS`: Komma-getrennte Liste aller wahlberechtigten Personen (ohne Leerzeichen zwischen Kommas)
* `CANDIDATES`: Komma-getrennte Liste aller Kandidaten (ohne Leerzeichen zwischen Kommas)

## Fehlerbehebung

* **Port bereits belegt**: Wenn der Port 8000 bereits verwendet wird, ändern Sie den Port in `docker-compose.yml` oder verwenden Sie im Docker-Run-Befehl `-p 8001:8000`
* **Daten persistieren**: Um die Schlüssel zwischen Neustarts zu erhalten, mounten Sie das data-Verzeichnis: `-v ./data:/app/data`

## Systemübersicht

1. **Wahlleiter** (Admin-Ansicht): Überwacht den Wahlprozess
2. **Wähler**: Authentifizieren sich, erhalten eine blinde Signatur und geben ihre Stimme ab
3. **Ergebnis-Anzeige**: Zeigt das Wahlergebnis in Echtzeit an

## Hinweis

Dieses Projekt ist nur eine Demonstration und nicht für den Einsatz in realen Wahlszenarien geeignet.

## Warnung

**Dies ist nur eine Demonstration!** Die Implementierung ist nicht für reale Wahlen oder andere sicherheitskritische Anwendungen geeignet. Sie dient ausschließlich zu Bildungszwecken.

## Konzept

Blinde Signaturen ermöglichen es einem Signierer, ein Dokument zu signieren, ohne den Inhalt zu sehen. Im Kontext einer Wahl:

1. Der Wähler "blendet" seine Stimmabgabe mit einem Zufallsfaktor
2. Der Wahlleiter signiert die geblendete Nachricht
3. Der Wähler "entblendet" die Signatur, erhält damit eine gültige Signatur für seine ursprüngliche Stimme
4. Die Stimme kann mit der Signatur abgegeben werden

Dies gewährleistet:
- **Anonymität**: Der Wahlleiter weiß nicht, für wen der Wähler stimmt
- **Nicht-Fälschbarkeit**: Nur berechtigte Wähler können gültige Stimmen abgeben

## Implementierte Ansätze

Dieses Projekt enthält zwei unterschiedliche Implementierungen:

1. **Modul-basiert**: `app/utils/crypto.py` - Funktionen für den kompletten Prozess
2. **Klassen-basiert**: `app/blind_signature.py` - OOP-Ansatz mit der `BlindSignature`-Klasse

## Demo ausführen

```bash
# Vollständige Demo mit Schritt-für-Schritt-Erklärung
python demo_blind_signature.py

# Einfachere Demo mit der BlindSignature-Klasse
python main.py
```

## Tests ausführen

```bash
# Alle Tests
python -m unittest test_crypto.py test_blind_signature.py

# Nur Modul-Tests
python -m unittest test_crypto.py

# Nur Klassen-Tests
python -m unittest test_blind_signature.py
```

## Mathematischer Hintergrund

Die Implementierung basiert auf dem Diffie-Hellman-Schlüsselaustausch und verwendet folgende Schritte:

1. **Systemparameter**: 
   - Primzahl p und Generator g

2. **Schlüsselgenerierung**:
   - Signierer wählt geheimen Schlüssel x
   - Öffentlicher Schlüssel y = g^x mod p

3. **Blindsignatur-Protokoll**:
   - Wähler generiert DH-Parameter a, A = g^a mod p
   - Signierer generiert DH-Parameter b, B = g^b mod p
   - Beide berechnen gemeinsamen Schlüssel K = g^(ab) mod p
   - Wähler blendet Nachricht: M_blind = (M * K) mod p
   - Signierer signiert: S_blind = (M_blind)^x mod p
   - Wähler entblendet: S = S_blind * (K^x)^(-1) mod p

4. **Verifikation**:
   - Prüfen ob S = M^x mod p

## Projektstruktur

```
├── app/
│   ├── utils/
│   │   └── crypto.py    # Funktionale Implementierung
│   └── blind_signature.py  # OOP-Implementierung
├── test_crypto.py       # Tests für crypto.py
├── test_blind_signature.py # Tests für BlindSignature
├── main.py              # Einfache Demo
└── demo_blind_signature.py # Ausführliche Demo
```

## Einschränkungen

Diese Demo hat folgende Einschränkungen:

- Verwendet kleine Primzahlen (p < 10.000)
- Enthält Approximationen bei der Entblendung
- Bietet keine Schutzmaßnahmen gegen Replay-Angriffe
- Implementiert keine Zero-Knowledge-Beweise
- Verwendet keine ausreichende Anonymisierung

## Lizenz

Dieses Projekt ist nur für Bildungszwecke bestimmt.

## Docker Usage

### Running with Docker

Build and run the application using Docker:

```bash
# Build the Docker image
docker build -t blind-signature-demo .

# Run the container
docker run -p 8000:8000 -v ./data:/app/data blind-signature-demo
```

### Running with Docker Compose

```bash
# Build and start the application
docker-compose up -d

# Stop the application
docker-compose down
```

### Pushing to Docker Hub

```bash
# Log in to Docker Hub
docker login

# Tag the image
docker tag blind-signature-demo YOUR-USERNAME/blind-signature-demo:latest

# Push to Docker Hub
docker push YOUR-USERNAME/blind-signature-demo:latest
``` 