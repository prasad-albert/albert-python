from collections.abc import Generator

import pytest

from albert.albert import Albert
from albert.collections.companies import Company

from ..seeding.companies import seeded_companies


@pytest.fixture(scope="module")
def client():
    return Albert()


def _list_asserts(returned_list):
    found = False
    for i, c in enumerate(returned_list):
        if i == 100:
            break
        found = True
        assert isinstance(c, Company)
        assert isinstance(c.name, str)
        assert isinstance(c.id, str)
        assert c.id.startswith("COM")
    assert found


def test_simple_company_list(client: Albert, seeded_companies):
    simple_list = client.companies.list()
    assert isinstance(simple_list, Generator)
    _list_asserts(simple_list)


def test_advanced_company_list(client: Albert, seeded_companies):
    adv_list = client.companies.list(name="Umbrella Corp", exact_match=True)
    assert isinstance(adv_list, Generator)
    adv_list = list(adv_list)
    for c in adv_list:
        assert "umbrella corp" in c.name.lower()
    _list_asserts(adv_list)


def test_company_get_by(client: Albert, seeded_companies):
    test_name = seeded_companies[0].name
    company = client.companies.get_by_name(name=test_name)
    assert isinstance(company, Company)
    assert company.name == test_name

    company_by_id = client.companies.get_by_id(id=company.id)
    assert isinstance(company_by_id, Company)
    assert company_by_id.name == test_name


def test_company_crud(client: Albert):
    new_company = Company(name="SDK Testing Corp.")
    registered_company = client.companies.create(company=new_company)
    assert isinstance(registered_company, Company)
    assert registered_company.id is not None
    assert registered_company.name == "SDK Testing Corp."

    renamed_company = client.companies.rename(
        old_name="SDK Testing Corp.", new_name="SDK Testing Corp. UPDATED"
    )

    assert isinstance(renamed_company, Company)
    assert renamed_company.name == "SDK Testing Corp. UPDATED"
    assert renamed_company.id == registered_company.id

    deleted = client.companies.delete(id=renamed_company.id)
    assert deleted
    assert not client.companies.company_exists(name="SDK Testing Corp. UPDATED")
