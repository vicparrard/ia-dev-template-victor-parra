from __future__ import annotations


def get_fake_transactions() -> list[dict]:
    """Repositorio fake in-memory con 5 transacciones fijas y deterministas."""
    return [
        {
            "transaction_id": "TXN-0001",
            "transaction_date": "2026-08-01",
            "estado": "approved",
            "amount": 100.0,
            "merchant_id": "MCHT-0001",
            "pan": "4111111111111111",
        },
        {
            "transaction_id": "TXN-0002",
            "transaction_date": "2026-08-05",
            "estado": "failed",
            "amount": 200.0,
            "merchant_id": "MCHT-0001",
            "pan": "5500000000000004",
        },
        {
            "transaction_id": "TXN-0003",
            "transaction_date": "2026-08-10",
            "estado": "approved",
            "amount": 150.0,
            "merchant_id": "MCHT-0001",
            "pan": "340000000000009",
        },
        {
            "transaction_id": "TXN-0004",
            "transaction_date": "2026-08-15",
            "estado": "pending",
            "amount": 75.5,
            "merchant_id": "MCHT-0002",
            "pan": "6011000000000000",
        },
        {
            "transaction_id": "TXN-0005",
            "transaction_date": "2026-08-20",
            "estado": "refunded",
            "amount": 250.0,
            "merchant_id": "MCHT-0001",
            "pan": "378282246310005",
        },
    ]
