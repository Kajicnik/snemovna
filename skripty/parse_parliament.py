import requests
import os
import re
from bs4 import BeautifulSoup
from pathlib import Path

def decode_html(html_bytes):
    return html_bytes.decode('windows-1250', errors='replace')

TRANSCRIPT_DIR = 'parliament_transcripts'
OUTPUT_BASE = 'parliament_speeches'

def get_session_number(fname):
    # e.g. 126-1.htm -> 126
    return fname.split('-')[0]

def extract_session_date(title):
    # Extract date from title (e.g., '15. ledna 2025')
    m = re.search(r'(\d{1,2}\..*?\d{4})', title)
    return m.group(1) if m else 'Unknown'

def parse_session_overview(session_overview_path):
    with open(session_overview_path, 'rb') as f:
        soup = BeautifulSoup(decode_html(f.read()), 'html.parser')
    title = soup.find('title').text
    session_date = extract_session_date(title)
    speech_map = {}
    for a in soup.find_all('a', href=True):
        href = a['href']
        if href.startswith('s') and '.htm#' in href:
            file_anchor = href.split('.htm#')
            filename = file_anchor[0] + '.htm'
            anchor = file_anchor[1]
            name = a.text.strip()
            speech_map[(filename, anchor)] = name
    return session_date, speech_map

def extract_speech_from_transcript(transcript_path, anchor):
    with open(transcript_path, 'rb') as f:
        tsoup = BeautifulSoup(decode_html(f.read()), 'html.parser')
    tag = tsoup.find(id=anchor)
    if not tag:
        return ''
    p = tag
    while p and p.name != 'p':
        p = p.parent
    if not p:
        return ''
    speech_parts = []
    current = p
    while current:
        anchor_in_p = current.find('a', id=True)
        if anchor_in_p and anchor_in_p != tag:
            break
        speech_parts.append(current.get_text(strip=True))
        next_sib = current.find_next_sibling()
        if not next_sib or next_sib.name != 'p':
            break
        anchor_in_next = next_sib.find('a', id=True)
        if anchor_in_next:
            break
        current = next_sib
    return '\n'.join(speech_parts)

def main():
    # Find all session overview files (e.g., 126-1.htm, 126-2.htm, ...)
    all_files = os.listdir(TRANSCRIPT_DIR)
    session_nums = set()
    for f in all_files:
        m = re.match(r'(\d+)-\d+\.htm$', f)
        if m:
            session_nums.add(m.group(1))
    session_nums = sorted(session_nums, key=int)
    for session_num in session_nums:
        # Find all parts for this session (e.g., 127-1.htm, 127-2.htm, ...)
        part_files = sorted([f for f in all_files if re.match(rf'{session_num}-\d+\.htm$', f)], key=lambda x: int(x.split('-')[1].split('.')[0]))
        speech_map = {}
        session_date = None
        for part_file in part_files:
            part_path = os.path.join(TRANSCRIPT_DIR, part_file)
            part_date, part_speech_map = parse_session_overview(part_path)
            if not session_date:
                session_date = part_date
            speech_map.update(part_speech_map)
        output_dir = os.path.join(OUTPUT_BASE, session_num)
        os.makedirs(output_dir, exist_ok=True)
        for (filename, anchor), speaker in speech_map.items():
            transcript_path = os.path.join(TRANSCRIPT_DIR, filename)
            if not os.path.exists(transcript_path):
                # Try to download the file from PSP website
                m = re.match(r's(\d{3})(\d{3})\.htm$', filename)
                if m:
                    session = m.group(1)
                    part = m.group(2)
                    url = f'https://www.psp.cz/eknih/2021ps/stenprot/{int(session):03d}schuz/s{session}{part}.htm'
                    print(f'Attempting to download missing transcript: {filename} from {url}')
                    try:
                        resp = requests.get(url, timeout=10)
                        if resp.status_code == 200:
                            with open(transcript_path, 'wb') as f:
                                f.write(resp.content)
                            print(f'Downloaded and saved {filename}')
                        else:
                            print(f'ERROR: Failed to download {filename} (HTTP {resp.status_code})')
                            continue
                    except Exception as e:
                        print(f'ERROR: Exception while downloading {filename}: {e}')
                        continue
                else:
                    print(f'WARNING: Referenced transcript file missing and cannot infer URL: {transcript_path}')
                    continue
            speech = extract_speech_from_transcript(transcript_path, anchor)
            out_name = f'{filename.replace(".htm", "")}_{anchor}.txt'
            out_path = os.path.join(output_dir, out_name)
            if not speech.strip():
                print(f'WARNING: No speech extracted for {filename}#{anchor} (speaker: {speaker})')
            else:
                print(f'Extracted: {out_name}')
            with open(out_path, 'w', encoding='utf-8') as out:
                out.write(f'File: {filename}\nAnchor: {anchor}\nDate: {session_date}\nSpeaker: {speaker}\n\nSpeech:\n{speech}\n')
        print(f'Extraction complete. Output in {output_dir}')

if __name__ == '__main__':
    main()
