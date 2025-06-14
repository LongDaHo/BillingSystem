import uvicorn
from fastapi import FastAPI
from modules.normal_chat.routers import router

app = FastAPI()
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("normal_chat:app", host="0.0.0.0", port=8080, reload=True)