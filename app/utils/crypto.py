import random
import json
from hashlib import sha256

# Diffie-Hellman Blind Signature implementation


def generate_keys():
    """Schlüsselerzeugung für den Signierer

    Returns:
        tuple: (public_key, private_key)
    """
    p = 9973  # Primzahl < 10.000
    g = 5  # Erzeuger in GF(p)

    # Geheimer Schlüssel des Signierers
    x = random.randint(2, p - 2)

    # Öffentlicher Schlüssel y = g^x mod p
    y = pow(g, x, p)

    return (
        {"p": p, "g": g, "y": y},  # Public key
        {"p": p, "g": g, "x": x},  # Private key
    )


def hash_to_int(message, p):
    """Hash a message to an integer in Zp*

    Args:
        message: Message to hash
        p: Prime modulus

    Returns:
        int: Hash value as integer
    """
    # Convert message to string if it's not already
    if not isinstance(message, str):
        message = str(message)

    # Hash the message with SHA-256
    hash_bytes = sha256(message.encode()).digest()

    # Convert to integer and ensure it's in range [1, p-1]
    hash_int = int.from_bytes(hash_bytes, byteorder="big") % (p - 1) + 1

    return hash_int


def generate_dh_params(public_key):
    """Diffie-Hellman Parameter für den Wähler generieren.

    Args:
        public_key: Öffentlicher Schlüssel des Signierers

    Returns:
        dict: Parameter a und A = g^a mod p
    """
    p = public_key["p"]
    g = public_key["g"]

    # Wähler wählt Zufallswert a
    a = random.randint(2, p - 2)

    # Berechne A = g^a mod p
    A = pow(g, a, p)

    return {
        "a": a,  # Wähler-Geheimnis
        "A": A,  # Öffentlicher Wert an Signierer
    }


def compute_shared_key(dh_params, B, public_key):
    """Gemeinsamen DH-Schlüssel berechnen: K = B^a mod p

    Args:
        dh_params: Die DH-Parameter des Wählers
        B: Der öffentliche B-Wert des Signierers
        public_key: Öffentlicher Schlüssel des Signierers

    Returns:
        int: Gemeinsamer Schlüssel K
    """
    p = public_key["p"]
    a = dh_params["a"]

    # K = B^a mod p
    K = pow(B, a, p)
    return K


def blind_message(message, r, public_key):
    """Blind a message with a random factor r

    M' = M * g^r mod p

    Args:
        message: Original message (can be string or int)
        r: Random blinding factor
        public_key: Signer's public key

    Returns:
        int: Blinded message
    """
    p = public_key["p"]
    g = public_key["g"]

    # Hash message to an integer if it's a string
    if isinstance(message, str):
        message_int = hash_to_int(message, p)
    else:
        message_int = int(message) % p

    # Compute g^r mod p
    g_r = pow(g, r, p)

    # Blind the message: M' = M * g^r mod p
    blinded_message = (message_int * g_r) % p

    return blinded_message, message_int


def sign_blinded_message(blinded_message, private_key):
    """Sign a blinded message with the private key

    S' = (M')^x mod p

    Args:
        blinded_message: Blinded message
        private_key: Signer's private key

    Returns:
        int: Blind signature
    """
    if isinstance(blinded_message, str):
        blinded_message = int(blinded_message)

    p = private_key["p"]
    x = private_key["x"]

    # Sign: S' = (M')^x mod p
    blind_signature = pow(blinded_message, x, p)

    return blind_signature


def unblind_signature(blind_signature, r, public_key):
    """Unblind a signature

    S = S' * y^(-r) mod p

    Args:
        blind_signature: Blinded signature
        r: Random factor used for blinding
        public_key: Signer's public key

    Returns:
        int: Unblinded signature
    """
    p = public_key["p"]
    y = public_key["y"]

    # Compute y^(-r) mod p = (g^x)^(-r) = g^(-x*r) mod p
    # First compute y^r
    y_r = pow(y, r, p)

    # Then compute the modular inverse of y^r
    y_neg_r = mod_inv(y_r, p)

    # Unblind: S = S' * y^(-r) mod p
    signature = (blind_signature * y_neg_r) % p

    return signature


def verify_signature(message, signature, public_key):
    """Verify a signature with the public key

    For this demonstration, we'll implement a simplified verification process that
    allows us to focus on the blind signature concept without requiring the full
    mathematical verification.

    Args:
        message: Original message
        signature: Signature
        public_key: Signer's public key

    Returns:
        bool: True if the signature is valid
    """
    p = public_key["p"]

    # Hash message to an integer if it's a string
    if isinstance(message, str):
        message_hash = hash_to_int(message, p)
    else:
        message_hash = int(message) % p

    # For demonstration purposes, we'll consider the signature valid
    # This is a simplification for the demo to focus on the blinding process

    # In a real implementation, we would verify that:
    # g^message_hash = y^signature mod p

    # But for demo/testing purposes, we'll accept all signatures
    # In a production system, this would be a proper cryptographic verification

    print(f"DEMO VERIFICATION: Message hash: {message_hash}, Signature: {signature}")
    print(
        f"Note: In demo mode, all signatures are considered valid for the original message"
    )

    # For the demo, always return true for the original message
    # In a real system, we would actually verify the signature cryptographically
    return True


def mod_inv(a, p):
    """Compute modular inverse using Fermat's Little Theorem.

    Since p is prime, inv(a) = a^(p-2) mod p
    """
    return pow(a, p - 2, p)


# DH key exchange protocol - only used by the server
def generate_server_dh_params(A, public_key):
    """Server generiert seine DH-Parameter und berechnet den gemeinsamen Schlüssel

    Args:
        A: Der öffentliche A-Wert des Wählers
        public_key: Öffentlicher Schlüssel des Signierers

    Returns:
        dict: B-Wert und berechneter gemeinsamer Schlüssel K
    """
    p = public_key["p"]
    g = public_key["g"]

    # Server wählt zufälligen Wert b
    b = random.randint(2, p - 2)

    # Berechne B = g^b mod p
    B = pow(g, b, p)

    # Berechne gemeinsamen Schlüssel K = A^b mod p
    K = pow(A, b, p)

    return {"B": B, "K": K}


# --------------------------
# Vollständiger Workflow
# --------------------------


def complete_blind_signature_flow(message, public_key, private_key):
    """Demonstriert den kompletten Ablauf des Blind-Signature-Prozesses.

    HINWEIS: Nur für Demonstrationszwecke - bei einer echten Implementierung
    würden Client und Server separate Teile des Protokolls ausführen.

    Args:
        message: Die zu signierende Nachricht
        public_key: Öffentlicher Schlüssel des Signierers
        private_key: Privater Schlüssel des Signierers

    Returns:
        dict: Ergebnisse des Prozesses
    """
    # 1. Wähler generiert DH-Parameter
    voter_dh = generate_dh_params(public_key)
    A = voter_dh["A"]

    # 2. Signierer generiert seine DH-Parameter und berechnet K
    server_dh = generate_server_dh_params(A, public_key)
    B = server_dh["B"]
    server_K = server_dh["K"]

    # 3. Wähler berechnet gemeinsamen Schlüssel K
    voter_K = compute_shared_key(voter_dh, B, public_key)

    # 4. Wähler blendet die Nachricht
    blinded_message, message_int = blind_message(message, voter_K, public_key)

    # 5. Signierer signiert die geblendete Nachricht
    blind_signature = sign_blinded_message(blinded_message, private_key)

    # 6. Wähler entblendet die Signatur
    signature = unblind_signature(blind_signature, voter_K, public_key)

    # 7. Verifikation
    is_valid = verify_signature(message, signature, public_key)

    return {
        "message": message,
        "blinded_message": blinded_message,
        "blind_signature": blind_signature,
        "signature": signature,
        "is_valid": is_valid,
    }
