import os
import re
import requests
import zipfile
from bs4 import BeautifulSoup

# Path to the downloaded index.htm
INDEX_FILE = "index.htm"
# Base URL for the zip files (adjust if needed)
BASE_URL = "https://www.psp.cz/eknih/2021ps/stenprot/zip/"
# Output directory for the downloaded zips and extracted files
OUT_DIR = "parliament_transcripts_zips"
EXTRACT_DIR = "parliament_transcripts"

os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(EXTRACT_DIR, exist_ok=True)


with open(INDEX_FILE, "r", encoding="windows-1250", errors="replace") as f:
    soup = BeautifulSoup(f, "html.parser")

# Find all zip links for sessions >= 127
zip_links = []
for a in soup.find_all("a", href=True):
    m = re.match(r"(\d+)schuz\.zip", a["href"])
    if m:
        session_num = int(m.group(1))
        if session_num >= 126:
            zip_links.append((session_num, a["href"]))

print(f"Found {len(zip_links)} zip links for sessions >= 127:")
for session_num, href in zip_links:
    print(f"  Session {session_num}: {href}")

# Download and extract each zip
for session_num, href in zip_links:
    zip_url = BASE_URL + href
    zip_path = os.path.join(OUT_DIR, href)
    session_prefix = f"{session_num}schuz"
    expected_files_exist = any(
        fname.startswith(session_prefix) for fname in os.listdir(EXTRACT_DIR)
    )
    if os.path.exists(zip_path):
        if expected_files_exist:
            print(f"Already downloaded {zip_path} and extracted, skipping.")
            continue
        else:
            print(f"Already downloaded {zip_path}, but not extracted. Extracting...")
    else:
        print(f"Downloading {zip_url} ...")
        try:
            r = requests.get(zip_url, stream=True, timeout=30)
            if r.status_code == 200:
                with open(zip_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"Downloaded {zip_path}.")
            else:
                print(f"Failed to download {zip_url} (status {r.status_code})")
                continue
        except Exception as e:
            print(f"Error downloading {zip_url}: {e}")
            continue
    print(f"Extracting {zip_path} ...")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(EXTRACT_DIR)
        print(f"Extracted {zip_path}.")
    except Exception as e:
        print(f"Error extracting {zip_path}: {e}")
print("Done.")
