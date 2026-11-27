from src.generator.seed_source import generate_orders


def test_generator_is_deterministic() -> None:
    first_run = generate_orders(100)
    second_run = generate_orders(100)

    assert first_run == second_run


def test_generator_creates_requested_number_of_rows() -> None:
    rows = generate_orders(25)

    assert len(rows) == 25


def test_generator_creates_unique_sequential_order_ids() -> None:
    rows = generate_orders(100)

    order_ids = [row[0] for row in rows]

    assert order_ids == list(range(1, 101))


def test_generated_quantities_are_in_expected_range() -> None:
    rows = generate_orders(100)

    quantities = [row[5] for row in rows]

    assert min(quantities) >= 1
    assert max(quantities) <= 5
