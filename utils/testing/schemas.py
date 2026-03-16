"""JSON Schema definitions for GitHub API response validation."""

REPO_SCHEMA = {
    "type": "object",
    "required": ["id", "name", "full_name", "owner", "html_url", "description", "fork", "url"],
    "properties": {
        "id": {"type": "integer"},
        "name": {"type": "string"},
        "full_name": {"type": "string"},
        "owner": {
            "type": "object",
            "required": ["login", "id"],
            "properties": {
                "login": {"type": "string"},
                "id": {"type": "integer"},
            },
        },
        "html_url": {"type": "string", "format": "uri"},
        "description": {"type": ["string", "null"]},
        "fork": {"type": "boolean"},
        "url": {"type": "string", "format": "uri"},
        "created_at": {"type": "string"},
        "updated_at": {"type": "string"},
        "stargazers_count": {"type": "integer"},
        "forks_count": {"type": "integer"},
        "language": {"type": ["string", "null"]},
    },
}

USER_SCHEMA = {
    "type": "object",
    "required": ["login", "id", "type", "html_url"],
    "properties": {
        "login": {"type": "string"},
        "id": {"type": "integer"},
        "type": {"type": "string", "enum": ["User", "Organization"]},
        "html_url": {"type": "string", "format": "uri"},
        "name": {"type": ["string", "null"]},
        "company": {"type": ["string", "null"]},
        "blog": {"type": ["string", "null"]},
        "location": {"type": ["string", "null"]},
        "email": {"type": ["string", "null"]},
        "bio": {"type": ["string", "null"]},
        "public_repos": {"type": "integer"},
        "followers": {"type": "integer"},
        "following": {"type": "integer"},
    },
}

ORG_SCHEMA = {
    "type": "object",
    "required": ["login", "id", "url", "description"],
    "properties": {
        "login": {"type": "string"},
        "id": {"type": "integer"},
        "url": {"type": "string", "format": "uri"},
        "description": {"type": ["string", "null"]},
        "name": {"type": ["string", "null"]},
        "company": {"type": ["string", "null"]},
        "blog": {"type": ["string", "null"]},
        "location": {"type": ["string", "null"]},
        "public_repos": {"type": "integer"},
        "public_gists": {"type": "integer"},
        "followers": {"type": "integer"},
        "following": {"type": "integer"},
    },
}

SEARCH_RESULT_SCHEMA = {
    "type": "object",
    "required": ["total_count", "incomplete_results", "items"],
    "properties": {
        "total_count": {"type": "integer"},
        "incomplete_results": {"type": "boolean"},
        "items": {"type": "array"},
    },
}

ISSUE_SCHEMA = {
    "type": "object",
    "required": ["id", "number", "title", "state", "user"],
    "properties": {
        "id": {"type": "integer"},
        "number": {"type": "integer"},
        "title": {"type": "string"},
        "state": {"type": "string", "enum": ["open", "closed"]},
        "user": {
            "type": "object",
            "required": ["login", "id"],
        },
        "labels": {"type": "array"},
        "created_at": {"type": "string"},
        "updated_at": {"type": "string"},
        "body": {"type": ["string", "null"]},
    },
}

GIST_SCHEMA = {
    "type": "object",
    "required": ["id", "url", "files", "public", "created_at"],
    "properties": {
        "id": {"type": "string"},
        "url": {"type": "string", "format": "uri"},
        "files": {"type": "object"},
        "public": {"type": "boolean"},
        "created_at": {"type": "string"},
        "description": {"type": ["string", "null"]},
    },
}

WORKFLOW_SCHEMA = {
    "type": "object",
    "required": ["total_count", "workflows"],
    "properties": {
        "total_count": {"type": "integer"},
        "workflows": {"type": "array"},
    },
}
