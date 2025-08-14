# AMR-WB Web Application

A Flask web application for converting PCAP network capture files containing voice audio data into playable audio files.

## Features

- **PCAP Analysis**: Examine network packets to identify voice codecs
- **Audio Conversion**: Convert RTP streams to playable audio formats
- **Multiple Codecs**: Support for AMR, AMR-WB, and EVS
- **Modern Web Interface**: Responsive design with drag-and-drop file upload
- **Web Standards Compliant**: Separated HTML, CSS, and JavaScript

## Project Structure

```
amr-wb-webapp/
├── app.py                 # Main Flask web server
├── pcap_parser.py         # Core conversion engine
├── templates/
│   └── index.html         # Semantic HTML structure
├── static/
│   ├── css/
│   │   └── styles.css     # All CSS styles
│   └── js/
│       └── app.js         # All JavaScript functionality
├── requirements.txt        # Python dependencies
└── run.sh                 # Startup script
```

## Web Standards Compliance

This application follows modern web development best practices:

- **Separation of Concerns**: HTML (structure), CSS (presentation), JavaScript (behavior)
- **Semantic HTML**: Proper use of `<header>`, `<main>`, `<section>` tags
- **Accessibility**: Proper labeling and ARIA-compliant structure
- **Responsive Design**: Mobile-first approach with CSS Grid and Flexbox
- **Modern JavaScript**: ES6+ features, async/await, event delegation

## Installation

1. Clone the repository
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python app.py
   ```

## Usage

1. Open your browser to `http://localhost:8888`
2. Upload a PCAP or PCAPNG file (max 100MB)
3. Choose to analyze the file first or convert directly
4. Select codec and framing options
5. Download the converted audio file

## Supported Formats

- **Input**: PCAP, PCAPNG files
- **Output**: 
  - `.3ga` for AMR and AMR-WB
  - `.evs-mime` for EVS codec

## API Endpoints

- `GET /` - Main web interface
- `POST /api/analyze` - Analyze PCAP file structure
- `POST /api/convert` - Convert PCAP to audio
- `GET /api/download/<filename>` - Download converted file
- `GET /api/health` - Health check

## Dependencies

- Flask 2.3.3
- Scapy 2.5.0
- Bitarray 2.9.1
- Werkzeug 2.3.7