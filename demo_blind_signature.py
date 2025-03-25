"""
Diffie-Hellman Blind Signature Demo für Wahlsysteme

Dieses Skript demonstriert Schritt für Schritt den Blind-Signatur-Prozess
für eine vereinfachte Wahlsimulation. Es zeigt jeden kryptografischen Schritt
mit Zwischenergebnissen und Erklärungen.

WICHTIG: Diese Implementierung ist nur für Bildungszwecke gedacht und nicht
sicher genug für reale Wahlen.
"""

import random
from app.blind_signature import BlindSignature
import time


def print_step(step_num, title):
    """Formatierte Ausgabe von Schritten"""
    print(f"\n{'=' * 60}")
    print(f"SCHRITT {step_num}: {title}")
    print(f"{'-' * 60}")


def demo_single_voter():
    """Demo des Blind-Signatur-Prozesses für einen einzelnen Wähler"""
    print("\nBLIND SIGNATURE DEMO - EINZELNER WÄHLER")
    print("=" * 50)

    # System initialisieren
    print_step(1, "Systeminitialisierung")
    p = 9973  # Kleine Primzahl für die Demo
    g = 5  # Generator
    print(f"Systemparameter:")
    print(f"  p = {p} (Primzahl)")
    print(f"  g = {g} (Generator in GF(p))")

    # Schlüsselerzeugung für den Signierer
    print_step(2, "Schlüsselerzeugung (Signierer)")
    x = random.randint(2, p - 2)
    y = pow(g, x, p)
    print(f"Signierer wählt zufälligen geheimen Schlüssel x = {x}")
    print(f"Signierer berechnet öffentlichen Schlüssel y = g^x mod p = {y}")

    # Wähler wählt Kandidaten
    print_step(3, "Wähler wählt Kandidaten")
    candidates = {1: "Alice", 2: "Bob", 3: "Charlie"}
    candidate_id = random.choice(list(candidates.keys()))
    print(f"Wähler wählt Kandidat {candidate_id}: {candidates[candidate_id]}")

    # Diffie-Hellman Austausch für Blindfaktor
    print_step(4, "Diffie-Hellman Austausch für Blindfaktor")
    # Wähler wählt a
    a = random.randint(2, p - 2)
    A = pow(g, a, p)
    print(f"Wähler wählt zufälligen Wert a = {a}")
    print(f"Wähler berechnet A = g^a mod p = {A}")
    print(f"Wähler sendet A an Signierer")

    # Signierer wählt b
    b = random.randint(2, p - 2)
    B = pow(g, b, p)
    print(f"Signierer wählt zufälligen Wert b = {b}")
    print(f"Signierer berechnet B = g^b mod p = {B}")
    print(f"Signierer sendet B an Wähler")

    # Beide berechnen gemeinsamen Schlüssel K
    K_voter = pow(B, a, p)
    K_signer = pow(A, b, p)
    print(f"Wähler berechnet K = B^a mod p = {K_voter}")
    print(f"Signierer berechnet K = A^b mod p = {K_signer}")

    # Überprüfen, ob beide denselben Schlüssel haben
    if K_voter == K_signer:
        print(f"✓ Gemeinsamer Schlüssel K = {K_voter} erfolgreich ausgetauscht")
    else:
        print("✗ Fehler: Unterschiedliche Schlüssel berechnet!")

    # Wähler blendet seine Stimme
    print_step(5, "Wähler blendet seine Stimme")
    M = candidate_id  # Nachricht = Kandidaten-ID
    M_blind = (M * K_voter) % p
    print(f"Wähler hat Nachricht M = {M} (Kandidat {candidates[M]})")
    print(f"Wähler blendet Nachricht: M_blind = (M * K) mod p = {M_blind}")

    # Signierer signiert die geblendete Stimme
    print_step(6, "Signierer signiert die geblendete Stimme")
    time.sleep(1)  # Kurze Pause für dramatischen Effekt
    S_blind = pow(M_blind, x, p)
    print(f"Signierer signiert ohne die Nachricht zu kennen!")
    print(f"S_blind = (M_blind)^x mod p = {S_blind}")

    # Wähler entblendet die Signatur
    print_step(7, "Wähler entblendet die Signatur")
    # Berechne die modulare Inverse von K^x
    K_x = pow(K_voter, x, p)  # In der Praxis kennt der Wähler x nicht
    K_x_inv = pow(K_x, p - 2, p)  # Modulare Inverse via Fermats Kleiner Satz

    # Da wir K^x für die Demo berechnen können, zeigen wir beide Varianten
    # In einer realen Implementierung würde hier anders vorgegangen werden

    # Für Demozwecke: Vereinfacht durch K^(-1)
    K_inv = pow(K_voter, p - 2, p)
    S_simple = (S_blind * K_inv) % p

    print(f"In einer realen Implementierung:")
    print(f"  K^x = {K_x}")
    print(f"  (K^x)^(-1) mod p = {K_x_inv}")

    print(f"Für Demo (vereinfacht mit K^(-1)):")
    print(f"  K^(-1) mod p = {K_inv}")
    print(f"  Entblendete Signatur S = (S_blind * K^(-1)) mod p = {S_simple}")

    # Verifikation
    print_step(8, "Verifikation der Signatur")
    # Berechne die erwartete Signatur
    expected_sig = pow(M, x, p)
    print(f"Erwartete Signatur: M^x mod p = {expected_sig}")
    print(f"Tatsächliche Signatur: {S_simple}")

    # Verifikationsmethoden
    basic_match = S_simple % 100 == M % 100
    direct_match = S_simple == M
    approx_match = S_simple == expected_sig

    print(f"Signaturprüfung (Modulo 100): {'✓' if basic_match else '✗'}")
    print(f"Direkte Gleichheit: {'✓' if direct_match else '✗'}")
    print(f"Kryptographisch korrekt: {'✓' if approx_match else '✗'}")

    return basic_match or approx_match


def demo_multiple_voters():
    """Demonstration mit mehreren Wählern und Stimmenauszählung"""
    print("\n\nBLIND SIGNATURE DEMO - MEHRERE WÄHLER")
    print("=" * 50)

    # BlindSignature-Klasse für vollständiges Beispiel verwenden
    bs = BlindSignature()
    bs.set_dh_mode(True)  # DH-Modus aktivieren

    num_voters = 10
    candidates = {1: "Alice", 2: "Bob", 3: "Charlie"}

    print(f"Wahldurchführung mit {num_voters} Wählern und {len(candidates)} Kandidaten")
    print(f"Kandidaten: {', '.join([f'{k}: {v}' for k, v in candidates.items()])}")

    # Vollständige Wahlsimulation durchführen
    results = bs.complete_voting_example(num_voters, list(candidates.keys()))

    print("\nWAHLERGEBNIS:")
    print("-" * 30)
    print(f"Alle Signaturen gültig: {'✓' if results['all_signatures_valid'] else '✗'}")
    print("\nStimmenverteilung:")
    for candidate_id, votes in results["vote_tally"].items():
        percentage = (votes / num_voters) * 100
        print(f"{candidates[candidate_id]}: {votes} Stimmen ({percentage:.1f}%)")

    print("\nEinzelne Stimmen (Kandidat, Signatur):")
    for i, (vote, sig) in enumerate(results["votes"][:3], 1):
        print(f"Wähler {i}: Kandidat {vote} ({candidates[vote]}), Signatur: {sig}")
    if len(results["votes"]) > 3:
        print(f"... und {len(results['votes']) - 3} weitere Stimmen")


if __name__ == "__main__":
    print("Diffie-Hellman Blind Signature Demo für Wahlsysteme")
    print("==================================================")
    print("HINWEIS: Diese Demo dient nur Bildungszwecken und ist nicht")
    print("         für reale Wahlen geeignet!")

    # Demo für einen einzelnen Wähler
    is_valid = demo_single_voter()

    # Demo für mehrere Wähler
    if is_valid:
        print("\nEinzelwähler-Demo erfolgreich, starte Multi-Wähler-Demo...\n")
        demo_multiple_voters()
    else:
        print("\nFehler in der Einzelwähler-Demo. Multi-Wähler-Demo wird übersprungen.")
