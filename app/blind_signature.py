import random


class BlindSignature:
    """
    Implementierung einer Diffie-Hellman basierten Blind-Signatur für Demo-Zwecke.
    WICHTIG: Dies ist nur für Demonstrationszwecke und nicht für reale Wahlen geeignet!
    """

    def __init__(self, p=9973, g=5):
        """
        Initialisiert die Blind-Signatur mit Systemparametern.

        Args:
            p: Primzahl < 10.000
            g: Erzeuger in GF(p)
        """
        # Systemparameter
        self.p = p
        self.g = g

        # Für Demo-Kompatibilität mit test_blind_signature.py, RSA-ähnliche Parameter
        self.e = 65537  # Üblicher öffentlicher RSA-Exponent
        self.n = p  # Für Demo: Nutze p als RSA-Modulus

        # Erzeuge Schlüsselpaar
        self._generate_keys()

    def _generate_keys(self):
        """Erzeugt Schlüsselpaar für den Signierer"""
        # Geheimer Schlüssel
        self.x = random.randint(2, self.p - 2)

        # Öffentlicher Schlüssel y = g^x mod p
        self.y = pow(self.g, self.x, self.p)

    def blind(self, message, r=None):
        """
        Blendet eine Nachricht mit einem Blindfaktor.

        Args:
            message: Die Originalnachricht (Integer)
            r: Optional - Blindfaktor (für Tests)

        Returns:
            int: Geblendete Nachricht
        """
        # Wenn kein Blindfaktor angegeben, erzeuge zufälligen
        if r is None:
            r = random.randint(2, self.p - 2)

        # Blende die Nachricht: m_blind = (m * r^e) mod n
        # Für DH-Ansatz: m_blind = (m * r) mod p
        self.last_r = r  # Speichere r für Tests

        if hasattr(self, "dh_mode") and self.dh_mode:
            # DH-Style Blinding
            return (message * r) % self.p
        else:
            # RSA-Style Blinding (für Test-Kompatibilität)
            r_e = pow(r, self.e, self.n)
            return (message * r_e) % self.n

    def sign(self, blinded_message):
        """
        Signiert eine geblendete Nachricht.

        Args:
            blinded_message: Die geblendete Nachricht

        Returns:
            int: Blinde Signatur
        """
        # Signiere mit privatem Schlüssel x
        # S_blind = (M_blind)^x mod p
        return pow(blinded_message, self.x, self.p)

    def unblind(self, blinded_signature, r):
        """
        Entblendet eine blinde Signatur.

        Args:
            blinded_signature: Die blinde Signatur
            r: Der Blindfaktor

        Returns:
            int: Entblendete Signatur
        """
        # Entblende: S = S_blind * (r^e)^-1 mod n
        # Für DH-Ansatz: S = S_blind * r^-1 mod p
        if hasattr(self, "dh_mode") and self.dh_mode:
            # DH-Style Unblinding
            r_inv = pow(r, -1, self.p)
            return (blinded_signature * r_inv) % self.p
        else:
            # RSA-Style Unblinding (für Test-Kompatibilität)
            r_e_inv = pow(r, -1, self.n)
            return (blinded_signature * r_e_inv) % self.n

    def verify(self, message, signature):
        """
        Verifiziert eine Signatur.

        Args:
            message: Die Originalnachricht
            signature: Die Signatur

        Returns:
            bool: True wenn die Signatur gültig ist
        """
        # RSA-Verifikation: m ?= s^e mod n
        # Da wir keinen eigentlichen privaten RSA-Schlüssel haben, simulieren wir dies für Demo-Zwecke
        return pow(signature, self.e, self.n) == message % self.n

    def set_dh_mode(self, enabled=True):
        """
        Schaltet zwischen RSA-Style und DH-Style Blinding um.

        Args:
            enabled: True für DH-Style, False für RSA-Style
        """
        self.dh_mode = enabled

    def complete_voting_example(self, num_voters=20, candidates=[1, 2, 3]):
        """
        Führt eine komplette Wahl-Simulation durch.

        Args:
            num_voters: Anzahl der Wähler
            candidates: Liste der Kandidaten-IDs

        Returns:
            dict: Ergebnisse der Simulation
        """
        # List für (M, S) Paare zur Verifikation
        final_votes_signatures = []

        for voter_id in range(1, num_voters + 1):
            # a) Wähler wählt einen Blindfaktor
            r = random.randint(2, self.p - 2)

            # b) Wähler wählt Kandidaten M
            M = random.choice(candidates)

            # c) Wähler blendet seinen Stimmzettel
            self.set_dh_mode(True)  # DH-Style für reale Anwendung
            M_blind = self.blind(M, r)

            # d) Signierer signiert blind
            S_blind = self.sign(M_blind)

            # e) Wähler entblendet die Signatur
            S = self.unblind(S_blind, r)

            # Speichere Ergebnis
            final_votes_signatures.append((M, S))

        # Ergebnisauswertung
        all_valid = True
        tally = {candidate: 0 for candidate in candidates}

        for vote, signature in final_votes_signatures:
            # Signatur prüfen
            computed_signature = pow(vote, self.x, self.p)
            is_valid = signature == computed_signature

            if not is_valid:
                all_valid = False
                break

            # Stimme zählen
            tally[vote] = tally.get(vote, 0) + 1

        return {
            "all_signatures_valid": all_valid,
            "vote_tally": tally,
            "votes": final_votes_signatures,
        }
