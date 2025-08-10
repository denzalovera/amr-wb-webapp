# AMR-WB Converter Web Application

A web-based GUI interface for the AMR-WB audio converter tool. This application provides an easy-to-use web interface for extracting AMR, AMR-WB, and EVS audio frames from PCAP files.

## Features

- **Web-based Interface**: Modern, responsive web UI with drag-and-drop file upload
- **Multiple Codec Support**: AMR, AMR-WB, and EVS codec extraction
- **Auto-detection**: Automatic codec detection or manual selection
- **Framing Options**: Support for IETF RFC4867 and Iu framing
- **File Download**: Direct download of converted audio files
- **Real-time Progress**: Visual feedback during conversion process

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Make sure the templates directory exists:
```bash
mkdir -p templates
```

## Usage

1. Start the web application:
```bash
python3 app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

3. Use the web interface to:
   - Upload a PCAP or PCAPNG file (drag-and-drop or click to select)
   - Choose codec (auto-detect recommended)
   - Select framing type (IETF or Iu)
   - Click "Convert Audio" to process the file
   - Download the resulting audio file

## API Endpoints

- `GET /` - Main web interface
- `POST /api/convert` - Convert PCAP file to audio
- `GET /api/download/<filename>` - Download converted audio file
- `GET /api/health` - Health check endpoint

## File Formats

### Input
- PCAP files (.pcap)
- PCAPNG files (.pcapng)
- Maximum file size: 100MB

### Output
- AMR/AMR-WB: .3ga files (playable with VLC)
- EVS: .evs-mime files (requires EVS decoder)

## Converting Output Files

### AMR/AMR-WB (.3ga files)
- Play directly with [VLC Media Player](https://www.videolan.org/)
- Convert to other formats with [FFmpeg](https://ffmpeg.org/):
```bash
ffmpeg -i output.3ga output.wav
```

### EVS (.evs-mime files)
- Use 3GPP EVS decoder (available in 3GPP TS26.442/TS26.443):
```bash
EVS_dec.exe -mime 48 output.evs-mime output.raw
```
- Import the .raw file into [Audacity](https://www.audacityteam.org/) with these settings:
  - Encoding: Signed 16-bit PCM
  - Byte order: Little endian
  - Channels: 1 Channel (Mono)
  - Sampling rate: 48000 Hz

## Configuration

The application can be configured by modifying these variables in `app.py`:

- `MAX_CONTENT_LENGTH`: Maximum upload file size (default: 100MB)
- `UPLOAD_FOLDER`: Temporary directory for file processing
- Host and port settings in the `app.run()` call

## Security Notes

- Files are automatically cleaned up after processing
- Only PCAP/PCAPNG files are accepted
- Output files are securely generated and served
- Temporary files are stored in system temp directory

## Limitations

Same as the original pcap_parser.py:
- Single channel audio only
- One codec frame per packet
- EVS: Only compact payload format supported
- Iu framing not supported for EVS codec