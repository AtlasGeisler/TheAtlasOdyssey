from dental_harness.integrations.pms import PMSIntegration


def _tool(integration, name):
    for tool in integration.get_tools():
        if tool.name == name:
            return tool
    raise AssertionError(f"tool {name} not found")


def test_integration_exposes_expected_tools():
    names = {t.name for t in PMSIntegration().get_tools()}
    assert names == {
        "pms_find_patients",
        "pms_get_patient",
        "pms_get_appointments",
        "pms_get_ledger",
        "pms_post_ledger_entry",
    }


def test_find_and_ledger_balance():
    integ = PMSIntegration()
    found = _tool(integ, "pms_find_patients").callback(query="lovelace")
    assert found["patients"][0]["id"] == "P1"

    ledger = _tool(integ, "pms_get_ledger").callback(patient_id="P1")
    assert ledger["balance"] == "400.00"


def test_post_ledger_entry_updates_balance():
    integ = PMSIntegration()
    post = _tool(integ, "pms_post_ledger_entry")
    post.callback(patient_id="P1", amount="-400.00", description="Payment")
    ledger = _tool(integ, "pms_get_ledger").callback(patient_id="P1")
    assert ledger["balance"] == "0.00"


def test_unknown_patient_returns_error_not_exception():
    integ = PMSIntegration()
    out = _tool(integ, "pms_get_ledger").callback(patient_id="nope")
    assert "error" in out
