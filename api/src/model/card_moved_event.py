from __future__ import annotations

from pydantic import BaseModel

from dto.requests import CardMovedWebhookRequest


class CardMovedEvent(BaseModel):
    card_type: str
    name: str
    description: str
    list_name: str | None
    username: str

    @staticmethod
    def to_card_moved_event(
        card_move_webhook_payload: CardMovedWebhookRequest,
    ) -> CardMovedEvent:
        item = card_move_webhook_payload.data.item
        lists = card_move_webhook_payload.data.included.lists
        list_name = next(
            (lst.name for lst in lists if lst.id == item.listId),
            None,
        )
        return CardMovedEvent(
            card_type=item.type,
            name=item.name,
            description=item.description,
            list_name=list_name,
            username=card_move_webhook_payload.user.username,
        )
