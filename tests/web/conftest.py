import contextlib
import functools
import http.server
import socket
import threading
from pathlib import Path

import pytest
from playwright.sync_api import Browser, Page, Playwright, sync_playwright

PROJECT_ROOT = Path(__file__).resolve().parents[2]
HTML_ROOT = PROJECT_ROOT / "html"


def find_free_port() -> int:
    with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


@pytest.fixture(scope="session")
def static_server_url() -> str:
    port = find_free_port()
    handler = functools.partial(
        http.server.SimpleHTTPRequestHandler,
        directory=str(HTML_ROOT),
    )
    server = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    yield f"http://127.0.0.1:{port}"

    server.shutdown()
    server.server_close()
    thread.join(timeout=5)


@pytest.fixture
def playwright() -> Playwright:
    with sync_playwright() as playwright:
        yield playwright


@pytest.fixture
def browser(playwright: Playwright) -> Browser:
    browser = playwright.chromium.launch()
    yield browser
    browser.close()


@pytest.fixture
def page(browser: Browser, static_server_url: str) -> Page:
    page = browser.new_page(accept_downloads=True)
    page.goto(static_server_url + "/index.html")
    yield page
    page.close()
