from src.models import Apartment, Bill, Parameters, Tenant, Transfer, ApartmentSettlement, TenantSettlement
 
 
class Manager:
    def __init__(self, parameters: Parameters):
        self.parameters = parameters 
 
        self.apartments = {}
        self.tenants = {}
        self.transfers = []
        self.bills = []
 
        self.load_data()
 
    def load_data(self):
        self.apartments = Apartment.from_json_file(self.parameters.apartments_json_path)
        self.tenants = Tenant.from_json_file(self.parameters.tenants_json_path)
        self.transfers = Transfer.from_json_file(self.parameters.transfers_json_path)
        self.bills = Bill.from_json_file(self.parameters.bills_json_path)
 
    def check_tenants_apartment_keys(self) -> bool:
        for tenant in self.tenants.values():
            if tenant.apartment not in self.apartments:
                return False
        return True
 
    def get_apartment_costs(self, apartment_key: str, year: int = None, month: int = None) -> float:
        if apartment_key not in self.apartments:
            raise ValueError(f"Apartment {apartment_key} does not exist")

        if month is not None and (month < 1 or month > 12):
            raise ValueError(f"Month {month} is invalid")

        if month is not None and year is None:
            raise ValueError("Year is required when month is provided")

        total = 0.0

        for bill in self.bills:
            if bill.apartment != apartment_key:
                continue

            if year is not None and bill.settlement_year != year:
                continue

            if month is not None and bill.settlement_month != month:
                continue

            total += bill.amount_pln

        return total

    def get_apartment_settlement(self, apartment_key: str, year: int, month: int) -> ApartmentSettlement:
        if apartment_key not in self.apartments:
            raise ValueError(f"Apartment {apartment_key} does not exist")

        if month < 1 or month > 12:
            raise ValueError(f"Month {month} is invalid")

        total_bills_pln = 0.0
        for bill in self.bills:
            if bill.apartment == apartment_key and bill.settlement_year == year and bill.settlement_month == month:
                total_bills_pln += bill.amount_pln

        total_rent_pln = 0.0
        total_due_pln = total_rent_pln - total_bills_pln

        return ApartmentSettlement(
            apartment=apartment_key,
            month=month,
            year=year,
            total_rent_pln=total_rent_pln,
            total_bills_pln=total_bills_pln,
            total_due_pln=total_due_pln
        )

    def get_tenant_settlements(self, apartment_key: str, year: int, month: int):
        if apartment_key not in self.apartments:
            raise ValueError(f"Apartment {apartment_key} does not exist")

        if month < 1 or month > 12:
            raise ValueError(f"Month {month} is invalid")

        apartment_settlement = self.get_apartment_settlement(apartment_key, year, month)
        tenants = [t for t in self.tenants.values() if t.apartment == apartment_key]

        if len(tenants) == 0:
            return []

        per_tenant_bills = apartment_settlement.total_bills_pln / len(tenants)

        result = []
        for tenant in tenants:
            total_due_pln = -per_tenant_bills
            balance_pln = total_due_pln
            result.append(TenantSettlement(
                tenant=tenant.name,
                apartment_settlement=f"{apartment_key}-{year}-{month}",
                month=month,
                year=year,
                rent_pln=tenant.rent_pln,
                bills_pln=per_tenant_bills,
                total_due_pln=total_due_pln,
                balance_pln=balance_pln
            ))

        return result

