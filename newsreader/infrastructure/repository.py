from typing import List, Optional, Union, Dict

import aiohttp
import os
from urllib.parse import quote

from newsreader.core.domain import News, User
from newsreader.db import user_table, database
from newsreader.core.repository import IUserRepository, INewsRepository


class UserRepositoryMock(IUserRepository):
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
                
    async def get_all(
        self,
        limit: int = 10,
        search: Optional[str] = None,
        categories: Optional[List[str]] = None,
        language: Optional[str] = None,
    ) -> List[News]:
        params: Dict[str, Union[str, int]] = {
            "api_token": self._api_token,
            "limit": limit,
        }
        if search:
            params['search'] = quote(search)
        if categories:
            params["categories"] = ",".join(categories)
        if language:
            params["language"] = language

        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self._base_url}all", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("data", [])
                else:
                    return []

    async def get_by_id(
        self,
        news_id: str
    ) -> News:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self._base_url}/{news_id}", params={'api_token': self._api_token}) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("data", [])
                else:
                    return []

class UserRepositoryDB(IUserRepository):
    async def get_by_id(self, user_id: int) -> User | None:
        query = user_table.select().where(user_table.c.id == user_id)
        result = await database.fetch_one(query)
        if result:
            return User.model_validate(result)
        return None

    async def create_user(self, user: User) -> int:
        query = user_table.insert().values(**user.model_dump(exclude={"id"}))
        user_id = await database.execute(query)
        return user_id

    async def delete_user(self, user_id: int) -> None:
        query = user_table.delete().where(user_table.c.id == user_id)
        await database.execute(query)

    async def update_user(self, user_id: int, user_data: User) -> None:
        query = user_table.update().where(user_table.c.id == user_id).values(**user_data.model_dump(exclude={"id"}))
        await database.execute(query)