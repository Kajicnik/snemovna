#!/usr/bin/env python3
"""
Script to concatenate files in a folder.
Usage: python concatenate_files.py [folder_path] [output_file] [options]
"""

import os
import sys
import argparse
from pathlib import Path

def concatenate_files(folder_path, output_file, file_pattern="*", include_filename=True, separator="\n" + "="*50 + "\n"):
    """
    Concatenate files in a folder into a single output file.
    
    Args:
        folder_path (str): Path to the folder containing files to concatenate
        output_file (str): Path to the output file
        file_pattern (str): Pattern to match files (e.g., "*.txt", "*.md")
        include_filename (bool): Whether to include filename headers in output
        separator (str): Separator between files
    """
    folder = Path(folder_path)
    
    if not folder.exists():
        print(f"Error: Folder '{folder_path}' does not exist.")
        return False
    
    if not folder.is_dir():
        print(f"Error: '{folder_path}' is not a directory.")
        return False
    
    # Get all files matching the pattern
    files = sorted(folder.glob(file_pattern))
    files = [f for f in files if f.is_file()]
    
    if not files:
        print(f"No files found matching pattern '{file_pattern}' in '{folder_path}'")
        return False
    
    print(f"Found {len(files)} files to concatenate:")
    for f in files:
        print(f"  - {f.name}")
    
    try:
        with open(output_file, 'w', encoding='utf-8') as outf:
            for i, file_path in enumerate(files):
                if include_filename:
                    if i > 0:
                        outf.write(separator)
                    outf.write(f"FILE: {file_path.name}\n\n")
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as inf:
                        content = inf.read()
                        
                        # Remove redundant metadata from parliament speech files but keep date and speaker
                        lines = content.split('\n')
                        filtered_lines = []
                        skip_metadata = True
                        
                        for line in lines:
                            if skip_metadata and line.startswith(('File: ', 'Anchor: ')):
                                continue
                            elif skip_metadata and line.startswith(('Date: ', 'Speaker: ')):
                                filtered_lines.append(line)
                                continue
                            elif skip_metadata and line.strip() == '':
                                continue
                            elif skip_metadata and line.startswith('Speech:'):
                                skip_metadata = False
                                filtered_lines.append('')  # Add empty line after metadata
                                continue
                            else:
                                skip_metadata = False
                                filtered_lines.append(line)
                        
                        filtered_content = '\n'.join(filtered_lines)
                        outf.write(filtered_content)
                        if not filtered_content.endswith('\n'):
                            outf.write('\n')
                except UnicodeDecodeError:
                    print(f"Warning: Could not read '{file_path}' as UTF-8, skipping...")
                    continue
                except Exception as e:
                    print(f"Warning: Error reading '{file_path}': {e}")
                    continue
        
        print(f"Successfully concatenated {len(files)} files into '{output_file}'")
        return True
        
    except Exception as e:
        print(f"Error writing to output file '{output_file}': {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Concatenate files in a folder")
    parser.add_argument("folder", help="Path to the folder containing files")
    parser.add_argument("output", help="Path to the output file")
    parser.add_argument("-p", "--pattern", default="*", help="File pattern to match (default: *)")
    parser.add_argument("--no-headers", action="store_true", help="Don't include filename headers")
    parser.add_argument("-s", "--separator", default="\n" + "="*50 + "\n", help="Separator between files")
    
    args = parser.parse_args()
    
    success = concatenate_files(
        folder_path=args.folder,
        output_file=args.output,
        file_pattern=args.pattern,
        include_filename=not args.no_headers,
        separator=args.separator
    )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
