# app/main.py
from fastapi import FastAPI, Depends, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .load_store import load_store
from .call_store import call_store
from .schemas import (
    CarrierAuthRequest,
    CarrierAuthResponse,
    LoadSearchQuery,
    LoadSearchResponse,
    NegotiationRequest,
    NegotiationResponse,
    NegotiationStatus,
    CallLogIn,
    CallLogEntry,
    DashboardMetrics,
)


app = FastAPI(
    title="Inbound Carrier Sales API",
    version="0.1.0",
    description="Backend API for HappyRobot inbound carrier automation POC.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def require_api_key(x_api_key: str = Header(..., alias="X-API-Key")):
    settings = get_settings()
    if x_api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    return True


@app.get("/health")
def health_check():
    return {"status": "ok"}


# -------------------------
# Carrier auth (FMCSA mock)
# -------------------------


@app.post(
    "/auth-carrier",
    response_model=CarrierAuthResponse,
    dependencies=[Depends(require_api_key)],
)
def auth_carrier(payload: CarrierAuthRequest):
    """
    Validate carrier MC number.

    For now we mock FMCSA integration with simple rules:
    - MC must be numeric
    - MC starting with '9' = ineligible
    - Others = eligible
    """
    mc = payload.mc_number.strip()

    if not mc.isdigit():
        return CarrierAuthResponse(
            eligible=False,
            reason="Invalid MC number format",
        )

    if mc.startswith("9"):
        return CarrierAuthResponse(
            eligible=False,
            carrier_name=None,
            risk_level="HIGH",
            reason="Mock: flagged as high risk / inactive",
        )

    
    return CarrierAuthResponse(
        eligible=True,
        carrier_name=f"Mock Carrier MC {mc}",
        risk_level="LOW",
        reason="Mock: active and in good standing",
    )


# -------------------------
# Load search
# -------------------------


@app.post(
    "/loads/search",
    response_model=LoadSearchResponse,
    dependencies=[Depends(require_api_key)],
)
def search_loads(query: LoadSearchQuery):
    loads = load_store.search(query)
    return LoadSearchResponse(loads=loads)


# -------------------------
# Negotiation logic
# -------------------------


@app.post(
    "/negotiate",
    response_model=NegotiationResponse,
    dependencies=[Depends(require_api_key)],
)
def negotiate(payload: NegotiationRequest):
    """
    Simple example business rules:

    - If carrier_offer >= 95% of listed_rate -> accept
    - If carrier_offer <= 85% of listed_rate and round >= 3 -> reject
    - Else counter somewhere between midpoint and 92% of listed rate
    """
    listed = payload.listed_rate
    offer = payload.carrier_offer

    if listed <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Listed rate must be positive.",
        )

    # Accept if close enough
    if offer >= 0.95 * listed:
        return NegotiationResponse(
            status=NegotiationStatus.accepted,
            final_rate=offer,
            message="Offer is within acceptable threshold. Accepting.",
        )

    # If too low after multiple rounds, reject
    if offer <= 0.85 * listed and payload.round >= 3:
        return NegotiationResponse(
            status=NegotiationStatus.rejected,
            message="Too far below target after multiple rounds. Rejecting.",
        )

    # Otherwise, counter
    midpoint = (listed + offer) / 2.0
    target_floor = listed * 0.92
    counter_rate = max(midpoint, target_floor)

    return NegotiationResponse(
        status=NegotiationStatus.counter,
        counter_rate=round(counter_rate, 2),
        message="Countering based on margin rules.",
    )


# -------------------------
# Call logging & metrics
# -------------------------


@app.post(
    "/call-log",
    response_model=CallLogEntry,
    dependencies=[Depends(require_api_key)],
)
def log_call(payload: CallLogIn):
    """
    Called by HappyRobot after the call completes.

    Payload includes:
    - outcome classification
    - sentiment classification
    - agreed_rate, listed_rate
    - summary / notes
    """
    entry = call_store.add(payload)
    return entry


@app.get(
    "/dashboard",
    response_model=DashboardMetrics,
    dependencies=[Depends(require_api_key)],
)
def dashboard_metrics():
    """
    Aggregated metrics to power the custom dashboard.
    """
    return call_store.get_metrics()


@app.get("/")
def root():
    return {
        "message": "Inbound Carrier Sales API is running.",
        "docs": "/docs",
        "health": "/health",
    }