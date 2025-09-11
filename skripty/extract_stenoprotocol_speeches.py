import re
from bs4 import BeautifulSoup

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

    # 1. Find all <b><a>author</a></b> tags as speech starts (standard case)
    nodes = list(p.descendants)
    i = 0
    found_any_author = False
    while i < len(nodes):
        node = nodes[i]
        if getattr(node, "name", None) == "b" and node.find("a") is not None:
            found_any_author = True
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
                        speech_parts.append(text)
                j += 1
            speech = " ".join(speech_parts).strip()
            if speech:
                speeches.append({
                    "author": author,
                    "speech": speech
                })
            i = j
        else:
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

# Example usage:
if __name__ == "__main__":
    with open("s127003.htm", "r", encoding="windows-1250") as f:
        html = f.read()
    speeches = extract_speeches_from_html(html)
    for s in speeches:
        print(f"AUTHOR: {s['author']}\nSPEECH: {s['speech']}\n{'-'*40}")