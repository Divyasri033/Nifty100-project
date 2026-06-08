from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional, List

class CompanyBase(BaseModel):
    symbol: str
    name: str
    sector: Optional[str] = None

class CompanyOut(CompanyBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class AnnualPLOut(BaseModel):
    year_ending: date
    revenue: Optional[float] = None
    net_profit: Optional[float] = None
    eps: Optional[float] = None
    model_config = ConfigDict(from_attributes=True)

class BalanceSheetOut(BaseModel):
    year_ending: date
    total_assets: Optional[float] = None
    total_debt: Optional[float] = None
    shareholder_equity: Optional[float] = None
    model_config = ConfigDict(from_attributes=True)

class CashFlowOut(BaseModel):
    year_ending: date
    operating_cf: Optional[float] = None
    investing_cf: Optional[float] = None
    financing_cf: Optional[float] = None
    model_config = ConfigDict(from_attributes=True)

class CompanyFinancials(CompanyOut):
    annual_pl: List[AnnualPLOut] = []
    balance_sheet: List[BalanceSheetOut] = []
    cash_flow: List[CashFlowOut] = []
    model_config = ConfigDict(from_attributes=True)

class ScreenerFilters(BaseModel):
    min_revenue: Optional[float] = None
    max_debt_to_equity: Optional[float] = None
    sector: Optional[str] = None