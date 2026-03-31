from src.models import Apartment
from src.manager import Manager
from src.models import Parameters
import pytest

def test_get_apartment_costs():
    parameters = Parameters()
    manager = Manager(parameters)

    apartment_key = list(manager.apartments.keys())[0]
 
    result = manager.get_apartment_costs(apartment_key, 2024, 3)
    assert isinstance(result, float)
    assert result >= 0.0
 
    empty_result = manager.get_apartment_costs(apartment_key, 1900, 1)
    assert empty_result == 0.0
 
    with pytest.raises(ValueError):
        manager.get_apartment_costs('INVALID', 2024, 3)