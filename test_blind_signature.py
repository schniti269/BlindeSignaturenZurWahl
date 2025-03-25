import unittest
from main import BlindSignature


class TestBlindSignature(unittest.TestCase):
    def setUp(self):
        self.blind_sig = BlindSignature()

    def test_blind_signature_process(self):
        # Original message
        original_message = 42

        # Blinding factor
        r = 5

        # Blind the message
        blinded_message = self.blind_sig.blind(original_message, r)

        # Sign the blinded message
        blinded_signature = self.blind_sig.sign(blinded_message)

        # Unblind the signature
        signature = self.blind_sig.unblind(blinded_signature, r)

        # Verify: For RSA-like signatures, verification is done by checking
        # if pow(signature, e, n) == message
        verified = (
            pow(signature, self.blind_sig.e, self.blind_sig.n) == original_message
        )

        self.assertTrue(verified, "Blind signature verification failed")

    def test_correct_blinding_math(self):
        # Test that (m * r^e) % n works as expected
        message = 10
        r = 3
        blinded = self.blind_sig.blind(message, r)
        expected = (
            message * pow(r, self.blind_sig.e, self.blind_sig.n)
        ) % self.blind_sig.n
        self.assertEqual(blinded, expected)

    def test_correct_unblinding_math(self):
        # Test that (bs * r^-1) % n works as expected
        blinded_sig = 100
        r = 3
        unblinded = self.blind_sig.unblind(blinded_sig, r)
        expected = (blinded_sig * pow(r, -1, self.blind_sig.n)) % self.blind_sig.n
        self.assertEqual(unblinded, expected)


if __name__ == "__main__":
    unittest.main()
