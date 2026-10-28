import pytest
from bike_share_rental import ride_cost, dock_status, can_unlock

def test_standard_ride():
    assert ride_cost("standard", 45, False, False) == 40

def test_unknown_bike_type():
    with pytest.raises(ValueError):
        ride_cost("scooter", 30, False, False)

def test_invalid_duration():
    with pytest.raises(ValueError):
        ride_cost("standard", 0, False, False)

def test_subscriber_free_first_block():
    assert ride_cost("standard", 20, True, False) == 0

def test_peak_surcharge_electric():
    assert ride_cost("electric", 30, False, True) == 50

def test_long_ride_surcharge():
    assert ride_cost("standard", 200, False, False) == 240

def test_dock_available():
    assert dock_status(5, 10) == "available"

def test_dock_invalid_capacity():
    with pytest.raises(ValueError):
        dock_status(0, 0)

def test_dock_negative_bikes():
    with pytest.raises(ValueError):
        dock_status(-1, 10)

def test_dock_empty():
    assert dock_status(0, 10) == "empty"

def test_dock_full():
    assert dock_status(10, 10) == "full"

def test_dock_few_bikes():
    assert dock_status(2, 10) == "few bikes"

def test_dock_few_slots():
    assert dock_status(8, 10) == "few slots"

def test_unlock_active_ride():
    assert can_unlock(500, True, 25) is False

def test_unlock_underage():
    assert can_unlock(500, False, 15) is False

def test_unlock_teen_enough_balance():
    assert can_unlock(100, False, 17) is True

def test_unlock_adult_enough_balance():
    assert can_unlock(50, False, 30) is True

def test_subscriber_pays_after_free_block():
    assert ride_cost("standard", 45, True, False) == 20

def test_peak_no_surcharge_for_cargo():
    assert ride_cost("cargo", 30, False, True) == 50

def test_no_long_ride_surcharge_at_180():
    assert ride_cost("standard", 180, False, False) == 120

def test_long_ride_surcharge_at_181():
    assert ride_cost("standard", 181, False, False) == 240

def test_negative_minutes():
    with pytest.raises(ValueError):
        ride_cost("electric", -5, False, False)

def test_dock_too_many_bikes():
    with pytest.raises(ValueError):
        dock_status(11, 10)

def test_dock_negative_capacity():
    with pytest.raises(ValueError):
        dock_status(1, -3)

def test_dock_boundary_three_bikes():
    assert dock_status(3, 10) == "available"

def test_dock_boundary_three_slots():
    assert dock_status(7, 10) == "available"

def test_unlock_age_16_low_balance():
    assert can_unlock(99, False, 16) is False

def test_unlock_age_16_ok_balance():
    assert can_unlock(100, False, 16) is True

def test_unlock_teen_low_balance():
    assert can_unlock(99, False, 17) is False

def test_unlock_adult_low_balance():
    assert can_unlock(49, False, 18) is False
