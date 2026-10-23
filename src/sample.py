"""Reproducible synthetic bookings, with no guest personal information."""
import numpy as np
import pandas as pd


def generate_sample(rows=1800, seed=42):
    rng = np.random.default_rng(seed)
    cities = ['Bengaluru', 'Mumbai', 'Jaipur', 'Goa', 'Delhi', 'Kochi']
    rooms = ['Standard', 'Deluxe', 'Suite']
    channels = ['Direct', 'Online travel agency', 'Corporate', 'Travel agent']
    records = []
    for i in range(rows):
        city = str(rng.choice(cities))
        room = str(rng.choice(rooms, p=[.52, .33, .15]))
        channel = str(rng.choice(channels, p=[.30, .42, .18, .10]))
        day = pd.Timestamp('2025-01-01') + pd.Timedelta(days=int(rng.integers(0, 365)))
        stars = int(rng.choice([3, 4, 5], p=[.30, .45, .25]))
        nights = int(rng.integers(1, 7))
        nightly = {'Standard': 3200, 'Deluxe': 5100, 'Suite': 9200}[room]
        value = round(nightly * nights * (stars / 4) * rng.uniform(.85, 1.25), 2)
        cancel_probability = .29 if channel == 'Online travel agency' else .12
        status = 'Cancelled' if rng.random() < cancel_probability else str(
            rng.choice(['Confirmed', 'Completed', 'Pending', 'No-show'], p=[.25, .67, .05, .03]))
        records.append({'booking_id': f'DEMO-{i+1:05}', 'booking_date': day.strftime('%Y-%m-%d'),
                        'city': city, 'property': f'{city} {"Grand" if stars == 5 else "Central" if stars == 4 else "Garden"}',
                        'channel': channel, 'room_type': room, 'status': status,
                        'star_rating': stars, 'booking_value': value,
                        'cost': round(value * rng.uniform(.65, .91), 2)})
    return pd.DataFrame(records)
