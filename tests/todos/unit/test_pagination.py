from datetime import datetime, timezone

from shared.http.pagination import clamp_limit, decode_cursor, encode_cursor


async def test_cursor_roundtrip_encodes_and_decodes_same_values() -> None:
    created_at = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
    todo_id = 42

    cursor = encode_cursor(created_at, todo_id)
    decoded_at, decoded_id = decode_cursor(cursor)

    assert decoded_at == created_at
    assert decoded_id == todo_id


def test_clamp_limit_returns_default_for_non_positive() -> None:
    assert clamp_limit(0) == 20
    assert clamp_limit(-5) == 20


def test_clamp_limit_clamps_to_max() -> None:
    assert clamp_limit(200) == 100
    assert clamp_limit(100) == 100
