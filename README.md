# News reader (API: https://www.thenewsapi.com/)

## Run in Docker

build: `docker compose build`

run: `docker compose up`

stop: `Ctrl+C`

remove: `docker compose down`

## Functionality:
- latest news
- search by criteria
- starred articles
- recommendation based on friends

## Separation to `/core`, `/infrastructure` and `/api`:
- `/core`: domain and interfaces of repository and services (internal DB and external API models)
- `/interface`: implementations of `/core` interfaces (external API requests in repository)
- `/api`: FastAPI routers, uses services from `/core` (handles requests from client)

## TODO:
- [x] fastapi routers (get all/by_id/favorites/friends/read_later user and top/all/by_id news)
- [x] repository, service interface
- [x] repository, service implementation
- [x] domain models (User, News)
- [x] dependency injection containers
- [x] database (with inital SQL data)
- [x] docker
- [x] HTTP exceptions
- [x] friends
- [x] recommendations
- [x] favorites
- [x] read_later