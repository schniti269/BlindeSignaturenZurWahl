from fastapi import FastAPI, Request, Form, Response, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import csv
import json
from pathlib import Path
from app.utils.crypto import (
    generate_keys,
    sign_blinded_message,
    verify_signature,
    generate_server_dh_params,
)

app = FastAPI(title="Blind Signature Voting Demo")

# Set up static files and templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

# Generate keys on startup if they don't exist
keys_file = Path("data/keys.json")
if not keys_file.exists():
    pub_key, priv_key = generate_keys()
    with open(keys_file, "w") as f:
        json.dump({"public_key": pub_key, "private_key": priv_key}, f)

# Load keys
with open(keys_file, "r") as f:
    keys = json.load(f)

# Store for DH session parameters
dh_sessions = {}


# Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/admin", response_class=HTMLResponse)
async def admin(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})


@app.get("/vote", response_class=HTMLResponse)
async def vote_page(request: Request):
    return templates.TemplateResponse("vote.html", {"request": request})


@app.post("/get-public-key")
async def get_public_key():
    return {"public_key": keys["public_key"]}


@app.post("/dh-exchange")
async def dh_exchange(request: Request):
    """Handle the DH key exchange protocol"""
    data = await request.json()
    client_id = data.get("client_id")
    client_A = data.get("A")

    try:
        # Convert A to integer
        A_int = int(client_A)

        # Generate server's DH parameters
        server_params = generate_server_dh_params(A_int, keys["public_key"])

        # Store server's shared key for this client
        dh_sessions[client_id] = {"K": server_params["K"]}

        # Return B to client
        return {"B": str(server_params["B"])}
    except (ValueError, TypeError) as e:
        return JSONResponse(
            status_code=400, content={"error": f"Invalid DH parameters: {str(e)}"}
        )


@app.post("/sign-ballot")
async def sign_ballot(request: Request):
    data = await request.json()
    student_id = data.get("student_id")
    blinded_ballot = data.get("blinded_ballot")
    client_id = data.get("client_id")

    # Check if student is in the list and hasn't voted
    students = []
    voted_students = []

    # Load student list
    try:
        # First try with UTF-8 encoding (most common)
        try:
            with open("data/students.csv", "r", encoding="utf-8") as f:
                students = [line.strip() for line in f.readlines() if line.strip()]
        except UnicodeDecodeError:
            # If UTF-8 fails, try with UTF-16
            with open("data/students.csv", "r", encoding="utf-16") as f:
                students = [line.strip() for line in f.readlines() if line.strip()]

        # Clean up any remaining null characters or BOM markers
        students = [s.replace("\x00", "").replace("\ufeff", "") for s in students if s]
        students = [s for s in students if s]  # Remove any empty strings after cleaning
    except FileNotFoundError:
        # Create sample file if doesn't exist
        with open("data/students.csv", "w", encoding="utf-8") as f:
            f.write("student1\nstudent2\nstudent3\nstudent4\nstudent5")
        students = ["student1", "student2", "student3", "student4", "student5"]

    # Load voted students
    try:
        with open("data/voted.csv", "r", encoding="utf-8") as f:
            voted_students = [line.strip() for line in f.readlines() if line.strip()]
    except FileNotFoundError:
        # Create file if doesn't exist
        with open("data/voted.csv", "w", encoding="utf-8") as f:
            pass

    # For student verification
    if student_id not in students:
        return JSONResponse(status_code=403, content={"error": "Student not in list"})
    elif student_id in voted_students:
        return JSONResponse(
            status_code=403, content={"error": "Student has already voted"}
        )

    # Make sure blinded_ballot is an integer
    try:
        blinded_ballot_int = int(blinded_ballot)
    except (ValueError, TypeError):
        return JSONResponse(
            status_code=400, content={"error": "Invalid blinded ballot format"}
        )

    # Sign blinded ballot
    blind_signature = sign_blinded_message(blinded_ballot_int, keys["private_key"])

    # Mark student as voted
    with open("data/voted.csv", "a") as f:
        f.write(f"{student_id}\n")

    return {"blind_signature": str(blind_signature)}


@app.post("/submit-vote")
async def submit_vote(request: Request):
    data = await request.json()
    vote = data.get("vote")
    signature = data.get("signature")
    candidate = data.get("candidate", "Unbekannt")  # Kandidatenname für Anzeige

    # Convert signature to integer if it's a string
    try:
        signature_int = int(signature)
    except (ValueError, TypeError):
        return JSONResponse(
            status_code=400, content={"error": f"Invalid signature format: {signature}"}
        )

    # Convert vote to integer if needed for verification
    try:
        vote_int = int(vote)
    except (ValueError, TypeError):
        return JSONResponse(
            status_code=400, content={"error": f"Invalid vote format: {vote}"}
        )

    # Verify signature
    if not verify_signature(vote_int, signature_int, keys["public_key"]):
        return JSONResponse(status_code=403, content={"error": "Invalid signature"})

    # Check if this ballot has been cast before
    cast_votes = []
    try:
        with open("data/votes.json", "r") as f:
            cast_votes = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        cast_votes = []

    # Check if this exact vote has been cast before
    for cast_vote in cast_votes:
        if cast_vote["signature"] == signature:
            return JSONResponse(status_code=403, content={"error": "Vote already cast"})

    # Use the provided candidate name instead of mapping
    candidate_name = candidate

    # Store vote
    cast_votes.append({"vote": candidate_name, "signature": signature})
    with open("data/votes.json", "w") as f:
        json.dump(cast_votes, f)

    return {"success": True}


@app.get("/results")
async def get_results():
    # Count votes
    votes = {}
    try:
        with open("data/votes.json", "r") as f:
            cast_votes = json.load(f)

        for vote_data in cast_votes:
            vote = vote_data["vote"]
            votes[vote] = votes.get(vote, 0) + 1
    except (FileNotFoundError, json.JSONDecodeError):
        votes = {}

    # Get participation
    students_count = 0
    voted_count = 0

    try:
        # First try with UTF-8 encoding (most common)
        try:
            with open("data/students.csv", "r", encoding="utf-8") as f:
                students_count = sum(1 for line in f if line.strip())
        except UnicodeDecodeError:
            # If UTF-8 fails, try with UTF-16
            with open("data/students.csv", "r", encoding="utf-16") as f:
                students_count = sum(1 for line in f if line.strip())
    except FileNotFoundError:
        students_count = 0

    try:
        with open("data/voted.csv", "r", encoding="utf-8") as f:
            voted_count = sum(1 for line in f if line.strip())
    except FileNotFoundError:
        voted_count = 0

    # Calculate participation percentage, ensure it's a number
    participation = (voted_count / students_count) * 100 if students_count > 0 else 0

    return {
        "votes": votes,
        "participation": round(participation, 2),
        "total_students": students_count,
        "voted_students": voted_count,
    }


@app.get("/voted-students")
async def get_voted_students():
    """Return a list of students who have voted"""
    voted_students = []

    try:
        # Try with UTF-8 encoding first
        try:
            with open("data/voted.csv", "r", encoding="utf-8") as f:
                voted_students = [
                    line.strip() for line in f.readlines() if line.strip()
                ]
        except UnicodeDecodeError:
            # If UTF-8 fails, try with UTF-16
            with open("data/voted.csv", "r", encoding="utf-16") as f:
                voted_students = [
                    line.strip() for line in f.readlines() if line.strip()
                ]

        # Clean up any BOM markers or null characters
        voted_students = [
            s.replace("\x00", "").replace("\ufeff", "") for s in voted_students if s
        ]
    except FileNotFoundError:
        voted_students = []

    return {"voted_students": voted_students}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
