import logging
from typing import List, Optional
from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, Query, HTTPException


from newsreader.container import Container
from newsreader.core.domain import User, News, NewsPreview
from newsreader.core.service import IUserService, INewsService

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

user_router = APIRouter()
news_router = APIRouter()


@user_router.get("/{user_id}", response_model=Optional[User])
@inject
async def get_user_by_id(
    user_id: int,
    service: IUserService = Depends(Provide[Container.user_service]),
) -> Optional[User]:
    try:
        user = await service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")


@user_router.post("/create")
@inject
async def create_user(
    user: User,
    service: IUserService = Depends(Provide[Container.user_service]),
) -> int:
    try:
        return await service.create_user(user)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")


@user_router.delete("/{user_id}")
@inject
async def delete_user(
    user_id: int,
    service: IUserService = Depends(Provide[Container.user_service]),
) -> None:
    try:
        return await service.delete_user(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")


@user_router.put("/{user_id}")
@inject
async def update_user(
    user_id: int,
    user_data: User,
    service: IUserService = Depends(Provide[Container.user_service]),
) -> None:
    try:
        return await service.update_user(user_id, user_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")


@user_router.get("/{user_id}/friends", response_model=List[User])
@inject
async def get_user_friends(
    user_id: int,
    service: IUserService = Depends(Provide[Container.user_service]),
):
    return await service.get_friends(user_id)


@user_router.post("/{user_id}/friends")
@inject
async def add_user_friend(
    user_id: int,
    friend_id: int,
    service: IUserService = Depends(Provide[Container.user_service]),
):
    try:
        return await service.add_friend(user_id, friend_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")


@user_router.delete("/{user_id}/friends/{friend_id}")
@inject
async def delete_user_friend(
    user_id: int,
    friend_id: int,
    user_service: IUserService = Depends(Provide[Container.user_service]),
):
    try:
        return await user_service.delete_friend(user_id, friend_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")


@user_router.get("/{user_id}/favorites", response_model=List[NewsPreview])
@inject
async def get_favorites(
    user_id: int,
    user_service: IUserService = Depends(Provide[Container.user_service]),
):
    try:
        return await user_service.get_favorites(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")


@user_router.post("/{user_id}/favorites")
@inject
async def add_to_favorites(
    user_id: int,
    news_id: str,
    title: str,
    user_service: IUserService = Depends(Provide[Container.user_service]),
):
    try:
        return await user_service.add_to_favorites(user_id, news_id, title)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")


@user_router.delete("/{user_id}/favorites")
@inject
async def delete_from_favorites(
    user_id: int,
    news_id: str,
    user_service: IUserService = Depends(Provide[Container.user_service]),
):
    try:
        return await user_service.delete_from_favorites(user_id, news_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")


@user_router.get("/{user_id}/recommended")
@inject
async def get_recommended_news(
    user_id: int,
    user_service: IUserService = Depends(Provide[Container.user_service]),
):
    try:
        return await user_service.get_recommended_news(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")


@news_router.get("/top", response_model=List[News])
@inject
async def get_top_news(
    limit: int = 10,
    categories: Optional[List[str]] = Query(None),
    language: Optional[str] = None,
    service: INewsService = Depends(Provide[Container.news_service]),
) -> List[News]:
    try:
        news = await service.get_top_news(
            limit=limit, categories=categories, language=language
        )
        if not news:
            raise HTTPException(status_code=404, detail=f"News not found")
        return news
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")


@news_router.get("/all", response_model=List[News])
@inject
async def get_all_news(
    limit: int = 10,
    search: Optional[str] = Query(None),
    categories: Optional[List[str]] = Query(None),
    language: Optional[str] = None,
    service: INewsService = Depends(Provide[Container.news_service]),
) -> List[News]:
    try:
        news = await service.get_all_news(
            search=search, limit=limit, categories=categories, language=language
        )
        if not news:
            raise HTTPException(status_code=404, detail=f"News not found")
        return news
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")


@news_router.get("/{news_id}", response_model=News)
@inject
async def get_news_by_id(
    news_id: str,
    service: INewsService = Depends(Provide[Container.news_service]),
) -> Optional[News]:
    try:
        news = await service.get_news_by_id(news_id)
        if not news:
            raise HTTPException(status_code=404, detail=f"News not found")
        return news
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")
