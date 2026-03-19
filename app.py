# ==============================================================================
# GOD MODE V14.0 - DYNAMIC COOKIE HEIST + AUTO-DESTRUCT SESSIONS
# ==============================================================================
from flask import Flask, request, jsonify, render_template_string, send_file, after_this_request
import yt_dlp
import os
import tempfile
import uuid
import shutil

app = Flask(__name__)

# [HTML_UI aur baaki ka UI render code same rahega, use yahan skip nahi karna hai, apni purani HTML paste kar lena]

@app.route('/')
def home(): 
    return jsonify({"status": "God Mode V14 Engine Online"})

# ==============================================================================
# NEW MASTER LOGIC: STEP 1 - RECEIVE COOKIES & CREATE SECURE VAULT
# ==============================================================================
@app.route('/api/arm_engine', methods=['POST'])
def arm_engine_api():
    data = request.json
    if not data or 'cookie_data' not in data:
        return jsonify({"error": "No payload received"}), 400

    session_id = str(uuid.uuid4())
    temp_dir = os.path.join(tempfile.gettempdir(), session_id)
    os.makedirs(temp_dir, exist_ok=True)
    
    # Save the dynamic cookie string to a temporary file
    cookie_path = os.path.join(temp_dir, 'cookies.txt')
    with open(cookie_path, 'w') as f:
        f.write(data['cookie_data'])

    return jsonify({"session_id": session_id})

# ==============================================================================
# NEW MASTER LOGIC: STEP 2 - STREAM & SHRED (AUTO-DESTRUCT)
# ==============================================================================
@app.route('/api/cloud_download', methods=['GET'])
def cloud_download_api():
    session_id = request.args.get('session_id')
    url = request.args.get('url')
    
    if not session_id or not url: 
        return jsonify({"error": "Missing parameters"}), 400

    temp_dir = os.path.join(tempfile.gettempdir(), session_id)
    cookie_path = os.path.join(temp_dir, 'cookies.txt')
    
    if not os.path.exists(cookie_path):
        return jsonify({"error": "Session expired or invalid"}), 403

    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
        'cookiefile': cookie_path,
        'quiet': True,
        'merge_output_format': 'mp4',
        'sleep_interval_requests': 2,
        'max_sleep_interval_requests': 6
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filepath = ydl.prepare_filename(info)
            
            base, _ = os.path.splitext(filepath)
            final_path = base + ".mp4"
            if not os.path.exists(final_path): 
                final_path = filepath
                
            clean_name = os.path.basename(final_path)

        # THE SHREDDER: Permanently delete the folder and cookies after streaming
        @after_this_request
        def cleanup(response):
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception: pass
            return response

        return send_file(final_path, as_attachment=True, download_name=clean_name)

    except Exception as e:
        # Shred even if download fails to prevent memory leaks
        try: shutil.rmtree(temp_dir, ignore_errors=True) 
        except: pass
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
