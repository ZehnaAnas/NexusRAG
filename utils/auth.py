"""
auth.py - two small, focused jobs:

1. get_current_owner: FastAPI "dependency" that proves WHO is calling
   (authentication). Any endpoint that adds
   `owner: str = Depends(get_current_owner)` to its function signature
   gets this run automatically before its own code executes.
 
2. storage_key: turns (owner, file_name) into one collision-proof
   string. This is the authorization half — it's computed ONCE at the
   API boundary, then passed down into the existing pipeline
   (loaders, vectorstore, chain cache) untouched. Those files never
   need to know "owner" exists; they just see a slightly different
   string than before. Keeping the change at the edge like this is a
   pattern worth reusing: the fewer files that need to understand a
   new concept, the smaller the chance of a bug slipping through one
   you forgot to update.
"""
from fastapi import Header, HTTPException
from utils.db import verify_api_key
 
 
async def get_current_owner(x_api_key: str = Header(..., alias="X-API-Key")) -> str:
    """
    Reads the X-API-Key header FastAPI extracted from the request,
    checks it against the database, and either returns the owner's
    name or raises a 401 before the endpoint body ever runs.
    """
    owner = verify_api_key(x_api_key)
    if owner is None:
        raise HTTPException(status_code=401, detail="Invalid or missing API key.")
    return owner
 
 
def storage_key(owner: str, file_name: str) -> str:
    """
    e.g. storage_key("alice", "resume.pdf") -> "alice__resume.pdf"
 
    Two different owners can now both upload "resume.pdf" without
    colliding on disk, in the vectorstore, or in the chain cache —
    and neither one can construct the other's key, because they never
    get to choose the "owner" part themselves; it comes from their
    verified API key, not from anything they typed.
    """
    return f"{owner}__{file_name}"