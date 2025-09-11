# Politician Speech Extractor

This script extracts all speeches from a specific politician from the parliament speech files.

## Usage

```bash
python extract_politician_speeches.py "Politician Name"
```

## Examples

```bash
# Extract all speeches by Andrej Babiš
python extract_politician_speeches.py "Andrej Babiš"

# Extract all speeches by Markéta Pekarová Adamová  
python extract_politician_speeches.py "Markéta Pekarová Adamová"

# Partial name matching also works
python extract_politician_speeches.py "Fiala"

# Save speeches to a file
python extract_politician_speeches.py "Andrej Babiš" > babis_speeches.txt

# Save only the speeches (without debug info) to a file
python extract_politician_speeches.py "Andrej Babiš" 2>/dev/null > babis_speeches.txt
```

## Output Format

The script outputs speeches in the requested format:
- Each speech as plain text
- Speeches separated by a single empty line
- No metadata, just the speech content

## Features

- **Flexible name matching**: Works with full names, partial names, and handles Czech diacritics
- **Comprehensive search**: Searches across all available parliamentary sessions (126-146)
- **Clean output**: Removes titles, speaker prefixes, and formatting metadata
- **Error handling**: Gracefully handles missing files and encoding issues

## Technical Details

The script:
1. Searches all session directories (126/, 127/, 128/, etc.)
2. Parses each speech file format (File, Anchor, Date, Speaker, Speech)
3. Normalizes names for comparison (removes diacritics, handles case)
4. Extracts only the speech content, removing metadata
5. Outputs speeches in chronological order

The name matching is flexible and handles:
- Full names: "Andrej Babiš"
- Partial names: "Babiš" or "Fiala" 
- Multiple words: All words must match somewhere in the speaker name
- Czech diacritics: Automatically normalized for matching
- Titles: Automatically removed (Poslanec, Předseda, Ministr, etc.)
