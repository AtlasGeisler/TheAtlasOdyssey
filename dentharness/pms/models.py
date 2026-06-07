"""Vendor-neutral data models.

These are the canonical shapes the agent and tools work with. Every PMS
adapter is responsible for translating its vendor's data into these types,
so nothing above the adapter layer ever sees a vendor-specific field.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional


class AppointmentStatus(str, Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


@dataclass(frozen=True)
class Patient:
    id: str
    first_name: str
    last_name: str
    date_of_birth: Optional[date] = None
    phone: Optional[str] = None
    email: Optional[str] = None

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()


@dataclass(frozen=True)
class Appointment:
    id: str
    patient_id: str
    start: datetime
    end: datetime
    provider: str
    status: AppointmentStatus = AppointmentStatus.SCHEDULED
    operatory: Optional[str] = None
    notes: Optional[str] = None


@dataclass(frozen=True)
class LedgerEntry:
    id: str
    patient_id: str
    posted_at: datetime
    # Positive = charge to the patient, negative = payment/credit.
    amount: Decimal
    description: str
    code: Optional[str] = None  # e.g. CDT procedure code


@dataclass(frozen=True)
class LedgerEntryDraft:
    """An entry to be posted. The adapter assigns the id and posted_at."""

    patient_id: str
    amount: Decimal
    description: str
    code: Optional[str] = None
