from albert import Albert
from albert.resources.btinsight import BTInsight, BTInsightRegistry


def test_update(client: Albert, seeded_btinsight: BTInsight):
    marker = "TEST"
    seeded_btinsight.output_key = marker
    seeded_btinsight.start_time = marker
    seeded_btinsight.end_time = marker
    seeded_btinsight.total_time = marker
    seeded_btinsight.registry = BTInsightRegistry(build_logs={"status": marker})

    updated_insight = client.btinsights.update(insight=seeded_btinsight)
    assert updated_insight.output_key == seeded_btinsight.output_key
    assert updated_insight.start_time == seeded_btinsight.start_time
    assert updated_insight.end_time == seeded_btinsight.end_time
    assert updated_insight.total_time == seeded_btinsight.total_time
    assert updated_insight.registry == seeded_btinsight.registry
