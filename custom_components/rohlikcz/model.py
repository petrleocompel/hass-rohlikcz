from dataclasses import dataclass
from typing import Any, List, TypeVar, Type, cast, Callable


T = TypeVar("T")


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_float(x: Any) -> float:
    assert isinstance(x, (float, int)) and not isinstance(x, bool)
    return float(x)


def to_float(x: Any) -> float:
    assert isinstance(x, float)
    return x


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


@dataclass
class DeliverySlot:
    id: int
    type: str
    since: str
    till: str

    @staticmethod
    def from_dict(obj: Any) -> 'DeliverySlot':
        assert isinstance(obj, dict)
        id = from_int(obj.get("id"))
        type = from_str(obj.get("type"))
        since = from_str(obj.get("since"))
        till = from_str(obj.get("till"))
        return DeliverySlot(id, type, since, till)

    def to_dict(self) -> dict:
        result: dict = {}
        result["id"] = from_int(self.id)
        result["type"] = from_str(self.type)
        result["since"] = from_str(self.since)
        result["till"] = from_str(self.till)
        return result


@dataclass
class Total:
    amount: float
    currency: str

    @staticmethod
    def from_dict(obj: Any) -> 'Total':
        assert isinstance(obj, dict)
        amount = from_float(obj.get("amount"))
        currency = from_str(obj.get("currency"))
        return Total(amount, currency)

    def to_dict(self) -> dict:
        result: dict = {}
        result["amount"] = to_float(self.amount)
        result["currency"] = from_str(self.currency)
        return result


@dataclass
class PriceComposition:
    total: Total

    @staticmethod
    def from_dict(obj: Any) -> 'PriceComposition':
        assert isinstance(obj, dict)
        total = Total.from_dict(obj.get("total"))
        return PriceComposition(total)

    def to_dict(self) -> dict:
        result: dict = {}
        result["total"] = to_class(Total, self.total)
        return result


@dataclass
class UpcomingOrder:
    id: int
    items_count: int
    price_composition: PriceComposition
    order_time: str
    delivery_slot: DeliverySlot

    @staticmethod
    def from_dict(obj: Any) -> 'UpcomingOrder':
        assert isinstance(obj, dict)
        id = from_int(obj.get("id"))
        items_count = from_int(obj.get("itemsCount"))
        price_composition = PriceComposition.from_dict(obj.get("priceComposition"))
        order_time = from_str(obj.get("orderTime"))
        delivery_slot = DeliverySlot.from_dict(obj.get("deliverySlot"))
        return UpcomingOrder(id, items_count, price_composition, order_time, delivery_slot)

    def to_dict(self) -> dict:
        result: dict = {}
        result["id"] = from_int(self.id)
        result["itemsCount"] = from_int(self.items_count)
        result["priceComposition"] = to_class(PriceComposition, self.price_composition)
        result["orderTime"] = from_str(self.order_time)
        result["deliverySlot"] = to_class(DeliverySlot, self.delivery_slot)
        return result


def upcoming_order_from_dict(s: Any) -> List[UpcomingOrder]:
    return from_list(UpcomingOrder.from_dict, s)


def upcoming_order_to_dict(x: List[UpcomingOrder]) -> Any:
    return from_list(lambda x: to_class(UpcomingOrder, x), x)
