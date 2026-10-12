"""Общие фикстуры и настройки для тестов API Музея Метрополитен."""

import logging
import time
from typing import Generator

import httpx
import pytest

from constants import BASE_URL, V1_1_BASE_URL

logger = logging.getLogger("met_api_tests")

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


def configure_logging() -> None:
    """Настраивает логирование с записью в файл и в консоль"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("met_api_tests.log", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


def log_request(request: httpx.Request) -> None:
    """Логирует исходящий HTTP-запрос"""
    logger.info("→ %s %s", request.method, request.url)


def log_response(response: httpx.Response) -> None:
    """Логирует полученный HTTP-ответ"""
    logger.info(
        "← %s %s [%d]",
        response.request.method,
        response.request.url,
        response.status_code,
    )
    if response.status_code >= 400:
        response.read()
        logger.error("Ошибка: %s", response.text)


@pytest.fixture(scope="session", autouse=True)
def setup_logging() -> None:
    """Автоматически настраивает логирование для всей сессии тестов"""
    configure_logging()


@pytest.fixture(scope="session")
def api_client() -> Generator[httpx.Client, None, None]:
    """Фикстура HTTP-клиента для эндпоинтов версии v1.

    Yields:
        httpx.Client: Клиент с базовым URL версии v1 и логированием.
    """
    client = httpx.Client(
        base_url=BASE_URL,
        timeout=30.0,
        headers={"User-Agent": USER_AGENT},
        event_hooks={
            "request": [log_request],
            "response": [log_response],
        },
    )
    yield client
    client.close()


@pytest.fixture(scope="session")
def search_client() -> Generator[httpx.Client, None, None]:
    """Фикстура HTTP-клиента для нового поиска (версия v1.1).

    Yields:
        httpx.Client: Клиент с базовым URL версии v1.1 и логированием.
    """
    client = httpx.Client(
        base_url=V1_1_BASE_URL,
        timeout=30.0,
        headers={"User-Agent": USER_AGENT},
        event_hooks={
            "request": [log_request],
            "response": [log_response],
        },
    )
    yield client
    client.close()


@pytest.fixture(autouse=True)
def slow_down_requests() -> None:
    """Замедляет выполнение тестов, чтобы не попасть под rate limit"""
    time.sleep(1)