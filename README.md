# SRT to Num Frames Tool

Extracts frame counts from SRT subtitle timecodes at 25fps.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
python3 -m src.main
```

No command-line arguments needed. The tool processes all SRT files automatically.

## Input/Output

- **Input**: SRT files in `USER-FILES/04.INPUT/`
- **Output**: `USER-FILES/05.OUTPUT/{timestamp}/{srt_filename}/`
  - Frame counts: `1.txt`, `2.txt`, etc. (named by subtitle index)

## SRT Format

Standard SRT format with subtitle index, timecodes, and optional text:

```srt
1
00:00:01,000 --> 00:00:03,500
Subtitle text (ignored by tool)

2
00:00:05,000 --> 00:00:08,000
Another subtitle
```

## Frame Calculation

- Converts SRT timecodes to frames at 25fps
- Calculates duration between start and end times
- Rounds up fractional frames to ensure full duration

## Example

Input SRT entry:
```
1
00:00:01,000 --> 00:00:03,500
```

Duration: 2.5 seconds  
Frame count: 2.5 × 25 = 62.5 → 63 frames (rounded up)

Output file `1.txt` contains: `63`