from albert.entity.companies import Company, CompanyCollection
from albert.albert import Albert
from albert.base_collection import OrderBy
import pytest
from typing import Generator


@pytest.fixture(scope="module")
def client():
    return Albert()


def _list_asserts(returned_list):
    for i, c in enumerate(returned_list):
        if i == 100:
            break
        assert isinstance(c, Company)
        assert isinstance(c.name, str)
        assert isinstance(c.id, str)
        assert c.id.startswith("COM")


def test_simple_company_list(client):
    simple_list = client.companies.list()
    assert isinstance(simple_list, Generator)
    _list_asserts(simple_list)


def test_advanced_company_list(client):
    adv_list = client.companies.list(name="Lenore", exact_match=False)
    assert isinstance(adv_list, Generator)
    for c in adv_list:
        assert "lenore" in c.name.lower()
    _list_asserts(adv_list)


def test_company_get_by(client):
    company = client.companies.get_by_name("Lenore Corp")
    assert isinstance(company, Company)
    assert company.name == "Lenore Corp"

    company_by_id = client.companies.get_by_id(company.id)
    assert isinstance(company_by_id, Company)
    assert company_by_id.name == "Lenore Corp"


def test_company_crud(client):
    new_company = Company(name="SDK Testing Corp.")
    registered_company = client.companies.create(new_company)
    assert isinstance(registered_company, Company)
    assert registered_company.id is not None
    assert registered_company.name == "SDK Testing Corp."

    renamed_company = client.companies.rename(
        old_name="SDK Testing Corp.", new_name="SDK Testing Corp. UPDATED"
    )

    assert isinstance(renamed_company, Company)
    assert renamed_company.name == "SDK Testing Corp. UPDATED"
    assert renamed_company.id == registered_company.id

    deleted = client.companies.delete(renamed_company.id)
    assert deleted
    assert not client.companies.company_exists("SDK Testing Corp. UPDATED")
