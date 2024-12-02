from abc import ABC, abstractmethod
from typing import List, Optional

from newsreader.core.domain import News, User

class IUserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: int) -> Optional[User]:
        pass

    @abstractmethod
    async def get_by_id(user_id) -> Optional[User]:
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


class INewsRepository(ABC):
    @abstractmethod
    async def get_top(
        self,
        limit: int = 10,
        categories: Optional[List[str]] = None,
        language: Optional[str] = None,
    ) -> List[News]:
        pass

    @abstractmethod
    async def get_all(
        self,
        limit: int = 10,
        search: Optional[str] = None,
        categories: Optional[List[str]] = None,
        language: Optional[str] = None,
    ) -> List[News]:
        pass

    @abstractmethod
    async def get_by_id(
        self,
        news_id: str
    ) -> List[News]:
        pass