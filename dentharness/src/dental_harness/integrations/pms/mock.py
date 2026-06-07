"""A self-contained, in-memory PMS adapter seeded with synthetic data.

This is the reference implementation and the template for writing your own.
The seed data is fictional. No real patient data is used at this stage.
"""

from __future__ import annotations

import itertools
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from typing import Sequence

from .adapter import PMSAdapter, PatientNotFound
from .models import (
    Appointment,
    AppointmentStatus,
    LedgerEntry,
    LedgerEntryDraft,
    Patient,
)


class MockPMS(PMSAdapter):
    name = "mock"

    def __init__(self) -> None:
        self._patients: dict[str, Patient] = {}
        self._appointments: dict[str, list[Appointment]] = {}
        self._ledger: dict[str, list[LedgerEntry]] = {}
        self._ids = itertools.count(1)
        self._seed()

    def get_patient(self, patient_id: str) -> Patient:
        try:
            return self._patients[patient_id]
        except KeyError:
            raise PatientNotFound(patient_id) from None

    def find_patients(self, query: str) -> Sequence[Patient]:
        q = query.strip().lower()
        if not q:
            return []
        return [
            p
            for p in self._patients.values()
            if q in p.full_name.lower()
            or (p.phone and q in p.phone)
            or (p.email and q in p.email.lower())
        ]

    def get_appointments(
        self, patient_id: str, *, on: date | None = None
    ) -> Sequence[Appointment]:
        self.get_patient(patient_id)
        appts = self._appointments.get(patient_id, [])
        if on is not None:
            appts = [a for a in appts if a.start.date() == on]
        return sorted(appts, key=lambda a: a.start)

    def get_ledger(self, patient_id: str) -> Sequence[LedgerEntry]:
        self.get_patient(patient_id)
        return sorted(self._ledger.get(patient_id, []), key=lambda e: e.posted_at)

    def post_ledger_entry(self, draft: LedgerEntryDraft) -> LedgerEntry:
        self.get_patient(draft.patient_id)
        entry = LedgerEntry(
            id=f"L{next(self._ids)}",
            patient_id=draft.patient_id,
            posted_at=datetime.now(),
            amount=draft.amount,
            description=draft.description,
            code=draft.code,
        )
        self._ledger.setdefault(draft.patient_id, []).append(entry)
        return entry

    def balance(self, patient_id: str) -> Decimal:
        return sum((e.amount for e in self.get_ledger(patient_id)), Decimal("0"))

    def _seed(self) -> None:
        today = date.today()
        p1 = Patient(
            id="P1",
            first_name="Ada",
            last_name="Lovelace",
            date_of_birth=date(1990, 12, 10),
            phone="555-0101",
            email="ada@example.com",
        )
        p2 = Patient(
            id="P2",
            first_name="Grace",
            last_name="Hopper",
            date_of_birth=date(1985, 12, 9),
            phone="555-0102",
            email="grace@example.com",
        )
        for p in (p1, p2):
            self._patients[p.id] = p

        self._appointments["P1"] = [
            Appointment(
                id="A1",
                patient_id="P1",
                start=datetime.combine(today + timedelta(days=2), time(9, 0)),
                end=datetime.combine(today + timedelta(days=2), time(9, 45)),
                provider="Dr. Geisler",
                status=AppointmentStatus.CONFIRMED,
                operatory="OP-1",
                notes="Root canal #14",
            )
        ]

        self._ledger["P1"] = [
            LedgerEntry(
                id="L0",
                patient_id="P1",
                posted_at=datetime.combine(today - timedelta(days=30), time()),
                amount=Decimal("1200.00"),
                description="Endodontic therapy #14",
                code="D3330",
            ),
            LedgerEntry(
                id="L0b",
                patient_id="P1",
                posted_at=datetime.combine(today - timedelta(days=25), time()),
                amount=Decimal("-800.00"),
                description="Insurance payment",
            ),
        ]
