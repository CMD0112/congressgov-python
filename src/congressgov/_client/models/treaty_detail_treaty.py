import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.treaty_detail_treaty_actions import TreatyDetailTreatyActions
    from ..models.treaty_detail_treaty_countries_parties_item import TreatyDetailTreatyCountriesPartiesItem
    from ..models.treaty_detail_treaty_index_terms_item import TreatyDetailTreatyIndexTermsItem
    from ..models.treaty_detail_treaty_parts import TreatyDetailTreatyParts
    from ..models.treaty_detail_treaty_related_docs_item import TreatyDetailTreatyRelatedDocsItem
    from ..models.treaty_detail_treaty_titles_item import TreatyDetailTreatyTitlesItem


T = TypeVar("T", bound="TreatyDetailTreaty")


@_attrs_define
class TreatyDetailTreaty:
    """
    Attributes:
        actions (Union[Unset, TreatyDetailTreatyActions]):
        congress_considered (Union[Unset, int]):  Example: 89.
        congress_received (Union[Unset, int]):  Example: 89.
        countries_parties (Union[Unset, list['TreatyDetailTreatyCountriesPartiesItem']]):
        in_force_date (Union[Unset, str]):
        index_terms (Union[Unset, list['TreatyDetailTreatyIndexTermsItem']]):
        number (Union[Unset, int]):  Example: 7.
        old_number (Union[Unset, str]):  Example: G. 89-1.
        old_number_display_name (Union[Unset, str]):  Example: Ex. G, 89th Congress, 1st Session.
        parts (Union[Unset, TreatyDetailTreatyParts]):
        related_docs (Union[Unset, list['TreatyDetailTreatyRelatedDocsItem']]):
        resolution_text (Union[Unset, str]):
        suffix (Union[Unset, str]):
        titles (Union[Unset, list['TreatyDetailTreatyTitlesItem']]):
        topic (Union[Unset, str]):  Example: Taxation.
        transmitted (Union[Unset, datetime.datetime]):  Example: 1965-08-05T00:00:00Z.
        update_date (Union[Unset, datetime.datetime]):  Example: 2022-02-26T16:25:25Z.
    """

    actions: Union[Unset, "TreatyDetailTreatyActions"] = UNSET
    congress_considered: Union[Unset, int] = UNSET
    congress_received: Union[Unset, int] = UNSET
    countries_parties: Union[Unset, list["TreatyDetailTreatyCountriesPartiesItem"]] = UNSET
    in_force_date: Union[Unset, str] = UNSET
    index_terms: Union[Unset, list["TreatyDetailTreatyIndexTermsItem"]] = UNSET
    number: Union[Unset, int] = UNSET
    old_number: Union[Unset, str] = UNSET
    old_number_display_name: Union[Unset, str] = UNSET
    parts: Union[Unset, "TreatyDetailTreatyParts"] = UNSET
    related_docs: Union[Unset, list["TreatyDetailTreatyRelatedDocsItem"]] = UNSET
    resolution_text: Union[Unset, str] = UNSET
    suffix: Union[Unset, str] = UNSET
    titles: Union[Unset, list["TreatyDetailTreatyTitlesItem"]] = UNSET
    topic: Union[Unset, str] = UNSET
    transmitted: Union[Unset, datetime.datetime] = UNSET
    update_date: Union[Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        actions: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.actions, Unset):
            actions = self.actions.to_dict()

        congress_considered = self.congress_considered

        congress_received = self.congress_received

        countries_parties: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.countries_parties, Unset):
            countries_parties = []
            for countries_parties_item_data in self.countries_parties:
                countries_parties_item = countries_parties_item_data.to_dict()
                countries_parties.append(countries_parties_item)

        in_force_date = self.in_force_date

        index_terms: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.index_terms, Unset):
            index_terms = []
            for index_terms_item_data in self.index_terms:
                index_terms_item = index_terms_item_data.to_dict()
                index_terms.append(index_terms_item)

        number = self.number

        old_number = self.old_number

        old_number_display_name = self.old_number_display_name

        parts: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.parts, Unset):
            parts = self.parts.to_dict()

        related_docs: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.related_docs, Unset):
            related_docs = []
            for related_docs_item_data in self.related_docs:
                related_docs_item = related_docs_item_data.to_dict()
                related_docs.append(related_docs_item)

        resolution_text = self.resolution_text

        suffix = self.suffix

        titles: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.titles, Unset):
            titles = []
            for titles_item_data in self.titles:
                titles_item = titles_item_data.to_dict()
                titles.append(titles_item)

        topic = self.topic

        transmitted: Union[Unset, str] = UNSET
        if not isinstance(self.transmitted, Unset):
            transmitted = self.transmitted.isoformat()

        update_date: Union[Unset, str] = UNSET
        if not isinstance(self.update_date, Unset):
            update_date = self.update_date.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if actions is not UNSET:
            field_dict["actions"] = actions
        if congress_considered is not UNSET:
            field_dict["congressConsidered"] = congress_considered
        if congress_received is not UNSET:
            field_dict["congressReceived"] = congress_received
        if countries_parties is not UNSET:
            field_dict["countriesParties"] = countries_parties
        if in_force_date is not UNSET:
            field_dict["inForceDate"] = in_force_date
        if index_terms is not UNSET:
            field_dict["indexTerms"] = index_terms
        if number is not UNSET:
            field_dict["number"] = number
        if old_number is not UNSET:
            field_dict["oldNumber"] = old_number
        if old_number_display_name is not UNSET:
            field_dict["oldNumberDisplayName"] = old_number_display_name
        if parts is not UNSET:
            field_dict["parts"] = parts
        if related_docs is not UNSET:
            field_dict["relatedDocs"] = related_docs
        if resolution_text is not UNSET:
            field_dict["resolutionText"] = resolution_text
        if suffix is not UNSET:
            field_dict["suffix"] = suffix
        if titles is not UNSET:
            field_dict["titles"] = titles
        if topic is not UNSET:
            field_dict["topic"] = topic
        if transmitted is not UNSET:
            field_dict["transmitted"] = transmitted
        if update_date is not UNSET:
            field_dict["updateDate"] = update_date

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.treaty_detail_treaty_actions import TreatyDetailTreatyActions
        from ..models.treaty_detail_treaty_countries_parties_item import TreatyDetailTreatyCountriesPartiesItem
        from ..models.treaty_detail_treaty_index_terms_item import TreatyDetailTreatyIndexTermsItem
        from ..models.treaty_detail_treaty_parts import TreatyDetailTreatyParts
        from ..models.treaty_detail_treaty_related_docs_item import TreatyDetailTreatyRelatedDocsItem
        from ..models.treaty_detail_treaty_titles_item import TreatyDetailTreatyTitlesItem

        d = dict(src_dict)
        _actions = d.pop("actions", UNSET)
        actions: Union[Unset, TreatyDetailTreatyActions]
        if isinstance(_actions, Unset):
            actions = UNSET
        else:
            actions = TreatyDetailTreatyActions.from_dict(_actions)

        congress_considered = d.pop("congressConsidered", UNSET)

        congress_received = d.pop("congressReceived", UNSET)

        countries_parties = []
        _countries_parties = d.pop("countriesParties", UNSET)
        for countries_parties_item_data in _countries_parties or []:
            countries_parties_item = TreatyDetailTreatyCountriesPartiesItem.from_dict(countries_parties_item_data)

            countries_parties.append(countries_parties_item)

        in_force_date = d.pop("inForceDate", UNSET)

        index_terms = []
        _index_terms = d.pop("indexTerms", UNSET)
        for index_terms_item_data in _index_terms or []:
            index_terms_item = TreatyDetailTreatyIndexTermsItem.from_dict(index_terms_item_data)

            index_terms.append(index_terms_item)

        number = d.pop("number", UNSET)

        old_number = d.pop("oldNumber", UNSET)

        old_number_display_name = d.pop("oldNumberDisplayName", UNSET)

        _parts = d.pop("parts", UNSET)
        parts: Union[Unset, TreatyDetailTreatyParts]
        if isinstance(_parts, Unset):
            parts = UNSET
        else:
            parts = TreatyDetailTreatyParts.from_dict(_parts)

        related_docs = []
        _related_docs = d.pop("relatedDocs", UNSET)
        for related_docs_item_data in _related_docs or []:
            related_docs_item = TreatyDetailTreatyRelatedDocsItem.from_dict(related_docs_item_data)

            related_docs.append(related_docs_item)

        resolution_text = d.pop("resolutionText", UNSET)

        suffix = d.pop("suffix", UNSET)

        titles = []
        _titles = d.pop("titles", UNSET)
        for titles_item_data in _titles or []:
            titles_item = TreatyDetailTreatyTitlesItem.from_dict(titles_item_data)

            titles.append(titles_item)

        topic = d.pop("topic", UNSET)

        _transmitted = d.pop("transmitted", UNSET)
        transmitted: Union[Unset, datetime.datetime]
        if isinstance(_transmitted, Unset) or _transmitted is None:
            transmitted = UNSET
        else:
            transmitted = isoparse(_transmitted)

        _update_date = d.pop("updateDate", UNSET)
        update_date: Union[Unset, datetime.datetime]
        if isinstance(_update_date, Unset) or _update_date is None:
            update_date = UNSET
        else:
            update_date = isoparse(_update_date)

        treaty_detail_treaty = cls(
            actions=actions,
            congress_considered=congress_considered,
            congress_received=congress_received,
            countries_parties=countries_parties,
            in_force_date=in_force_date,
            index_terms=index_terms,
            number=number,
            old_number=old_number,
            old_number_display_name=old_number_display_name,
            parts=parts,
            related_docs=related_docs,
            resolution_text=resolution_text,
            suffix=suffix,
            titles=titles,
            topic=topic,
            transmitted=transmitted,
            update_date=update_date,
        )

        treaty_detail_treaty.additional_properties = d
        return treaty_detail_treaty

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
