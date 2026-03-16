# Constants Conventions

## Structure
- `data/constants.py` — Global constants (base URL, status codes, endpoint templates, rate limits)
- `data/<domain>_constants.py` — Domain-specific constants (test data, expected values, required fields)

## Naming
- HTTP status codes: `HTTP_<code>_<NAME>` (e.g., `HTTP_200_OK`, `HTTP_404_NOT_FOUND`)
- Endpoint templates: `ENDPOINT_<DOMAIN>_<ACTION>` (e.g., `ENDPOINT_REPOS`, `ENDPOINT_USER_REPOS`)
- Required fields: `<ENTITY>_REQUIRED_FIELDS` (e.g., `REPO_REQUIRED_FIELDS`)
- Test data: `TEST_<ENTITY>_<PROPERTY>` (e.g., `TEST_USERNAME`, `TEST_ORG`)
- Expected values: `<ENTITY>_EXPECTED` (e.g., `OCTOCAT_EXPECTED`)

## Rules
- Never hardcode URLs, status codes, or field names in test files.
- Always import from the appropriate `data/` module.
- Add new constants to the relevant module, not inline.
