# 📉 The Buffett Bot (S&P 500 Quality Scanner)

> "Markets are random. Cash flow is fact."

**A high-performance algorithmic scanner that automates Warren Buffett's core investing principles.** This project rejects the "hype" of the stock market. Instead, it subjects the S&P 500 to a ruthless, mathematical stress test—filtering companies based on Return on Invested Capital (ROIC), Balance Sheet Safety, and Pricing Power.

![Dashboard Preview](https://via.placeholder.com/800x400/0A0C10/00D185?text=DASHBOARD+PREVIEW)
*(Replace this link with a screenshot of your actual PHP Dashboard)*

---

## ⚡ Engineering Alpha: Features

This isn't just a basic screener. It is an optimized data pipeline designed for **speed** and **financial rigor**.

* **🚀 Multi-Threaded Scanning:** Analyzes 500+ stocks in under 60 seconds using Python `concurrent.futures`.
* **🧠 Smart Caching:** Implements a local database cache to prevent redundant API calls. Fundamental data (which changes quarterly) is stored for 7 days.
* **🕵️ The Accounting Lie Detector:** Automatically flags companies where **Net Income** (Accounting Profit) is significantly higher than **Free Cash Flow** (Real Cash).
* **💎 The "Elite" Filter:** A hard-coded gauntlet that rejects 98% of stocks based on:
    * **Moat:** Gross Margins > 45%
    * **Engine:** ROIC > 25%
    * **Safety:** Debt-to-Equity < 0.5
* **📊 Dark Mode Dashboard:** A clean, bloat-free PHP interface built with Tailwind CSS to visualize the "Survivors."

---

## 🛠️ Tech Stack

* **Core Logic:** Python 3.10+
* **Data Source:** Yahoo Finance (`yfinance`)
* **Database:** MySQL
* **Frontend:** PHP 8.0+, Tailwind CSS (CDN)

---

## ⚙️ Installation & Setup

### 1. Database Setup
You need a local MySQL instance running. Create a database named `investor_dashboard` and run the included SQL script (see `database_setup.sql`) to create the `stocks` table.

### 2. Python Dependencies
Install the required libraries:
```bash
pip install yfinance mysql-connector-python pandas requests numpy

3. Configure Database Connection
Open market_scanner.py and update the DB_CONFIG dictionary with your local credentials:

Python

DB_CONFIG = {
    'host': 'localhost',
    'user': 'your_username', 
    'password': 'your_password',
    'database': 'investor_dashboard',
    'port': 3306 # Default MySQL port
}
4. Run the Scanner
Execute the Python script to fetch data and populate the database:

Bash

python market_scanner.py
You will see the terminal light up with red (REJECTED) and green (SURVIVOR) logs.

5. Launch the Dashboard
Serve the index.php file using a local PHP server (XAMPP, MAMP, or built-in PHP):

Bash

php -S localhost:8000
Open your browser to http://localhost:8000.

🎛️ Configuration (God Mode)
You can tweak the strictness of the "Buffett Bot" by modifying the constants at the top of market_scanner.py:

Python

# THE "ELITE" FILTERS
MIN_GROSS_MARGIN = 45.0     # Pricing power requirement
MIN_ROIC = 25.0             # Management efficiency requirement
MAX_DEBT_TO_EQUITY = 0.5    # Leverage limit
MIN_FCF_YIELD = 5.0         # Valuation floor (5% = 20x P/FCF)
⚠️ Disclaimer
This software is for educational purposes only. The code provided here is a tool for analysis, not financial advice. The "Survivors" list is generated based on historical data and specific programmed criteria. Always conduct your own due diligence before making investment decisions.

Built by [Your Name / Code & Capital] Follow the math, not the narrative.


***

### 📂 Bonus: `database_setup.sql`

Your users will need this file to create the database table that matches your Python code perfectly. Create a new file named `database_setup.sql` and include this in your repo:

```sql
CREATE DATABASE IF NOT EXISTS investor_dashboard;
USE investor_dashboard;

CREATE TABLE IF NOT EXISTS stocks (
    ticker VARCHAR(10) PRIMARY KEY,
    company_name VARCHAR(255),
    price DECIMAL(10, 2),
    safety_score INT,
    cash_engine_score INT,
    roic_current DECIMAL(10, 2),
    debt_to_equity DECIMAL(10, 2),
    gross_margin_3yr_avg DECIMAL(10, 2),
    fcf_yield DECIMAL(10, 2),
    status VARCHAR(20), -- 'SURVIVOR' or 'REJECTED'
    failure_reasons TEXT,
    valuation_status VARCHAR(20), -- 'BARGAIN', 'FAIR', 'PRICEY'
    lie_detector_status VARCHAR(20), -- 'VERIFIED' or 'SUSPICIOUS'
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);