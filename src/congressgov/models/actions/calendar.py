from __future__ import annotations
from ..base.model import Model


class CalendarNumber(Model):
    calendarNumber: int | None = None
    number: int | None = None

    @property
    def calendar_number(self) -> int | None:
        return self.calendarNumber

    @calendar_number.setter
    def calendar_number(self, value: int | None) -> None:
        self.calendarNumber = value


# CalendarNumber.model_rebuild()  # Handled by centralized rebuild system
