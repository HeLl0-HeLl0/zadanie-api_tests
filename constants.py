"""Константы для тестов API Музея Метрополитен.

Значения подобраны на основе документации API
(https://metmuseum.github.io/) и не меняются между запусками тестов.
"""

BASE_URL = "https://collectionapi.metmuseum.org/public/collection/v1"
"""Базовый URL API версии v1 (объекты, устаревший поиск)"""

V1_1_BASE_URL = "https://collectionapi.metmuseum.org/public/collection/v1.1"
"""Базовый URL API версии v1.1 (новый пагинированный поиск)"""

VALID_OBJECT_ID = 436535
"""Известный идентификатор произведения (картина Ван Гога «Ирисы»)"""

INVALID_OBJECT_ID = 999999999
"""Заведомо несуществующий идентификатор для проверки статуса 404"""

DEFAULT_SEARCH_QUERY = "sunflower"
"""Ключевое слово для поиска, гарантированно дающее много результатов"""

RATE_LIMIT_PER_SECOND = 80
"""Ограничение скорости запросов, установленное API (80 запросов/сек)"""

DEPARTMENT_ID_EUROPEAN_PAINTINGS = 11
"""ID отдела European Paintings в классификации музея"""