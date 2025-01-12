from typing import List, Optional, Union, Dict

import aiohttp
import os
from urllib.parse import quote
from sqlalchemy import select, delete, insert
from sqlalchemy.exc import SQLAlchemyError
from newsreader.core.domain import News, User, NewsPreview
from newsreader.db import (
    user_table,
    user_friends_table,
    user_favorites_table,
    read_later_table,
    database,
)
from newsreader.core.repository import IUserRepository, INewsRepository
from fastapi import HTTPException


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


async def _handle_api_response(response: aiohttp.ClientResponse):
    """Helper to handle API responses and errors"""
    try:
        response.raise_for_status()
        return await response.json()
    except aiohttp.ClientError as e:
        raise HTTPException(status_code=500, detail=f"Network error: {e}")
    except HTTPException as e:
        raise HTTPException(
            status_code=response.status, detail=f"API Error: {e.detail}"
        )  # Raise the already created HTTP Exception
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unknown error: {e}")


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
                data = await _handle_api_response(response)
                news_list = data.get("data", [])
                validated_news = []
                for news_data in news_list:
                    try:
                        validated_news.append(News.model_validate(news_data))
                    except (KeyError, ValueError) as e:
                        print(f"Error parsing news: {e}")
                return validated_news

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
                data = await _handle_api_response(response)
                news_list = data.get("data", [])
                validated_news = []
                for news_data in news_list:
                    try:
                        validated_news.append(News.model_validate(news_data))
                    except (KeyError, ValueError) as e:
                        print(f"Error parsing news: {e}")
                return validated_news

    async def get_by_id(self, news_id: str) -> Optional[News]:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self._base_url}/uuid/{news_id}",
                params={"api_token": self._api_token},
            ) as response:
                data = await _handle_api_response(response)
                if data:
                    return News.model_validate(data)
                else:
                    return None


class UserRepositoryDB(IUserRepository):
    async def get_all(self) -> List[User]:
        query = user_table.select()
        results = await database.fetch_all(query)
        users = []
        for row in results:
            user = User.model_validate(row)
            user.friends = await self.get_friend_ids(user.id)
            user.favorites = await self.get_favorites(user.id)
            user.read_later = await self.get_read_later(user.id)
            users.append(user)

        return users

    async def get_by_id(self, user_id: int) -> User | None:
        query = user_table.select().where(user_table.c.id == user_id)
        result = await database.fetch_one(query)
        if result:
            user = User.model_validate(result)
            user.friends = await self.get_friend_ids(user_id)
            user.favorites = await self.get_favorites(user_id)
            user.read_later = await self.get_read_later(user_id)
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
            **user.model_dump(
                exclude={"id", "friends", "favorites", "read_later"}
            )
        )
        user_id = await database.execute(query)
        return user_id

    async def delete_user(self, user_id: int) -> None:
        del_favorites_query = delete(user_favorites_table).where(
            user_favorites_table.c.user_id == user_id
        )
        del_read_later_query = delete(read_later_table).where(
            read_later_table.c.user_id == user_id
        )
        del_friend_query1 = delete(user_friends_table).where(
            (user_friends_table.c.user_id == user_id)
            | (user_friends_table.c.friend_id == user_id)
        )
        del_user_query2 = delete(user_table).where(user_table.c.id == user_id)

        async with database.transaction():
            await database.execute(del_favorites_query)
            await database.execute(del_read_later_query)
            await database.execute(del_friend_query1)
            await database.execute(del_user_query2)

    async def update_user(self, user_id: int, user_data: User) -> None:
        async with database.transaction():
            # update the user name
            query = (
                user_table.update()
                .where(user_table.c.id == user_id)
                .values(name=user_data.name)
            )
            await database.execute(query)

            # fetch all existing user id
            existing_users = await database.fetch_all(select(user_table.c.id))
            existing_user_ids = {row["id"] for row in existing_users}

            # validate friends
            for friend_id in user_data.friends:
                if friend_id not in existing_user_ids:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Friend with ID {friend_id} does not exist.",
                    )
                if friend_id == user_id:
                    raise HTTPException(
                        status_code=400,
                        detail="Cannot add yourself as a friend.",
                    )

            # delete existing friends
            delete_friends_query = user_friends_table.delete().where(
                (user_friends_table.c.user_id == user_id)
                | (user_friends_table.c.friend_id == user_id)
            )
            await database.execute(delete_friends_query)

            # insert new friends with bidirectional relationships
            if user_data.friends:
                insert_friends = []
                for friend_id in user_data.friends:
                    insert_friends.append(
                        {"user_id": user_id, "friend_id": friend_id}
                    )
                    insert_friends.append(
                        {"user_id": friend_id, "friend_id": user_id}
                    )
                await database.execute_many(
                    user_friends_table.insert(), insert_friends
                )

            # delete existing favorites
            delete_favorites_query = user_favorites_table.delete().where(
                user_favorites_table.c.user_id == user_id
            )
            await database.execute(delete_favorites_query)

            # insert new favorites
            if user_data.favorites:
                insert_favorites = []
                for favorite in user_data.favorites:
                    insert_favorites.append(
                        {
                            "user_id": user_id,
                            "news_id": favorite.uuid,
                            "title": favorite.title,
                        }
                    )
                await database.execute_many(
                    user_favorites_table.insert(), insert_favorites
                )

            # delete existing read later
            delete_read_later_query = read_later_table.delete().where(
                read_later_table.c.user_id == user_id
            )
            await database.execute(delete_read_later_query)

            # insert new read later
            if user_data.read_later:
                insert_read_later = []
                for read_later in user_data.read_later:
                    insert_read_later.append(
                        {
                            "user_id": user_id,
                            "news_id": read_later.uuid,
                            "title": read_later.title,
                        }
                    )
                await database.execute_many(
                    read_later_table.insert(), insert_read_later
                )

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
        query1 = delete(user_friends_table).where(
            (user_friends_table.c.user_id == user_id)
            & (user_friends_table.c.friend_id == friend_id)
        )
        await database.execute(query1)

        query2 = delete(user_friends_table).where(
            (user_friends_table.c.user_id == friend_id)
            & (user_friends_table.c.friend_id == user_id)
        )
        await database.execute(query2)

    async def get_favorites(self, user_id: int) -> List[NewsPreview]:
        query = select(
            user_favorites_table.c.news_id, user_favorites_table.c.title
        ).where(user_favorites_table.c.user_id == user_id)
        results = await database.fetch_all(query)
        return [
            NewsPreview(uuid=row["news_id"], title=row["title"])
            for row in results
        ]  # minimal info (retrive from API for all details)

    async def add_to_favorites(
        self, user_id: int, news_id: str, title: str
    ) -> None:
        query = insert(user_favorites_table).values(
            user_id=user_id, news_id=news_id, title=title
        )
        await database.execute(query)

    async def delete_from_favorites(self, user_id: int, news_id: str) -> None:
        query = delete(user_favorites_table).where(
            (user_favorites_table.c.user_id == user_id)
            & (user_favorites_table.c.news_id == news_id)
        )
        await database.execute(query)

    async def get_recommended_news(self, user_id: int) -> List[NewsPreview]:
        friends = await self.get_friends(user_id)
        recommendations = []
        seen_news_ids = set()
        for friend in friends:
            favorites = await self.get_favorites(friend.id)
            for favorite in favorites:
                if favorite.uuid not in seen_news_ids:
                    recommendations.append(favorite)
                    seen_news_ids.add(favorite.uuid)
        return recommendations

    async def get_read_later(self, user_id: int) -> List[NewsPreview]:
        query = select(
            read_later_table.c.news_id, read_later_table.c.title
        ).where(read_later_table.c.user_id == user_id)
        results = await database.fetch_all(query)
        return [
            NewsPreview(uuid=row["news_id"], title=row["title"])
            for row in results
        ]

    async def add_read_later(
        self, user_id: int, news_id: str, title: str
    ) -> None:
        query = insert(read_later_table).values(
            user_id=user_id, news_id=news_id, title=title
        )
        await database.execute(query)

    async def delete_read_later(self, user_id: int, news_id: str) -> None:
        query = delete(read_later_table).where(
            (read_later_table.c.user_id == user_id)
            & (read_later_table.c.news_id == news_id)
        )
        await database.execute(query)
