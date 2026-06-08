from fastapi import FastAPI, Depends, HTTPException, Security, Request, Form
from fastapi.security import APIKeyHeader
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app import database, crud, schemas
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key

app = FastAPI(title="Nifty 100 Financial Intelligence API", version="1.0")

# Setup for HTML templates and static files
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def startup():
    await database.engine.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.engine.dispose()

# ------------------- HTML ROUTES (Website) -------------------

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    async with database.AsyncSessionLocal() as db:
        companies = await crud.get_all_companies(db, limit=10)
    return templates.TemplateResponse("home.html", {"request": request, "companies": companies})

@app.get("/companies", response_class=HTMLResponse)
async def company_list_page(request: Request, page: int = 1, limit: int = 20):
    skip = (page - 1) * limit
    async with database.AsyncSessionLocal() as db:
        companies = await crud.get_all_companies(db, skip=skip, limit=limit)
        total = await crud.get_total_companies(db)
    total_pages = (total + limit - 1) // limit
    return templates.TemplateResponse("companies.html", {
        "request": request,
        "companies": companies,
        "page": page,
        "total_pages": total_pages
    })

@app.get("/company/{symbol}", response_class=HTMLResponse)
async def company_detail_page(request: Request, symbol: str):
    async with database.AsyncSessionLocal() as db:
        company = await crud.get_company_by_symbol(db, symbol)
        if not company:
            return templates.TemplateResponse("404.html", {"request": request}, status_code=404)
        annual_pl_list = company.annual_pl or []
        annual_pl_list.sort(key=lambda x: x.year_ending)
        chart_data = {
            "years": [pl.year_ending.year for pl in annual_pl_list if pl.year_ending],
            "revenues": [float(pl.revenue) if pl.revenue else None for pl in annual_pl_list]
        }
    return templates.TemplateResponse("company_detail.html", {
        "request": request,
        "company": company,
        "chart_data": chart_data
    })

@app.get("/compare", response_class=HTMLResponse)
async def compare_page(request: Request):
    async with database.AsyncSessionLocal() as db:
        companies = await crud.get_all_companies(db, limit=100)
    return templates.TemplateResponse("compare.html", {"request": request, "companies": companies})

@app.get("/screener", response_class=HTMLResponse)
async def screener_page(request: Request):
    async with database.AsyncSessionLocal() as db:
        sectors = await crud.get_distinct_sectors(db)
    return templates.TemplateResponse("screener.html", {"request": request, "sectors": sectors})

# Simplified sector route – passes only company list; template fetches details via API
@app.get("/sector/{sector_name}", response_class=HTMLResponse)
async def sector_detail_page(request: Request, sector_name: str):
    async with database.AsyncSessionLocal() as db:
        companies = await crud.get_companies_by_sector(db, sector_name)
        if not companies:
            return templates.TemplateResponse("404.html", {"request": request}, status_code=404)
        # Pass only the symbol and name (JSON‑serializable)
        companies_data = [{"symbol": c.symbol, "name": c.name or ""} for c in companies]
    return templates.TemplateResponse("sector.html", {
        "request": request,
        "sector": sector_name,
        "companies": companies_data
    })

# ------------------- JSON API ROUTES -------------------
# (Public endpoints – no API key required)

@app.get("/api/companies", response_model=list[schemas.CompanyOut])
async def list_companies(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(database.get_db)):
    companies = await crud.get_all_companies(db, skip, limit)
    return companies

@app.get("/api/companies/{symbol}", response_model=schemas.CompanyFinancials)
async def get_company(symbol: str, db: AsyncSession = Depends(database.get_db)):
    symbol = symbol.strip()
    company = await crud.get_company_by_symbol(db, symbol)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company

# ------------------- SECURED API ROUTES (require API key) -------------------
@app.post("/api/screener", response_model=list[schemas.CompanyOut])
async def screener_endpoint(filters: schemas.ScreenerFilters, db: AsyncSession = Depends(database.get_db), api_key: str = Depends(verify_api_key)):
    companies = await crud.screener(db, filters)
    return companies

# Public screener endpoint for the website (no API key required)
@app.post("/api/public/screener", response_model=list[schemas.CompanyOut])
async def public_screener(filters: schemas.ScreenerFilters, db: AsyncSession = Depends(database.get_db)):
    companies = await crud.screener(db, filters)
    return companies

    