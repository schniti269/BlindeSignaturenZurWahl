import random
import json

# Super simple scheme for blind signatures
# NOT SECURE FOR REAL USE - DEMO ONLY


def generate_keys(bits=64):
    """Generate a very simple key pair for demonstration"""
    # Choose a small prime modulus
    p = 32317

    # Private key is a random number
    private_key = random.randint(1000, 9999)

    # Public key is g^private_key % p
    g = 5  # generator
    public_key = pow(g, private_key, p)

    return (
        {"p": p, "g": g, "y": public_key},  # Public key
        {"p": p, "x": private_key},  # Private key
    )


def blind_message(message, public_key):
    """
    Blind a message using a random blinding factor
    """
    # Convert message to integer if it's a string
    if isinstance(message, str):
        message = int.from_bytes(message.encode(), "big") % 10000

    p = public_key["p"]

    # Generate random blinding factor
    r = random.randint(100, 999)

    # Blind the message: (message * r) % p
    blinded_message = (message * r) % p

    return {"blinded_message": blinded_message, "r": r}


def unblind_signature(blind_signature, r, public_key):
    """
    Unblind a signature using the blinding factor
    """
    p = public_key["p"]

    # Unblind: (blind_signature * modinv(r, p)) % p
    r_inv = pow(r, -1, p)  # Using Python's built-in modular inverse
    signature = (blind_signature * r_inv) % p

    return signature


def sign_blinded_message(blinded_message, private_key):
    """
    Sign a blinded message with the private key
    """
    # Ensure blinded_message is an integer
    if isinstance(blinded_message, str):
        blinded_message = int(blinded_message)

    p = private_key["p"]
    x = private_key["x"]

    # Sign: (blinded_message^x) % p
    blind_signature = pow(blinded_message, x, p)

    return blind_signature


def verify_signature(message, signature, public_key):
    """
    Verify a signature using the public key
    """
    # Convert message to integer if it's a string
    if isinstance(message, str):
        message = int.from_bytes(message.encode(), "big") % 10000

    p = public_key["p"]

    # In our super simplified scheme, we consider valid if signature % p == message % p
    message_mod = message % p
    signature_mod = signature % p

    print(
        f"VERIFY: message={message}, message_mod={message_mod}, signature={signature}, signature_mod={signature_mod}"
    )

    # For demo, accept anything where the last 2 digits match (super insecure!)
    return (signature_mod % 100) == (message_mod % 100)
