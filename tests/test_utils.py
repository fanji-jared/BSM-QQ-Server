import pytest

from src.utils.helpers import parse_command, validate_player_name, format_server_status
from src.bsm.models import ServerInfo, ServerStatus


class TestParseCommand:
    def test_parse_simple_command(self):
        result = parse_command("/mc status", "/mc")
        assert result == ("status", [], {})

    def test_parse_command_with_args(self):
        result = parse_command("/mc start myserver", "/mc")
        assert result == ("start", ["myserver"], {})

    def test_parse_command_with_kwargs(self):
        result = parse_command("/mc cmd help server=default", "/mc")
        assert result == ("cmd", ["help"], {"server": "default"})

    def test_parse_no_prefix(self):
        result = parse_command("status", "/mc")
        assert result is None

    def test_parse_empty_after_prefix(self):
        result = parse_command("/mc", "/mc")
        assert result == ("help", [], {})


class TestValidatePlayerName:
    def test_valid_name(self):
        assert validate_player_name("Steve") is True
        assert validate_player_name("player_123") is True

    def test_invalid_name_too_short(self):
        assert validate_player_name("ab") is False

    def test_invalid_name_too_long(self):
        assert validate_player_name("a" * 17) is False

    def test_invalid_name_special_chars(self):
        assert validate_player_name("player-name") is False
        assert validate_player_name("player name") is False


class TestFormatServerStatus:
    def test_running_server(self):
        server = ServerInfo(
            name="test",
            status=ServerStatus.RUNNING,
            version="1.20.0",
            online_players=5,
            max_players=10,
            uptime="2h 30m",
        )
        result = format_server_status(server)
        assert "🟢" in result
        assert "test" in result
        assert "running" in result

    def test_stopped_server(self):
        server = ServerInfo(
            name="test",
            status=ServerStatus.STOPPED,
        )
        result = format_server_status(server)
        assert "🔴" in result
        assert "stopped" in result
