// Base URL of your FastAPI server (utils/main.py -> uvicorn.run(app, host="localhost", port=8000))
const BASE_URL = "http://localhost:8000";

/**
 * Uploads a file to the RAG backend.
 * NOTE: this assumes the backend fix below (main.py) is applied, so the
 * server responds with the real filename instead of the raw UploadFile repr.
 */
export async function uploadFile(file) {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${BASE_URL}/upload/file`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Upload failed");
  }
  return res.json(); // { message: file_name, status: "processing" }
}

/**
 * Polls processing status for a given file name.
 */
export async function getStatus(fileName) {
  const res = await fetch(
    `${BASE_URL}/upload/status/${encodeURIComponent(fileName)}`
  );
  if (!res.ok) throw new Error("Could not fetch status");
  return res.json(); // { file_name, status }
}

/**
 * Asks a question about a given document.
 * NOTE: sent as POST — see the main.py fix below. Browsers' fetch()
 * cannot attach a body to a GET request, so the original @app.get
 * route for this endpoint is unreachable from any real frontend.
 */
export async function askQuestion(question, fileName) {
  const res = await fetch(`${BASE_URL}/upload/question`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, file_name: fileName }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "The question could not be answered");
  }
  const data = await res.json();
  return data.message;
}
