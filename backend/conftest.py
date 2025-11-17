"""
Global pytest configuration and fixtures.

This conftest.py ensures proper event loop management across all test suites,
preventing "Event loop is closed" errors when running repositories and services tests together.
"""
import asyncio
import pytest
from typing import Generator


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """
    Create a single event loop for the entire test session.

    This fixture explicitly creates and closes an event loop for the entire test session,
    preventing interference between test repositories and test services.

    The session scope ensures:
    - All tests share the same event loop
    - No "Event loop is closed" errors between test modules
    - Proper cleanup after all tests complete

    Yields:
        asyncio.AbstractEventLoop: The event loop for the test session
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    yield loop

    # Cleanup: close the loop and ensure all pending tasks are cancelled
    try:
        # Cancel all running tasks
        pending = asyncio.all_tasks(loop)
        for task in pending:
            task.cancel()

        # Wait for all tasks to complete cancellation
        if pending:
            loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))

        # Close the loop
        loop.close()
    except Exception:
        # Ignore cleanup errors
        pass
    finally:
        # Unset the event loop
        asyncio.set_event_loop(None)
