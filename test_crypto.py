import unittest
from app.utils.crypto import (
    generate_keys,
    generate_dh_params,
    compute_shared_key,
    blind_message,
    sign_blinded_message,
    unblind_signature,
    verify_signature,
    complete_blind_signature_flow,
    generate_server_dh_params,
)


class TestCrypto(unittest.TestCase):
    def test_blind_signature_flow(self):
        """Test the complete blind signature process"""
        # Generate key pair
        pub_key, priv_key = generate_keys()

        # Original message (integer)
        message = 42

        # Test with the complete flow function
        result = complete_blind_signature_flow(message, pub_key, priv_key)

        # Assert that signature is valid
        self.assertTrue(result["is_valid"], "Signatur Verifikation fehlgeschlagen")

    def test_step_by_step_process(self):
        """Test the cryptographic process step by step"""
        # 1. Generate key pair
        pub_key, priv_key = generate_keys()

        # 2. Original message (integer for simplicity)
        message = 42

        # 3. Generate DH params for voter
        voter_dh = generate_dh_params(pub_key)

        # 4. Server generates DH params and computes shared key
        server_dh = generate_server_dh_params(voter_dh["A"], pub_key)
        B = server_dh["B"]
        server_K = server_dh["K"]

        # 5. Voter computes shared key
        voter_K = compute_shared_key(voter_dh, B, pub_key)

        # Verify both sides computed the same shared key
        self.assertEqual(
            voter_K,
            server_K,
            "DH Schlüsselaustausch fehlgeschlagen - unterschiedliche K-Werte",
        )

        # 6. Blind the message
        blinded_message = blind_message(message, voter_K, pub_key)

        # 7. Sign the blinded message
        blind_signature = sign_blinded_message(blinded_message, priv_key)

        # 8. Unblind the signature
        signature = unblind_signature(blind_signature, voter_K, pub_key)

        # 9. Verify the signature
        is_valid = verify_signature(message, signature, pub_key)

        self.assertTrue(is_valid, "Stufenweise Signatur Verifikation fehlgeschlagen")

    def test_string_message(self):
        """Test mit einer Textnachricht"""
        pub_key, priv_key = generate_keys()

        # Nachricht als String
        message = "Kandidat A"

        # Test with the complete flow function
        result = complete_blind_signature_flow(message, pub_key, priv_key)

        # Assert that signature is valid
        self.assertTrue(
            result["is_valid"], "String-Nachricht Signatur Verifikation fehlgeschlagen"
        )

    def test_multiple_voters(self):
        """Test mit mehreren Wählern"""
        pub_key, priv_key = generate_keys()

        # Simuliere mehrere Wähler die für verschiedene Kandidaten stimmen
        candidates = [1, 2, 3]  # Kandidaten-IDs
        num_voters = 10

        for voter_id in range(num_voters):
            # Wähle zufälligen Kandidaten
            candidate = candidates[voter_id % len(candidates)]

            # Führe Blind-Signatur durch
            result = complete_blind_signature_flow(candidate, pub_key, priv_key)

            # Prüfe ob Signatur gültig ist
            self.assertTrue(result["is_valid"], f"Wähler {voter_id} Signatur ungültig")


if __name__ == "__main__":
    unittest.main()
