# ==============================================================================
# GOD MODE V12.15.0 - CLOUD API ENABLED + DYNAMIC THEME + CODEC SYNC
# ==============================================================================
from flask import Flask, request, jsonify, render_template_string, send_file, after_this_request
import yt_dlp
import os
import tkinter as tk
from tkinter import filedialog
import gc
import time
import tempfile

app = Flask(__name__)

download_state = {
    "status": "idle",
    "percent": "0.0%",
    "downloaded": "0.0 MB",
    "total": "0.0 MB"
}

HTML_UI = """
<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>God Mode Engine V12.15.0 - Hacker Pro UI</title>
    <style>
        :root { 
            --bg-color: #f4f4f5; --text-color: #18181b; --card-bg: #ffffff; 
            --border: #d4d4d8; --accent: #16a34a; --danger: #dc2626; 
            --input-bg: #ffffff; --radius: 6px; --box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            --icon-color: #52525b; --clear-icon: #a1a1aa;
            --size-color: #2563eb; 
        }
        [data-theme="dark"] { 
            --bg-color: #09090b; --text-color: #f4f4f5; --card-bg: #18181b; 
            --border: #27272a; --accent: #22c55e; --input-bg: #09090b;
            --icon-color: #a1a1aa; --clear-icon: #52525b;
            --size-color: #22d3ee; 
        }
        
        * { box-sizing: border-box; font-family: 'Segoe UI Black', 'Segoe UI', system-ui, sans-serif; transition: background-color 0.15s, border-color 0.15s; }
        
        body { 
            background: var(--bg-color); color: var(--text-color); 
            margin: 0; padding: 0; width: 100vw; height: 100vh; 
            display: flex; flex-direction: column; overflow: hidden;
        }

        .theme-container { position: absolute; top: 15px; right: 20px; z-index: 1000; }
        .theme-toggle-btn { 
            cursor: pointer; padding: 8px; border-radius: var(--radius); 
            background: var(--card-bg); border: 1px solid var(--border); 
            color: var(--text-color); display: flex; align-items: center; justify-content: center;
        }
        .theme-toggle-btn svg { width: 22px; height: 22px; fill: none; stroke: currentColor; stroke-width: 2; }
        #icon-moon { display: none; } [data-theme="light"] #icon-moon { display: block; } [data-theme="light"] #icon-sun { display: none; }

        .main-container { 
            width: 100%; height: 100%; padding: 25px 40px;
            display: flex; flex-direction: column; align-items: center;
        }

        .top-dashboard { 
            display: flex; gap: 20px; width: 100%; max-width: 1500px; 
            margin-bottom: 20px; align-items: stretch; justify-content: center;
        }

        .input-group { position: relative; flex: 1; max-width: 850px; }
        .url-box { 
            width: 100%; height: 100%; padding: 22px 180px 22px 50px; 
            background: var(--input-bg); border: 3px solid var(--border); 
            color: var(--text-color); border-radius: var(--radius); outline: none; 
            font-size: 18px; font-weight: 400; 
            box-shadow: var(--box-shadow);
        }
        .url-box:focus { border-color: var(--accent); }
        .clear-btn { 
            position: absolute; left: 12px; top: 50%; transform: translateY(-50%); 
            cursor: pointer; color: var(--clear-icon); display: flex; align-items: center; z-index: 10; 
        }
        .clear-btn:hover { color: var(--danger); }
        
        .dl-master-trigger {
            position: absolute; right: 8px; top: 50%; transform: translateY(-50%);
            background: var(--accent); color: white; border: none; padding: 14px 32px;
            border-radius: var(--radius); cursor: pointer; font-weight: 900; font-size: 16px; display: flex; align-items: center;
        }
        .dl-master-trigger:hover { background: #15803d; }

        .status-panel {
            width: 320px; background: var(--card-bg); border: 2px solid var(--border);
            border-radius: var(--radius); display: flex; align-items: center; justify-content: center;
            font-weight: 900; color: var(--accent); font-size: 14px; letter-spacing: 1px; 
            text-transform: uppercase; box-shadow: var(--box-shadow); text-align: center; padding: 15px;
            flex-shrink: 0;
        }

        #mediaBox { 
            width: 100%; max-width: 1500px; display: flex; gap: 30px; 
            height: calc(100vh - 110px); align-items: start; 
        }

        .thumb-col { 
            flex: 0 0 500px; 
            display: flex; flex-direction: column; gap: 15px; 
            height: 100%; overflow-y: auto; padding-right: 5px;
        }
        
        .thumb-img { 
            width: 100%; border-radius: var(--radius); border: 2px solid var(--border); 
            object-fit: cover; aspect-ratio: 16/9; box-shadow: var(--box-shadow);
            flex-shrink: 0;
        }

        .duration-badge {
            background: var(--card-bg); border: 1px solid var(--border);
            color: var(--accent); font-weight: 900; font-size: 18px; letter-spacing: 0.5px;
            padding: 10px; border-radius: var(--radius); text-align: center;
            box-shadow: var(--box-shadow); flex-shrink: 0; text-transform: uppercase;
        }

        .right-col { 
            flex: 1; display: flex; flex-direction: column; min-width: 0; 
            height: 100%; gap: 20px;
        }

        .header-meta {
            display: flex; flex-direction: row; gap: 20px; background: var(--card-bg); 
            padding: 15px 20px; border: 1px solid var(--border); border-radius: var(--radius);
            align-items: stretch; box-shadow: var(--box-shadow); flex-shrink: 0;
        }
        
        .title-editor { 
            background: transparent; border: 1px dashed var(--border); color: var(--text-color);
            font-size: 16px; font-weight: 400; 
            width: 100%; resize: none; padding: 12px; flex: 1;
            min-height: 100px; 
        }
        .title-editor:focus { outline: none; border-color: var(--accent); }

        .grids-wrapper { 
            display: grid; 
            grid-template-columns: 1fr 1fr; 
            gap: 20px; flex: 1; min-height: 0; align-items: start; 
            overflow-y: auto; padding-right: 5px;
        }
        
        .section-box { 
            background: var(--card-bg); border: 1px solid var(--border); 
            border-radius: var(--radius); padding: 15px; display: flex; flex-direction: column;
            box-shadow: var(--box-shadow); height: max-content;
        }
        
        .grid-header { 
            font-size: 22px; font-weight: 900; margin-bottom: 15px; 
            display: flex; align-items: center; justify-content: center; gap: 10px; 
            border-bottom: 2px solid var(--border); padding-bottom: 10px; text-transform: uppercase;
        }

        .btn-scroll-area { 
            display: grid; grid-template-columns: 1fr 1fr; gap: 12px; align-content: start;
        }
        
        .format-btn { 
            display: flex; justify-content: center; align-items: center; flex-direction: row;
            padding: 14px 10px; 
            background: var(--bg-color); border: 2px solid var(--border);
            border-radius: var(--radius); cursor: pointer; color: inherit; text-decoration: none; text-align: center; gap: 8px;
        }
        .format-btn:hover { background: var(--accent); border-color: var(--accent); }
        .format-btn:hover .f-label, .format-btn:hover .f-size, .format-btn:hover .b-rate { color: white !important; }
        
        .format-btn.compact { padding: 10px 8px; }

        .f-label { font-weight: 900; font-size: 16px; transition: color 0.15s; }
        .f-size { font-size: 15px; font-weight: 900; color: var(--size-color); opacity: 0.95; transition: color 0.15s; }
        
        .b-rate { 
            font-size: 11px; font-weight: 800; color: var(--icon-color); 
            letter-spacing: 0.5px; text-transform: uppercase; display: flex; align-items: center;
            transition: color 0.15s;
        }
        
        .res-badge { font-size: 12px; font-weight: 800; opacity: 0.85; margin-left: 3px; }

        .skeleton { opacity: 0.35; pointer-events: none; border: 2px dashed var(--icon-color); background: transparent !important; }

        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }
    </style>
</head>
<body>

    <div class="theme-container"><button class="theme-toggle-btn" onclick="toggleTheme()"><svg id="icon-sun" viewBox="0 0 24 24"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg><svg id="icon-moon" viewBox="0 0 24 24"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg></button></div>

    <div class="main-container">
        
        <div class="top-dashboard">
            <div class="input-group">
                <div class="clear-btn" onclick="clearUrl()">
                    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                </div>
                <input type="text" id="ytLink" class="url-box" placeholder="Paste YouTube URL Here..." oninput="debounceTrigger()">
                <button class="dl-master-trigger" onclick="pasteAndScan()">
                    <svg style="vertical-align:middle; margin-right:8px;" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path><rect x="8" y="2" width="8" height="4" rx="1" ry="1"></rect></svg>
                    PASTE
                </button>
            </div>
            
            <div id="status" class="status-panel">CORE ENGINE STANDBY</div>
        </div>

        <div id="mediaBox">
            
            <div class="thumb-col">
                <img id="mThumb" class="thumb-img" src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='500' height='281' style='background:%2327272a'%3E%3Cpath fill='%2352525b' d='M250 105c-20 0-38 18-38 38s18 38 38 38 38-18 38-38-18-38-38-38zm-12 52v-28l28 14-28 14z'/%3E%3C/svg%3E" alt="Thumbnail">
                
                <div id="mDuration" class="duration-badge">Duration: 00:00</div>
                
                <div class="section-box">
                    <div class="grid-header" style="color:#3b82f6">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z"/></svg>
                        AUDIO (MP3)
                    </div>
                    <div id="audioGrid" class="btn-scroll-area">
                        </div>
                </div>
            </div>

            <div class="right-col">
                <div class="header-meta">
                    <textarea id="mTitle" class="title-editor" readonly>AWAITING MEDIA STREAM...</textarea>
                </div>

                <div class="grids-wrapper">
                    <div class="section-box">
                        <div class="grid-header" style="color:var(--accent)">
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M17 10.5V7c0-.55-.45-1-1-1H4c-.55 0-1 .45-1 1v10c0 .55.45 1 1 1h12c.55 0 1-.45 1-1v-3.5l4 4v-11l-4 4z"/></svg>
                            VIDEO (MP4)
                        </div>
                        <div id="mp4Grid" class="btn-scroll-area">
                            </div>
                    </div>

                    <div class="section-box">
                        <div class="grid-header" style="color:#f59e0b">
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M21 3H3c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h18c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-9 9l-5-5h10l-5 5z"/></svg>
                            VIDEO (WEBM)
                        </div>
                        <div id="webmGrid" class="btn-scroll-area">
                            </div>
                    </div>
                </div>
            </div>

        </div>
    </div>

    <script>
        let timeout; let pollTimer = null;
        let globalDurationSec = 0;

        function renderSkeletons() {
            const skelTemplate = `
                <div class="format-btn skeleton">
                    <div style="display:flex; flex-direction:column; align-items:center; gap:4px; width:100%;">
                        <div style="display:flex; align-items:baseline; justify-content:center; gap:6px; flex-wrap:wrap;">
                            <span class="f-label">HQ</span>
                            <span class="f-size">(0.00 MB)</span>
                        </div>
                        <div class="b-rate">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" style="margin-right:4px;"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>
                            0 kbps
                        </div>
                    </div>
                </div>`;
            const skelBlock = skelTemplate.repeat(6);
            document.getElementById('mp4Grid').innerHTML = skelBlock; 
            document.getElementById('webmGrid').innerHTML = skelBlock;
            
            const skelAudioTemplate = `
                <div class="format-btn compact skeleton">
                    <div style="display:flex; flex-direction:column; align-items:center; gap:4px; width:100%;">
                        <div style="display:flex; align-items:baseline; justify-content:center; gap:6px; flex-wrap:wrap;">
                            <span class="f-label">AUDIO</span>
                            <span class="f-size">(0.00 MB)</span>
                        </div>
                        <div class="b-rate">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" style="margin-right:4px;"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>
                            0 kbps
                        </div>
                    </div>
                </div>`;
            document.getElementById('audioGrid').innerHTML = skelAudioTemplate.repeat(4);
        }
        
        window.onload = renderSkeletons;

        function debounceTrigger() { 
            clearTimeout(timeout); 
            timeout = setTimeout(() => { if(document.getElementById('ytLink').value.length > 10) runScan(); }, 600); 
        }

        async function pasteAndScan() {
            try {
                const text = await navigator.clipboard.readText();
                if(text.length > 5) { 
                    document.getElementById('ytLink').value = text; 
                    runScan(); 
                }
            } catch (err) { 
                document.getElementById('status').innerText = "PASTE MANUALLY"; 
                document.getElementById('status').style.color = "var(--danger)"; 
                document.getElementById('status').style.borderColor = "var(--danger)";
            }
        }

        function clearUrl() {
            document.getElementById('ytLink').value = '';
            document.getElementById('status').innerText = 'CORE ENGINE STANDBY'; 
            document.getElementById('status').style.color = "var(--accent)";
            document.getElementById('status').style.borderColor = "var(--border)";
            document.getElementById('mTitle').value = 'AWAITING MEDIA STREAM...'; 
            document.getElementById('mTitle').setAttribute('readonly', 'true');
            document.getElementById('mDuration').innerText = 'Duration: 00:00';
            document.getElementById('mThumb').src = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='500' height='281' style='background:%2327272a'%3E%3Cpath fill='%2352525b' d='M250 105c-20 0-38 18-38 38s18 38 38 38 38-18 38-38-18-38-38-38zm-12 52v-28l28 14-28 14z'/%3E%3C/svg%3E";
            renderSkeletons();
        }

        function toggleTheme() { 
            const html = document.documentElement; 
            const isDark = html.getAttribute('data-theme') === 'dark'; 
            html.setAttribute('data-theme', isDark ? 'light' : 'dark'); 
        }

        async function runScan() {
            const val = document.getElementById('ytLink').value;
            if(!val) return;
            const statusEl = document.getElementById('status');
            statusEl.innerText = "FETCHING META..."; 
            statusEl.style.color = "var(--accent)";
            statusEl.style.borderColor = "var(--accent)";
            
            try {
                const res = await fetch('/api/scan?url=' + encodeURIComponent(val));
                const data = await res.json();
                if(data.error) throw new Error(data.error);

                document.getElementById('mTitle').value = data.title; 
                document.getElementById('mTitle').removeAttribute('readonly');
                document.getElementById('mThumb').src = data.thumbnail;
                document.getElementById('mDuration').innerText = "Duration: " + data.duration;
                globalDurationSec = data.duration_sec || 0;

                buildGrid('mp4Grid', data.mp4, 'video'); 
                buildGrid('webmGrid', data.webm, 'video');
                buildAudioGrid();

                statusEl.innerText = "SYSTEM ARMED";
            } catch (e) { 
                statusEl.innerText = "BAN DETECTED"; 
                statusEl.style.color = "var(--danger)"; 
                statusEl.style.borderColor = "var(--danger)";
            }
        }

        function buildGrid(id, list, type) {
            const grid = document.getElementById(id); grid.innerHTML = "";
            list.forEach(item => {
                const btn = document.createElement('div'); btn.className = 'format-btn';
                const size = item.size ? (item.size / (1024*1024)).toFixed(2) + " MB" : "N/A";
                const bitrate = item.bitrate || "AUTO VBR";
                
                let badge = "";
                if(item.res === '720p' || item.res === '1080p') badge = " <span class='res-badge'>HD</span>";
                else if(item.res === '1440p') badge = " <span class='res-badge'>2K</span>";
                else if(item.res === '2160p') badge = " <span class='res-badge'>4K</span>";

                btn.innerHTML = `
                    <div style="display:flex; flex-direction:column; align-items:center; gap:4px; width:100%;">
                        <div style="display:flex; align-items:baseline; justify-content:center; gap:6px; flex-wrap:wrap;">
                            <span class="f-label">${item.res}${badge}</span>
                            <span class="f-size">(${size})</span>
                        </div>
                        <div class="b-rate">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" style="margin-right:4px;"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>
                            ${bitrate}
                        </div>
                    </div>`;
                    
                btn.onclick = () => startExtraction(item.f_id, item.ext, '0');
                grid.appendChild(btn);
            });
        }

        function buildAudioGrid() {
            const grid = document.getElementById('audioGrid'); grid.innerHTML = "";
            
            const audioOpts = [
                { label: '48K (mp3)', ext: 'mp3', br: '48' },
                { label: '128K (m4a)', ext: 'm4a', br: '128' }, 
                { label: '128K (mp3)', ext: 'mp3', br: '128' },
                { label: '256K (mp3)', ext: 'mp3', br: '256' }
            ];
            
            audioOpts.forEach(opt => {
                const btn = document.createElement('div'); btn.className = 'format-btn compact';
                let sizeStr = "N/A";
                if(globalDurationSec > 0) {
                    const sizeMB = (parseInt(opt.br) * globalDurationSec) / 8192;
                    sizeStr = sizeMB.toFixed(2) + " MB";
                }
                
                btn.innerHTML = `
                    <div style="display:flex; flex-direction:column; align-items:center; gap:4px; width:100%;">
                        <div style="display:flex; align-items:baseline; justify-content:center; gap:6px; flex-wrap:wrap;">
                            <span class="f-label">${opt.label}</span>
                            <span class="f-size">(${sizeStr})</span>
                        </div>
                        <div class="b-rate">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" style="margin-right:4px;"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>
                            ${opt.br} kbps
                        </div>
                    </div>`;
                btn.onclick = () => startExtraction('bestaudio', opt.ext, opt.br);
                grid.appendChild(btn);
            });
        }

        async function trackProgress() {
            try {
                const res = await fetch('/api/progress'); const data = await res.json();
                const statusEl = document.getElementById('status');
                if (data.status === 'downloading') {
                    statusEl.innerText = `${data.percent} ( ${data.downloaded} )`;
                    statusEl.style.color = "var(--accent)";
                } else if (data.status === 'muxing') {
                    statusEl.innerText = "MERGING A/V...";
                    statusEl.style.color = "#f59e0b";
                    statusEl.style.borderColor = "#f59e0b";
                }
            } catch (e) {}
        }

        async function startExtraction(fid, ext, bitrate) {
            const cleanTitle = document.getElementById('mTitle').value.replace(/[^a-zA-Z0-9 ]/g, "");
            const statusEl = document.getElementById('status');
            statusEl.style.color = "#f59e0b"; statusEl.style.borderColor = "#f59e0b";
            statusEl.innerText = "AWAITING PATH...";
            
            if(pollTimer) clearInterval(pollTimer);
            pollTimer = setInterval(trackProgress, 800);

            try {
                const resp = await fetch('/api/download', {
                    method: 'POST', headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ url: document.getElementById('ytLink').value, fid, title: cleanTitle, ext, bitrate })
                });
                clearInterval(pollTimer);
                const res = await resp.json();
                if(res.status === "success") { 
                    statusEl.innerText = "SAVED"; 
                    statusEl.style.color = "var(--accent)"; 
                    statusEl.style.borderColor = "var(--accent)";
                } else { 
                    statusEl.innerText = res.status === "cancelled" ? "ABORTED" : "MUX ERROR"; 
                    statusEl.style.color = "var(--danger)"; 
                    statusEl.style.borderColor = "var(--danger)";
                }
            } catch(e) { 
                if(pollTimer) clearInterval(pollTimer); 
                statusEl.innerText = "CRITICAL FAILURE"; 
                statusEl.style.color = "var(--danger)"; 
                statusEl.style.borderColor = "var(--danger)";
            }
        }
    </script>
</body>
</html>
"""

# ------------------------------------------------------------------------------
# BACKEND
# ------------------------------------------------------------------------------
@app.route('/')
def home(): return render_template_string(HTML_UI)

@app.route('/api/scan')
def scan_api():
    url = request.args.get('url')
    ydl_opts = {
        'quiet': True, 'no_warnings': True, 'cookiefile': 'cookies.txt',
        'sleep_interval_requests': 2, 'max_sleep_interval_requests': 6,   
        'ignoreerrors': True, 'extract_flat': False
    } 
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info: return jsonify({"error": "No data returned (Possible strict CAPTCHA block)"}), 500

            mp4_list, webm_list = [], []
            res_list = [144, 240, 360, 480, 720, 1080, 1440, 2160]
            
            for f in info.get('formats', []):
                h = f.get('height')
                ext = f.get('ext')
                if h in res_list:
                    if ext == 'mp4': audio_query = "bestaudio[ext=m4a]/bestaudio" 
                    else: audio_query = "bestaudio[ext=webm]/bestaudio" 
                        
                    vbr = f.get('vbr') or f.get('tbr') or 0
                    bitrate_str = f"{int(vbr)} kbps" if vbr > 0 else "AUTO VBR"
                    vid_data = {"f_id": f"{f['format_id']}+{audio_query}", "res": f"{h}p", "size": f.get('filesize') or f.get('filesize_approx'), "ext": ext, "bitrate": bitrate_str}
                    if ext == 'mp4': mp4_list.append(vid_data)
                    elif ext == 'webm': webm_list.append(vid_data)

            mp4_sorted = sorted(mp4_list, key=lambda x: int(x['res'][:-1]))
            webm_sorted = sorted(webm_list, key=lambda x: int(x['res'][:-1]))
            def unique_res(v_list):
                seen = set(); res = []
                for v in v_list:
                    if v['res'] not in seen: seen.add(v['res']); res.append(v)
                return res

            return jsonify({"title": info.get('title', 'Unknown Title'), "thumbnail": info.get('thumbnail', ''), "duration": info.get('duration_string', '00:00'), "duration_sec": info.get('duration', 0), "mp4": unique_res(mp4_sorted), "webm": unique_res(webm_sorted)})
    except Exception as e: return jsonify({"error": str(e)}), 500


@app.route('/api/progress')
def progress_api():
    global download_state
    return jsonify(download_state)

def dlp_progress_hook(d):
    global download_state
    if d['status'] == 'downloading':
        total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
        down = d.get('downloaded_bytes', 0)
        if total > 0:
            pct = (down / total) * 100
            download_state['percent'] = f"{pct:.1f}%"
            download_state['downloaded'] = f"{down / (1024*1024):.2f} MB"
            download_state['total'] = f"{total / (1024*1024):.2f} MB"
            download_state['status'] = 'downloading'
    elif d['status'] == 'finished':
        download_state['status'] = 'muxing'

# --- ORIGINAL ROUTE (For Local PC) ---
@app.route('/api/download', methods=['POST'])
def download_api():
    global download_state
    data = request.json
    download_state = {"status": "idle", "percent": "0.0%", "downloaded": "0.0 MB", "total": "0.0 MB"}
    
    root = tk.Tk(); root.attributes("-topmost", True); root.withdraw()
    path = filedialog.asksaveasfilename(initialfile=f"{data['title']}.{data['ext']}", defaultextension=f".{data['ext']}")
    root.destroy()
    
    if not path: return jsonify({"status": "cancelled"})
    bitrate = data.get('bitrate', '192')
    ydl_opts = {'format': data['fid'], 'outtmpl': path, 'cookiefile': 'cookies.txt', 'quiet': True, 'noprogress': True, 'progress_hooks': [dlp_progress_hook], 'sleep_interval_requests': 2, 'max_sleep_interval_requests': 6, 'merge_output_format': data['ext'] if data['ext'] in ['mp4', 'webm'] else None, 'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': data['ext'],'preferredquality': bitrate}] if data['ext'] in ['mp3', 'm4a'] else []}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl: ydl.download([data['url']])
        gc.collect()
        return jsonify({"status": "success", "path": path})
    except Exception as e: return jsonify({"status": "error", "message": str(e)}), 500


# ==============================================================================
# NEW MASTER FIX: DIRECT CLOUD STREAMING ROUTE (FOR CHROME EXTENSION)
# ==============================================================================
@app.route('/api/cloud_download', methods=['GET'])
def cloud_download_api():
    url = request.args.get('url')
    if not url: return jsonify({"error": "No URL provided"}), 400

    # Create a temporary directory that auto-deletes
    temp_dir = tempfile.mkdtemp()
    
    # We will strictly lock it to Best MP4 Quality + M4A Audio for universal compatibility
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
        'cookiefile': 'cookies.txt',
        'quiet': True,
        'merge_output_format': 'mp4',
        'sleep_interval_requests': 2,
        'max_sleep_interval_requests': 6
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filepath = ydl.prepare_filename(info)
            
            # Ensure it sends .mp4 if FFmpeg merged it
            base, _ = os.path.splitext(filepath)
            final_path = base + ".mp4"
            if not os.path.exists(final_path): 
                final_path = filepath
                
            clean_name = os.path.basename(final_path)

        # Garbage Collector: Delete file from Cloud Server after sending to Extension
        @after_this_request
        def cleanup(response):
            try:
                os.remove(final_path)
                os.rmdir(temp_dir)
            except Exception: pass
            return response

        # Stream the file directly to the Chrome Extension
        return send_file(final_path, as_attachment=True, download_name=clean_name)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # OS will automatically assign a Port in Cloud (e.g., Render/AWS)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)