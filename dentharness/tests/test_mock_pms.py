from datetime import date
from decimal import Decimal

import pytest

from dentharness.pms import LedgerEntryDraft, PatientNotFound, get_pms
from dentharness.pms.mock import MockPMS


@pytest.fixture
def pms() -> MockPMS:
    return MockPMS()


def test_get_patient(pms: MockPMS) -> None:
    assert pms.get_patient("P1").full_name == "Ada Lovelace"


def test_get_patient_missing(pms: MockPMS) -> None:
    with pytest.raises(PatientNotFound):
        pms.get_patient("nope")


def test_find_patients(pms: MockPMS) -> None:
    assert [p.id for p in pms.find_patients("hopper")] == ["P2"]
    assert pms.find_patients("") == []


def test_balance_reflects_seed(pms: MockPMS) -> None:
    # 1200 charge - 800 payment
    assert pms.balance("P1") == Decimal("400.00")


def test_post_ledger_entry_updates_balance(pms: MockPMS) -> None:
    pms.post_ledger_entry(
        LedgerEntryDraft(
            patient_id="P1", amount=Decimal("-400.00"), description="Payment"
        )
    )
    assert pms.balance("P1") == Decimal("0.00")


def test_get_appointments_day_filter(pms: MockPMS) -> None:
    assert pms.get_appointments("P1", on=date(1900, 1, 1)) == []
    assert len(pms.get_appointments("P1")) == 1


def test_registry_default_is_mock() -> None:
    assert isinstance(get_pms(), MockPMS)


def test_registry_unknown() -> None:
    with pytest.raises(ValueError):
        get_pms("does-not-exist")
