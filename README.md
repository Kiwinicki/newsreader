# News reader (API: https://www.thenewsapi.com/)

## Run
install project: `make install`

run project: `make run`

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
- [-] fastapi routers (user CRUD and top/all/uuid news)
- [-] repository interface
- [-] service interface
- [-] repository (initial) implementation
- [-] service (initial) implementation
- [-] domain models (User, News)
- [x] dependency injection containers
- [ ] database