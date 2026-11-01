
from pathlib import Path
from urllib.parse import urljoin
from zipfile import ZipFile, BadZipFile
import re
import time
import requests
from bs4 import BeautifulSoup

BASE = "https://www.fhwa.dot.gov/bridge/nbi/"
RAW = Path("data/raw")
RAW.mkdir(parents=True, exist_ok=True)

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})

def valid_zip(path):
    try:
        with ZipFile(path) as z:
            return bool(z.namelist()) and z.testzip() is None
    except (BadZipFile, OSError):
        return False

def find_download_url(year):
    page_url = f"{BASE}ascii{year}.cfm"
    response = session.get(page_url, timeout=60)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Find the "Delimited Files" section.
    headings = soup.find_all(
        re.compile(r"^h[1-6]$")
    )

    heading = next(
        (
            h for h in headings
            if "delimited files" in h.get_text(
                " ", strip=True
            ).lower()
        ),
        None
    )

    if heading is None:
        raise ValueError("Delimited Files section not found")

    # Search only after the Delimited Files heading.
    for element in heading.next_elements:
        if getattr(element, "name", None) in (
            "h2", "h3"
        ):
            break

        if getattr(element, "name", None) != "a":
            continue

        href = element.get("href", "")
        if "nbiYear=" not in href:
            continue

        # Check the surrounding text for the single-file option.
        parent = element.parent
        description = parent.get_text(" ", strip=True).lower()

        if "in a single file" in description:
            disclaimer_url = urljoin(page_url, href)

            disclaimer = session.get(
                disclaimer_url, timeout=60
            )
            disclaimer.raise_for_status()

            disclaimer_soup = BeautifulSoup(
                disclaimer.text, "html.parser"
            )

            proceed = disclaimer_soup.find(
                "a", string=re.compile(
                    "Proceed to Data", re.I
                )
            )

            if proceed is None:
                raise ValueError("Proceed to Data link missing")

            return urljoin(
                disclaimer_url, proceed["href"]
            )

    raise ValueError("Single-file download link not found")

def download_year(year):
    destination = RAW / f"nbi_{year}.zip"
    temporary = RAW / f"nbi_{year}.part"

    if destination.exists() and valid_zip(destination):
        print(f"{year}: already downloaded")
        return True

    try:
        url = find_download_url(year)
        print(f"{year}: downloading from {url}")

        with session.get(
            url, stream=True, timeout=(30, 180)
        ) as response:
            response.raise_for_status()

            with open(temporary, "wb") as file:
                for chunk in response.iter_content(
                    chunk_size=1024 * 1024
                ):
                    if chunk:
                        file.write(chunk)

        if not valid_zip(temporary):
            raise ValueError("Downloaded file is not a valid ZIP")

        temporary.replace(destination)
        print(f"{year}: SUCCESS")
        return True

    except Exception as error:
        print(f"{year}: FAILED - {error}")
        temporary.unlink(missing_ok=True)
        return False

failed = []

for year in range(1992, 2026):
    if not download_year(year):
        failed.append(year)
    time.sleep(1)

print("\nFinished.")
print("Failed years:", failed)
