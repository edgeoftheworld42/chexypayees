import string
import time
import requests
import csv

# ========== CONFIGURATION ==========
API_URL = "https://app.chexy.co/api/billpay/fetch"
CHARSET = string.ascii_lowercase + string.digits
PAGE_SIZE = 10
MAX_DEPTH = 6           # stop at this prefix length, just in case
REQUEST_DELAY = 0.2     # seconds between requests
# ====================================

def fetch_payees(prefix):
    """Call the API with a prefix and return payee list."""
    try:
        response = requests.get(API_URL, params={"query": prefix})
        response.raise_for_status()
        data = response.json()
        return data.get("data", [])
    except Exception as e:
        print(f"[ERROR] prefix={prefix!r}: {e}")
        return []

def crawl_prefix(prefix, seen):
    """Recursively crawl the prefix space using depth-first logic."""
    results = fetch_payees(prefix)
    
    # Add results to seen (dedupe by ID)
    for payee in results:
        seen[payee["id"]] = payee

    print(f"Prefix '{prefix}' → {len(results)} results (Total: {len(seen)})")

    # If full page returned and we haven't hit max depth, keep going deeper
    if len(results) == PAGE_SIZE and len(prefix) < MAX_DEPTH:
        for char in CHARSET:
            crawl_prefix(prefix + char, seen)

def crawl_all():
    """Start the crawl with one character at a time."""
    seen = {}

    for char in CHARSET:
        crawl_prefix(char, seen)

    return seen

def save_to_csv(payees, filename="chexy_payees.csv"):
    """Write discovered payees to a CSV file."""
    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "name"])
        writer.writeheader()
        for payee in payees.values():
            writer.writerow(payee)
    print(f"\n✅ Saved {len(payees)} payees to {filename}")

def main():
    print("🔍 Starting smart prefix crawl...")
    payees = crawl_all()
    save_to_csv(payees)

if __name__ == "__main__":
    main()
