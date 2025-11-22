# app/fmcsa.py
import httpx
from fastapi import HTTPException
from .config import get_settings
from .schemas import CarrierAuthResponse

FMCSA_URL = "https://mobile.fmcsa.dot.gov/qc/services/carriers/{mc}?webKey={key}"

async def lookup_fmcsa(mc: str) -> CarrierAuthResponse:
    settings = get_settings()

    url = FMCSA_URL.format(mc=mc, key=settings.fmcsa_api_key)

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url)
    
    if resp.status_code != 200:
        raise HTTPException(500, f"FMCSA API error: {resp.text}")

    data = resp.json()

    # If nothing returned
    carriers = (
        data.get("content", {})
            .get("carrier", [])
    )

    if not carriers:
        return CarrierAuthResponse(
            eligible=False,
            carrier_name=None,
            risk_level="UNKNOWN",
            reason="FMCSA returned no carrier data"
        )

    carrier = carriers[0]

    allowed = carrier.get("allowedToOperate", "N")
    eligible = allowed.upper() == "Y"

    return CarrierAuthResponse(
        eligible=eligible,
        carrier_name=carrier.get("legalName"),
        risk_level="HIGH" if not eligible else "LOW",
        reason="FMCSA official classification"
    )
