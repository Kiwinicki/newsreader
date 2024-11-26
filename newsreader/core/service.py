from abc import ABC, abstractmethod
from typing import List, Optional

from newsreader.core.domain import News, User


class IUserService(ABC):
    @abstractmethod
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        pass

    @abstractmethod
    async def create_user(self, user: User) -> int:
        pass

    @abstractmethod
    async def delete_user(self, user_id: int) -> None:
        pass

    @abstractmethod
    async def update_user(self, user_id: int, user_data: User) -> None:
        pass


class INewsService(ABC):
    @abstractmethod
    async def get_top_news(
        self,
        limit: int = 10,
        categories: Optional[List[str]] = None,
        language: Optional[str] = None,
    ) -> List[News]:
        pass

    @abstractmethod
    async def get_all_news(
        self,
        limit: int = 10,
        search: Optional[str] = None,
        categories: Optional[List[str]] = None,
        language: Optional[str] = None,
    ) -> List[News]:
        pass

    @abstractmethod
    async def get_news_by_id(
        self,
        news_id: str
    ) -> List[News]:
        pass