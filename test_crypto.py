import unittest
from app.utils.crypto import (
    generate_keys,
    blind_message,
    sign_blinded_message,
    unblind_signature,
    verify_signature,
)


class TestCrypto(unittest.TestCase):
    def test_blind_signature_flow(self):
        """Test the complete blind signature process"""
        # Generate key pair
        pub_key, priv_key = generate_keys()

        # Original message
        message = "Test message"

        # Convert message to integer
        message_int = int.from_bytes(message.encode(), "big")

        # Blind the message
        blind_result = blind_message(message_int, pub_key)
        blinded_message = blind_result["blinded_message"]
        r = blind_result["r"]

        # Sign the blinded message
        blind_signature = sign_blinded_message(blinded_message, priv_key)

        # Unblind the signature
        signature = unblind_signature(blind_signature, r, pub_key)

        # Verify the signature
        is_valid = verify_signature(message_int, signature, pub_key)

        # Assert that signature is valid
        self.assertTrue(is_valid, "Signature verification failed")

    def test_end_to_end_string(self):
        """Test with string message end-to-end"""
        pub_key, priv_key = generate_keys()

        # Original message as string
        message = "Kandidat A"

        # Blind
        blind_result = blind_message(message, pub_key)

        # Sign
        blind_signature = sign_blinded_message(
            blind_result["blinded_message"], priv_key
        )

        # Unblind
        signature = unblind_signature(blind_signature, blind_result["r"], pub_key)

        # Verify
        is_valid = verify_signature(message, signature, pub_key)

        self.assertTrue(is_valid, "End-to-end string signature verification failed")


if __name__ == "__main__":
    unittest.main()
