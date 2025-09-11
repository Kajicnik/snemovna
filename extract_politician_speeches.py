#!/usr/bin/env python3
"""
Script to extract all speeches from a specific politician from parliament speech files.
Usage: python extract_politician_speeches.py "Politician Name"
"""

import os
import sys
import glob
import re
from pathlib import Path


def extract_speaker_name(line):
    """Extract the clean speaker name from the speaker line."""
    # Remove the double colon and any title prefixes
    if "::" in line:
        speaker_part = line.split("::")[0].strip()
        # Remove common titles and prefixes
        prefixes_to_remove = [
            "Předseda vlády", "Předsedkyně vlády", 
            "Předseda PSP", "Předsedkyně PSP",
            "Místopředseda PSP", "Místopředsedkyně PSP",
            "Poslanec", "Poslankyně",
            "Ministr", "Ministryně",
            "Speaker:", "Předsedající:"
        ]
        
        for prefix in prefixes_to_remove:
            if speaker_part.startswith(prefix):
                speaker_part = speaker_part[len(prefix):].strip()
                break
        
        return speaker_part
    return line.strip()


def normalize_name(name):
    """Normalize name for comparison (remove diacritics, convert to lowercase)."""
    # Simple diacritics removal for Czech names
    diacritics_map = {
        'á': 'a', 'č': 'c', 'ď': 'd', 'é': 'e', 'ě': 'e', 'í': 'i', 
        'ň': 'n', 'ó': 'o', 'ř': 'r', 'š': 's', 'ť': 't', 'ú': 'u', 
        'ů': 'u', 'ý': 'y', 'ž': 'z',
        'Á': 'A', 'Č': 'C', 'Ď': 'D', 'É': 'E', 'Ě': 'E', 'Í': 'I',
        'Ň': 'N', 'Ó': 'O', 'Ř': 'R', 'Š': 'S', 'Ť': 'T', 'Ú': 'U',
        'Ů': 'U', 'Ý': 'Y', 'Ž': 'Z'
    }
    
    normalized = name
    for czech_char, latin_char in diacritics_map.items():
        normalized = normalized.replace(czech_char, latin_char)
    
    return normalized.lower().strip()


def name_matches(speaker_name, target_name):
    """Check if speaker name matches target name (flexible matching)."""
    speaker_normalized = normalize_name(speaker_name)
    target_normalized = normalize_name(target_name)
    
    # Exact match
    if speaker_normalized == target_normalized:
        return True
    
    # Check if all words in target name are in speaker name
    target_words = target_normalized.split()
    speaker_words = speaker_normalized.split()
    
    # If target has multiple words, all must be present in speaker name
    if len(target_words) > 1:
        return all(word in speaker_words for word in target_words)
    
    # Single word target - check if it's in any part of speaker name
    return any(target_normalized in word for word in speaker_words)


def extract_speeches_from_file(file_path, target_politician):
    """Extract speech content from a single file if it matches the target politician."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.strip().split('\n')
        
        # Find the Speaker line
        speaker_line = None
        speech_start_idx = None
        
        for i, line in enumerate(lines):
            if line.startswith("Speaker:"):
                speaker_line = line[8:].strip()  # Remove "Speaker:" prefix
                speech_start_idx = i + 1
                break
        
        if not speaker_line:
            return None
        
        # Extract clean speaker name
        clean_speaker_name = extract_speaker_name(speaker_line)
        
        # Check if this speaker matches our target
        if not name_matches(clean_speaker_name, target_politician):
            return None
        
        # Find the speech content (starts after "Speech:" line)
        speech_content = []
        speech_found = False
        
        for line in lines[speech_start_idx:]:
            if line.strip() == "Speech:":
                speech_found = True
                continue
            elif speech_found:
                speech_content.append(line)
        
        if speech_content:
            # Join the speech content and clean it up
            speech_text = '\n'.join(speech_content).strip()
            
            # Remove the speaker name from the beginning if it's repeated
            if speech_text.startswith(speaker_line):
                speech_text = speech_text[len(speaker_line):].strip()
                if speech_text.startswith("::"):
                    speech_text = speech_text[2:].strip()
            
            return speech_text
        
    except Exception as e:
        print(f"Error processing file {file_path}: {e}", file=sys.stderr)
        return None
    
    return None


def find_all_speeches(base_path, politician_name):
    """Find all speeches by a given politician across all sessions."""
    speeches = []
    
    # Get all session directories
    parliament_speeches_dir = os.path.join(base_path, "parliament_speeches")
    
    if not os.path.exists(parliament_speeches_dir):
        print(f"Error: Parliament speeches directory not found: {parliament_speeches_dir}")
        return speeches
    
    session_dirs = [d for d in os.listdir(parliament_speeches_dir) 
                   if os.path.isdir(os.path.join(parliament_speeches_dir, d)) and d.isdigit()]
    
    session_dirs.sort()
    
    for session_dir in session_dirs:
        session_path = os.path.join(parliament_speeches_dir, session_dir)
        
        # Get all speech files in this session
        speech_files = glob.glob(os.path.join(session_path, "s*.txt"))
        speech_files.sort()
        
        for speech_file in speech_files:
            speech_content = extract_speeches_from_file(speech_file, politician_name)
            if speech_content:
                speeches.append(speech_content)
    
    return speeches


def main():
    if len(sys.argv) != 2:
        print("Usage: python extract_politician_speeches.py \"Politician Name\"")
        print("Example: python extract_politician_speeches.py \"Andrej Babiš\"")
        print("Example: python extract_politician_speeches.py \"Markéta Pekarová Adamová\"")
        sys.exit(1)
    
    politician_name = sys.argv[1]
    base_path = os.path.dirname(os.path.abspath(__file__))
    
    print(f"Searching for speeches by: {politician_name}", file=sys.stderr)
    print(f"Base path: {base_path}", file=sys.stderr)
    
    speeches = find_all_speeches(base_path, politician_name)
    
    if not speeches:
        print(f"No speeches found for politician: {politician_name}", file=sys.stderr)
        sys.exit(1)
    
    print(f"Found {len(speeches)} speeches", file=sys.stderr)
    
    # Output all speeches in the requested format
    for i, speech in enumerate(speeches):
        print(speech)
        if i < len(speeches) - 1:  # Don't add newline after the last speech
            print()


if __name__ == "__main__":
    main()
