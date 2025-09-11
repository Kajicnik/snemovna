#!/usr/bin/env python3
"""
Enhanced Parliament Speech Analysis Script with Additional Insights
"""

import json
import statistics

def load_analysis_data():
    """Load the speaker analysis data."""
    with open('/home/draco/Projects/cyberCraft/snemovna/speaker_analysis.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_additional_insights():
    """Generate additional analytical insights."""
    data = load_analysis_data()
    speakers = data['speaker_statistics']
    session_totals = data['session_totals']
    
    print("\n" + "="*80)
    print("ADDITIONAL INSIGHTS AND ANALYSIS")
    print("="*80)
    
    # Most prolific speakers (by total words)
    print("\nTOP 10 SPEAKERS BY TOTAL WORDS SPOKEN:")
    print("-" * 50)
    word_leaders = sorted(speakers, key=lambda x: x['total_words'], reverse=True)[:10]
    for i, speaker in enumerate(word_leaders, 1):
        print(f"{i:2d}. {speaker['speaker'][:45]:<45} {speaker['total_words']:>8,} words")
    
    # Most verbose speakers (highest average words per speech)
    print("\nTOP 10 MOST VERBOSE SPEAKERS (avg words per speech):")
    print("-" * 60)
    verbose_speakers = sorted(speakers, key=lambda x: x['avg_word_length'], reverse=True)[:10]
    for i, speaker in enumerate(verbose_speakers, 1):
        print(f"{i:2d}. {speaker['speaker'][:35]:<35} {speaker['avg_word_length']:>6.1f} words/speech ({speaker['speech_count']:>3} speeches)")
    
    # Most active across sessions
    print("\nTOP 10 SPEAKERS MOST ACTIVE ACROSS SESSIONS:")
    print("-" * 55)
    active_speakers = sorted(speakers, key=lambda x: len(x['sessions']), reverse=True)[:10]
    for i, speaker in enumerate(active_speakers, 1):
        sessions_count = len(speaker['sessions'])
        avg_participation = sum(speaker['session_percentages'].values()) / len(speaker['session_percentages'])
        print(f"{i:2d}. {speaker['speaker'][:35]:<35} {sessions_count:>2} sessions (avg {avg_participation:>4.1f}%)")
    
    # Session analysis
    print("\nSESSION ACTIVITY ANALYSIS:")
    print("-" * 40)
    session_activity = []
    for session, totals in session_totals.items():
        avg_words_per_speech = totals['total_words'] / totals['total_speeches'] if totals['total_speeches'] > 0 else 0
        session_activity.append((session, totals['total_speeches'], totals['total_words'], avg_words_per_speech))
    
    # Sort by total speeches
    session_activity.sort(key=lambda x: x[1], reverse=True)
    
    print("Most active sessions (by number of speeches):")
    for session, speeches, words, avg_words in session_activity[:5]:
        print(f"  Session {session}: {speeches:>3} speeches, {words:>6,} words (avg {avg_words:>5.1f} words/speech)")
    
    # Statistics overview
    print("\nSTATISTICAL OVERVIEW:")
    print("-" * 30)
    
    # Speaker speech count distribution
    speech_counts = [s['speech_count'] for s in speakers]
    word_totals = [s['total_words'] for s in speakers]
    avg_lengths = [s['avg_word_length'] for s in speakers]
    
    print(f"Speech count distribution:")
    print(f"  Min: {min(speech_counts)}, Max: {max(speech_counts)}, Median: {statistics.median(speech_counts):.1f}")
    print(f"  Mean: {statistics.mean(speech_counts):.1f}, Std Dev: {statistics.stdev(speech_counts):.1f}")
    
    print(f"\nTotal words distribution:")
    print(f"  Min: {min(word_totals):,}, Max: {max(word_totals):,}, Median: {statistics.median(word_totals):,.1f}")
    print(f"  Mean: {statistics.mean(word_totals):,.1f}, Std Dev: {statistics.stdev(word_totals):,.1f}")
    
    print(f"\nAverage speech length distribution:")
    print(f"  Min: {min(avg_lengths):.1f}, Max: {max(avg_lengths):.1f}, Median: {statistics.median(avg_lengths):.1f}")
    print(f"  Mean: {statistics.mean(avg_lengths):.1f}, Std Dev: {statistics.stdev(avg_lengths):.1f}")
    
    # Top speakers by session
    print(f"\nTOP SPEAKER IN EACH SESSION (by speech count):")
    print("-" * 50)
    
    session_leaders = {}
    for speaker_data in speakers:
        for session in speaker_data['sessions']:
            session_speech_count = sum(1 for s in speaker_data['sessions'] if s == session)
            # This is a simplification - we'd need to calculate actual speeches per session from raw data
            # For now, we'll use the percentage to estimate activity
            session_percentage = speaker_data['session_percentages'].get(session, 0)
            
            if session not in session_leaders or session_percentage > session_leaders[session][1]:
                session_leaders[session] = (speaker_data['speaker'], session_percentage, speaker_data['speech_count'])
    
    for session in sorted(session_leaders.keys()):
        speaker, percentage, total_speeches = session_leaders[session]
        print(f"  Session {session}: {speaker[:40]:<40} ({percentage:>4.1f}% participation)")

if __name__ == "__main__":
    try:
        generate_additional_insights()
    except FileNotFoundError:
        print("Please run analyze_speakers.py first to generate the analysis data.")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
