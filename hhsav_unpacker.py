#!/usr/bin/env python3
"""
HHSav Unpacker - Hackhub Save File Extractor
Usage: python hhsav_unpacker.py <input.hhsav> [output.json]
"""

import gzip
import json
import sys
import os
from pathlib import Path


def unpack_hhsav(input_path, output_path=None):
    """
    Unpack a .hhsav file (gzip compressed JSON) to a readable JSON file.
    
    Args:
        input_path: Path to the .hhsav file
        output_path: Optional path for output JSON file
    
    Returns:
        dict: The unpacked data as a Python dictionary
    """
    input_path = Path(input_path)
    
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    if output_path is None:
        output_path = input_path.parent / f"{input_path.stem}_unpacked.json"
    else:
        output_path = Path(output_path)
    
    print(f"[*] Reading: {input_path}")
    print(f"[*] File size: {input_path.stat().st_size:,} bytes")
    
    # Read and decompress gzip data
    with open(input_path, 'rb') as f:
        compressed_data = f.read()
    
    print(f"[*] Decompressing gzip data...")
    try:
        decompressed_data = gzip.decompress(compressed_data)
    except Exception as e:
        raise ValueError(f"Failed to decompress: {e}. File may be corrupted or not a valid .hhsav file.")
    
    print(f"[*] Decompressed size: {len(decompressed_data):,} bytes")
    
    # Parse JSON
    print(f"[*] Parsing JSON data...")
    try:
        data = json.loads(decompressed_data)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON: {e}")
    
    # Write output
    print(f"[*] Writing to: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"[+] Successfully unpacked to: {output_path}")
    
    return data


def inspect_hhsav(input_path, max_items=50):
    """
    Inspect a .hhsav file without fully unpacking it.
    
    Args:
        input_path: Path to the .hhsav file
        max_items: Maximum number of top-level items to show
    
    Returns:
        dict: The unpacked data
    """
    input_path = Path(input_path)
    
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    print(f"[*] Inspecting: {input_path}")
    print(f"[*] File size: {input_path.stat().st_size:,} bytes")
    
    with open(input_path, 'rb') as f:
        compressed_data = f.read()
    
    decompressed_data = gzip.decompress(compressed_data)
    data = json.loads(decompressed_data)
    
    print(f"\n{'='*60}")
    print(f"HHSav File Summary")
    print(f"{'='*60}")
    print(f"Total top-level keys: {len(data)}")
    
    # Show GlobalStore summary if exists
    if 'GlobalStore' in data:
        gs = data['GlobalStore']
        print(f"\n--- GlobalStore ({len(gs)} items) ---")
        for i, key in enumerate(sorted(gs.keys())[:max_items]):
            val = gs[key]
            if isinstance(val, dict):
                print(f"  {key}: {{...}} ({len(val)} sub-items)")
            elif isinstance(val, list):
                print(f"  {key}: [...] ({len(val)} items)")
            elif isinstance(val, str) and len(val) > 50:
                print(f"  {key}: \"{val[:47]}...\"")
            else:
                print(f"  {key}: {val}")
    
    # Show all top-level keys
    print(f"\n--- Top-level Keys ---")
    for key in sorted(data.keys()):
        print(f"  - {key}")
    
    return data


def repack_hhsav(json_path, output_path=None):
    """
    Repack a JSON file back into .hhsav format.
    
    Args:
        json_path: Path to the JSON file
        output_path: Optional path for output .hhsav file
    
    Returns:
        Path: Path to the created .hhsav file
    """
    json_path = Path(json_path)
    
    if not json_path.exists():
        raise FileNotFoundError(f"Input file not found: {json_path}")
    
    if output_path is None:
        output_path = json_path.parent / f"{json_path.stem}.hhsav"
    else:
        output_path = Path(output_path)
    
    print(f"[*] Reading: {json_path}")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"[*] Serializing JSON...")
    json_data = json.dumps(data, ensure_ascii=False)
    
    print(f"[*] Compressing with gzip...")
    compressed_data = gzip.compress(json_data.encode('utf-8'))
    
    print(f"[*] Writing to: {output_path}")
    with open(output_path, 'wb') as f:
        f.write(compressed_data)
    
    print(f"[+] Successfully repacked to: {output_path}")
    print(f"[*] Output size: {output_path.stat().st_size:,} bytes")
    
    return output_path


def main():
    """Main entry point with command-line argument support."""
    
    if len(sys.argv) < 2:
        # Interactive mode
        print("=" * 60)
        print("HHSav Unpacker - Hackhub Save File Extractor")
        print("=" * 60)
        print()
        
        # Find .hhsav files in current directory
        hhsav_files = list(Path('.').glob('*.hhsav')) + list(Path('.').glob('*.HHSav'))
        
        if hhsav_files:
            print("Found .hhsav files:")
            for i, f in enumerate(hhsav_files, 1):
                print(f"  [{i}] {f}")
            print()
            
            try:
                choice = input("Select a file number to unpack (or press Enter to exit): ").strip()
                if not choice:
                    print("Exiting.")
                    return
                
                idx = int(choice) - 1
                if 0 <= idx < len(hhsav_files):
                    file_path = str(hhsav_files[idx])
                    print(f"\n[*] Unpacking: {file_path}")
                    data = unpack_hhsav(file_path)
                    print(f"\n[+] Done! Extracted {len(data)} top-level keys.")
                    return
                else:
                    print("Invalid selection.")
                    return
            except ValueError:
                print("Invalid input.")
                return
            except KeyboardInterrupt:
                print("\nCancelled.")
                return
        
        print("Usage:")
        print("  python hhsav_unpacker.py unpack <file.hhsav> [output.json]")
        print("  python hhsav_unpacker.py inspect <file.hhsav>")
        print("  python hhsav_unpacker.py repack <file.json> [output.hhsav]")
        print()
        print("Or run this script without arguments for interactive mode.")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'unpack':
        if len(sys.argv) < 3:
            print("Usage: python hhsav_unpacker.py unpack <input.hhsav> [output.json]")
            sys.exit(1)
        data = unpack_hhsav(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
        print(f"\n[+] Done! Extracted {len(data)} top-level keys.")
    
    elif command == 'inspect':
        if len(sys.argv) < 3:
            print("Usage: python hhsav_unpacker.py inspect <input.hhsav>")
            sys.exit(1)
        inspect_hhsav(sys.argv[2])
    
    elif command == 'repack':
        if len(sys.argv) < 3:
            print("Usage: python hhsav_unpacker.py repack <input.json> [output.hhsav]")
            sys.exit(1)
        repack_hhsav(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == '__main__':
    main()
