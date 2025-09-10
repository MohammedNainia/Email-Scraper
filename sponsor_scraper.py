import re
import time
import csv
import os
import smtplib
import pandas as pd
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

# Selectors to look for clickable Contact/Press/Partnership buttons/links
CONTACT_SELECTORS = [
    "a:has-text('Contact Us')",
    "a:has-text('Contact')",
    "a:has-text('Press')",
    "a:has-text('Media')",
    "a:has-text('PR')",
    "a:has-text('Partnership')",
    "a:has-text('Partner')",
    "a:has-text('Creators')",
    "button:has-text('Contact')",
    "a[aria-label*='Contact' i]",
    "a[href*='contact' i]",
    "a[href*='press' i]",
    "a[href*='media' i]",
    "a[href*='partner' i]",
    "a[href*='creator' i]",
]

EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE)


def send_email(smtp_host, smtp_port, smtp_user, smtp_pass, to_addr, csv_path, found_count):
    """Send the results CSV via SMTP"""
    msg = MIMEMultipart()
    msg["From"] = smtp_user
    msg["To"] = to_addr
    msg["Subject"] = f"[Sponsorship Bot] {found_count} emails found"

    body = MIMEText(f"Attached are {found_count} deduped emails scraped from targets.\nFile: {os.path.basename(csv_path)}", "plain")
    msg.attach(body)

    with open(csv_path, "rb") as f:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(f.read())
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", f'attachment; filename="{os.path.basename(csv_path)}"')
    msg.attach(part)

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_user, [to_addr], msg.as_string())


def crawl_targets(csv_file="targets.csv", out_csv="emails.csv", delay=2.5, click_timeout=6000):
    """Visit each target, click contact buttons, extract emails"""
    df = pd.read_csv(csv_file)
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
        ))
        page = ctx.new_page()

        for i, row in df.iterrows():
            brand = str(row.get("brand", "")).strip()
            url = str(row.get("url", "")).strip()
            print(f"[{i+1}/{len(df)}] {brand} → {url}")

            try:
                page.goto(url, timeout=30000, wait_until="domcontentloaded")
                page.wait_for_timeout(1500)  # let JS render

                # Try clicking any likely contact element
                for sel in CONTACT_SELECTORS:
                    try:
                        el = page.locator(sel).first
                        if el.count() and el.is_visible():
                            with page.expect_navigation(timeout=click_timeout):
                                el.click()
                            page.wait_for_timeout(1200)
                            break
                    except Exception:
                        continue

                content = page.content()
                text_blob = ""
                try:
                    text_blob = page.inner_text("body")
                except Exception:
                    pass

                emails = set(EMAIL_RE.findall(content)) | set(EMAIL_RE.findall(text_blob))
                filtered = {e for e in emails if not any(bad in e.lower() for bad in ["noreply@", "no-reply@", "donotreply@"])}

                for e in sorted(filtered):
                    results.append({"brand": brand, "source": page.url, "email": e})

                time.sleep(delay)
            except Exception as e:
                print(f"  !! error for {brand}: {e}")
                continue

        browser.close()

    # Dedupe by email
    deduped = {}
    for r in results:
        deduped[r["email"].lower()] = r
    out_rows = list(deduped.values())

    os.makedirs(os.path.dirname(out_csv) or ".", exist_ok=True)
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["brand", "source", "email"])
        writer.writeheader()
        writer.writerows(out_rows)

    print(f"Saved {len(out_rows)} unique emails → {out_csv}")
    return out_csv, len(out_rows)


if __name__ == "__main__":
    load_dotenv()
    csv_path, count = crawl_targets(csv_file="targets.csv", out_csv="emails.csv")

    SMTP_HOST = os.getenv("SMTP_HOST")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER")
    SMTP_PASS = os.getenv("SMTP_PASS")
    MAIL_TO   = os.getenv("MAIL_TO")

    if all([SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, MAIL_TO]):
        send_email(SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, MAIL_TO, csv_path, count)
        print(f"Emailed results to {MAIL_TO}")
    else:
        print("SMTP env not set; skipped emailing. (Results saved locally)")
