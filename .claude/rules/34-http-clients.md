# HTTP Client Patterns

## Architecture
```
tests → GitHubAPI (facade) → GitHubHTTPClient → requests.Session
                                    ↕
                              RateLimiter
```

## GitHubHTTPClient
- Located at `utils/http/client.py`
- Handles auth headers, API versioning, rate limiting, retries
- All methods have automatic retry with exponential backoff (tenacity)
- Never bypass this client with raw `requests.*` calls

## GitHubAPI Facade
- Located at `utils/api/github_api.py`
- Domain sub-APIs: `repos`, `users`, `orgs`, `search`, `issues`, `gists`, `actions`
- Each sub-API wraps endpoints with typed methods
- Tests should use `api.<domain>.<method>()` pattern

## Adding New Endpoints
1. Add the endpoint template to `data/constants.py`
2. Add the method to the appropriate sub-API class in `github_api.py`
3. Add test constants to `data/<domain>_constants.py`
4. Write tests in `tests/<domain>/`
