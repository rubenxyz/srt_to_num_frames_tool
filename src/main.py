#!/usr/bin/env python3
"""
SRT to Num Frames Tool - Calculate frame counts from SRT subtitle timecodes at 25fps.

Parses SRT files recursively from USER-FILES/04.INPUT/,
extracts subtitle timecodes, calculates frame duration,
and outputs individual frame count files to USER-FILES/05.OUTPUT/.
"""

import math
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List

import srt
from natsort import natsorted

# Module constants
DEFAULT_FPS = 25
INPUT_DIR = "USER-FILES/04.INPUT"
OUTPUT_DIR = "USER-FILES/05.OUTPUT"


def fail_with_error(message: str) -> None:
    """
    Print error message and exit with status code 1.
    
    Args:
        message: Error message to display
    """
    print(f"ERROR: {message}")
    sys.exit(1)


def timedelta_to_frames(td: timedelta, fps: int = DEFAULT_FPS) -> float:
    """
    Convert timedelta to frame number at specified fps.
    
    Args:
        td: Timedelta object
        fps: Frames per second (default 25)
    
    Returns:
        Frame number as float
    """
    total_seconds = td.total_seconds()
    return total_seconds * fps


def calculate_subtitle_frames(subtitle: srt.Subtitle) -> int:
    """
    Calculate frame count for a subtitle entry, rounding up fractionals.
    
    Args:
        subtitle: SRT subtitle object with start and end times
    
    Returns:
        Frame count as integer (rounded up if fractional)
    
    Raises:
        ValueError: If end time is before or equal to start time
    """
    start_frames = timedelta_to_frames(subtitle.start)
    end_frames = timedelta_to_frames(subtitle.end)
    
    if end_frames <= start_frames:
        raise ValueError(
            f"End time must be after start time (subtitle {subtitle.index})"
        )
    
    duration = end_frames - start_frames
    return math.ceil(duration)


def parse_srt_file(file_path: Path) -> List[srt.Subtitle]:
    """
    Parse an SRT file and return list of subtitle objects.
    
    Args:
        file_path: Path to SRT file
    
    Returns:
        List of srt.Subtitle objects
    
    Raises:
        ValueError: If SRT format is invalid
        FileNotFoundError: If file doesn't exist
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        fail_with_error(f"File not found: {file_path}")
    
    try:
        subtitles = list(srt.parse(content))
    except srt.SRTParseError as e:
        fail_with_error(f"Cannot parse SRT file {file_path}: {e}")
    except Exception as e:
        fail_with_error(f"Unexpected error parsing SRT file {file_path}: {e}")
    
    if not subtitles:
        fail_with_error(f"No subtitles found in {file_path}")
    
    return subtitles


def process_srt_file(srt_path: Path, output_base: Path) -> int:
    """
    Process a single SRT file and output frame counts.
    
    Args:
        srt_path: Path to SRT file
        output_base: Base output directory for this file
    
    Returns:
        Number of subtitles processed
    """
    subtitles = parse_srt_file(srt_path)
    
    # Create output directory for this SRT file
    output_dir = output_base / srt_path.stem
    output_dir.mkdir(parents=True, exist_ok=True)
    
    processed_count = 0
    
    for subtitle in subtitles:
        try:
            # Calculate frame duration
            frame_count = calculate_subtitle_frames(subtitle)
            
            # Write frame count to file with SRT filename suffix
            write_frame_count_file(output_dir, subtitle.index, frame_count, srt_path.stem)
            
            print(f"  Subtitle {subtitle.index}: {frame_count} frames")
            processed_count += 1
            
        except ValueError as e:
            fail_with_error(f"{e} in {srt_path}")
    
    return processed_count


def write_frame_count_file(output_dir: Path, subtitle_index: int, frame_count: int, srt_filename: str) -> None:
    """
    Write frame count to individual text file.
    
    Args:
        output_dir: Directory to write file to
        subtitle_index: Index number for filename
        frame_count: Number of frames to write
        srt_filename: SRT filename stem to use as prefix
    """
    output_file = output_dir / f"{srt_filename}_{subtitle_index}.txt"
    with open(output_file, 'w') as f:
        f.write(str(frame_count))


def setup_paths() -> tuple[Path, Path]:
    """
    Setup input and output directory paths.
    
    Returns:
        Tuple of (input_dir, output_base) paths
    """
    base_path = Path(__file__).parent.parent
    input_dir = base_path / INPUT_DIR
    output_base = base_path / OUTPUT_DIR
    
    if not input_dir.exists():
        fail_with_error(f"Input directory does not exist: {input_dir}")
    
    return input_dir, output_base


def discover_srt_files(input_dir: Path) -> List[Path]:
    """
    Discover and sort SRT files recursively in input directory.
    
    Args:
        input_dir: Directory to search for SRT files
    
    Returns:
        List of SRT file paths, naturally sorted
    """
    srt_files = list(input_dir.rglob("*.srt"))
    
    if not srt_files:
        fail_with_error(f"No SRT files found in {input_dir}")
    
    return natsorted(srt_files)


def process_srt_files():
    """
    Process all SRT files from input directory.
    """
    # Setup paths and discover files
    input_dir, output_base = setup_paths()
    srt_files = discover_srt_files(input_dir)
    
    print(f"Found {len(srt_files)} SRT file(s) to process")
    
    # Create timestamped output directory
    timestamp = datetime.now().strftime("%y%m%d_%H%M%S")
    output_dir = output_base / f"{timestamp}_NUM_FRAMES"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Output directory: {output_dir}")
    print()
    
    # Process all files
    total_subtitles = 0
    
    for srt_file in srt_files:
        relative_path = srt_file.relative_to(input_dir)
        print(f"Processing: {relative_path}")
        
        # Process file and get subtitle count
        subtitle_count = process_srt_file(srt_file, output_dir)
        total_subtitles += subtitle_count
        
        print(f"  Processed {subtitle_count} subtitles")
        print()
    
    # Summary
    print(f"Successfully processed {total_subtitles} subtitle(s) from {len(srt_files)} file(s)")
    print(f"Output files written to: {output_dir}")


def main():
    """
    Main execution: process SRT files directly with no arguments.
    """
    process_srt_files()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        fail_with_error(f"Unexpected error: {e}")