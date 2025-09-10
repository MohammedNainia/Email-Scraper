# Email Scraper for Outreach

## Overview
A simple Python script that automates collecting contact emails from websites.  
It visits each target site, looks for **Contact / Partnership / Press** pages, extracts emails, removes duplicates, and saves them into a clean CSV.  
Optionally, the script can email the results automatically using SMTP.

---

## Features
- Reads targets from a CSV file (`targets.csv`)  
- Crawls websites and follows likely contact/partnership links  
- Extracts valid emails (ignores `noreply` or similar)  
- Removes duplicates and outputs a clean `emails.csv`  
- Sends results by email if SMTP is configured  

---

## Requirements
- Python 3.9+  
- [Playwright](https://playwright.dev/python/)  
- pandas  
- python-dotenv  

Install dependencies with:

```bash
pip install -r requirements.txt

**## Setup**
Create a .env file in the project root with your SMTP credentials:
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASS=your_app_password
MAIL_TO=recipient@email.com

Prepare a targets.csv with at least two columns:

brand,url
Brand A,https://example.com
Brand B,https://anotherexample.com
