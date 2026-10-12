"""Pydantic-модели для валидации ответов API Музея Метрополитен."""

from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Tag(BaseModel):
    """Модель тега произведения искусства"""

    term: str
    aat_url: Optional[str] = Field(None, alias="AAT_URL")
    wikidata_url: Optional[str] = Field(None, alias="Wikidata_URL")

    model_config = ConfigDict(populate_by_name=True)


class Constituent(BaseModel):
    """Модель участника создания произведения (художник, мастер и т.д.)"""

    constituent_id: int = Field(alias="constituentID")
    role: str
    name: str
    constituent_ulan_url: Optional[str] = Field(
        None, alias="constituentULAN_URL"
    )
    constituent_wikidata_url: Optional[str] = Field(
        None, alias="constituentWikidata_URL"
    )
    gender: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


class Measurement(BaseModel):
    """Модель измерения элемента произведения"""

    element_name: str = Field(alias="elementName")
    element_description: Optional[str] = Field(
        None, alias="elementDescription"
    )
    element_measurements: dict = Field(alias="elementMeasurements")

    model_config = ConfigDict(populate_by_name=True)


class ArtObject(BaseModel):
    """Модель полного описания произведения искусства.

    Соответствует ответу эндпоинта GET /objects/{objectID}.
    """

    object_id: int = Field(alias="objectID")
    is_highlight: bool = Field(alias="isHighlight")
    accession_number: str = Field(alias="accessionNumber")
    accession_year: str = Field(alias="accessionYear")
    is_public_domain: bool = Field(alias="isPublicDomain")
    primary_image: str = Field(alias="primaryImage")
    primary_image_small: str = Field(alias="primaryImageSmall")
    additional_images: List[str] = Field(alias="additionalImages")
    constituents: Optional[List[Constituent]] = None
    department: str
    object_name: str = Field(alias="objectName")
    title: str
    culture: Optional[str] = None
    period: Optional[str] = None
    dynasty: Optional[str] = None
    reign: Optional[str] = None
    portfolio: Optional[str] = None
    artist_role: Optional[str] = Field(None, alias="artistRole")
    artist_prefix: Optional[str] = Field(None, alias="artistPrefix")
    artist_display_name: Optional[str] = Field(
        None, alias="artistDisplayName"
    )
    artist_display_bio: Optional[str] = Field(None, alias="artistDisplayBio")
    artist_suffix: Optional[str] = Field(None, alias="artistSuffix")
    artist_alpha_sort: Optional[str] = Field(None, alias="artistAlphaSort")
    artist_nationality: Optional[str] = Field(None, alias="artistNationality")
    artist_begin_date: Optional[str] = Field(None, alias="artistBeginDate")
    artist_end_date: Optional[str] = Field(None, alias="artistEndDate")
    artist_gender: Optional[str] = Field(None, alias="artistGender")
    artist_wikidata_url: Optional[str] = Field(
        None, alias="artistWikidata_URL"
    )
    artist_ulan_url: Optional[str] = Field(None, alias="artistULAN_URL")
    object_date: str = Field(alias="objectDate")
    object_begin_date: int = Field(alias="objectBeginDate")
    object_end_date: int = Field(alias="objectEndDate")
    medium: str
    dimensions: str
    dimensions_parsed: Optional[Any] = Field(None, alias="dimensionsParsed")
    measurements: Optional[List[Measurement]] = None
    credit_line: str = Field(alias="creditLine")
    geography_type: Optional[str] = Field(None, alias="geographyType")
    city: Optional[str] = None
    state: Optional[str] = None
    county: Optional[str] = None
    country: Optional[str] = None
    region: Optional[str] = None
    subregion: Optional[str] = None
    locale: Optional[str] = None
    locus: Optional[str] = None
    excavation: Optional[str] = None
    river: Optional[str] = None
    classification: str
    rights_and_reproduction: Optional[str] = Field(
        None, alias="rightsAndReproduction"
    )
    link_resource: Optional[str] = Field(None, alias="linkResource")
    metadata_date: str = Field(alias="metadataDate")
    repository: str
    object_url: str = Field(alias="objectURL")
    tags: Optional[List[Tag]] = None

    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow",
    )

    @field_validator("object_url")
    @classmethod
    def validate_object_url(cls, v: str) -> str:
        """Проверяет, что objectURL ведёт на сайт музея"""
        if not v.startswith("https://www.metmuseum.org/"):
            raise ValueError("objectURL должен вести на сайт музея")
        return v


class SearchResponse(BaseModel):
    """Модель ответа эндпоинта поиска.

    Соответствует ответу GET /v1.1/search.
    """

    total: int
    object_ids: Optional[List[int]] = Field(None, alias="objectIDs")

    model_config = ConfigDict(populate_by_name=True, extra="allow")