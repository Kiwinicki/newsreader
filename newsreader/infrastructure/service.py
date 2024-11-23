from typing import List, Optional
from newsreader.core.domain import User, News
from newsreader.core.repository import IUserRepository, INewsRepository
from newsreader.core.service import IUserService, INewsService


class UserService(IUserService):

    _repository: IUserRepository

    def __init__(self, repository: IUserRepository):
        self._repository = repository

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        return await self._repository.get_by_id(user_id)
    
    async def create_user(self, user: User) -> int:
        return await self._repository.create_user(user)

    async def delete_user(self, user_id: int) -> None:
        await self._repository.delete_user(user_id)

    async def update_user(self, user_id: int, user_data: User) -> None:
        await self._repository.update_user(user_id=user_id, user_data=user_data)


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