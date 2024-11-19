from typing import List, Optional, Union, Dict

import aiohttp
import os

from newsreader.core.domain import News, User
from newsreader.core.repository import IUserRepository, INewsRepository


users_db = {
    1: User(id=1, name="John Doe"),
    2: User(id=2, name="Jane Doe"),
}

class UserRepository(IUserRepository):
    async def get_by_id(self, user_id: int) -> Optional[User]:
        return users_db.get(user_id)
    
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
                    print(data['data'])
                    return [News(**item) for item in data.get("data", [])]
                else:
                    return []