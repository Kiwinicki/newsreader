from abc import ABC, abstractmethod
from typing import List, Optional

from newsreader.core.domain import News, User


class IUserService(ABC):
    @abstractmethod
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
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