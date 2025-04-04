import pytest
from Bot import start
from aiogram.types import Message
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock


@pytest_asyncio.fixture
async def mock_message():
    message = AsyncMock(spec=Message)
    message.from_user = MagicMock()
    message.from_user.full_name = 'Test user'
    message.answer = AsyncMock()
    return message


@pytest.mark.asyncio
async def test_start(mock_message):
    await start(mock_message)
    expected_text = 'Hello Test user!\nI am the first Python bot developer Shynkar Snizhana'
    mock_message.answer.assert_called_once_with(expected_text)
