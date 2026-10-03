from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from routers import scan, phish, guard, auth
from auth.deps import get_current_user
from database.db import init_db, get_history, delete_scan, clear_history

app = FastAPI(
    title="AXIOMGUARD",
    description="AI-Powered Cybersecurity Intelligence Platform",
    version="1.0.0"
)

# Allow frontend and Chrome extension to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize SQLite database (creates table if it doesn't exist)
init_db()

# Register all module routers
app.include_router(auth.router, prefix="/api/auth", tags=["AUTH"])
app.include_router(scan.router, prefix="/api/scan", tags=["AXIOM//SCAN"])
app.include_router(phish.router, prefix="/api/phish", tags=["AXIOM//PHISH"])
app.include_router(guard.router, prefix="/api/guard", tags=["AXIOM//GUARD"])

@app.get("/")
def root():
    return {
        "platform": "AXIOMGUARD",
        "tagline": "Because security should be absolute.",
        "modules": ["AXIOM//SCAN", "AXIOM//PHISH", "AXIOM//GUARD"],
        "status": "online"
    }

@app.get("/api/history")
def scan_history(current_user: dict = Depends(get_current_user)):
    return {"history": get_history(20, user_id=current_user["id"])}

@app.delete("/api/history/{entry_id}")
def remove_scan(entry_id: int, current_user: dict = Depends(get_current_user)):
    deleted = delete_scan(entry_id, user_id=current_user["id"])
    if deleted:
        return {"success": True, "message": f"Entry {entry_id} deleted"}
    return {"success": False, "message": "Entry not found"}

@app.delete("/api/history")
def wipe_history(current_user: dict = Depends(get_current_user)):
    clear_history(user_id=current_user["id"])
    return {"success": True, "message": "All history cleared"}