"""Test adding external statistics from Tibber."""
from unittest.mock import AsyncMock

from homeassistant.components.recorder.statistics import statistics_during_period
from homeassistant.components.tibber.sensor import TibberDataCoordinator
from homeassistant.util import dt as dt_util

from .test_common import CONSUMPTION_DATA_1, mock_get_homes

from tests.components.recorder.common import async_wait_recording_done_without_instance


async def test_async_setup_entry(hass, recorder_mock):
    """Test setup Tibber."""
    tibber_connection = AsyncMock()
    tibber_connection.name = "tibber"
    tibber_connection.fetch_consumption_data_active_homes.return_value = None
    tibber_connection.get_homes = mock_get_homes

    coordinator = TibberDataCoordinator(hass, tibber_connection)
    await coordinator._async_update_data()
    await async_wait_recording_done_without_instance(hass)

    # Validate consumption
    statistic_id = "tibber:energy_consumption_home_id"

    stats = await hass.async_add_executor_job(
        statistics_during_period,
        hass,
        dt_util.parse_datetime(CONSUMPTION_DATA_1[0]["from"]),
        None,
        [statistic_id],
        "hour",
        True,
    )

    assert len(stats) == 1
    assert len(stats[statistic_id]) == 3
    _sum = 0
    for k, stat in enumerate(stats[statistic_id]):
        assert stat["start"] == dt_util.parse_datetime(CONSUMPTION_DATA_1[k]["from"])
        assert stat["state"] == CONSUMPTION_DATA_1[k]["consumption"]
        assert stat["mean"] is None
        assert stat["min"] is None
        assert stat["max"] is None
        assert stat["last_reset"] is None

        _sum += CONSUMPTION_DATA_1[k]["consumption"]
        assert stat["sum"] == _sum

    # Validate cost
    statistic_id = "tibber:energy_totalcost_home_id"

    stats = await hass.async_add_executor_job(
        statistics_during_period,
        hass,
        dt_util.parse_datetime(CONSUMPTION_DATA_1[0]["from"]),
        None,
        [statistic_id],
        "hour",
        True,
    )

    assert len(stats) == 1
    assert len(stats[statistic_id]) == 3
    _sum = 0
    for k, stat in enumerate(stats[statistic_id]):
        assert stat["start"] == dt_util.parse_datetime(CONSUMPTION_DATA_1[k]["from"])
        assert stat["state"] == CONSUMPTION_DATA_1[k]["totalCost"]
        assert stat["mean"] is None
        assert stat["min"] is None
        assert stat["max"] is None
        assert stat["last_reset"] is None

        _sum += CONSUMPTION_DATA_1[k]["totalCost"]
        assert stat["sum"] == _sum
