from pathlib import Path
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from prod_assistant.workflow.agentic_rag_workflow import AgenticRAG

app = FastAPI()

# --- repo root (.. / .. / .. from prod_assistant/router/main.py) ---
REPO_ROOT = Path(__file__).resolve().parents[2]
TEMPLATES_DIR = (REPO_ROOT / "templates").resolve()
STATIC_DIR = (REPO_ROOT / "static").resolve()

# Safety: ensure dirs exist (prevents RuntimeError on mount)
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR.mkdir(parents=True, exist_ok=True)

print(f"[BOOT] TEMPLATES_DIR={TEMPLATES_DIR}  exists={TEMPLATES_DIR.exists()}")
print(f"[BOOT] STATIC_DIR   ={STATIC_DIR}   exists={STATIC_DIR.exists()}")

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Routes ----------
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

@app.get("/healthz")
def healthz():
    return {"ok": True}

@app.post("/get", response_class=HTMLResponse)
async def chat(msg: str = Form(...)):
    rag_agent = AgenticRAG()
    return rag_agent.run(msg)

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("prod_assistant.router.main:app", host="0.0.0.0", port=8000, reload=True)
#     uvicorn prod_assistant.router.main:app --reload --port 8000
