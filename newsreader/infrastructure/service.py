from typing import List, Optional
from newsreader.core.domain import User, News, NewsPreview
from newsreader.core.repository import IUserRepository, INewsRepository
from newsreader.core.service import IUserService, INewsService
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

def _handle_db_error(func):
    """Helper to handle database errors"""
    async def wrapper(*args, **kwargs):
       try:
           return await func(*args, **kwargs)
       except SQLAlchemyError as e:
           raise HTTPException(status_code=500, detail=f"Database error: {e}")
    return wrapper


class UserService(IUserService):
    _repository: IUserRepository

    def __init__(self, repository: IUserRepository):
        self._repository = repository

    @_handle_db_error
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        return await self._repository.get_by_id(user_id)

    @_handle_db_error
    async def create_user(self, user: User) -> int:
        return await self._repository.create_user(user)

    @_handle_db_error
    async def delete_user(self, user_id: int) -> None:
        await self._repository.delete_user(user_id)

    @_handle_db_error
    async def update_user(self, user_id: int, user_data: User) -> None:
        await self._repository.update_user(user_id=user_id, user_data=user_data)

    @_handle_db_error
    async def get_friends(self, user_id: int) -> List[User]:
        return await self._repository.get_friends(user_id)

    @_handle_db_error
    async def add_friend(self, user_id: int, friend_id: int) -> None:
        return await self._repository.add_friend(user_id, friend_id)

    @_handle_db_error
    async def delete_friend(self, user_id: int, friend_id: int) -> None:
        return await self._repository.delete_friend(user_id, friend_id)

    @_handle_db_error
    async def get_favorites(self, user_id: int) -> List[NewsPreview]:
        return await self._repository.get_favorites(user_id)

    @_handle_db_error
    async def add_to_favorites(
        self, user_id: int, news_id: str, title: str
    ) -> None:
        await self._repository.add_to_favorites(user_id, news_id, title)

    @_handle_db_error
    async def delete_from_favorites(self, user_id: int, news_id: str) -> None:
        await self._repository.delete_from_favorites(user_id, news_id)

    @_handle_db_error
    async def get_recommended_news(self, user_id: int) -> List[NewsPreview]:
        return await self._repository.get_recommended_news(user_id)


class NewsService(INewsService):
    _repository: INewsRepository

    def __init__(self, repository: INewsRepository):
        self._repository = repository

    async def get_top_news(
        self,
        limit: int = 10,
        categories: Optional[List[str]] = None,
        language: Optional[str] = None,
    ) -> List[News]:
        return await self._repository.get_top(limit, categories, language)

    async def get_all_news(
        self,
        limit: int = 10,
        search: Optional[str] = None,
        categories: Optional[List[str]] = None,
        language: Optional[str] = None,
    ) -> List[News]:
        return await self._repository.get_all(
            limit, search, categories, language
        )

    async def get_news_by_id(self, news_id: str) -> Optional[News]:
        return await self._repository.get_by_id(news_id)