# News reader (API: https://www.thenewsapi.com/)

## Run in Docker

build: `docker compose build`

run: `docker compose up`

stop: `docker compose down` - Removed or `Ctrl+C` - Stopped

## Functionality:
- latest news
- search by criteria
- starred articles
- recommendation based on friends

## Separation to /core, /infrastructure and /api:
- /core: domain and interfaces of repository and services (internal DB and external API models)
- /interface: implementations of /core interfaces (external API requests in repository)
- /api: FastAPI routers, uses services from /core (handles requests from client)

## TODO:
- [x] fastapi routers (user CRUD and top/all/uuid news)
- [x] repository interface
- [x] service interface
- [x] repository (initial) implementation
- [x] service (initial) implementation
- [x] domain models (User, News)
- [x] dependency injection containers
- [x] database
- [x] docker
- [ ] HTTP exceptions
- [x] friends
- [x] recommendations
- [x] favorites