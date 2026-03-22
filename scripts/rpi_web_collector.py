#!/usr/bin/env python3
"""
Web-based Dataset Collector for Raspberry Pi
Access from laptop browser at http://192.168.100.197:8080
No GUI needed on Raspberry Pi
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import subprocess
import os
from urllib.parse import parse_qs, urlparse
from datetime import datetime

class DatasetCollectorHandler(BaseHTTPRequestHandler):
    """HTTP request handler for dataset collection"""
    
    # Dataset configuration
    BASE_DIR = "/home/beans/coffee_dataset_final"
    BEANS_PER_SET = 50
    TARGETS = {
        'good_curve': 1050,
        'good_back': 450,
        'bad_curve': 1050,
        'bad_back': 450
    }
    SETS_NEEDED = {
        'good_curve': 21,
        'good_back': 9,
        'bad_curve': 21,
        'bad_back': 9
    }
    
    def do_GET(self):
        """Handle GET requests"""
        path = urlparse(self.path).path
        
        if path == '/':
            self.serve_main_page()
        elif path == '/status':
            self.serve_status()
        elif path == '/preview':
            self.serve_preview()
        else:
            self.send_error(404)
    
    def do_POST(self):
        """Handle POST requests"""
        path = urlparse(self.path).path
        
        if path == '/capture':
            self.handle_capture()
        elif path == '/brightness':
            self.handle_brightness()
        else:
            self.send_error(404)
    
    def serve_main_page(self):
        """Serve main HTML page"""
        counts = self.load_counts()
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Coffee Bean Dataset Collector</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        h1 {{
            color: #333;
            text-align: center;
        }}
        .status {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .category {{
            margin: 15px 0;
            padding: 15px;
            background: #f9f9f9;
            border-left: 4px solid #4CAF50;
            border-radius: 4px;
        }}
        .progress-bar {{
            width: 100%;
            height: 20px;
            background: #e0e0e0;
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }}
        .progress-fill {{
            height: 100%;
            background: #4CAF50;
            transition: width 0.3s;
        }}
        .controls {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        button {{
            padding: 15px 30px;
            font-size: 16px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            margin: 5px;
            transition: background 0.3s;
        }}
        .btn-capture {{
            background: #4CAF50;
            color: white;
        }}
        .btn-capture:hover {{
            background: #45a049;
        }}
        .btn-preview {{
            background: #2196F3;
            color: white;
        }}
        .btn-preview:hover {{
            background: #0b7dda;
        }}
        select {{
            padding: 10px;
            font-size: 16px;
            border-radius: 4px;
            border: 1px solid #ddd;
            margin: 5px;
        }}
        .brightness {{
            margin: 20px 0;
        }}
        input[type="range"] {{
            width: 100%;
        }}
        .message {{
            padding: 15px;
            margin: 10px 0;
            border-radius: 4px;
        }}
        .success {{
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }}
        .error {{
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }}
    </style>
</head>
<body>
    <h1>📷 Coffee Bean Dataset Collector</h1>
    
    <div class="status">
        <h2>Progress Status</h2>
        {self.generate_status_html(counts)}
    </div>
    
    <div class="controls">
        <h2>Capture Controls</h2>
        
        <div>
            <label>Category:</label>
            <select id="category">
                <option value="good_curve">Good Beans - Curve</option>
                <option value="good_back">Good Beans - Back</option>
                <option value="bad_curve">Bad Beans - Curve</option>
                <option value="bad_back">Bad Beans - Back</option>
            </select>
        </div>
        
        <div style="margin: 20px 0;">
            <button class="btn-capture" onclick="captureImage()">📷 Capture Image</button>
            <button class="btn-preview" onclick="window.open('/preview', '_blank')">📹 Preview</button>
        </div>
        
        <div class="brightness">
            <h3>💡 LED Brightness</h3>
            <input type="range" id="brightness" min="0" max="100" value="80" 
                   oninput="updateBrightness(this.value)">
            <span id="brightness-value">80%</span>
        </div>
        
        <div id="message"></div>
    </div>
    
    <script>
        function captureImage() {{
            const category = document.getElementById('category').value;
            const messageDiv = document.getElementById('message');
            
            messageDiv.innerHTML = '<div class="message">Capturing image...</div>';
            
            fetch('/capture', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{category: category}})
            }})
            .then(response => response.json())
            .then(data => {{
                if (data.success) {{
                    messageDiv.innerHTML = '<div class="message success">✓ ' + data.message + '</div>';
                    setTimeout(() => location.reload(), 2000);
                }} else {{
                    messageDiv.innerHTML = '<div class="message error">✗ ' + data.message + '</div>';
                }}
            }})
            .catch(error => {{
                messageDiv.innerHTML = '<div class="message error">✗ Error: ' + error + '</div>';
            }});
        }}
        
        function updateBrightness(value) {{
            document.getElementById('brightness-value').textContent = value + '%';
            
            fetch('/brightness', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{brightness: parseInt(value)}})
            }});
        }}
        
        // Auto-refresh status every 10 seconds
        setInterval(() => {{
            location.reload();
        }}, 10000);
    </script>
</body>
</html>
"""
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def generate_status_html(self, counts):
        """Generate HTML for status display"""
        html = ""
        
        for key in ['good_curve', 'good_back', 'bad_curve', 'bad_back']:
            current = counts[key]
            needed = self.SETS_NEEDED[key]
            beans_collected = current * self.BEANS_PER_SET
            total_beans = self.TARGETS[key]
            percentage = (current / needed) * 100 if needed > 0 else 0
            
            quality, side = key.split('_')
            
            html += f"""
            <div class="category">
                <strong>{quality.title()} - {side.title()}</strong><br>
                Sets: {current}/{needed} | Beans: {beans_collected}/{total_beans}
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {percentage}%"></div>
                </div>
            </div>
            """
        
        return html
    
    def serve_status(self):
        """Serve status as JSON"""
        counts = self.load_counts()
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(counts).encode())
    
    def serve_preview(self):
        """Serve camera preview page"""
        html = """
<!DOCTYPE html>
<html>
<head>
    <title>Camera Preview</title>
    <style>
        body {
            margin: 0;
            padding: 20px;
            background: #000;
            text-align: center;
        }
        h1 {
            color: white;
        }
        img {
            max-width: 100%;
            height: auto;
        }
    </style>
</head>
<body>
    <h1>📹 Live Camera Preview</h1>
    <p style="color: white;">Preview updates every 2 seconds</p>
    <img id="preview" src="" alt="Loading...">
    
    <script>
        function updatePreview() {
            const img = document.getElementById('preview');
            img.src = '/preview_image?' + new Date().getTime();
        }
        
        updatePreview();
        setInterval(updatePreview, 2000);
    </script>
</body>
</html>
"""
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def handle_capture(self):
        """Handle capture request"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode())
        
        category = data.get('category')
        counts = self.load_counts()
        
        # Validate category
        if category not in counts:
            self.send_json_response({'success': False, 'message': 'Invalid category'})
            return
        
        # Check if target reached
        if counts[category] >= self.SETS_NEEDED[category]:
            self.send_json_response({'success': False, 'message': 'Target already reached'})
            return
        
        # Capture image
        quality, side = category.split('_')
        current_set = counts[category] + 1
        
        output_dir = f"{self.BASE_DIR}/{quality}_beans/{side}"
        os.makedirs(output_dir, exist_ok=True)
        
        filename = f"{quality}_{side}_set{current_set:02d}.jpg"
        filepath = os.path.join(output_dir, filename)
        
        # Capture
        try:
            result = subprocess.run([
                "rpicam-still", "-o", filepath,
                "--width", "4608", "--height", "2592",
                "--timeout", "5000",
                "--autofocus-mode", "auto",
                "--autofocus-range", "macro",
                "--lens-position", "0.0",
                "--contrast", "1.2",
                "--sharpness", "1.8",
                "--quality", "95",
                "--nopreview"
            ], capture_output=True, timeout=10)
            
            if result.returncode == 0:
                counts[category] += 1
                self.save_counts(counts)
                
                self.send_json_response({
                    'success': True,
                    'message': f'Set {current_set} captured: {filename}'
                })
            else:
                self.send_json_response({
                    'success': False,
                    'message': 'Capture failed'
                })
        
        except Exception as e:
            self.send_json_response({
                'success': False,
                'message': str(e)
            })
    
    def handle_brightness(self):
        """Handle brightness control"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode())
        
        brightness = data.get('brightness', 80)
        
        # Send to light daemon
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(('localhost', 9999))
            sock.sendall(f"{brightness}\n".encode())
            response = sock.recv(1024).decode()
            sock.close()
            
            self.send_json_response({'success': True, 'brightness': brightness})
        except Exception as e:
            self.send_json_response({'success': False, 'message': str(e)})
    
    def send_json_response(self, data):
        """Send JSON response"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def load_counts(self):
        """Load counts from file"""
        count_file = "/home/beans/dataset_counts_final.json"
        
        if os.path.exists(count_file):
            with open(count_file, 'r') as f:
                return json.load(f)
        else:
            return {
                'good_curve': 0,
                'good_back': 0,
                'bad_curve': 0,
                'bad_back': 0
            }
    
    def save_counts(self, counts):
        """Save counts to file"""
        count_file = "/home/beans/dataset_counts_final.json"
        with open(count_file, 'w') as f:
            json.dump(counts, f, indent=2)
    
    def log_message(self, format, *args):
        """Override to reduce logging"""
        pass


def main():
    """Start web server"""
    PORT = 8080
    
    print("="*60)
    print("Coffee Bean Dataset Collector - Web Interface")
    print("="*60)
    print(f"Server starting on port {PORT}")
    print(f"\nAccess from your laptop browser:")
    print(f"  http://192.168.100.197:{PORT}")
    print(f"\nPress Ctrl+C to stop")
    print("="*60 + "\n")
    
    server = HTTPServer(('0.0.0.0', PORT), DatasetCollectorHandler)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\nShutting down server...")
        server.shutdown()


if __name__ == "__main__":
    main()
