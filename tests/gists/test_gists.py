"""Tests for gist-related endpoints.

Validates public gist listing and single gist retrieval.
"""

import pytest

from data.gists_constants import GIST_REQUIRED_FIELDS
from utils.api.github_api import GitHubAPI
from utils.testing.helpers import assert_json_keys


@pytest.mark.test_gists
class TestListPublicGists:
    """GET /gists/public — list public gists."""

    def test_list_public_gists_returns_list(self, api: GitHubAPI):
        """Verify public gist listing returns a non-empty list."""
        gists = api.gists.list_public_gists(per_page=5)
        assert isinstance(gists, list)
        assert len(gists) > 0

    def test_gist_has_required_fields(self, api: GitHubAPI):
        """Verify each gist has required fields."""
        gists = api.gists.list_public_gists(per_page=3)
        for gist in gists:
            assert "id" in gist
            assert "url" in gist
            assert "files" in gist
            assert "public" in gist

    def test_gist_files_are_non_empty(self, api: GitHubAPI):
        """Verify each gist has at least one file."""
        gists = api.gists.list_public_gists(per_page=3)
        for gist in gists:
            assert len(gist["files"]) > 0


@pytest.mark.test_gists
class TestGetGist:
    """GET /gists/{gist_id} — retrieve a specific gist."""

    def test_get_gist_by_id(self, api: GitHubAPI):
        """Verify fetching a gist by ID from the public listing."""
        # First get a valid gist ID
        gists = api.gists.list_public_gists(per_page=1)
        assert len(gists) > 0
        gist_id = gists[0]["id"]

        # Then fetch it directly
        gist = api.gists.get_gist(gist_id)
        assert gist["id"] == gist_id

    def test_get_gist_has_files_content(self, api: GitHubAPI):
        """Verify a fetched gist includes file content."""
        gists = api.gists.list_public_gists(per_page=1)
        gist = api.gists.get_gist(gists[0]["id"])

        for filename, file_info in gist["files"].items():
            assert "filename" in file_info
            assert "size" in file_info
