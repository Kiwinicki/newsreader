from typing import List, Optional
from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, Query


from newsreader.container import Container
from newsreader.core.domain import User, News
from newsreader.core.service import IUserService, INewsService

user_router = APIRouter()
news_router = APIRouter()


@user_router.get("/{user_id}", response_model=Optional[User])
@inject
async def get_user_by_id(
    user_id: int,
    service: IUserService = Depends(Provide[Container.user_service]),
) -> Optional[User]:
    return await service.get_user_by_id(user_id)

@news_router.get("/top", response_model=List[News])
@inject
async def get_top_news(
    limit: int = 10,
    categories: Optional[List[str]] = Query(None),
    language: Optional[str] = None,
    service: INewsService = Depends(Provide[Container.news_service]),
) -> List[News]:
    return await service.get_top_news(limit=limit, categories=categories, language=language)
