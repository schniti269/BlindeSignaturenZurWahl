from fastapi import FastAPI, Request, Form, Response, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import json
from pathlib import Path
from app.utils.crypto import (
    generate_keys,
    sign_blinded_message,
    verify_signature,
    generate_server_dh_params,
)

app = FastAPI(title="Blind Signature Voting Demo")


# Load and validate configuration from environment variables
def load_env_var(name, default=None):
    value = os.getenv(name, default)
    if value is None:
        raise ValueError(f"Environment variable {name} is required")
    return value


try:
    COURSE_NAME = load_env_var("COURSE_NAME")
    VOTING_STUDENTS = json.loads(load_env_var("VOTING_STUDENTS"))
    CANDIDATES = json.loads(load_env_var("CANDIDATES"))

    # Validate the loaded data
    if not isinstance(VOTING_STUDENTS, list):
        raise ValueError("VOTING_STUDENTS must be a JSON array")
    if not isinstance(CANDIDATES, list):
        raise ValueError("CANDIDATES must be a JSON array")
    if not CANDIDATES:
        raise ValueError("CANDIDATES cannot be empty")
except Exception as e:
    print(f"Error loading configuration: {str(e)}")
    raise

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

# In-memory storage
voted_students = []
cast_votes = []

# Store for DH session parameters
dh_sessions = {}


# Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html", {"request": request, "course_name": COURSE_NAME}
    )


@app.get("/admin", response_class=HTMLResponse)
async def admin(request: Request):
    return templates.TemplateResponse(
        "admin.html",
        {
            "request": request,
            "course_name": COURSE_NAME,
            "voting_students": VOTING_STUDENTS,
            "candidates": CANDIDATES,
        },
    )


@app.get("/vote", response_class=HTMLResponse)
async def vote_page(request: Request):
    return templates.TemplateResponse(
        "vote.html",
        {"request": request, "course_name": COURSE_NAME, "candidates": CANDIDATES},
    )


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
    global voted_students
    data = await request.json()
    student_id = data.get("student_id")
    blinded_ballot = data.get("blinded_ballot")
    client_id = data.get("client_id")

    # Check if student is in the list and hasn't voted
    if student_id not in VOTING_STUDENTS:
        return JSONResponse(
            status_code=403, content={"error": "Student not authorized to vote"}
        )

    # Check if student has already voted
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
    voted_students.append(student_id)

    return {"blind_signature": str(blind_signature)}


@app.post("/submit-vote")
async def submit_vote(request: Request):
    global cast_votes
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

    # Check if this exact vote has been cast before
    for cast_vote in cast_votes:
        if cast_vote["signature"] == signature:
            return JSONResponse(status_code=403, content={"error": "Vote already cast"})

    # Use the provided candidate name instead of mapping
    candidate_name = candidate

    # Store vote in memory
    cast_votes.append({"vote": candidate_name, "signature": signature})

    return {"success": True}


@app.get("/results")
async def get_results():
    global cast_votes

    # Count votes
    votes = {}
    for vote_data in cast_votes:
        vote = vote_data["vote"]
        votes[vote] = votes.get(vote, 0) + 1

    # Get participation
    students_count = len(VOTING_STUDENTS)
    voted_count = len(voted_students)

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
    global voted_students

    return {"voted_students": voted_students}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
