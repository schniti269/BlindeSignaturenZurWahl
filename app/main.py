from fastapi import FastAPI, Request, Form, Response, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import csv
import json
from pathlib import Path
from app.utils.crypto import generate_keys, sign_blinded_message, verify_signature

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


@app.post("/sign-ballot")
async def sign_ballot(request: Request):
    data = await request.json()
    student_id = data.get("student_id")
    blinded_ballot = data.get("blinded_ballot")

    # Check if student is in the list and hasn't voted
    students = []
    voted_students = []

    # Load student list
    try:
        with open("data/students.csv", "r") as f:
            students = [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        # Create sample file if doesn't exist
        with open("data/students.csv", "w") as f:
            f.write("student1\nstudent2\nstudent3\nstudent4\nstudent5")
        students = ["student1", "student2", "student3", "student4", "student5"]

    # Load voted students
    try:
        with open("data/voted.csv", "r") as f:
            voted_students = [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        # Create file if doesn't exist
        with open("data/voted.csv", "w") as f:
            pass

    # Verify student can vote
    if student_id not in students:
        return JSONResponse(status_code=403, content={"error": "Student not in list"})

    if student_id in voted_students:
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

    # Display debug info
    print(f"RECEIVED VOTE: {vote}")
    print(f"SIGNATURE: {signature}")

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
    print(f"Verifying: vote={vote_int}, signature={signature_int}")
    if not verify_signature(vote_int, signature_int, keys["public_key"]):
        print(f"Verification failed: {vote_int} with signature {signature_int}")
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

    # Map numeric vote back to candidate text
    # This is just for display purposes in the results
    if vote_int > 0:  # This is a simplistic mapping
        if vote_int % 3 == 0:
            candidate_name = "Kandidat A"
        elif vote_int % 3 == 1:
            candidate_name = "Kandidat B"
        else:
            candidate_name = "Kandidat C"
    else:
        candidate_name = "Ungültige Stimme"

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
        with open("data/students.csv", "r") as f:
            students_count = sum(1 for line in f if line.strip())
    except FileNotFoundError:
        pass

    try:
        with open("data/voted.csv", "r") as f:
            voted_count = sum(1 for line in f if line.strip())
    except FileNotFoundError:
        pass

    participation = (voted_count / students_count) * 100 if students_count > 0 else 0

    return {
        "votes": votes,
        "participation": round(participation, 2),
        "total_students": students_count,
        "voted_students": voted_count,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
