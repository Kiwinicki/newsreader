import os
from dotenv import load_dotenv

load_dotenv()
print('API_KEY:', os.getenv('API_KEY'))

from fastapi import FastAPI
from newsreader.api.routers import user_router, news_router
from newsreader.container import Container

container = Container()
container.wire(modules=["newsreader.api.routers"])

app = FastAPI(debug=True)
app.include_router(user_router, prefix="/user")
app.include_router(news_router, prefix="/news")