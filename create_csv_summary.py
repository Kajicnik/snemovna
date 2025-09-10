#!/usr/bin/env python3
"""
Generate CSV summary from the speaker analysis results
"""

import json
import csv

def create_csv_summary():
    # Load the JSON data
    with open('/home/draco/Projects/cyberCraft/snemovna/speaker_analysis.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Create CSV with speaker statistics
    csv_file = '/home/draco/Projects/cyberCraft/snemovna/speaker_statistics.csv'
    
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Write header
        writer.writerow([
            'Rank',
            'Speaker',
            'Speech Count',
            'Total Words',
            'Total Characters', 
            'Average Words per Speech',
            'Median Words per Speech',
            'Average Characters per Speech',
            'Median Characters per Speech',
            'Number of Sessions',
            'Sessions Active',
            'Average Session Participation %'
        ])
        
        # Write data for each speaker
        for i, speaker_data in enumerate(data['speaker_statistics'], 1):
            avg_participation = sum(speaker_data['session_percentages'].values()) / len(speaker_data['session_percentages'])
            
            writer.writerow([
                i,
                speaker_data['speaker'],
                speaker_data['speech_count'],
                speaker_data['total_words'],
                speaker_data['total_chars'],
                f"{speaker_data['avg_word_length']:.1f}",
                f"{speaker_data['median_word_length']:.1f}",
                f"{speaker_data['avg_char_length']:.1f}",
                f"{speaker_data['median_char_length']:.1f}",
                len(speaker_data['sessions']),
                ', '.join(speaker_data['sessions']),
                f"{avg_participation:.2f}%"
            ])
    
    print(f"CSV summary saved to: {csv_file}")

if __name__ == "__main__":
    create_csv_summary()
