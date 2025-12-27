from enum import StrEnum
from urllib.parse import quote

from .base import GBMApiBase

GBM_APP = 'https://app.gbm.com'


class MarketType(StrEnum):
    SIC = "SIC"
    BMW = "BMV"


class CommodityType(StrEnum):
    DIVISAS = "2eb6d3be-4f51-4551-93fc-006930518e4d"
    MATERIA_PRIMA = "f3851585-1456-4fcd-a6cb-23ef31dd351b"


class GBMApi(GBMApiBase):
    API_URL = "https://api.gbm.com"
    ORIGIN = "https://homebroker.gbm.com"

    def session(self):
        # Initiate API Session
        return self._request(
            path="/v1/session",
            json={
                "identity_token": self.auth.identity_token()
            }
        )

    # ACCOUNT MANAGER ELIGIBILITY
    def account_manager_eligibility(self):
        return self._request(
            path=f"/v1/account-manager-eligibility"
        )

    # NOTIFICATIONS
    def notifications_details(self):
        return self._request(
            path=f"/v1/notifications/details"
        )

    # LEGAL DOCUMENTS
    def legal_documents(self):
        return self._request(
            path=f"/v2/legal-documents"
        )

    # CATALOGS
    def catalogs_zip_location(self, zip_code):
        return self._request(
            path=f"/v1/catalogs/countries/MEX/zip-locations/{zip_code}"
        )

    # OPENING STATUS
    def opening_status(self):
        return self._request(
            path=f"/v3/opening-status",
        )

    # PARTIES
    def parties(self):
        return self._request(
            path=f"/v1/parties",
        )

    def parties_tax_information(self, party_id):
        return self._request(
            path=f"/v1/parties/{party_id}/tax-information",
        )

    def parties_countries(self, party_id):
        return self._request(
            path=f"/v1/parties/{party_id}/countries",
        )

    def parties_identifiers(self, party_id):
        return self._request(
            path=f"/v1/parties/{party_id}/identifiers",
        )

    def parties_telephones(self, party_id):
        return self._request(
            path=f"/v1/parties/{party_id}/telephones",
        )

    # ACCOUNTS
    def accounts_smart_cash_rates(self, account_id):
        return self._request(
            path=f"/v1/accounts/{account_id}/smart-cash-rates",
        )

    # CONTRACTS
    def contracts(self):
        return self._request(
            path=f"/v1/contracts",
        )

    def contracts_accounts(self, contract_id, is_thematic_type_included=True):
        return self._request(
            path=f"/v2/contracts/{contract_id}/accounts" + f"?isThematicTypeIncluded={is_thematic_type_included}" if is_thematic_type_included else "",
        )

    def contracts_summary(self, contract_id, is_thematic_type_included=True):
        return self._request(
            path=f"/v1/contracts/{contract_id}/summary" + f"?isThematicTypeIncluded={is_thematic_type_included}" if is_thematic_type_included else "",
        )

    def contracts_composition(self, contract_id, is_thematic_type_included=True):
        return self._request(
            path=f"/v1/contracts/{contract_id}/composition" + f"?isThematicTypeIncluded={is_thematic_type_included}" if is_thematic_type_included else "",
        )

    # MARKETS
    def markets(self, market_type: MarketType):
        return self._request(
            path=f"/v1/markets/{market_type}",
        )

    def markets_commodities(self, type_id: CommodityType):
        return self._request(
            path=f"/v1/markets/commodities?type_id={type_id}"
        )

    def markets_details(self, market_type: MarketType, ticker):
        ticker = quote(ticker)
        return self._request(
            path=f"/v1/markets/{market_type}/securities/{ticker}/detail"
        )

    def markets_level_one(self, market_type: MarketType, ticker):
        ticker = quote(ticker)
        return self._request(
            path=f"/v1/markets/{market_type}/securities/{ticker}/level-one"
        )

    def markets_level_two(self, market_type: MarketType, ticker):
        ticker = quote(ticker)
        return self._request(
            path=f"/v1/markets/{market_type}/securities/{ticker}/level-two"
        )

    def markets_trade_details(self, market_type: MarketType, ticker):
        ticker = quote(ticker)
        return self._request(
            path=f"/v1/markets/{market_type}/securities/{ticker}/trade-details",
        )

    def markets_historical_trades(self, market_type: MarketType, ticker, start_date, end_date):
        ticker = quote(ticker)
        start_date = start_date.strftime("%Y-%m-%d")
        end_date = end_date.strftime("%Y-%m-%d")
        return self._request(
            path=f"/v1/markets/{market_type}/securities/{ticker}/historical-trades?start_date={start_date}&end_date={end_date}",
        )
