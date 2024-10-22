from albert.albert import Albert
from albert.resources.custom_fields import CustomField


def test_update(client: Albert):
    # get field
    cf = next(client.custom_fields.list())
    # modify locally
    cf.hidden = True
    # update
    cf_updated = client.custom_fields.update(updated_object=cf)
    assert isinstance(cf_updated, CustomField)
    assert cf_updated.hidden == True
    # modify locally
    cf_updated.hidden = False
    # update
    cf = client.custom_fields.update(updated_object=cf_updated)
    assert isinstance(cf, CustomField)
    assert cf.hidden == True
