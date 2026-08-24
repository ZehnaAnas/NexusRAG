"""
validation.py - the checkpoint all uploaded files must pass through
before they touch the filesystem or get queued for processing.

Rule of thumb this file follows: anything that came from a client
request is untrusted until proven otherwise. Every check here exists
to answer on question - "could this input make my server do
something I didn't intend?"
"""
import os 
from pathlib import Path
from utils.config import UPLOAD_DIR

# Allow-list, not a block-list. It's much easier to reason about 
# "these are the only types we accept" that to try to enumerate every
# dangerous file type that might exist.

ALLOWED_EXTENSIONS = {".pdf",".docx",".pptx",".txt",".csv",".md"}

# 20MB is a reasonable ceiling for the kind of documents this app is
# built for (reports, decks, resumes). Adjust if you have a real use
# case for bigger files - just pick a real number, not "unlimited."
MAX_FILE_SIZE_BYTES = 20*1024*1024

class UploadValidationError(Exception):
    """Raised whenever an uploaded file fails any validation check."""
    pass

def validate_filename(file_name:str) -> str:
    """
    Takes whatever filename the client sent and returns a name that's
    safe to use for a path on disk. Raises UploadValidationError if 
    the file can't be made safe (wrong type, empty, etc).
    """
    if not file_name or not file_name.strip():
        raise UploadValidationError("Filename cannot be empty.")

    # Layer 1 - sanitize: os.path.basename() keeps only the LAST
    # path segment, discarding everything before it. This alone
    # neutralizes both attacks we demonstrated:
    # "../../../../tmp/evil.txt" -> "evil.txt"
    # "/etc/passwd" -> "passwd"
    safe_name = os.path.basename(file_name)

    # Layer 2 - whitelist: only accept extensions this app actually
    # knows how to process.
    extension = Path(safe_name).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        allowed = ",".join(sorted(ALLOWED_EXTENSIONS))
        raise UploadValidationError(
            f"'{extension or 'no extension'} is not a supported file type."
            f"Allowed types: {allowed}"
        )

    # Layer 3 - verify (defense in depth): build the REAL final path
    # and prove it's still inside UPLOAD_DIR. resolve() turns a path
    # into its absolute, symlink-free form, so this check can't be 
    # fooled by tricks layer 1 didn't anticipate.

    upload_root = UPLOAD_DIR.resolve()
    candidate_path = (UPLOAD_DIR/safe_name).resolve()
    if candidate_path != upload_root and upload_root not in candidate_path.parents:
        raise UploadValidationError("Resolved file path escapes the upload directory.")
    return safe_name

def validate_file_size(contents: bytes) -> None:
    """
    Guards against empty uploads and oversized ones. This isn't a
    path-safety check = it's the same "don't trust input" principle
    applied to resource usage instead of file location.
    """
    size = len(contents)
    if size == 0:
        raise UploadValidationError("Uploaded file is empty.")
    if size > MAX_FILE_SIZE_BYTES:
        raise UploadValidationError(
            f"File is {size/1_000_000:.1f} MB, which exceeds the "
            f"{MAX_FILE_SIZE_BYTES/1_000_000:.0f} MB limit."
        )