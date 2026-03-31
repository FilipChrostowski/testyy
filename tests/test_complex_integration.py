

from src.manager import Manager
from src.models import Parameters, Bill, Tenant
import pytest


def test_get_apartment_costs_for_month_and_year_and_history():
    manager = Manager(Parameters())
    manager.apartments['test-apartment'] = None

    manager.bills.append(Bill(
        apartment='test-apartment',
        date_due='2025-03-10',
        settlement_year=2025,
        settlement_month=3,
        amount_pln=250.0,
        type='utilities'
    ))

    manager.bills.append(Bill(
        apartment='test-apartment',
        date_due='2025-03-20',
        settlement_year=2025,
        settlement_month=3,
        amount_pln=150.0,
        type='rent'
    ))

    manager.bills.append(Bill(
        apartment='test-apartment',
        date_due='2025-04-05',
        settlement_year=2025,
        settlement_month=4,
        amount_pln=100.0,
        type='electricity'
    ))

    manager.bills.append(Bill(
        apartment='test-apartment',
        date_due='2024-03-12',
        settlement_year=2024,
        settlement_month=3,
        amount_pln=300.0,
        type='gas'
    ))

    assert manager.get_apartment_costs('test-apartment', 2025, 3) == 400.0
    assert manager.get_apartment_costs('test-apartment', 2025) == 500.0
    assert manager.get_apartment_costs('test-apartment') == 800.0

    with pytest.raises(ValueError):
        manager.get_apartment_costs('test-apartment', 2025, 13)

    with pytest.raises(ValueError):
        manager.get_apartment_costs('test-apartment', None, 3)

    with pytest.raises(ValueError):
        manager.get_apartment_costs('missing-apartment', 2025, 3)


def test_apartment_settlement_balance():
    manager = Manager(Parameters())
    manager.apartments['a1'] = None
    manager.apartments['a2'] = None

    manager.bills.append(Bill(
        apartment='a1',
        date_due='2025-03-05',
        settlement_year=2025,
        settlement_month=3,
        amount_pln=120.0,
        type='water'
    ))
    manager.bills.append(Bill(
        apartment='a1',
        date_due='2025-03-15',
        settlement_year=2025,
        settlement_month=3,
        amount_pln=80.0,
        type='electricity'
    ))
    manager.bills.append(Bill(
        apartment='a1',
        date_due='2025-04-10',
        settlement_year=2025,
        settlement_month=4,
        amount_pln=50.0,
        type='gas'
    ))
    manager.bills.append(Bill(
        apartment='a2',
        date_due='2025-03-09',
        settlement_year=2025,
        settlement_month=3,
        amount_pln=200.0,
        type='water'
    ))

    settlement_a1_2025_3 = manager.get_apartment_settlement('a1', 2025, 3)
    assert settlement_a1_2025_3.apartment == 'a1'
    assert settlement_a1_2025_3.year == 2025
    assert settlement_a1_2025_3.month == 3
    assert settlement_a1_2025_3.total_rent_pln == 0.0
    assert settlement_a1_2025_3.total_bills_pln == 200.0
    assert settlement_a1_2025_3.total_due_pln == -200.0

    settlement_a1_2025_4 = manager.get_apartment_settlement('a1', 2025, 4)
    assert settlement_a1_2025_4.total_bills_pln == 50.0
    assert settlement_a1_2025_4.total_due_pln == -50.0

    settlement_a2_2025_3 = manager.get_apartment_settlement('a2', 2025, 3)
    assert settlement_a2_2025_3.total_bills_pln == 200.0

    with pytest.raises(ValueError):
        manager.get_apartment_settlement('a1', 2025, 13)

    with pytest.raises(ValueError):
        manager.get_apartment_settlement('missing', 2025, 3)


def test_tenant_settlements_share_and_empty():
    manager = Manager(Parameters())
    manager.apartments['a1'] = None
    manager.apartments['a3'] = None

    manager.tenants['t1'] = Tenant(
        name='t1', apartment='a1', room='1', rent_pln=500.0, deposit_pln=0.0,
        date_agreement_from='2024-01-01', date_agreement_to='2026-01-01'
    )
    manager.tenants['t2'] = Tenant(
        name='t2', apartment='a1', room='2', rent_pln=600.0, deposit_pln=0.0,
        date_agreement_from='2024-01-01', date_agreement_to='2026-01-01'
    )
    manager.tenants['t3'] = Tenant(
        name='t3', apartment='a3', room='1', rent_pln=700.0, deposit_pln=0.0,
        date_agreement_from='2024-01-01', date_agreement_to='2026-01-01'
    )

    manager.bills.append(Bill(
        apartment='a1', date_due='2025-03-05', settlement_year=2025, settlement_month=3,
        amount_pln=300.0, type='water'
    ))
    manager.bills.append(Bill(
        apartment='a1', date_due='2025-03-15', settlement_year=2025, settlement_month=3,
        amount_pln=100.0, type='electricity'
    ))

    tenant_settlements = manager.get_tenant_settlements('a1', 2025, 3)
    assert len(tenant_settlements) == 2
    assert tenant_settlements[0].tenant in ('t1', 't2')
    assert tenant_settlements[1].tenant in ('t1', 't2')
    assert tenant_settlements[0].bills_pln == 200.0
    assert tenant_settlements[1].bills_pln == 200.0
    assert tenant_settlements[0].total_due_pln == -200.0
    assert tenant_settlements[1].total_due_pln == -200.0
    assert tenant_settlements[0].balance_pln == -200.0
    assert tenant_settlements[1].balance_pln == -200.0

    # jeden najemca
    manager.tenants.pop('t2')
    single = manager.get_tenant_settlements('a1', 2025, 3)
    assert len(single) == 1
    assert single[0].bills_pln == 400.0

    # brak najemców w mieszkaniu
    manager.tenants.pop('t1')
    no_one = manager.get_tenant_settlements('a1', 2025, 3)
    assert no_one == []

    with pytest.raises(ValueError):
        manager.get_tenant_settlements('missing', 2025, 3)

