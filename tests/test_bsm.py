import pytest

from src.bsm.exceptions import (
    BSMError,
    BSMAuthenticationError,
    BSMConnectionError,
    BSMNotFoundError,
    BSMServerError,
)
from src.bsm.models import ServerInfo, ServerStatus, TaskResult, AuthToken


class TestModels:
    def test_server_info_defaults(self):
        server = ServerInfo(name="test")
        assert server.status == ServerStatus.UNKNOWN
        assert server.online_players == 0
        assert server.max_players == 0

    def test_task_result(self):
        result = TaskResult(status="success", message="Server started")
        assert result.status == "success"
        assert result.message == "Server started"
        assert result.details is None

    def test_auth_token(self):
        token = AuthToken(access_token="abc123")
        assert token.access_token == "abc123"
        assert token.token_type == "bearer"


class TestExceptions:
    def test_bsm_error(self):
        with pytest.raises(BSMError):
            raise BSMError("Test error")

    def test_auth_error_inheritance(self):
        assert issubclass(BSMAuthenticationError, BSMError)

    def test_connection_error_inheritance(self):
        assert issubclass(BSMConnectionError, BSMError)

    def test_not_found_error_inheritance(self):
        assert issubclass(BSMNotFoundError, BSMError)

    def test_server_error_inheritance(self):
        assert issubclass(BSMServerError, BSMError)
