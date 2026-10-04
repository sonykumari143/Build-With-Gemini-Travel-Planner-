"""Public API tools for travel information and currency conversion."""

import json
import os
import urllib.parse
import urllib.request


def get_destination_public_holidays(country_code: str, year: int = 2026) -> str:
    """Fetch official public holidays for a travel destination country using Nager.Date Public API.

    Args:
        country_code: Two-letter ISO country code (e.g. 'JP' for Japan, 'FR' for France, 'US' for USA, 'GB' for UK).
        year: Calendar year (defaults to 2026).

    Returns:
        JSON string listing the public holidays, dates, and local names.
    """
    try:
        code = country_code.strip().upper()
        url = f"https://date.nager.at/api/v3/PublicHolidays/{year}/{code}"
        
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            
        holidays = [
            {
                "date": h.get("date"),
                "name": h.get("name"),
                "localName": h.get("localName")
            }
            for h in data
        ]
        return json.dumps({"countryCode": code, "year": year, "holidays": holidays}, indent=2)
    except Exception as e:
        return f"Error fetching public holidays for {country_code}: {str(e)}"


def get_currency_exchange_rates(base_currency: str = "USD", target_currencies: str = "JPY,EUR,GBP") -> str:
    """Fetch live foreign exchange rates for travelers using Frankfurter Open API.

    Args:
        base_currency: Base currency code (e.g. 'USD', 'EUR', 'GBP').
        target_currencies: Comma-separated target currency codes (e.g. 'JPY,EUR,GBP').

    Returns:
        JSON string of exchange rates.
    """
    try:
        base = base_currency.strip().upper()
        targets = target_currencies.strip().upper()
        
        # Check optional environment variable for custom API endpoint
        api_host = os.getenv("EXCHANGE_RATE_API_HOST", "api.frankfurter.app")
        url = f"https://{api_host}/latest?from={base}&to={targets}"
        
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            
        return json.dumps(data, indent=2)
    except Exception as e:
        return f"Error fetching currency exchange rates: {str(e)}"
