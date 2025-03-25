"""
Generate keys and necessary files for the blind signature voting demo
"""

import json
import os
from app.utils.crypto import generate_keys

# Create data directory if it doesn't exist
os.makedirs("data", exist_ok=True)

# Generate keys
pub_key, priv_key = generate_keys()

# Save keys to file
with open("data/keys.json", "w") as f:
    json.dump({"public_key": pub_key, "private_key": priv_key}, f)

# Create students.csv if it doesn't exist
if not os.path.exists("data/students.csv"):
    with open("data/students.csv", "w") as f:
        f.write("student1\nstudent2\nstudent3\nstudent4\nstudent5\n")

# Create empty voted.csv if it doesn't exist
if not os.path.exists("data/voted.csv"):
    with open("data/voted.csv", "w") as f:
        f.write("")

# Create empty votes.json if it doesn't exist
if not os.path.exists("data/votes.json"):
    with open("data/votes.json", "w") as f:
        f.write("[]")

print("Generated all necessary files for the blind signature voting demo")
print("- data/keys.json")
print("- data/students.csv")
print("- data/voted.csv")
print("- data/votes.json")
