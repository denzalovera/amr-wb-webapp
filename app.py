#!/usr/bin/env python3
"""
Flask Web Application for AMR-WB Converter
Provides a web interface for the pcap_parser.py functionality
"""

import os
import tempfile
import logging
from flask import Flask, request, jsonify, render_template, send_file
from werkzeug.utils import secure_filename
import subprocess
import json

app = Flask(__name__, static_folder='static')
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {'pcap', 'pcapng'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_pcap():
    """Analyze PCAP file to show RTP stream information"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '' or not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(input_path)
        
        # Analyze with custom script
        cmd = ['python3', '-c', f'''
from scapy.all import *
import struct

packets = rdpcap("{input_path}")
print(f"Total packets: {{len(packets)}}")

streams = {{}}
for packet in packets:
    if UDP in packet:
        try:
            rtp = RTP(packet[UDP].load)
            key = (rtp.sourcesync, rtp.payload_type)
            if key not in streams:
                streams[key] = {{"count": 0, "sizes": set(), "pt": rtp.payload_type, "ssrc": hex(rtp.sourcesync)}}
            streams[key]["count"] += 1
            streams[key]["sizes"].add(len(rtp.load))
        except:
            pass

print("\\nRTP Streams found:")
for (ssrc, pt), info in streams.items():
    sizes = sorted(info["sizes"])
    print(f"SSRC: {{info['ssrc']}}, PT: {{pt}}, Packets: {{info['count']}}, Payload sizes: {{sizes}}")

# Check codec compatibility
amr_sizes = [13, 14, 16, 18, 20, 21, 27, 32, 6]
amrwb_sizes = [18, 24, 33, 37, 41, 47, 51, 59, 61, 7]  
evs_sizes = [6, 7, 17, 18, 20, 23, 24, 32, 33, 36, 40, 41, 46, 50, 58, 60, 61, 80, 120, 160, 240, 320]

print("\\nCodec Analysis:")
for (ssrc, pt), info in streams.items():
    sizes = list(info["sizes"])
    amr_match = any(s in amr_sizes for s in sizes)
    amrwb_match = any(s in amrwb_sizes for s in sizes)
    evs_match = any(s in evs_sizes for s in sizes)
    
    likely_codec = "Unknown"
    if amr_match and not amrwb_match: likely_codec = "AMR"
    elif amrwb_match and not amr_match: likely_codec = "AMR-WB"  
    elif evs_match: likely_codec = "EVS"
    elif sizes == [160]: likely_codec = "G.711 (PCMU/PCMA)"
    
    print(f"Stream {{info['ssrc']}}: {{likely_codec}}")
''']
        
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        
        # Clean up
        try:
            os.remove(input_path)
        except:
            pass
            
        return jsonify({
            'success': True,
            'analysis': result.stdout,
            'error': result.stderr if result.stderr else None
        })
        
    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@app.route('/api/convert', methods=['POST'])
def convert_pcap():
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Only .pcap and .pcapng files are allowed'}), 400
        
        # Get optional parameters
        codec = request.form.get('codec', 'guess')
        framing = request.form.get('framing', 'ietf')
        
        # Validate parameters
        supported_codecs = ['guess', 'amr', 'amr-wb', 'evs']
        supported_framings = ['ietf', 'iu']
        
        if codec not in supported_codecs:
            return jsonify({'error': f'Unsupported codec: {codec}'}), 400
        
        if framing not in supported_framings:
            return jsonify({'error': f'Unsupported framing: {framing}'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(input_path)
        
        # Generate output filename
        base_name = os.path.splitext(filename)[0]
        output_extension = '.3ga' if codec in ['guess', 'amr', 'amr-wb'] else '.evs-mime'
        output_filename = f"{base_name}_converted{output_extension}"
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
        
        # Run pcap_parser.py
        cmd = [
            'python3', 'pcap_parser.py',
            '-i', input_path,
            '-o', output_path,
            '-c', codec,
            '-f', framing
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.path.dirname(os.path.abspath(__file__)))
        
        # Clean up input file
        try:
            os.remove(input_path)
        except:
            pass
        
        if result.returncode != 0:
            error_msg = result.stderr or result.stdout or 'Unknown error occurred'
            
            # Provide more specific error messages
            if 'IndexError: list index out of range' in error_msg:
                error_msg = 'Invalid RTP packet format detected. This PCAP may contain non-AMR/AMR-WB/EVS data or corrupted packets. Try analyzing the file first to verify codec compatibility.'
            elif 'Unable to guess the codec used' in error_msg:
                error_msg = 'Could not detect AMR/AMR-WB/EVS codec in this file. Use the "Analyze PCAP" feature to see what codecs are present.'
            
            return jsonify({'error': f'Conversion failed: {error_msg}'}), 500
        
        # Check if output file was created
        if not os.path.exists(output_path):
            return jsonify({'error': 'Output file was not created'}), 500
        
        # Parse the output for statistics
        output_lines = result.stdout.split('\n')
        stats = {}
        for line in output_lines:
            if 'Codec:' in line:
                stats['output'] = line.strip()
            elif 'AMR samples:' in line:
                stats['detection'] = line.strip()
        
        return jsonify({
            'success': True,
            'output_file': output_filename,
            'stats': stats,
            'message': 'Conversion completed successfully'
        })
        
    except Exception as e:
        logger.error(f"Conversion error: {str(e)}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/api/download/<filename>')
def download_file(filename):
    try:
        # Security check - only allow downloading files with expected extensions
        if not (filename.endswith('.3ga') or filename.endswith('.evs-mime')):
            return jsonify({'error': 'Invalid file type'}), 400
        
        safe_filename = secure_filename(filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        # Send file and then clean up
        response = send_file(
            file_path,
            as_attachment=True,
            download_name=safe_filename
        )
        
        # Clean up file after a delay (using a simple approach)
        import threading
        def delayed_cleanup():
            import time
            time.sleep(5)  # Wait 5 seconds for download to complete
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"Cleaned up file: {file_path}")
            except Exception as e:
                logger.warning(f"Could not clean up file {file_path}: {e}")
        
        cleanup_thread = threading.Thread(target=delayed_cleanup)
        cleanup_thread.daemon = True
        cleanup_thread.start()
        
        return response
        
    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        return jsonify({'error': f'Download failed: {str(e)}'}), 500

@app.route('/api/health')
def health_check():
    return jsonify({'status': 'healthy', 'version': '1.0.0'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888, debug=True)