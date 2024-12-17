from typing import List, Optional, Union, Dict

import aiohttp
import os
from urllib.parse import quote
from sqlalchemy import select, delete, insert
from newsreader.core.domain import News, User, NewsPreview
from newsreader.db import (
    user_table,
    user_friends_table,
    user_favorites,
    database,
)
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
        self._api_token = os.getenv("API_KEY")
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
            async with session.get(
                f"{self._base_url}top", params=params
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    news_list = data.get("data", [])
                    validated_news = []
                    for news_data in news_list:
                        try:
                            validated_news.append(
                                News.model_validate(news_data)
                            )
                        except (KeyError, ValueError) as e:
                            print(f"Error parsing news: {e}")
                    return validated_news
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
            params["search"] = quote(search)
        if categories:
            params["categories"] = ",".join(categories)
        if language:
            params["language"] = language

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self._base_url}all", params=params
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    news_list = data.get("data", [])
                    validated_news = []
                    for news_data in news_list:
                        try:
                            validated_news.append(
                                News.model_validate(news_data)
                            )
                        except (KeyError, ValueError) as e:
                            print(f"Error parsing news: {e}")
                    return validated_news
                else:
                    return []

    async def get_by_id(self, news_id: str) -> Optional[News]:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self._base_url}/uuid/{news_id}",
                params={"api_token": self._api_token},
            ) as response:
                if response.status == 200:
                    try:
                        data = await response.json()
                        if data:
                            return News.model_validate(data)
                        else:
                            return None
                    except (KeyError, ValueError, IndexError) as e:
                        print(f"Error parsing news data: {e}")
                        return None
                else:
                    return None


class UserRepositoryDB(IUserRepository):
    async def get_by_id(self, user_id: int) -> User | None:
        query = user_table.select().where(user_table.c.id == user_id)
        result = await database.fetch_one(query)
        if result:
            user = User.model_validate(result)
            user.friends = await self.get_friend_ids(user_id)
            return user
        return None

    async def get_friend_ids(self, user_id: int) -> List[int]:
        query = select(user_friends_table.c.friend_id).where(
            user_friends_table.c.user_id == user_id
        )
        results = await database.fetch_all(query)
        return [row["friend_id"] for row in results] if results else []

    async def create_user(self, user: User) -> int:
        query = user_table.insert().values(
            **user.model_dump(exclude={"id", "friends", "favorites"})
        )
        user_id = await database.execute(query)
        return user_id

    async def delete_user(self, user_id: int) -> None:
        # first delete user from friends, second delete user
        del_friend_query1 = delete(user_friends_table).where(
            (user_friends_table.c.user_id == user_id)
            | (user_friends_table.c.friend_id == user_id)
        )
        del_user_query2 = delete(user_table).where(user_table.c.id == user_id)

        async with database.transaction():
            await database.execute(del_friend_query1)
            await database.execute(del_user_query2)

    async def update_user(self, user_id: int, user_data: User) -> None:
        query = (
            user_table.update()
            .where(user_table.c.id == user_id)
            .values(name=user_data.name)
        )
        await database.execute(query)

    async def get_friends(self, user_id: int) -> List[User]:
        friend_ids = await self.get_friend_ids(user_id)
        query = select(user_table).where(user_table.c.id.in_(friend_ids))
        results = await database.fetch_all(query)
        return [User.model_validate(result) for result in results]

    async def add_friend(self, user_id: int, friend_id: int) -> None:
        # check if both users exist
        query_user = select(user_table).where(user_table.c.id == user_id)
        query_friend = select(user_table).where(user_table.c.id == friend_id)
        user = await database.fetch_one(query_user)
        friend = await database.fetch_one(query_friend)

        if user and friend and user_id != friend_id:
            query1 = insert(user_friends_table).values(
                user_id=user_id, friend_id=friend_id
            )
            await database.execute(query1)
            query2 = insert(user_friends_table).values(
                user_id=friend_id, friend_id=user_id
            )
            await database.execute(query2)
        else:
            raise ValueError("User or friend not exist")

    async def delete_friend(self, user_id: int, friend_id: int) -> None:
        query = delete(user_friends_table).where(
            (user_friends_table.c.user_id == user_id)
            & (user_friends_table.c.friend_id == friend_id)
        )
        await database.execute(query)

    async def get_favorites(self, user_id: int) -> List[NewsPreview]:
        query = select(user_favorites.c.news_id, user_favorites.c.title).where(
            user_favorites.c.user_id == user_id
        )
        results = await database.fetch_all(query)
        return [
            NewsPreview(uuid=row["news_id"], title=row["title"])
            for row in results
        ]  # minimal info (retrive from API for all details)

    async def add_to_favorites(
        self, user_id: int, news_id: str, title: str
    ) -> None:
        query = insert(user_favorites).values(
            user_id=user_id, news_id=news_id, title=title
        )
        await database.execute(query)

    async def delete_from_favorites(self, user_id: int, news_id: str) -> None:
        query = delete(user_favorites).where(
            (user_favorites.c.user_id == user_id)
            & (user_favorites.c.news_id == news_id)
        )
        await database.execute(query)

    async def get_recommended_posts(self, user_id: int) -> List[NewsPreview]:
        friends = await self.get_friends(user_id)
        recommendations: set = set()
        for friend in friends:
            recommendations.update(await self.get_favorites(friend.id))
        return list(recommendations)
