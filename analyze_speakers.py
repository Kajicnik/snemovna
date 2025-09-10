#!/usr/bin/env python3
"""
Parliament Speech Analysis Script

This script analyzes all parliament speeches from the parliament_speeches folder
and generates statistics about speakers including:
- Number of speeches per speaker
- Average, median, and total length of speeches
- Percentage of session where they spoke
"""

import os
import re
from collections import defaultdict
from pathlib import Path
import statistics
import json

def parse_speech_file(file_path):
    """Parse a single speech file and extract metadata."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract metadata using regex
    file_match = re.search(r'File: (.+)', content)
    anchor_match = re.search(r'Anchor: (.+)', content)
    date_match = re.search(r'Date: (.+)', content)
    speaker_match = re.search(r'Speaker: (.+)', content)
    
    # Extract speech content (everything after "Speech:" line)
    speech_match = re.search(r'Speech:\n(.+)', content, re.DOTALL)
    
    if not all([file_match, anchor_match, date_match, speaker_match, speech_match]):
        print(f"Warning: Could not parse all metadata from {file_path}")
        return None
    
    speech_text = speech_match.group(1).strip()
    
    # Count words and characters
    word_count = len(speech_text.split())
    char_count = len(speech_text)
    
    return {
        'file': file_match.group(1),
        'anchor': anchor_match.group(1),
        'date': date_match.group(1),
        'speaker': speaker_match.group(1).strip(),
        'speech_text': speech_text,
        'word_count': word_count,
        'char_count': char_count,
        'session': os.path.basename(os.path.dirname(file_path))
    }

def clean_speaker_name(speaker):
    """Clean and normalize speaker names."""
    # Remove common prefixes and suffixes
    speaker = re.sub(r'^(Poslanec|Poslankyně|Místopředseda|Místopředsedkyně|Předseda|Předsedkyně|Ministr|Ministryně)\s+', '', speaker)
    speaker = re.sub(r'\s+(PSP|ÚS|vlády).*$', '', speaker)
    speaker = re.sub(r'::.*$', '', speaker)  # Remove everything after ::
    return speaker.strip()

def analyze_speeches():
    """Main analysis function."""
    
    # Data structures to store analysis
    speaker_stats = defaultdict(lambda: {
        'speech_count': 0,
        'total_words': 0,
        'total_chars': 0,
        'word_lengths': [],
        'char_lengths': [],
        'sessions': set(),
        'speeches_by_session': defaultdict(int)
    })
    
    session_totals = defaultdict(lambda: {
        'total_words': 0,
        'total_chars': 0,
        'total_speeches': 0
    })
    
    # Path to parliament speeches
    speeches_dir = Path('/home/draco/Projects/cyberCraft/snemovna/parliament_speeches')
    
    # Process all speech files
    total_files = 0
    processed_files = 0
    
    for session_dir in speeches_dir.iterdir():
        if session_dir.is_dir() and session_dir.name != 'backup':
            session_name = session_dir.name
            print(f"Processing session {session_name}...")
            
            session_file_count = 0
            for speech_file in session_dir.glob('*.txt'):
                total_files += 1
                session_file_count += 1
                
                speech_data = parse_speech_file(speech_file)
                if speech_data:
                    processed_files += 1
                    speaker = clean_speaker_name(speech_data['speaker'])
                    
                    # Update speaker statistics
                    stats = speaker_stats[speaker]
                    stats['speech_count'] += 1
                    stats['total_words'] += speech_data['word_count']
                    stats['total_chars'] += speech_data['char_count']
                    stats['word_lengths'].append(speech_data['word_count'])
                    stats['char_lengths'].append(speech_data['char_count'])
                    stats['sessions'].add(session_name)
                    stats['speeches_by_session'][session_name] += 1
                    
                    # Update session totals
                    session_totals[session_name]['total_words'] += speech_data['word_count']
                    session_totals[session_name]['total_chars'] += speech_data['char_count']
                    session_totals[session_name]['total_speeches'] += 1
            
            print(f"  Processed {session_file_count} files from session {session_name}")
    
    print(f"\nTotal files found: {total_files}")
    print(f"Successfully processed: {processed_files}")
    print(f"Failed to process: {total_files - processed_files}")
    
    # Calculate final statistics
    final_stats = []
    
    for speaker, stats in speaker_stats.items():
        if stats['speech_count'] > 0:  # Only include speakers with speeches
            # Calculate averages and medians
            avg_word_length = statistics.mean(stats['word_lengths'])
            median_word_length = statistics.median(stats['word_lengths'])
            avg_char_length = statistics.mean(stats['char_lengths'])
            median_char_length = statistics.median(stats['char_lengths'])
            
            # Calculate session percentages
            session_percentages = {}
            for session in stats['sessions']:
                speaker_speeches = stats['speeches_by_session'][session]
                total_session_speeches = session_totals[session]['total_speeches']
                percentage = (speaker_speeches / total_session_speeches * 100) if total_session_speeches > 0 else 0
                session_percentages[session] = percentage
            
            final_stats.append({
                'speaker': speaker,
                'speech_count': stats['speech_count'],
                'total_words': stats['total_words'],
                'total_chars': stats['total_chars'],
                'avg_word_length': avg_word_length,
                'median_word_length': median_word_length,
                'avg_char_length': avg_char_length,
                'median_char_length': median_char_length,
                'sessions': sorted(list(stats['sessions'])),
                'session_percentages': session_percentages
            })
    
    # Sort by speech count (descending)
    final_stats.sort(key=lambda x: x['speech_count'], reverse=True)
    
    return final_stats, session_totals

def generate_report(stats, session_totals):
    """Generate a comprehensive report."""
    
    print("\n" + "="*80)
    print("PARLIAMENT SPEECH ANALYSIS REPORT")
    print("="*80)
    
    # Top speakers by number of speeches
    print(f"\nTOP 20 SPEAKERS BY NUMBER OF SPEECHES:")
    print("-" * 60)
    print(f"{'Rank':<4} {'Speaker':<35} {'Speeches':<10} {'Total Words':<12}")
    print("-" * 60)
    
    for i, speaker_stat in enumerate(stats[:20], 1):
        print(f"{i:<4} {speaker_stat['speaker'][:34]:<35} {speaker_stat['speech_count']:<10} {speaker_stat['total_words']:<12}")
    
    # Detailed statistics for top 10 speakers
    print(f"\n\nDETAILED STATISTICS FOR TOP 10 SPEAKERS:")
    print("=" * 80)
    
    for i, speaker_stat in enumerate(stats[:10], 1):
        print(f"\n{i}. {speaker_stat['speaker']}")
        print("-" * len(f"{i}. {speaker_stat['speaker']}"))
        print(f"  Total speeches: {speaker_stat['speech_count']}")
        print(f"  Total words: {speaker_stat['total_words']:,}")
        print(f"  Total characters: {speaker_stat['total_chars']:,}")
        print(f"  Average speech length: {speaker_stat['avg_word_length']:.1f} words ({speaker_stat['avg_char_length']:.1f} chars)")
        print(f"  Median speech length: {speaker_stat['median_word_length']:.1f} words ({speaker_stat['median_char_length']:.1f} chars)")
        print(f"  Active in sessions: {', '.join(speaker_stat['sessions'])}")
        
        # Session percentages
        print(f"  Session participation percentages:")
        for session in sorted(speaker_stat['session_percentages'].keys()):
            percentage = speaker_stat['session_percentages'][session]
            print(f"    Session {session}: {percentage:.2f}%")
    
    # Session summary
    print(f"\n\nSESSION SUMMARY:")
    print("-" * 40)
    for session in sorted(session_totals.keys()):
        totals = session_totals[session]
        print(f"Session {session}: {totals['total_speeches']} speeches, {totals['total_words']:,} words")
    
    # Overall statistics
    total_speakers = len(stats)
    total_speeches = sum(s['speech_count'] for s in stats)
    total_words = sum(s['total_words'] for s in stats)
    
    print(f"\n\nOVERALL STATISTICS:")
    print("-" * 30)
    print(f"Total speakers: {total_speakers}")
    print(f"Total speeches: {total_speeches}")
    print(f"Total words: {total_words:,}")
    print(f"Average speeches per speaker: {total_speeches/total_speakers:.1f}")
    print(f"Average words per speech: {total_words/total_speeches:.1f}")

def save_detailed_json(stats, session_totals):
    """Save detailed statistics to JSON file."""
    output_data = {
        'speaker_statistics': stats,
        'session_totals': {k: dict(v) for k, v in session_totals.items()},
        'summary': {
            'total_speakers': len(stats),
            'total_speeches': sum(s['speech_count'] for s in stats),
            'total_words': sum(s['total_words'] for s in stats),
        }
    }
    
    # Convert sets to lists for JSON serialization
    for speaker_stat in output_data['speaker_statistics']:
        if 'sessions' in speaker_stat and isinstance(speaker_stat['sessions'], set):
            speaker_stat['sessions'] = sorted(list(speaker_stat['sessions']))
    
    output_file = '/home/draco/Projects/cyberCraft/snemovna/speaker_analysis.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nDetailed analysis saved to: {output_file}")

if __name__ == "__main__":
    print("Starting parliament speech analysis...")
    
    try:
        stats, session_totals = analyze_speeches()
        generate_report(stats, session_totals)
        save_detailed_json(stats, session_totals)
        
        print(f"\nAnalysis complete! Found {len(stats)} speakers.")
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()
