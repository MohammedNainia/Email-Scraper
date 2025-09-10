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
