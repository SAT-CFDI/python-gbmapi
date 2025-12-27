from datetime import date
from decimal import Decimal
from enum import IntEnum, Enum
from time import time

from . import GBMAuth
from .base import GBMApiBase
from .utils import format_date, format_date_end


class InstrumentType(IntEnum):
    SIC = 2
    BMW = 0


class CapitalOrderType(IntEnum):
    NORMAL_BUY = 1
    NORMAL_SELL = 8


class ProcessStatus(IntEnum):
    NEW = 2
    CANCELED = 5
    FULL = 7
    PARTIAL = 8
    REJECTED = 9

#
# class Direction(Enum):
#     BUY = True
#     SELL = False


APP_ID = 16


class GBMHomebrokerApi(GBMApiBase):
    API_URL = "https://homebroker-api.gbm.com"
    ORIGIN = "https://homebroker.gbm.com"

    def __init__(self, auth: GBMAuth, account_id: str, legacy_contract_id: str, collecting_account: str):
        super().__init__(auth)
        self.account_id = account_id
        self.legacy_contract_id = legacy_contract_id
        self.collecting_account = collecting_account

    def calculate_order_hash(self, issue_id, qty: int, capital_order_type_id: CapitalOrderType):
        return "{0}{1}{2}{3}{4}{5}".format(
            APP_ID,
            int(time() * 1000),
            self.legacy_contract_id,
            issue_id.replace(" ", ""),
            qty,
            capital_order_type_id
        )

    # ANALYSIS
    def analysis_get_t_rules_wl_historical_performance_view(self, start_date: date, market_id):
        return self._request(
            path="/GBMP/api/Analysis/GetTRulesWlHistoricalPerformanceView",
            json={
                "startDate": start_date.isoformat(),
                "marketId": market_id  # 4 -SIC
            }
        )

    # APP MANAGEMENT
    def app_management_get_user_app_configuration(self):
        return self._request(
            path="/GBMP/api/AppManagement/GetUserAppConfiguration"
        )

    def app_management_get_trading_market_configuration(self):
        return self._request(
            path="/GBMP/api/AppManagement/GetTradingMarketConfiguration"
        )

    def app_management_get_agreement_log(self):
        return self._request(
            path="/GBMP/api/appmanagement/GetAgreementLog",
            json={
                "agreementTypeId": 17
            }
        )

    def app_management_get_capital_market_operation_time(self):
        return self._request(
            path="/GBMP/api/AppManagement/GetCapitalMarketOperationTime"
        )

    # MARKET
    def market_get_market_price_monitor_detail(self, instrument_type: InstrumentType):
        return self._request(
            path="/GBMP/api/Market/GetMarketPriceMonitorDetail",
            json={
                "isOnLine": True,
                "instrumentType": instrument_type,
            }
        )

    # CASH
    def cash_get_banks(self):
        return self._request(
            path="/GBMP/api/Cash/GetBanks"
        )

    # UTILITIES
    def utilities_get_central_hour(self):
        return self._request(
            path="/GBMP/api/Utilities/GetCentralHour"
        )

    # OPERATION
    def operation_get_blotter_orders(self, instrument_types: list, process_date: date = None):
        process_date = process_date or date.today()
        return self._request(
            path="/GBMP/api/Operation/GetBlotterOrders",
            json={
                "instrumentTypes": instrument_types,  # [0, 2],
                "processDate": format_date(process_date),
                "accountId": self.legacy_contract_id,
                "contractId": self.legacy_contract_id,
            }
        )

    def operation_get_contract_buying_power(self, is_real_time: bool = False):
        payload = {
            "request": self.legacy_contract_id
        }
        if is_real_time:
            payload["isRealTime"] = is_real_time

        return self._request(
            path="/GBMP/api/Operation/GetContractBuyingPower",
            json=payload
        )

    def operation_get_contract_properties(self, is_real_time: bool = False):
        payload = {
            "request": self.legacy_contract_id
        }
        if is_real_time:
            payload["isRealTime"] = is_real_time

        return self._request(
            path="/GBMP/api/Operation/GetContractProperties",
            json=payload
        )

    def operation_register_capital_order(self, issue_id: str, instrument_type: InstrumentType, qty: int, price: int | float | Decimal, capital_order_type_id: CapitalOrderType, duration: int = 1):
        return self._request(
            path="/GBMP/api/Operation/RegisterCapitalOrder",
            headers={
                'device-latitude': self.auth.latitude,
                'device-longitude': self.auth.longitude,
            },
            json={
                "contractId": self.legacy_contract_id,
                "duration": duration,
                "orders": [
                    {
                        "issueId": issue_id,
                        "instrumentType": instrument_type,
                        "quantity": qty,
                        "price": price,
                        "capitalOrderTypeId": capital_order_type_id,
                        "hash": self.calculate_order_hash(issue_id, qty=qty, capital_order_type_id=capital_order_type_id)
                    }
                ]
            }
        )

    def operation_cancel_order(self, electronic_order_id, is_predispatch_order, vigencia):
        return self._request(
            path="/GBMP/api/Operation/CancelOrder",
            json={
                "ElectronicOrderId": electronic_order_id,
                "IsPredispatchOrder": is_predispatch_order,
                "vigencia": vigencia
            }
        )

    # PORTFOLIO
    def portfolio_get_time_weighted_return(self):
        return self._request(
            path="/GBMP/api/Portfolio/GetTimeWeightedReturn",
            json={
                "request": self.legacy_contract_id
            }
        )

    def get_historical_cash_operations(self, start_date: date, end_date: date):
        return self._request(
            path="/GBMP/api/Operation/GetHistoricalCashOperations",
            json={
                "startDate": format_date(start_date),
                "endDate": format_date_end(end_date),
                "contractId": self.legacy_contract_id,
                "speiAccount": self.collecting_account
            }
        )

    def portfolio_get_position_summary(self, is_real_time: bool = False):
        payload = {
            "request": self.legacy_contract_id
        }
        if is_real_time:
            payload["isRealTime"] = is_real_time

        return self._request(
            path="/GBMP/api/Portfolio/GetPositionSummary",
            json=payload
        )

    def portfolio_get_transactions(self, start_date: date, end_date: date, is_settlement: bool = False):
        return self._request(
            path="/GBMP/api/Portfolio/GetTransactions",
            json={
                "isSettlement": is_settlement,  # False,
                "pageIndex": 0,
                "pageSize": 50,
                "sortTransaction": 23,
                "startDate": format_date(start_date),  # "2021-01-05T06:00:00.000Z",
                "endDate": format_date(end_date),  # "2021-02-05T06:00:00.000Z",
                "contractId": self.legacy_contract_id,
                "ascendent": True
            }
        )
