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