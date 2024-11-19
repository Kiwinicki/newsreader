from typing import List, Optional, Union, Dict

import aiohttp
import os

from newsreader.core.domain import News, User
from newsreader.core.repository import IUserRepository, INewsRepository


class UserRepository(IUserRepository):
    def __init__(self):
        self.users_db = {
            0: User(id=0, name="John Doe"),
            1: User(id=1, name="Tom Doe"),
        }
        self.max_id = 1

    async def get_by_id(self, user_id: int) -> Optional[User]:
        return self.users_db.get(user_id)

    async def create_user(self, user: User) -> int:
        self.max_id = self.max_id + 1
        user.id = self.max_id
        self.users_db[self.max_id] = user
        return self.max_id

    async def delete_user(self, user_id: int) -> None:
        self.users_db.pop(user_id)

    async def update_user(self, user_id: int, user_data: User) -> None:
        user_data.id = user_id
        if self.users_db.get(user_id):
            self.users_db[user_id] = user_data
    
class NewsRepository(INewsRepository):
    def __init__(self):
        self._api_token: str = os.getenv("API_KEY")
        self._base_url = "https://api.thenewsapi.com/v1/news/"

    async def get_top(
        self,
        limit: int = 10,
        categories: Optional[List[str]] = None,
        language: Optional[str] = None,
    ) -> List[News]:
        params: Dict[str, Union[str, int]] = {
            "api_token": self._api_token,
            "limit": limit,
        }
        if categories:
            params["categories"] = ",".join(categories)
        if language:
            params["language"] = language

        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self._base_url}top", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("data", [])
                else:
                    return []