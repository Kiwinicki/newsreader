from abc import ABC, abstractmethod
from typing import List, Optional

from newsreader.core.domain import News, User

class IUserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: int) -> Optional[User]:
        pass

    async def get_by_id(user_id) -> Optional[User]:
        pass

    async def create_user(self, user: User) -> int:
        pass

    async def delete_user(self, user_id: int) -> None:
        pass

    async def update_user(self, user_id: int, user_data: User) -> None:
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