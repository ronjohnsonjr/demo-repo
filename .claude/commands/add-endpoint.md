# Add Endpoint

Add a new GitHub API endpoint to the test framework. Follow these steps:

1. Add endpoint template to `data/constants.py`
2. Add domain constants to `data/<domain>_constants.py`
3. Add API method to `utils/api/github_api.py` under the appropriate sub-API class
4. Add JSON schema to `utils/testing/schemas.py`
5. Create test file at `tests/<domain>/test_<endpoint>.py`
6. Run `make test` and `make lint` to verify

Endpoint to add: $ARGUMENTS
