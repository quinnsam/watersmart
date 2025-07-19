"""Test the WaterSmart coordinator."""

import datetime as dt

from freezegun import freeze_time
from homeassistant.util.dt import get_default_time_zone, start_of_local_day

from custom_components.watersmart.coordinator import WaterSmartUpdateCoordinator


@freeze_time("2024-07-18 12:00:00-07:00")
async def test_records_from_first_full_day_continue_today(
    hass, mock_watersmart_client, snapshot
):
    """Test _records_from_first_full_day to cover the continue condition for today's records."""
    hourly = []
    now = dt.datetime.now(tz=get_default_time_zone())

    # Records for today (should trigger continue)
    hourly.extend(
        [
            {
                "read_datetime": int((now - dt.timedelta(hours=i)).timestamp()),
                "gallons": 1.0,
                "read_id": i,
                "meter_id": "meter1",
            }
            for i in range(5)
        ]
    )

    # Records for a past full day (to ensure the function eventually finds a full day)
    past_day_start = start_of_local_day(now) - dt.timedelta(days=2)
    hourly.extend(
        [
            {
                "read_datetime": int(
                    (past_day_start + dt.timedelta(hours=i)).timestamp()
                ),
                "gallons": 2.0,
                "read_id": 100 + i,
                "meter_id": "meter1",
            }
            for i in range(24)
        ]
    )

    hourly.reverse()  # Simulate chronological order from client

    mock_watersmart_client.async_get_hourly_data.return_value = hourly

    coordinator = WaterSmartUpdateCoordinator(
        hass,
        mock_watersmart_client,
        "test_host",
        "test_user",
    )

    data = await coordinator._async_update_data()

    assert snapshot == data
