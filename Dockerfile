# syntax=docker/dockerfile:1
# ^ Required for the --mount=type=cache feature used below (BuildKit
# Dockerfile syntax). Must be the very first line of the file.

# --- FROM: pick the exact base to build on ---
# This fixes the ONE thing requirements.txt can never fix: the Python
# version itself. "slim" is a smaller Debian-based image with just
# enough OS to run Python -- much smaller than the full default image.
FROM python:3.11-slim

# --- WORKDIR: every following instruction runs from here ---
WORKDIR /app

# --- System-level dependencies ---
# The Unstructured library (used to parse PDFs/docx/etc) needs real
# OS-level tools, not just Python packages, to handle certain file
# types -- this is exactly the category of dependency requirements.txt
# CANNOT express. If you hit a missing-binary error for a specific
# file type later, this is the block you'd extend.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmagic1 \
    poppler-utils \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# --- Dependencies BEFORE code, on purpose ---
# Docker builds in layers, and caches each layer that hasn't changed.
# By copying ONLY requirements.txt first and installing it here, a
# later change to your application code (main.py, utils/*.py) does
# NOT invalidate this layer -- so rebuilding after a code change
# reuses the cached, already-installed dependencies instead of
# reinstalling everything from scratch. If we copied all the code
# first, every single code edit would force a full reinstall.
COPY requirements.txt .

# NOTE: this project pulls in some genuinely large packages (torch,
# for PDF layout detection) -- large enough that a slow connection
# can time out partway through a single file. Two things make that
# survivable instead of painful:
#
# 1. --mount=type=cache gives pip a PERSISTENT download cache across
#    builds, without that cache ending up in the final image. If a
#    build fails after successfully downloading torch, the NEXT
#    build reuses that cached download instead of starting over --
#    this replaces the --no-cache-dir approach from earlier, which
#    traded away exactly this resilience for a smaller image. The
#    cache mount gets us both: small final image, fast retries.
# 2. --timeout and --retries give slow/flaky connections more room
#    before pip gives up on a single file.
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --timeout 120 --retries 10 -r requirements.txt

# --- Now bring in the actual application code ---
COPY . .

# --- Documentation, not enforcement ---
# EXPOSE doesn't actually open the port by itself -- it's a label for
# humans (and tools like docker-compose) saying "this container
# listens on 8000." The real exposure happens via `docker run -p` or
# a docker-compose "ports:" entry.
EXPOSE 8000

# --- The command that runs when the container starts ---
# Using uvicorn directly (not "python main.py") is the standard way
# to run a FastAPI app in production-style setups -- it's the same
# entrypoint tools like docker-compose and cloud platforms expect.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]