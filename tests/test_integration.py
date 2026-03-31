from src.models import Apartment
from src.manager import Manager
from src.models import Parameters
import pytest


def test_load_data():
    parameters = Parameters()
    manager = Manager(parameters)
    assert isinstance(manager.apartments, dict)
    assert isinstance(manager.tenants, dict)
    assert isinstance(manager.transfers, list)
    assert isinstance(manager.bills, list)
 
    for apartment_key, apartment in manager.apartments.items():
        assert isinstance(apartment, Apartment)
        assert apartment.key == apartment_key
 
def test_tenants_in_manager():
    parameters = Parameters()
    manager = Manager(parameters)
    assert len(manager.tenants) > 0
    names = [tenant.name for tenant in manager.tenants.values()]
    for tenant in ['Jan Nowak', 'Adam Kowalski', 'Ewa Adamska']:
        assert tenant in names
 
def test_if_tenants_have_valid_apartment_keys():
    parameters = Parameters()
    manager = Manager(parameters)
    assert manager.check_tenants_apartment_keys() == True
 
    manager.tenants['tenant-1'].apartment = 'invalid-key'
    assert manager.check_tenants_apartment_keys() == False
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