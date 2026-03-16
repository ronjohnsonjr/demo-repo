"""Constants specific to search endpoint tests."""

# Search queries that should always return results
SEARCH_QUERIES_REPOS = [
    "language:python stars:>10000",
    "tetris language:javascript",
    "org:google language:go",
]

SEARCH_QUERIES_USERS = [
    "torvalds",
    "location:san+francisco type:user",
    "followers:>1000",
]

SEARCH_QUERIES_ISSUES = [
    "repo:facebook/react is:open label:bug",
    "repo:microsoft/vscode is:issue is:open",
]

SEARCH_REQUIRED_FIELDS = [
    "total_count",
    "incomplete_results",
    "items",
]
