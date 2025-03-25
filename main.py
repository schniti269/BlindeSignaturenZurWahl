from app.blind_signature import BlindSignature

# Export the BlindSignature class
BlindSignature = BlindSignature

if __name__ == "__main__":
    # Simple demo of the blind signature voting process
    blind_sig = BlindSignature()

    # Run a complete voting example
    result = blind_sig.complete_voting_example(num_voters=20, candidates=[1, 2, 3])

    print("Blind Signature Wahlsimulation")
    print("============================")
    print(f"Alle Signaturen gültig? {result['all_signatures_valid']}")
    print("\nStimmauszählung:")
    for candidate, votes in result["vote_tally"].items():
        print(f"Kandidat {candidate}: {votes} Stimmen")

    print("\nSystemparameter:")
    print(f"p = {blind_sig.p}")
    print(f"g = {blind_sig.g}")
    print(f"Öffentlicher Schlüssel y = {blind_sig.y}")
