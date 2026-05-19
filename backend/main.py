from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from agent import agent

app = FastAPI(title="GitHub Dev Card Generator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def health_check():
    return {"status": "ok"}

@app.get("/generate/{username}")
async def generate_card(username: str):
    data = await agent.generate_card_data(username)
    return data

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
