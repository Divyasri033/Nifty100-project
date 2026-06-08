from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, index=True)
    name = Column(String)
    sector = Column(String, nullable=True)

    annual_pl = relationship("AnnualPL", back_populates="company")
    balance_sheet = relationship("BalanceSheet", back_populates="company")
    cash_flow = relationship("CashFlow", back_populates="company")

class AnnualPL(Base):
    __tablename__ = "annual_pl"
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    year_ending = Column(Date)
    revenue = Column(Numeric, nullable=True)
    expenses = Column(Numeric, nullable=True)
    net_profit = Column(Numeric, nullable=True)
    eps = Column(Numeric, nullable=True)

    company = relationship("Company", back_populates="annual_pl")

class BalanceSheet(Base):
    __tablename__ = "balance_sheet"
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    year_ending = Column(Date)
    total_assets = Column(Numeric, nullable=True)
    total_debt = Column(Numeric, nullable=True)
    shareholder_equity = Column(Numeric, nullable=True)

    company = relationship("Company", back_populates="balance_sheet")

class CashFlow(Base):
    __tablename__ = "cash_flow"
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    year_ending = Column(Date)
    operating_cf = Column(Numeric, nullable=True)
    investing_cf = Column(Numeric, nullable=True)
    financing_cf = Column(Numeric, nullable=True)

    company = relationship("Company", back_populates="cash_flow")