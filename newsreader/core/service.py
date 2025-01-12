from abc import ABC, abstractmethod
from typing import List, Optional

from newsreader.core.domain import News, User, NewsPreview


class IUserService(ABC):
    @abstractmethod
    async def get_all_users(self) -> List[User]:
        pass

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

    @abstractmethod
    async def get_friends(self, user_id: int) -> List[User]:
        pass

    @abstractmethod
    async def add_friend(self, user_id: int, friend_id: int) -> None:
        pass

    @abstractmethod
    async def delete_friend(self, user_id: int, friend_id: int) -> None:
        pass

    @abstractmethod
    async def get_favorites(self, user_id: int) -> List[NewsPreview]:
        pass

    @abstractmethod
    async def add_to_favorites(
        self, user_id: int, news_id: str, title: str
    ) -> None:
        pass

    @abstractmethod
    async def delete_from_favorites(self, user_id: int, news_id: str) -> None:
        pass

    @abstractmethod
    async def get_recommended_news(self, user_id: int) -> List[NewsPreview]:
        pass

    @abstractmethod
    async def get_read_later(self, user_id: int) -> List[NewsPreview]:
        pass

    @abstractmethod
    async def add_read_later(
        self, user_id: int, news_id: str, title: str
    ) -> None:
        pass

    @abstractmethod
    async def delete_read_later(self, user_id: int, news_id: str) -> None:
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
    async def get_news_by_id(self, news_id: str) -> Optional[News]:
        pass
