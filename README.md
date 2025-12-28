# 📉 The Buffett Bot

### S&P 500 Quality & Cash-Flow Scanner

> **Markets are noisy. Cash flow is fact.**

**The Buffett Bot** is a high-performance fundamental scanner that automates Warren Buffett–style quality investing.  
It ignores narratives, price action, and hype — and instead subjects the **entire S&P 500** to a strict, cash-flow-driven stress test.

Only businesses with **strong economics, clean balance sheets, and real cash generation** survive.

* * *

## 🧠 Investment Philosophy

This project is built on three non-negotiables:

1.  **Quality beats stories**
    
2.  **Cash flow > accounting earnings**
    
3.  **Great businesses are rare**
    

The scanner enforces these principles mechanically — no discretion, no bias.

* * *

## 📊 Dashboard Preview

![Dashboard Preview](https://via.placeholder.com/800x400/0A0C10/00D185?text=DASHBOARD+PREVIEW)

> Replace this image with a screenshot of your actual PHP dashboard.

* * *

## ⚡ Engineering Alpha — Core Features

This is not a basic screener. It is a **production-grade data pipeline** optimized for speed, accuracy, and financial rigor.

### 🚀 Performance

*   **Multi-threaded scanning** using `concurrent.futures`
    
*   Processes **500+ stocks in under 60 seconds**
    

### 🧠 Smart Caching

*   Local MySQL cache prevents redundant API calls
    
*   Fundamental data cached for **7 days** (quarterly relevance)
    

### 🕵️ Accounting Lie Detector

*   Flags companies where **Net Income ≫ Free Cash Flow**
    
*   Identifies earnings manipulation and low-quality profits
    

### 💎 The “Elite” Filter (98% Rejection Rate)

Only companies that pass all of the following survive:

*   **Pricing Power:** Gross Margin > **45%**
    
*   **Capital Efficiency:** ROIC > **25%**
    
*   **Balance Sheet Safety:** Debt-to-Equity < **0.5**
    
*   **Valuation Discipline:** Minimum Free Cash Flow Yield
    

### 📊 Dashboard

*   Dark-mode PHP dashboard
    
*   Built with **Tailwind CSS**
    
*   Zero bloat, zero JavaScript frameworks
    
*   Focused on decision-grade information only
    

* * *

## 🛠️ Tech Stack

**Backend**

*   Python **3.10+**
    
*   `yfinance`
    
*   `pandas`, `numpy`
    
*   MySQL
    

**Frontend**

*   PHP **8.0+**
    
*   Tailwind CSS (CDN)
    

* * *

## ⚙️ Installation & Setup

### 1️⃣ Database Setup

You need a local MySQL instance running.

Create the database and table using the provided SQL file:

`mysql -u root -p < database_setup.sql`

This creates:

*   Database: `investor_dashboard`
    
*   Table: `stocks`
    

* * *

### 2️⃣ Python Dependencies

Install required libraries:

`pip install yfinance mysql-connector-python pandas requests numpy`

* * *

### 3️⃣ Configure Database Connection

Open `market_scanner.py` and update the database credentials:

`DB_CONFIG = {     "host": "localhost",     "user": "your_username",     "password": "your_password",     "database": "investor_dashboard",     "port": 3306 }`

* * *

### 4️⃣ Run the Scanner

Execute the scanner:

`python market_scanner.py`

Expected output:

*   🟥 **REJECTED** — failed one or more quality checks
    
*   🟩 **SURVIVOR** — elite business, passed all filters
    

* * *

### 5️⃣ Launch the Dashboard

Serve the PHP dashboard locally:

`php -S localhost:8000`

Open in browser:

`http://localhost:8000`

* * *

## 🎛️ Configuration — “God Mode”

You control the strictness of the scanner from the top of `market_scanner.py`:

`# ELITE QUALITY FILTERS  MIN_GROSS_MARGIN = 45.0      # Pricing power requirement MIN_ROIC = 25.0              # Capital efficiency requirement MAX_DEBT_TO_EQUITY = 0.5     # Balance sheet safety MIN_FCF_YIELD = 5.0          # Valuation floor (5% = ~20x P/FCF)`

Tighten these → fewer survivors  
Loosen them → more compromises

* * *

## ⚠️ Disclaimer

This project is **for educational and analytical purposes only**.

*   Not financial advice
    
*   No guarantees
    
*   Based on historical financial data
    
*   Assumes clean source data
    

Always perform your own due diligence before investing.

* * *

## 🧱 Database Schema

### 📂 `database_setup.sql`

Create this file in your repository:

`CREATE DATABASE IF NOT EXISTS investor_dashboard; USE investor_dashboard;  CREATE TABLE IF NOT EXISTS stocks (     ticker VARCHAR(10) PRIMARY KEY,     company_name VARCHAR(255),     price DECIMAL(10, 2),      safety_score INT,     cash_engine_score INT,      roic_current DECIMAL(10, 2),     debt_to_equity DECIMAL(10, 2),     gross_margin_3yr_avg DECIMAL(10, 2),     fcf_yield DECIMAL(10, 2),      status VARCHAR(20),              -- SURVIVOR | REJECTED     failure_reasons TEXT,      valuation_status VARCHAR(20),    -- BARGAIN | FAIR | PRICEY     lie_detector_status VARCHAR(20), -- VERIFIED | SUSPICIOUS      updated_at DATETIME DEFAULT CURRENT_TIMESTAMP );`

* * *

## 🧠 Author

**Built by Code & Capital**  
Follow the math. Ignore the narrative.
