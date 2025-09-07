import os
import re
import time
import json
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict
import requests
from bs4 import BeautifulSoup

# --- Extractor logic (NEW VERSION, as discussed) ---
def extract_speeches_from_html(html_content):
    """
    Extracts speeches and their authors from given stenoprotocol HTML content, including cases
    where only a narrative or continuation marker is present instead of <b><a> tags.
    Returns:
        List of dicts: [{ "author": author_name, "speech": text }]
    """
    soup = BeautifulSoup(html_content, "html.parser")
    speeches = []

    # Try to find the main content div
    p = soup.find("div", {"id": "main-content"})
    if p is None:
        p = soup  # fallback: whole document

    # 1. Find all <b><a>author</a></b> tags as speech starts (standard case),
    # but also parse <p> for speaker labels like "Poslanec ... :"
    nodes = list(p.descendants)
    i = 0
    speaker_label_re = re.compile(r"^(Místopředseda PSP|Předseda PSP|Poslanec|Poslankyně|Ministr|Ministryně|Zpravodaj|Zpravodajka|Předsedající|Místopředsedkyně PSP) ([^:]+) ?: ?", re.UNICODE)
    while i < len(nodes):
        node = nodes[i]
        # Standard case: <b><a> tag
        if getattr(node, "name", None) == "b" and node.find("a") is not None:
            author_tag = node.find("a")
            author = author_tag.get_text(strip=True)
            speech_parts = []
            j = i + 1
            while j < len(nodes):
                n = nodes[j]
                if getattr(n, "name", None) == "b" and n.find("a") is not None:
                    break
                if getattr(n, "name", None) == "p":
                    text = n.get_text(" ", strip=True)
                    if text:
                        # Check for speaker label at start of paragraph
                        m = speaker_label_re.match(text)
                        if m:
                            real_author = m.group(1) + " " + m.group(2)
                            speech_text = text[m.end():].strip()
                            if speech_text:
                                speeches.append({"author": real_author, "speech": speech_text})
                        else:
                            speech_parts.append(text)
                j += 1
            # If no speaker label found, treat as speech by <b><a> author
            speech = " ".join(speech_parts).strip()
            if speech:
                speeches.append({"author": author, "speech": speech})
            i = j
        else:
            # Also handle paragraphs outside <b><a> blocks that start with speaker label
            if getattr(node, "name", None) == "p":
                text = node.get_text(" ", strip=True)
                m = speaker_label_re.match(text)
                if m:
                    real_author = m.group(1) + " " + m.group(2)
                    speech_text = text[m.end():].strip()
                    if speech_text:
                        speeches.append({"author": real_author, "speech": speech_text})
            i += 1

    # 2. Handle case: Only narrative/continuation marker, like (pokračuje Andrej Babiš)
    # Look for plain text or <br> with "(pokračuje ...)" and then paragraphs
    if not speeches:
        # Try to find a marker with "(pokračuje SOMEONE)" or "(pokračuje: SOMEONE)" (with or without diacritics)
        # Also handle cases with <br>(pokračuje Andrej Babiš)<br>
        marker_re = re.compile(r"\(pokra[čc]uje[:]? ([^)]+)\)", re.IGNORECASE)
        # Find all text nodes in order
        for idx, node in enumerate(nodes):
            if isinstance(node, str):
                m = marker_re.search(node)
                if m:
                    author = m.group(1).strip()
                    # Collect following <p> tags as speech
                    speech_parts = []
                    for n2 in nodes[idx+1:]:
                        if getattr(n2, "name", None) == "p":
                            text = n2.get_text(" ", strip=True)
                            if text:
                                speech_parts.append(text)
                        # Stop on next marker or nav
                        elif isinstance(n2, str) and marker_re.search(n2):
                            break
                        elif getattr(n2, "name", None) == "div" and "document-nav" in n2.get("class", []):
                            break
                    speech = " ".join(speech_parts).strip()
                    if speech:
                        speeches.append({
                            "author": author,
                            "speech": speech
                        })
                    break  # Only handle first found, unless multiple continuation markers per page

    return speeches

# --- Crawler logic (unchanged except for extractor call) ---

BASE_URL = "https://www.psp.cz/eknih/2021ps/stenprot/{session_id}/s{session_num}{part:03d}.htm"
DATA_DIR = "parliament_transcripts"
SPEECHES_DIR = "parliament_speeches"
STATE_FILE = "crawler_state.json"
MAX_THREADS = 8  # Adjust for your system/network

def ensure_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(SPEECHES_DIR, exist_ok=True)

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {}

def download_transcript(session_num: int, part: int) -> str:
    session_id = f"{session_num}schuz"
    url = BASE_URL.format(session_id=session_id, session_num=session_num, part=part)
    local_file = os.path.join(DATA_DIR, f"{session_id}_s{session_num}{part:03d}.htm")

    if os.path.exists(local_file):
        with open(local_file, "r", encoding="windows-1250", errors="replace") as f:
            return f.read()
    max_retries = 5
    backoff = 2  # seconds
    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200 and "html" in resp.headers.get("Content-Type", ""):
                with open(local_file, "w", encoding="windows-1250", errors="replace") as f:
                    f.write(resp.text)
                return resp.text
            else:
                print(f"Non-200 or non-HTML response for {url} (status: {resp.status_code})")
                return ""
        except Exception as e:
            print(f"Attempt {attempt} failed to download {url}: {e}")
            if attempt < max_retries:
                sleep_time = backoff * (2 ** (attempt - 1))
                print(f"Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
            else:
                print(f"Giving up on {url} after {max_retries} attempts.")
                return ""

def save_speeches_for_session(session_num, all_speeches):
    out_file = os.path.join(SPEECHES_DIR, f"s{session_num}.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(all_speeches, f, ensure_ascii=False, indent=2)

def crawl_session(session_num, state, lock):
    print(f"Starting crawl for session {session_num}")
    part = 1
    session_id = f"{session_num}schuz"
    all_speeches = []
    while True:
        transcript_key = f"{session_id}_s{session_num}{part:03d}"
        if state.get(transcript_key) == "done":
            part += 1
            continue
        html = download_transcript(session_num, part)
        if not html:
            # Stop if we get a 404 or empty (assuming no gaps in part numbers)
            break
        speeches = extract_speeches_from_html(html)
        all_speeches.extend(speeches)
        with lock:
            state[transcript_key] = "done"
            save_state(state)
        part += 1
    save_speeches_for_session(session_num, all_speeches)
    print(f"Completed crawl for session {session_num}")

def main(start_session=127, end_session=None):
    ensure_dirs()
    state = load_state()
    lock = threading.Lock()
    # Optionally, set end_session for a limit; otherwise, crawl up to the latest available.
    # For this script, let's crawl up to session 130 by default for demonstration.
    # You can set end_session=None to crawl "forever".
    if end_session is None:
        end_session = start_session + 3
    # One thread per session, each session serially crawls its parts
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = []
        for session_num in range(start_session, end_session + 1):
            futures.append(executor.submit(crawl_session, session_num, state, lock))
        for fut in as_completed(futures):
            fut.result()  # raises if any thread failed

if __name__ == "__main__":
    main()