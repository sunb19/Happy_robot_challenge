# app/schemas.py
from datetime import datetime, date
from enum import Enum
from typing import Optional, List, Dict

from pydantic import BaseModel


class CarrierAuthRequest(BaseModel):
    mc_number: str


class CarrierAuthResponse(BaseModel):
    eligible: bool
    carrier_name: Optional[str] = None
    risk_level: Optional[str] = None
    reason: Optional[str] = None


class Load(BaseModel):
    load_id: str
    origin: str
    destination: str
    pickup_datetime: datetime
    delivery_datetime: datetime
    equipment_type: str
    loadboard_rate: float
    notes: Optional[str] = None
    weight: Optional[float] = None
    commodity_type: Optional[str] = None
    num_of_pieces: Optional[int] = None
    miles: Optional[float] = None
    dimensions: Optional[str] = None


class LoadSearchQuery(BaseModel):
    origin: str | None = None         
    destination: str | None = None     
    equipment_type: str | None = None
    pickup_date: date | None = None    
    max_miles: int | None = None
    min_rate: int | None = None


class LoadSearchResponse(BaseModel):
    loads: List[Load]


class NegotiationStatus(str, Enum):
    accepted = "accepted"
    counter = "counter"
    rejected = "rejected"


class NegotiationRequest(BaseModel):
    load_id: str
    listed_rate: float
    carrier_offer: float
    round: int  # 1..3


class NegotiationResponse(BaseModel):
    status: NegotiationStatus
    final_rate: Optional[float] = None
    counter_rate: Optional[float] = None
    message: str


class CallOutcome(str, Enum):
    booked = "booked"
    rejected_by_carrier = "rejected_by_carrier"
    rejected_by_broker = "rejected_by_broker"
    carrier_ineligible = "carrier_ineligible"
    no_viable_loads = "no_viable_loads"
    other = "other"


class Sentiment(str, Enum):
    very_negative = "very_negative"
    negative = "negative"
    neutral = "neutral"
    positive = "positive"
    very_positive = "very_positive"


class CallLogEntry(BaseModel):
    call_id: str
    timestamp: datetime
    carrier_mc: str
    carrier_name: Optional[str] = None
    load_id: Optional[str] = None
    listed_rate: Optional[float] = None
    agreed_rate: Optional[float] = None
    outcome: CallOutcome
    sentiment: Sentiment
    rounds_of_negotiation: Optional[int] = None
    transcript_summary: Optional[str] = None
    notes: Optional[str] = None


class CallLogIn(BaseModel):
    """
    What the HappyRobot agent will POST to your backend at end of call.
    """
    call_id: str
    carrier_mc: str
    carrier_name: Optional[str] = None
    load_id: Optional[str] = None
    listed_rate: Optional[float] = None
    agreed_rate: Optional[float] = None
    outcome: CallOutcome
    sentiment: Sentiment
    rounds_of_negotiation: Optional[int] = None
    transcript_summary: Optional[str] = None
    notes: Optional[str] = None


class DashboardMetrics(BaseModel):
    total_calls: int
    total_booked: int
    conversion_rate: float
    avg_discount_percent: Optional[float]
    outcomes_breakdown: Dict[str, int]
    sentiment_breakdown: Dict[str, int]
