from contextlib import asynccontextmanager
from .utils.rag_helpers import initialize_rag_system
from fastapi import Request, FastAPI
from .routes.stocks import router as stocksRouter
from .routes.tickers import router as tickersRouter
from .auth.routes import router as authRouter


@asynccontextmanager
async def lifespan(app:FastAPI):
    # instantiate vector store and agent
    agent=initialize_rag_system()
    app.state.agent=agent
    yield 

def get_agent(request:Request):
    return request.app.state.agent

app=FastAPI(lifespan=lifespan)

app.include_router(stocksRouter)
app.include_router(tickersRouter)
app.include_router(authRouter)

@app.get("/")
async def root():
    return {"message":"hello world",
            }
