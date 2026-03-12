from dto.requests import CardMovedWebhookRequest
from fastapi import APIRouter
from model.card_moved_event import CardMovedEvent

router = APIRouter()


@router.post("/card-moved", status_code=200)
async def webhook(payload: CardMovedWebhookRequest):
    _ = CardMovedEvent.to_card_moved_event(payload)
    return {"ok": True}
