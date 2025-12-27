import yfinance as yf
import mysql.connector
import pandas as pd
import requests
from io import StringIO
import time
import concurrent.futures
import math
import numpy as np
from datetime import datetime, timedelta

# ==========================================
# 🚀 USER CONFIGURATION (START HERE)
# ==========================================

# 1. DATABASE SETUP
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root', 
    'password': 'root', # ⚠️ CHANGE THIS to your local DB password
    'database': 'investor_dashboard',
    'port': 8889
}

# 2. CACHE SETTINGS (SPEED OPTIMIZATION)
# Fundamental data (Debt, Margins) only changes quarterly (every 90 days).
# There is no need to re-download data every time you run the script.
# Default: 7 days. If data is newer than 7 days, we skip the download and use the DB.
# Set to 0 to force a fresh download for all stocks.
CACHE_DURATION_DAYS = 7 

# 3. THE "ELITE" FILTERS (The Warren Buffett Logic)
MIN_GROSS_MARGIN = 45.0     # MOAT: Pricing power. Standard: 40% | Elite: 50%+
MIN_ROIC = 25.0             # ENGINE: Management efficiency. S&P Avg: 10% | Elite: 20%+
MAX_DEBT_TO_EQUITY = 0.5    # SAFETY: Leverage risk. Lower is better. > 2.0 is dangerous.
MIN_FCF_YIELD = 5.0         # VALUATION: The "interest rate" you get. 5% = 20x P/FCF.


# ==========================================
# ⚙️ CORE SYSTEM (DO NOT MODIFY UNLESS EXPERT)
# ==========================================

def get_db_connection():
    """Establishes connection to your local MySQL database."""
    return mysql.connector.connect(**DB_CONFIG)

def get_cached_data(ticker):
    """
    Checks if we already analyzed this stock recently.
    Returns the cached result if it's fresh, otherwise returns None.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # We only need the status and date to decide if we skip
        query = "SELECT status, failure_reasons, fcf_yield, updated_at FROM stocks WHERE ticker = %s"
        cursor.execute(query, (ticker,))
        result = cursor.fetchone()
        conn.close()

        if result:
            last_updated = result['updated_at']
            # Calculate age of data
            if datetime.now() - last_updated < timedelta(days=CACHE_DURATION_DAYS):
                return result
    except Exception:
        return None
    return None

def save_to_db(ticker, name, price, safety, cash, roic, de, gross_margin, fcf_yield, status, reason, val_status, lie_status):
    """Upsert logic: Inserts or updates the stock record."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = """INSERT INTO stocks 
                 (ticker, company_name, price, safety_score, cash_engine_score, 
                  roic_current, debt_to_equity, gross_margin_3yr_avg, fcf_yield, 
                  status, failure_reasons, valuation_status, lie_detector_status, updated_at)
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                 ON DUPLICATE KEY UPDATE
                 company_name=%s, price=%s, safety_score=%s, cash_engine_score=%s, 
                 roic_current=%s, debt_to_equity=%s, gross_margin_3yr_avg=%s, fcf_yield=%s,
                 status=%s, failure_reasons=%s, valuation_status=%s, lie_detector_status=%s,
                 updated_at=NOW()"""
        
        vals = (ticker, name, price, safety, cash, roic, de, gross_margin, fcf_yield, status, reason, val_status, lie_status,
                name, price, safety, cash, roic, de, gross_margin, fcf_yield, status, reason, val_status, lie_status)
        
        cursor.execute(sql, vals)
        conn.commit()
        conn.close()
    except Exception:
        pass

def get_data_with_retry(ticker, retries=2):
    """Fetches data from Yahoo Finance. Retries if connection blips."""
    for i in range(retries):
        try:
            stock = yf.Ticker(ticker)
            return stock
        except Exception:
            time.sleep(1) 
    return None

def sanitize_float(val):
    """Cleans messy data (NaN, Infinity, None) into a clean 0.0 float."""
    if val is None or math.isnan(val) or math.isinf(val): return 0.0
    return float(val)

def analyze_stock(ticker):
    """
    The Brain 🧠
    1. Checks Cache (Speed Boost)
    2. Fetches Data (If no cache)
    3. Calculates Metrics
    4. Saves to DB
    """
    
    # --- STEP 1: CACHE CHECK ---
    # Before downloading, check if we have fresh data in DB
    cached = get_cached_data(ticker)
    if cached:
        # ⚡ CACHE HIT: Print existing result and skip expensive API call
        if cached['status'] == 'SURVIVOR':
            print(f"🟢 {ticker} [CACHED]: SURVIVOR (Yield: {cached['fcf_yield']:.1f}%)")
        else:
            reason = cached['failure_reasons'] if cached['failure_reasons'] else "Unknown"
            print(f"🔴 {ticker} [CACHED]: {reason[:100]}...")
        return # STOP HERE. Job done.

    # --- STEP 2: FRESH DOWNLOAD ---
    stock = get_data_with_retry(ticker)
    if not stock: return

    try:
        # INFO FETCH
        info = stock.info
        if not info or 'currentPrice' not in info: return

        # Basic Identifiers
        price = info.get('currentPrice', 0)
        short_name = info.get('shortName', ticker)
        market_cap = info.get('marketCap', 1)
        
        # Key Financials (Current TTM)
        total_debt = sanitize_float(info.get('totalDebt', 0))
        total_equity = sanitize_float(info.get('totalStockholderEquity', 1))
        de = sanitize_float(info.get('debtToEquity', 0)) / 100 
        net_income = sanitize_float(info.get('netIncomeToCommon', 0))

        # HISTORICAL ANALYSIS (3-YEAR LOOKBACK)
        gms = []
        roics = []
        financials = stock.financials
        balance = stock.balance_sheet
        
        if not financials.empty and not balance.empty:
            num_years = min(3, len(financials.columns), len(balance.columns))
            
            for i in range(num_years):
                try:
                    # Use .iloc for positional indexing
                    revenue = sanitize_float(financials.iloc[financials.index.get_loc('Total Revenue'), i]) if 'Total Revenue' in financials.index else 0
                    gross_profit = sanitize_float(financials.iloc[financials.index.get_loc('Gross Profit'), i]) if 'Gross Profit' in financials.index else 0
                    
                    if revenue > 1000000: 
                        gm = (gross_profit / revenue) * 100
                        gms.append(gm)

                    net_inc = sanitize_float(financials.iloc[financials.index.get_loc('Net Income'), i]) if 'Net Income' in financials.index else 0
                    
                    long_debt = sanitize_float(balance.iloc[balance.index.get_loc('Long Term Debt'), i]) if 'Long Term Debt' in balance.index else 0
                    
                    short_debt = 0
                    if 'Current Debt' in balance.index:
                        short_debt = sanitize_float(balance.iloc[balance.index.get_loc('Current Debt'), i])
                    elif 'Short Long Term Debt' in balance.index:
                         short_debt = sanitize_float(balance.iloc[balance.index.get_loc('Short Long Term Debt'), i])

                    total_debt_hist = long_debt + short_debt
                    
                    eq_idx = balance.index.get_loc('Total Stockholder Equity') if 'Total Stockholder Equity' in balance.index else -1
                    equity_hist = sanitize_float(balance.iloc[eq_idx, i]) if eq_idx != -1 else 0
                    
                    invested = equity_hist + total_debt_hist
                    
                    if invested > 1000000: 
                        roic_hist = (net_inc / invested) * 100
                        roic_hist = min(200.0, max(-100.0, roic_hist))
                        roics.append(roic_hist)
                        
                except Exception:
                    continue

        # AVERAGING LOGIC
        current_gm = info.get('grossMargins', 0) * 100
        current_roic = (net_income / (total_equity + total_debt) * 100) if (total_equity + total_debt) > 0 else 0
        current_roic = min(200.0, current_roic)

        if len(gms) > 0:
            avg_gm = float(np.mean(gms))
            min_gm = float(np.min(gms))
        else:
            avg_gm = current_gm
            min_gm = current_gm

        if len(roics) > 0:
            avg_roic = float(np.mean(roics))
            min_roic = float(np.min(roics))
        else:
            avg_roic = current_roic
            min_roic = current_roic

        # Final Metrics
        gross_margin = avg_gm  
        roic = avg_roic  

        # CASH FLOW & YIELD
        fcf = 0
        try:
            cf = stock.cashflow
            if not cf.empty:
                if 'Free Cash Flow' in cf.index:
                    fcf = cf.loc['Free Cash Flow'].iloc[0]
                elif 'Operating Cash Flow' in cf.index and 'Capital Expenditure' in cf.index:
                    fcf = cf.loc['Operating Cash Flow'].iloc[0] + cf.loc['Capital Expenditure'].iloc[0]
                else:
                    fcf = sanitize_float(info.get('freeCashFlow', 0))
            else:
                 fcf = sanitize_float(info.get('freeCashFlow', 0))
        except:
            fcf = sanitize_float(info.get('freeCashFlow', 0))

        fcf_yield = (fcf / market_cap * 100) if market_cap > 0 else 0

        # LIE DETECTOR
        lie_status = "VERIFIED"
        if net_income > 0 and fcf < (net_income * 0.7):
            lie_status = "SUSPICIOUS"

        # --- THE ELITE FILTERS ---
        failure_reasons = []

        if avg_gm < MIN_GROSS_MARGIN: 
            failure_reasons.append(f"WEAK MOAT (AVG GM {avg_gm:.0f}%, MIN {min_gm:.0f}%)")
        elif min_gm < (MIN_GROSS_MARGIN * 0.8):
             failure_reasons.append(f"UNSTABLE MOAT (MIN GM {min_gm:.0f}%)")
        
        if avg_roic < MIN_ROIC: 
            failure_reasons.append(f"WEAK ENGINE (AVG ROIC {avg_roic:.1f}%)")
        elif min_roic < (MIN_ROIC * 0.8):
            failure_reasons.append(f"UNSTABLE ENGINE (MIN ROIC {min_roic:.1f}%)")

        if de > MAX_DEBT_TO_EQUITY: 
            failure_reasons.append(f"HIGH DEBT (D/E {de:.2f})")

        if fcf_yield < MIN_FCF_YIELD:
             failure_reasons.append(f"EXPENSIVE (YIELD {fcf_yield:.1f}%)")

        if lie_status == "SUSPICIOUS":
            failure_reasons.append("POOR CASH QUALITY")

        # --- VERDICT ---
        if not failure_reasons:
            status = "SURVIVOR"
            reason = "BUFFETT ELITE"
            print(f"🟢 {ticker}: SURVIVOR (Yield: {fcf_yield:.1f}%)")
        else:
            status = "REJECTED"
            reason = ' | '.join(failure_reasons)
            print(f"🔴 {ticker}: {reason[:100]}...")

        if fcf_yield > 8.0: val_status = "BARGAIN"
        elif fcf_yield > 4.5: val_status = "FAIR"
        else: val_status = "PRICEY"

        # Scores
        roic_part = min(60, (roic / 40) * 60)
        margin_part = min(40, (gross_margin / 80) * 40)
        cash_score = int(roic_part + margin_part)
        safety_score = int(max(0, 100 - (de * 200)))

        save_to_db(ticker, short_name, price, safety_score, cash_score, roic, de, gross_margin, fcf_yield, status, reason, val_status, lie_status)

    except Exception as e:
        pass

def get_sp500_tickers():
    """Scrapes Wikipedia for the current S&P 500 list."""
    try:
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        df = pd.read_html(StringIO(requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).text))[0]
        return df['Symbol'].str.replace('.', '-', regex=False).tolist()
    except:
        return ["AAPL", "MSFT", "GOOG", "AMZN", "NVDA", "TSLA"]

# ==========================================
# ▶️ EXECUTION
# ==========================================
if __name__ == "__main__":
    start_time = time.time()
    
    tickers = get_sp500_tickers()
    print(f"\n--- ELITE SCANNING {len(tickers)} ASSETS (Cache: {CACHE_DURATION_DAYS} days) ---")
    
    # Using 4 workers is safer to avoid segmentation faults on local machines
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(analyze_stock, tickers)
        
    end_time = time.time()
    elapsed = end_time - start_time
    
    print("-" * 40)
    print(f"✅ DONE. Scanned {len(tickers)} stocks in {elapsed:.2f} seconds.")
    print(f"⚡ Speed: {len(tickers)/elapsed:.2f} stocks/sec")
    print("-" * 40)