from collections.abc import Iterator

import pytest

from albert import Albert
from albert.resources.btmodel import BTModel, BTModelRegistry, BTModelSession
from tests.helpers import suppress_http_errors


@pytest.fixture
def seeded_btmodelsession(client: Albert) -> Iterator[BTModelSession]:
    model_session = BTModelSession(name="Test Model Session")
    model_session = client.btmodelsessions.create(model_session=model_session)
    yield model_session
    with suppress_http_errors():
        client.btmodelsessions.delete(id=model_session.id)


def test_update_model_session(client: Albert, seeded_btmodelsession: BTModelSession):
    marker = "TEST"
    seeded_btmodelsession.registry = BTModelRegistry(build_logs={"status": marker})

    updated_model_session = client.btmodelsessions.update(model_session=seeded_btmodelsession)
    assert updated_model_session.registry == seeded_btmodelsession.registry


def test_update_model(static_btmodelsession: BTModelSession, static_btmodel: BTModel):
    model = static_btmodel.model_copy()

    marker = "TEST"
    model.start_time = marker
    model.end_time = marker
    model.total_time = marker
    model.model_binary_key = marker

    updated_model = static_btmodelsession.models.update(model=model)
    assert updated_model.start_time == model.start_time
    assert updated_model.end_time == model.end_time
    assert updated_model.total_time == model.total_time
    assert updated_model.model_binary_key == model.model_binary_key
