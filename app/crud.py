from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import List
from app import models, schemas

async def get_all_companies(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(models.Company).offset(skip).limit(limit))
    return result.scalars().all()

async def get_company_by_symbol(db: AsyncSession, symbol: str):
    result = await db.execute(
        select(models.Company)
        .where(models.Company.symbol == symbol)
        .options(
            selectinload(models.Company.annual_pl),
            selectinload(models.Company.balance_sheet),
            selectinload(models.Company.cash_flow)
        )
    )
    return result.scalar_one_or_none()

# Keep the old function if you still use it elsewhere
async def get_company_financials(db: AsyncSession, company_id: int):
    pl_result = await db.execute(
        select(models.AnnualPL).where(models.AnnualPL.company_id == company_id).order_by(models.AnnualPL.year_ending)
    )
    pl = pl_result.scalars().all()
    bs_result = await db.execute(
        select(models.BalanceSheet).where(models.BalanceSheet.company_id == company_id).order_by(models.BalanceSheet.year_ending)
    )
    bs = bs_result.scalars().all()
    cf_result = await db.execute(
        select(models.CashFlow).where(models.CashFlow.company_id == company_id).order_by(models.CashFlow.year_ending)
    )
    cf = cf_result.scalars().all()
    return pl, bs, cf

async def screener(db: AsyncSession, filters: schemas.ScreenerFilters):
    query = select(models.Company)
    # Add filters here as needed (can be extended)
    result = await db.execute(query)
    return result.scalars().all()

# --- New functions for the website ---

async def get_total_companies(db: AsyncSession) -> int:
    result = await db.execute(select(func.count()).select_from(models.Company))
    return result.scalar()

async def get_distinct_sectors(db: AsyncSession) -> List[str]:
    result = await db.execute(
        select(models.Company.sector)
        .distinct()
        .where(models.Company.sector.isnot(None))
    )
    sectors = result.scalars().all()
    return [s for s in sectors if s]

async def get_companies_by_sector(db: AsyncSession, sector_name: str, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(models.Company)
        .where(models.Company.sector == sector_name)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()