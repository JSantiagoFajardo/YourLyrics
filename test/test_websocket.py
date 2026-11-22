
import json

import pytest

from infrastructure.api.websocket_server import WebSocketServer


def test_process_valid_message():
    received = []

    server = WebSocketServer(
        on_message=received.append
    )

    message = {
        "type": "playback_update",
        "title": "My Song",
        "position": 30
    }

    server._process_message(json.dumps(message))

    assert received == [message]


def test_process_invalid_json():
    errors = []

    server = WebSocketServer(
        on_message=lambda data: None,
        on_error=errors.append
    )

    server._process_message("{invalid json}")

    assert len(errors) == 1
    assert isinstance(errors[0], json.JSONDecodeError)


def test_process_non_object_json():
    errors = []

    server = WebSocketServer(
        on_message=lambda data: None,
        on_error=errors.append
    )

    server._process_message(json.dumps([1, 2, 3]))

    assert len(errors) == 1
    assert isinstance(errors[0], ValueError)


def test_callback_receives_decoded_data():
    received = []

    server = WebSocketServer(
        on_message=lambda data: received.append(data["title"])
    )

    server._process_message(
        '{"title": "My Song"}'
    )

    assert received == ["My Song"]


def test_invalid_message_without_error_callback():
    server = WebSocketServer(
        on_message=lambda data: None
    )

    server._process_message("{invalid json}")
