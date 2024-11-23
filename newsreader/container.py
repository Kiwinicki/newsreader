from dependency_injector import containers, providers
from newsreader.infrastructure.repository import UserRepository, NewsRepository
from newsreader.infrastructure.service import UserService, NewsService


class Container(containers.DeclarativeContainer):
    user_repository = providers.Singleton(UserRepository)
    news_repository = providers.Singleton(NewsRepository)

    user_service = providers.Factory(UserService, repository=user_repository)
    news_service = providers.Factory(NewsService, repository=news_repository)