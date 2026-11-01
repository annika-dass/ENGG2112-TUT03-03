
from pathlib import Path
from zipfile import ZipFile, BadZipFile
import re

raw_folder = Path("data/raw")

zip_files = sorted(raw_folder.glob("*.zip"))

print(f"Total ZIP files found: {len(zip_files)}")
print("-" * 60)

years_found = set()

for path in zip_files:
    year_match = re.search(r"(19\d{2}|20\d{2})", path.name)

    if year_match:
        years_found.add(int(year_match.group()))

    try:
        with ZipFile(path) as archive:
            names = archive.namelist()
            valid = archive.testzip() is None

            print(f"\n{path.name}")
            print(f"  Valid ZIP: {valid}")
            print(f"  Files inside: {len(names)}")

            for name in names[:3]:
                print(f"    {name}")

    except BadZipFile:
        print(f"\n{path.name}: INVALID ZIP")

expected_years = set(range(1992, 2026))
missing = sorted(expected_years - years_found)

print("\n" + "=" * 60)
print(f"Years found: {len(years_found)}")
print(f"Missing years: {missing}")
print("=" * 60)
