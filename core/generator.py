"""Generate mock records from a field-to-type schema."""

from collections.abc import Callable
from typing import Any

from faker import Faker


def _price(fake: Faker) -> float:
    return round(fake.pyfloat(min_value=1, max_value=1000, right_digits=2), 2)


def _integer(fake: Faker) -> int:
    return fake.random_int()


def _text(fake: Faker) -> str:
    return fake.text(max_nb_chars=200)


def _date(fake: Faker) -> str:
    return fake.date()


def generate_mock_dataset(schema: dict[str, str], count: int = 10) -> list[dict[str, Any]]:
    """Return ``count`` records, using each schema value as a Faker field type.

    Example schema: ``{"full_name": "name", "contact": "email"}``.
    """
    providers: dict[str, Callable[[Faker], Any]] = {
        "name": lambda fake: fake.name(),
        "email": lambda fake: fake.email(),
        "address": lambda fake: fake.address(),
        "company": lambda fake: fake.company(),
        "date": _date,
        "phone": lambda fake: fake.phone_number(),
        "text": _text,
        "integer": _integer,
        "price": _price,
    }

    unknown_types = sorted(set(schema.values()) - providers.keys())
    if unknown_types:
        raise ValueError(f"Unsupported field type(s): {', '.join(unknown_types)}")
    if count < 0:
        raise ValueError("count must not be negative")

    fake = Faker()
    return [
        {field_name: providers[field_type](fake) for field_name, field_type in schema.items()}
        for _ in range(count)
    ]
