# app/call_store.py
from collections import Counter
from datetime import datetime
from typing import List

from .schemas import CallLogEntry, CallLogIn, DashboardMetrics, CallOutcome


class CallStore:
    def __init__(self) -> None:
        self._calls: List[CallLogEntry] = []

    def add(self, call_in: CallLogIn) -> CallLogEntry:
        entry = CallLogEntry(
            timestamp=datetime.utcnow(),
            **call_in.dict(),
        )
        self._calls.append(entry)
        return entry

    def all(self) -> List[CallLogEntry]:
        return self._calls

    def get_metrics(self) -> DashboardMetrics:
        total = len(self._calls)
        booked = sum(1 for c in self._calls if c.outcome == CallOutcome.booked)
        conversion = (booked / total * 100.0) if total else 0.0

       
        discounts = []
        for c in self._calls:
            if (
                c.outcome == CallOutcome.booked and
                c.listed_rate is not None and
                c.agreed_rate is not None and
                c.listed_rate > 0
            ):
                discount_pct = (c.listed_rate - c.agreed_rate) / c.listed_rate * 100.0
                discounts.append(discount_pct)
        avg_discount = sum(discounts) / len(discounts) if discounts else None

        outcome_counts = Counter(c.outcome.value for c in self._calls)
        sentiment_counts = Counter(c.sentiment.value for c in self._calls)

        return DashboardMetrics(
            total_calls=total,
            total_booked=booked,
            conversion_rate=conversion,
            avg_discount_percent=avg_discount,
            outcomes_breakdown=dict(outcome_counts),
            sentiment_breakdown=dict(sentiment_counts),
        )


call_store = CallStore()
