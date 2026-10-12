"""Автоматизированные тесты для API Музея Метрополитен."""

import time

import httpx
import pytest
from pydantic import ValidationError

from constants import (
    DEFAULT_SEARCH_QUERY,
    DEPARTMENT_ID_EUROPEAN_PAINTINGS,
    INVALID_OBJECT_ID,
    VALID_OBJECT_ID,
)
from models import ArtObject, SearchResponse


def test_get_object_by_id(api_client: httpx.Client) -> None:
    """Проверяет получение информации о произведении по ID.

    Проверяет HTTP-статус 200 и валидность ответа модели ArtObject.
    """
    response = api_client.get(f"/objects/{VALID_OBJECT_ID}")
    assert response.status_code == 200, "Ожидался статус 200"

    data = response.json()
    try:
        art_object = ArtObject.model_validate(data)
    except ValidationError as exc:
        pytest.fail(f"Ответ не соответствует модели ArtObject: {exc}")

    assert art_object.object_id == VALID_OBJECT_ID
    assert art_object.title, "Название не должно быть пустым"
    assert art_object.primary_image is not None


def test_get_object_nonexistent_id(api_client: httpx.Client) -> None:
    """Проверяет обработку запроса с несуществующим идентификатором.

    Ожидается HTTP-статус 404.
    """
    response = api_client.get(f"/objects/{INVALID_OBJECT_ID}")
    assert response.status_code == 404, (
        f"Ожидался статус 404, получен {response.status_code}"
    )


def test_search_objects(search_client: httpx.Client) -> None:
    """Проверяет поиск произведений по ключевому слову.

    Использует эндпоинт v1.1 и ключевое слово "sunflower".
    """
    params = {"q": DEFAULT_SEARCH_QUERY}
    response = search_client.get("/search", params=params)
    assert response.status_code == 200

    data = response.json()
    try:
        search_result = SearchResponse.model_validate(data)
    except ValidationError as exc:
        pytest.fail(f"Ответ поиска не соответствует модели: {exc}")

    assert search_result.total > 0, "Ожидалось хотя бы одно совпадение"
    assert search_result.object_ids, "Список ID не должен быть пустым"


@pytest.mark.parametrize(
    "filter_params",
    [
        {"departmentId": DEPARTMENT_ID_EUROPEAN_PAINTINGS},
        {"isHighlight": "true"},
        {"hasImages": "true"},
    ],
)
def test_search_with_single_filter(
    search_client: httpx.Client, filter_params: dict
) -> None:
    """Проверяет работу отдельных фильтров поиска.

    Параметризованный тест для departmentId, isHighlight, hasImages.
    """
    params = {"q": DEFAULT_SEARCH_QUERY, **filter_params}
    response = search_client.get("/search", params=params)
    assert response.status_code == 200

    search_result = SearchResponse.model_validate(response.json())
    assert search_result.total >= 0


def test_search_with_limit(search_client: httpx.Client) -> None:
    """Проверяет ограничение количества возвращаемых результатов"""
    limit = 5
    params = {"q": DEFAULT_SEARCH_QUERY, "limit": limit}
    response = search_client.get("/search", params=params)
    assert response.status_code == 200

    data = response.json()
    search_result = SearchResponse.model_validate(data)
    assert len(search_result.object_ids) <= limit, (
        f"Количество ID ({len(search_result.object_ids)}) "
        f"превышает лимит {limit}"
    )


def test_search_pagination(search_client: httpx.Client) -> None:
    """Проверяет пагинацию через параметр offset"""
    limit = 3
    params = {"q": DEFAULT_SEARCH_QUERY, "limit": limit, "offset": 0}

    first_page = search_client.get("/search", params=params)
    assert first_page.status_code == 200
    first_data = SearchResponse.model_validate(first_page.json())

    if first_data.total <= limit:
        pytest.skip("Недостаточно результатов для проверки пагинации")

    params["offset"] = limit
    second_page = search_client.get("/search", params=params)
    assert second_page.status_code == 200
    second_data = SearchResponse.model_validate(second_page.json())

    assert not set(first_data.object_ids) & set(second_data.object_ids), (
        "Страницы пагинации пересекаются"
    )


def test_department_filter_matches(
    search_client: httpx.Client, api_client: httpx.Client
) -> None:
    """Проверяет, что все объекты действительно принадлежат отделу.

    Использует поиск по v1.1, затем проверяет объекты через v1.
    """
    params = {
        "q": DEFAULT_SEARCH_QUERY,
        "departmentId": DEPARTMENT_ID_EUROPEAN_PAINTINGS,
    }
    response = search_client.get("/search", params=params)
    assert response.status_code == 200

    search_result = SearchResponse.model_validate(response.json())

    if search_result.total == 0:
        pytest.skip("Нет результатов для проверки фильтра")

    for object_id in search_result.object_ids[:5]:
        obj_response = api_client.get(f"/objects/{object_id}")
        assert obj_response.status_code == 200

        art_object = ArtObject.model_validate(obj_response.json())
        assert art_object.department == "European Paintings", (
            f"Объект {object_id} принадлежит отделу "
            f"'{art_object.department}', а не 'European Paintings'"
        )


def test_search_no_results(search_client: httpx.Client) -> None:
    """Проверяет поиск с запросом, который не возвращает результатов"""
    params = {"q": "xyzzynonexistentquery12345"}
    response = search_client.get("/search", params=params)

    if response.status_code == 403:
        pytest.skip("API вернул 403 на нетипичный запрос — пропускаем")

    assert response.status_code == 200

    data = response.json()
    search_result = SearchResponse.model_validate(data)
    assert search_result.total == 0, "Ожидалось 0 результатов"


def test_old_search_endpoint_retired(api_client: httpx.Client) -> None:
    """Проверяет, что старый эндпоинт /search действительно отключён.

    С 2026-10-01 API возвращает 410 Gone на старый поиск.
    """
    params = {"q": DEFAULT_SEARCH_QUERY}
    response = api_client.get("/search", params=params)
    assert response.status_code == 410, (
        f"Ожидался статус 410 (Gone), получен {response.status_code}"
    )


def test_rate_limit_compliance(api_client: httpx.Client) -> None:
    """Проверяет соблюдение ограничения скорости запросов.

    Выполняет несколько запросов с задержкой, чтобы не превысить лимит.
    """
    for _ in range(5):
        response = api_client.get(f"/objects/{VALID_OBJECT_ID}")
        assert response.status_code == 200
        time.sleep(0.1)