# Blinde Signaturen zur Wahl - Demo

Dieses Projekt demonstriert die Verwendung von blinden Signaturen basierend auf dem Diffie-Hellman-Schlüsselaustausch, speziell für die Anwendung in einem Wahlsystem.

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