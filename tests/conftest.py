import pandas as pd
import pytest
from src.validation import validate


@pytest.fixture
def raw():
    return pd.DataFrame({
        'booking_id': ['A', 'B', 'C', 'D'],
        'booking_date': ['2025-01-01', '2025-01-31', '2025-02-01', '2025-02-10'],
        'status': ['Confirmed', 'Cancelled', 'Completed', 'Pending'],
        'booking_value': [100, 200, 300, 400], 'cost': [60, 120, 210, 200],
        'channel': ['Direct', 'OTA', 'Direct', 'OTA'],
        'room_type': ['Standard', 'Suite', 'Suite', 'Standard'],
        'city': ['Goa', 'Goa', 'Delhi', 'Delhi'], 'star_rating': [3, 4, 5, 3],
    })


@pytest.fixture
def clean(raw):
    return validate(raw).accepted
