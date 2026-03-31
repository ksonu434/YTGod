# =======================================================================================
# GOD MODE V12.15.1 - CLOUD EDITION (NAT ROUTING FIXED)
# =======================================================================================
from flask import Flask, request, jsonify, render_template_string, send_file
from yt_dlp.utils import download_range_func
import yt_dlp
import os
import gc
import time
import re  

app = Flask(__name__)

download_states = {}
system_logs = [] 

class GodModeLogger(object):
    def debug(self, msg):
        system_logs.append({"type": "info", "msg": msg, "time": time.strftime("%H:%M:%S")})
        if len(system_logs) > 150: system_logs.pop(0)

    def warning(self, msg):
        system_logs.append({"type": "warning", "msg": msg, "time": time.strftime("%H:%M:%S")})
        if len(system_logs) > 150: system_logs.pop(0)

    def error(self, msg):
        system_logs.append({"type": "error", "msg": msg, "time": time.strftime("%H:%M:%S")})
        if len(system_logs) > 150: system_logs.pop(0)

HTML_UI = r"""
<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>God Mode Engine V12.15.1 - Hacker Pro UI</title>
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
        
        * { box-sizing: border-box; font-family: 'Segoe UI Black', 'Segoe UI', system-ui, sans-serif; transition: all 0.3s ease; scrollbar-width: none; }
        ::-webkit-scrollbar { display: none; width: 0px; background: transparent; }
        
        body { background: var(--bg-color); color: var(--text-color); margin: 0; padding: 0; width: 100vw; height: 100vh; display: flex; flex-direction: column; overflow-x: hidden; }
        .main-container { width: 100%; height: 100%; padding: 25px 40px; display: flex; flex-direction: column; align-items: center; }

        .settings-panel { position: fixed; top: 0; left: 0; width: 360px; height: 100vh; background: var(--card-bg); border-right: 2px solid var(--border); box-shadow: 10px 0 30px rgba(0,0,0,0.4); z-index: 9999; padding: 30px 25px; display: flex; flex-direction: column; gap: 20px; transform: translateX(-100%); opacity: 0; pointer-events: none; transition: transform 0.35s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.3s ease; }
        .settings-panel.open { transform: translateX(0); opacity: 1; pointer-events: auto; }
        .settings-header { display: flex; justify-content: space-between; align-items: center; font-size: 20px; font-weight: 900; color: var(--accent); border-bottom: 2px solid var(--border); padding-bottom: 15px; }
        .close-settings { background: none; border: none; color: var(--text-color); cursor: pointer; display: flex; padding: 5px; }
        .close-settings:hover { color: var(--danger); transform: scale(1.1); }
        
        .toggle-row { display: flex; justify-content: space-between; align-items: center; font-size: 14px; font-weight: 800; color: var(--text-color); cursor: pointer; padding: 10px 0; border-bottom: 1px dashed var(--border); }
        .toggle-row input { display: none; }
        .toggle-slider { position: relative; width: 50px; height: 26px; background: var(--border); border-radius: 30px; transition: 0.3s; flex-shrink: 0; }
        .toggle-slider::after { content: ""; position: absolute; top: 3px; left: 4px; width: 20px; height: 20px; background: white; border-radius: 50%; transition: 0.3s; box-shadow: 0 2px 4px rgba(0,0,0,0.2); }
        .toggle-row input:checked + .toggle-slider { background: var(--accent); }
        .toggle-row input:checked + .toggle-slider::after { transform: translateX(22px); }

        .glass-modal { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(0,0,0,0.6); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); z-index: 10000; display: flex; justify-content: center; align-items: center; opacity: 0; pointer-events: none; transition: 0.3s ease; }
        .glass-modal.active { opacity: 1; pointer-events: auto; }
        .glass-content { background: rgba(24, 24, 27, 0.85); border: 1px solid rgba(255,255,255,0.1); padding: 25px; border-radius: 12px; box-shadow: 0 10px 40px rgba(0,0,0,0.5); color: white; max-width: 700px; width: 95%; transform: translateY(20px); transition: 0.3s ease; }
        .glass-modal.active .glass-content { transform: translateY(0); }
        
        #liveLogContainer { font-family: Consolas, monospace; font-size: 13px; line-height: 1.5; background: #000; color: #4ade80; padding: 15px; border-radius: 8px; height: 400px; overflow-y: auto; border: 1px solid #3f3f46; }
        .log-time { color: #a1a1aa; margin-right: 8px; }
        .log-error { color: #f87171; }
        .log-warning { color: #fbbf24; }
        .log-info { color: #4ade80; }

        .top-dashboard { display: flex; gap: 15px; width: 100%; max-width: 100%; margin-bottom: 20px; align-items: stretch; justify-content: flex-start; height: 70px; }
        .menu-trigger-btn { cursor: pointer; border-radius: var(--radius); padding: 0; background: var(--card-bg); border: 2px solid var(--border); color: var(--text-color); display: flex; align-items: center; justify-content: center; box-shadow: var(--box-shadow); flex-shrink: 0; width: 70px; }
        .menu-trigger-btn:hover { border-color: var(--accent); color: var(--accent); }
        .input-group { position: relative; flex: 3; max-width: 1400px; } 
        .clear-btn { position: absolute; left: 15px; top: 50%; transform: translateY(-50%); cursor: pointer; color: var(--clear-icon); display: flex; align-items: center; z-index: 10; }
        .clear-btn:hover { color: var(--danger); transform: translateY(-50%) scale(1.1); }
        .url-box { width: 100%; height: 100%; padding: 0 160px 0 50px; background: var(--input-bg); border: 3px solid var(--border); color: var(--text-color); border-radius: var(--radius); outline: none; font-size: 18px; font-weight: 400; box-shadow: var(--box-shadow); text-align: left; display: block; line-height: normal; }
        .url-box:focus { border-color: var(--accent); }
        .dl-master-trigger { position: absolute; right: 8px; top: 50%; transform: translateY(-50%); background: var(--accent); color: white; border: none; padding: 0 32px; height: calc(100% - 16px); border-radius: var(--radius); cursor: pointer; font-weight: 900; font-size: 16px; display: flex; align-items: center; justify-content: center; }
        .dl-master-trigger:hover { background: #15803d; transform: translateY(-50%) scale(1.02); }
        .status-panel { flex: 2; background: var(--card-bg); border: 2px solid var(--border); border-radius: var(--radius); display: flex; align-items: center; justify-content: center; font-weight: 900; color: var(--accent); font-size: 18px; letter-spacing: 2px; text-transform: uppercase; box-shadow: var(--box-shadow); text-align: center; padding: 0 20px; }

        #mediaBox { width: 100%; display: flex; gap: 30px; height: calc(100vh - 135px); align-items: start; padding-left: 5px; padding-right: 5px; }
        .thumb-col { flex: 0 0 500px; display: flex; flex-direction: column; gap: 15px; height: 100%; overflow-y: auto; padding-right: 5px; }
        .thumb-img { width: 100%; border-radius: var(--radius); border: 2px solid var(--border); object-fit: cover; aspect-ratio: 16/9; box-shadow: var(--box-shadow); flex-shrink: 0; }
        .right-col { flex: 1; display: flex; flex-direction: column; min-width: 0; height: 100%; gap: 20px; }
        .header-meta { display: flex; flex-direction: row; gap: 20px; background: var(--card-bg); padding: 15px 20px; border: 2px solid #8b5cf6; border-radius: var(--radius); align-items: stretch; box-shadow: var(--box-shadow); flex-shrink: 0; }
        .title-editor { background: transparent; border: 1px dashed var(--border); color: var(--text-color); font-size: 16px; font-weight: 400; width: 100%; resize: none; padding: 12px; flex: 1; min-height: 100px; }
        .title-editor:focus { outline: none; border-color: var(--accent); background: var(--bg-color); }
        .duration-badge { background: var(--card-bg); border: 2px solid #10b981; color: var(--accent); font-weight: 900; font-size: 18px; letter-spacing: 0.5px; padding: 10px 20px; border-radius: var(--radius); text-align: center; box-shadow: var(--box-shadow); flex-shrink: 0; display: flex; align-items: center; justify-content: center; min-width: 150px; }

        .grids-wrapper { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; flex: 1; min-height: 0; align-items: start; overflow-y: auto; padding-right: 5px; }
        .section-box { background: var(--card-bg); border: 2px solid var(--border); border-radius: var(--radius); padding: 15px; display: flex; flex-direction: column; box-shadow: var(--box-shadow); height: max-content; transition: opacity 0.3s; }
        .grid-header { font-size: 22px; font-weight: 900; margin-bottom: 15px; display: flex; align-items: center; justify-content: center; gap: 10px; border-bottom: 2px solid var(--border); padding-bottom: 10px; text-transform: uppercase; }
        .btn-scroll-area { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; align-content: start; }
        .format-btn { display: flex; justify-content: center; align-items: center; flex-direction: row; padding: 14px 10px; background: var(--bg-color); border: 2px solid var(--border); border-radius: var(--radius); cursor: pointer; color: inherit; text-align: center; gap: 8px; }
        .format-btn:hover { background: var(--accent); border-color: var(--accent); transform: translateY(-2px); box-shadow: 0 4px 12px rgba(22, 163, 74, 0.2); }
        .format-btn:hover .f-label, .format-btn:hover .f-size, .format-btn:hover .b-rate { color: white !important; }
        .format-btn.compact { padding: 10px 8px; }
        .f-label { font-weight: 900; font-size: 16px; transition: color 0.15s; }
        .f-size { font-size: 15px; font-weight: 900; color: var(--size-color); opacity: 0.95; transition: color 0.15s; }
        .b-rate { font-size: 11px; font-weight: 800; color: var(--icon-color); letter-spacing: 0.5px; text-transform: uppercase; display: flex; align-items: center; transition: color 0.15s; }
        .res-badge { font-size: 12px; font-weight: 800; opacity: 0.85; margin-left: 3px; }
        .skeleton { opacity: 0.35; pointer-events: none; border: 2px dashed var(--icon-color); background: transparent !important; }

        @media (max-width: 1024px) {
            .top-dashboard { flex-wrap: wrap; padding-left: 0; height: auto; gap: 10px; }
            .menu-trigger-btn { width: 55px; height: 55px; }
            .input-group { flex: 1; min-width: 60%; height: 55px; }
            .status-panel { flex: 1; min-width: 100%; height: 55px; font-size: 14px; padding: 0 10px; }
            .url-box { padding: 0 110px 0 45px; font-size: 16px; text-align: left; }
            .clear-btn { left: 12px; }
            .dl-master-trigger { right: 6px; padding: 0 20px; font-size: 14px; }
            body { overflow-y: auto; height: auto; }
            .main-container { padding: 15px; }
            #mediaBox { display: flex; flex-direction: column; height: auto; overflow: visible; padding: 0; gap: 15px; }
            .thumb-col, .right-col, .grids-wrapper { display: contents; } 
            #mThumb { order: 1; margin-bottom: 0; width: 100%; height: auto; }
            #metaSection { order: 2; padding: 10px; align-items: center; gap: 10px; flex-wrap: nowrap; width: 100%; }
            #trimSection { order: 3; width: 100%; }
            #audioSection { order: 4; width: 100%; }
            #mp4Section { order: 5; width: 100%; }
            #webmSection { order: 6; width: 100%; }
            .title-editor { min-height: 55px; flex: 1; font-size: 15px; padding: 10px; }
            .duration-badge { min-width: auto; flex: 0 0 120px; height: 55px; font-size: 15px; padding: 0 10px; }
        }
    </style>
</head>
<body>
    <div id="errorModal" class="glass-modal">
        <div class="glass-content">
            <div style="display:flex; justify-content:space-between; border-bottom: 1px solid rgba(255,255,255,0.2); padding-bottom: 10px; margin-bottom: 15px;">
                <h3 style="margin:0; color: #60a5fa; display:flex; align-items:center; gap:8px;">
                    <web-icon name="view"></web-icon> ULTIMATE ERROR ENCYCLOPEDIA
                </h3>
                <button onclick="closeErrorModal()" style="background:none; border:none; color:white; cursor:pointer;"><web-icon name="close"></web-icon></button>
            </div>
            <div style="font-family: monospace; font-size: 14px; line-height: 1.6; color: #e2e8f0; max-height: 65vh; overflow-y: auto; padding-right: 10px;">
                <b style="color:#f87171;">[01] Network Armor Active (NAT Fixed)</b><br>
                <span style="color:#4ade80;">[FIX]</span> Docker NAT routing collision fixed. IPv4 is forced safely without binding to 0.0.0.0.<br><br>
                <b style="color:#f87171;">[02] Sign in to confirm you're not a bot</b><br>
                <span style="color:#4ade80;">[FIX]</span> YouTube blocked the cloud IP. Upload 'cookies.txt' to HF Files to fix.<br><br>
                <b style="color:#f87171;">[03] Missing Qualities / n-challenge failed</b><br>
                <span style="color:#4ade80;">[FIX]</span> Node.js environment is handled by Docker.<br><br>
            </div>
        </div>
    </div>

    <div id="terminalModal" class="glass-modal">
        <div class="glass-content" style="max-width: 800px;">
            <div style="display:flex; justify-content:space-between; border-bottom: 1px solid rgba(255,255,255,0.2); padding-bottom: 10px; margin-bottom: 15px;">
                <h3 style="margin:0; color: #fbbf24; display:flex; align-items:center; gap:8px;">
                    <web-icon name="terminal"></web-icon> LIVE CLOUD TERMINAL
                </h3>
                <button onclick="closeTerminalModal()" style="background:none; border:none; color:white; cursor:pointer;"><web-icon name="close"></web-icon></button>
            </div>
            <div id="liveLogContainer">
                <div class="log-info"><span class="log-time">[00:00:00]</span> SYSTEM: Engine Initialized. Listening for logs...</div>
            </div>
        </div>
    </div>

    <div id="settingsPanel" class="settings-panel">
        <div class="settings-header">
            <div style="display:flex; align-items:center; gap:10px;">
                <web-icon name="menu"></web-icon> ENGINE SETTINGS
            </div>
            <button class="close-settings" onclick="toggleSettings()" title="Close"><web-icon name="close"></web-icon></button>
        </div>
        <label class="toggle-row"><span style="display:flex; align-items:center; gap:10px;"><web-icon name="moon"></web-icon> DARK THEME</span><input type="checkbox" id="toggleThemeSwitch" onchange="toggleTheme()" checked><span class="toggle-slider"></span></label>
        <label class="toggle-row"><span style="display:flex; align-items:center; gap:10px; color:#fbbf24;"><web-icon name="zap"></web-icon> FAST DOWNLOAD ENGINE</span><input type="checkbox" id="toggleFastDL" onchange="updateSettings()"><span class="toggle-slider"></span></label>
        <label class="toggle-row"><span style="display:flex; align-items:center; gap:10px;"><web-icon name="playlist"></web-icon> PLAYLIST MODE</span><input type="checkbox" id="togglePlaylist" onchange="updateSettings()"><span class="toggle-slider"></span></label>
        <label class="toggle-row"><span style="display:flex; align-items:center; gap:10px;"><web-icon name="trim"></web-icon> TRIM MODULE</span><input type="checkbox" id="toggleTrim" onchange="updateSettings()"><span class="toggle-slider"></span></label>
        <label class="toggle-row"><span style="display:flex; align-items:center; gap:10px;"><web-icon name="webm"></web-icon> WEBM FORMAT</span><input type="checkbox" id="toggleWebm" checked onchange="updateSettings()"><span class="toggle-slider"></span></label>
        <div style="margin-top: auto; border-top: 1px dashed var(--border); padding-top: 20px;">
            <div style="font-size: 13px; color: var(--icon-color); font-weight: 900; margin-bottom: 12px; letter-spacing: 1px;">DIAGNOSTICS & LOGS</div>
            <div style="display: flex; gap: 8px;">
                <button class="format-btn" style="flex: 1; padding: 10px; font-size: 13px;" onclick="openErrorModal()"><web-icon name="view"></web-icon> MAN</button>
                <button class="format-btn" style="flex: 1; padding: 10px; font-size: 13px; border-color: #fbbf24; color: #fbbf24;" onclick="openTerminalModal()"><web-icon name="terminal"></web-icon> TERM</button>
                <button class="format-btn" style="flex: 1; padding: 10px; font-size: 13px; border-color: var(--accent); color: var(--accent);" onclick="downloadErrorLog()"><web-icon name="download"></web-icon> LOG</button>
            </div>
        </div>
    </div>

    <div class="main-container">
        <div class="top-dashboard">
            <button class="menu-trigger-btn" onclick="toggleSettings()" title="Open Settings"><web-icon name="menu"></web-icon></button>
            <div class="input-group">
                <div class="clear-btn" onclick="clearUrl()"><web-icon name="clear"></web-icon></div>
                <input type="text" id="ytLink" class="url-box" placeholder="Paste YouTube URL Here..." oninput="debounceTrigger()" onclick="this.select()">
                <button class="dl-master-trigger" onclick="pasteAndScan()"><web-icon name="paste"></web-icon> PASTE</button>
            </div>
            <div id="status" class="status-panel">CORE ENGINE STANDBY</div>
        </div>
        <div id="mediaBox">
            <div class="thumb-col">
                <img id="mThumb" class="thumb-img" src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='500' height='281' style='background:%2327272a'%3E%3Cpath fill='%2352525b' d='M250 105c-20 0-38 18-38 38s18 38 38 38 38-18 38-38-18-38-38-38zm-12 52v-28l28 14-28 14z'/%3E%3C/svg%3E" alt="Thumbnail">
                <div id="trimSection" class="section-box" style="border-color: #a855f7;">
                    <div class="grid-header" style="color:#a855f7"><web-icon name="trim"></web-icon> TRIM VIDEO</div>
                    <div style="display: flex; gap: 15px;">
                        <div style="flex: 1; display: flex; flex-direction: column; gap: 8px;"><input type="text" id="trimStart" class="url-box" style="padding: 10px; font-size: 18px; height: 50px; text-align: center; font-weight: 900; width: 100%; letter-spacing: 2px;" placeholder="00:00" onclick="this.select()"></div>
                        <div style="flex: 1; display: flex; flex-direction: column; gap: 8px;"><input type="text" id="trimEnd" class="url-box" style="padding: 10px; font-size: 18px; height: 50px; text-align: center; font-weight: 900; width: 100%; letter-spacing: 2px;" placeholder="00:00" onclick="this.select()"></div>
                    </div>
                </div>
                <div id="audioSection" class="section-box" style="border-color: #3b82f6;">
                    <div class="grid-header" style="color:#3b82f6"><web-icon name="audio"></web-icon> AUDIO (MP3/M4A)</div>
                    <div id="audioGrid" class="btn-scroll-area"></div>
                </div>
            </div>
            <div class="right-col">
                <div id="metaSection" class="header-meta">
                    <textarea id="mTitle" class="title-editor" readonly spellcheck="false" onclick="this.select()">AWAITING MEDIA STREAM...</textarea>
                    <div id="mDuration" class="duration-badge">Duration: 00:00</div>
                </div>
                <div class="grids-wrapper">
                    <div id="mp4Section" class="section-box" style="border-color: var(--accent);">
                        <div class="grid-header" style="color:var(--accent)"><web-icon name="mp4"></web-icon> VIDEO (MP4)</div>
                        <div id="mp4Grid" class="btn-scroll-area"></div>
                    </div>
                    <div id="webmSection" class="section-box" style="border-color: #f59e0b;">
                        <div class="grid-header" style="color:#f59e0b"><web-icon name="webm"></web-icon> VIDEO (WEBM)</div>
                        <div id="webmGrid" class="btn-scroll-area"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const IconDict = {
            'menu': `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" width="24" height="24"><line x1="3" y1="12" x2="21" y2="12"></line><line x1="3" y1="6" x2="21" y2="6"></line><line x1="3" y1="18" x2="21" y2="18"></line></svg>`,
            'close': `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" width="24" height="24"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>`,
            'clear': `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" width="28" height="28"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>`,
            'paste': `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true" width="18" height="18" style="vertical-align:middle; margin-right:8px;"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1 2-2V6a2 2 0 0 1 2-2h2"></path><rect x="8" y="2" width="8" height="4" rx="1" ry="1"></rect></svg>`,
            'moon': `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true" width="24" height="24"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>`,
            'trim': `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" width="24" height="24"><circle cx="6" cy="6" r="3"></circle><circle cx="6" cy="18" r="3"></circle><line x1="20" y1="4" x2="8.12" y2="15.88"></line><line x1="14.47" y1="14.48" x2="20" y2="20"></line><line x1="8.12" y1="8.12" x2="12" y2="12"></line></svg>`,
            'audio': `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true" width="24" height="24"><path d="M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z"/></svg>`,
            'mp4': `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true" width="24" height="24"><path d="M17 10.5V7c0-.55-.45-1-1-1H4c-.55 0-1 .45-1 1v10c0 .55.45 1 1 1h12c.55 0 1-.45 1-1v-3.5l4 4v-11l-4 4z"/></svg>`,
            'webm': `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true" width="24" height="24"><path d="M21 3H3c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h18c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-9 9l-5-5h10l-5 5z"/></svg>`,
            'bitrate': `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" width="12" height="12" style="margin-right:4px;"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>`,
            'playlist': `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true" width="24" height="24"><line x1="8" y1="6" x2="21" y2="6"></line><line x1="8" y1="12" x2="21" y2="12"></line><line x1="8" y1="18" x2="21" y2="18"></line><line x1="3" y1="6" x2="3.01" y2="6"></line><line x1="3" y1="12" x2="3.01" y2="12"></line><line x1="3" y1="18" x2="3.01" y2="18"></line></svg>`,
            'download': `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true" width="20" height="20" style="vertical-align:middle; margin-right:5px;"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>`,
            'view': `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true" width="20" height="20" style="vertical-align:middle; margin-right:5px;"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>`,
            'zap': `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" width="24" height="24"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>`,
            'terminal': `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" width="20" height="20" style="vertical-align:middle; margin-right:5px;"><polyline points="4 17 10 11 4 5"></polyline><line x1="12" y1="19" x2="20" y2="19"></line></svg>`
        };

        const svgCache = new Map();
        class WebIcon extends HTMLElement {
            connectedCallback() {
                const name = this.getAttribute('name');
                if (!name) return;
                if (svgCache.has(name)) { this.insertAdjacentHTML('beforeend', svgCache.get(name)); } 
                else if (IconDict[name]) { svgCache.set(name, IconDict[name]); this.insertAdjacentHTML('beforeend', IconDict[name]); }
            }
        }
        customElements.define('web-icon', WebIcon);

        let timeout; let globalDurationSec = 0; let globalActiveTaskId = null; 
        let isPlaylistMode = false; let isFastDL = false; let logInterval = null;

        window.onload = () => {
            renderSkeletons();
            if (localStorage.getItem('theme') === 'light') { document.documentElement.setAttribute('data-theme', 'light'); document.getElementById('toggleThemeSwitch').checked = false; } 
            else { document.documentElement.setAttribute('data-theme', 'dark'); document.getElementById('toggleThemeSwitch').checked = true; }
            updateSettings(); 
        };

        function toggleSettings() { document.getElementById('settingsPanel').classList.toggle('open'); }
        document.addEventListener('click', function(event) {
            const panel = document.getElementById('settingsPanel');
            const isClickInsidePanel = panel.contains(event.target);
            const isClickOnTrigger = event.target.closest('.menu-trigger-btn');
            if (panel.classList.contains('open') && !isClickInsidePanel && !isClickOnTrigger) panel.classList.remove('open');
        });

        function updateSettings() {
            isPlaylistMode = document.getElementById('togglePlaylist').checked;
            isFastDL = document.getElementById('toggleFastDL').checked; 
            document.getElementById('trimSection').style.display = document.getElementById('toggleTrim').checked ? 'flex' : 'none';
            document.getElementById('webmSection').style.display = document.getElementById('toggleWebm').checked ? 'flex' : 'none';
            if(document.getElementById('ytLink').value.trim().length > 5) debounceTrigger();
        }

        function toggleTheme() { 
            const html = document.documentElement; const isDark = html.getAttribute('data-theme') === 'dark'; 
            if(isDark) { html.setAttribute('data-theme', 'light'); localStorage.setItem('theme', 'light'); document.getElementById('toggleThemeSwitch').checked = false; } 
            else { html.setAttribute('data-theme', 'dark'); localStorage.setItem('theme', 'dark'); document.getElementById('toggleThemeSwitch').checked = true; }
        }

        function openErrorModal() { document.getElementById('errorModal').classList.add('active'); document.getElementById('settingsPanel').classList.remove('open'); }
        function closeErrorModal() { document.getElementById('errorModal').classList.remove('active'); }

        function openTerminalModal() { document.getElementById('terminalModal').classList.add('active'); document.getElementById('settingsPanel').classList.remove('open'); startLogPolling(); }
        function closeTerminalModal() { document.getElementById('terminalModal').classList.remove('active'); stopLogPolling(); }

        function startLogPolling() {
            if(logInterval) clearInterval(logInterval);
            logInterval = setInterval(async () => {
                try {
                    const res = await fetch('/api/logs'); const logs = await res.json();
                    const container = document.getElementById('liveLogContainer'); container.innerHTML = '';
                    if (logs.length === 0) container.innerHTML = '<div class="log-info"><span class="log-time">[00:00:00]</span> SYSTEM: Engine Initialized. Listening for logs...</div>';
                    else {
                        logs.forEach(log => {
                            let cssClass = 'log-info';
                            if(log.type === 'error') cssClass = 'log-error';
                            if(log.type === 'warning') cssClass = 'log-warning';
                            container.innerHTML += `<div class="${cssClass}"><span class="log-time">[${log.time}]</span> ${log.msg}</div>`;
                        });
                    }
                    container.scrollTop = container.scrollHeight;
                } catch(e) {}
            }, 1000); 
        }
        function stopLogPolling() { if(logInterval) { clearInterval(logInterval); logInterval = null; } }

        function downloadErrorLog() {
            const logText = "GodMode Server Log dumped from Cloud Memory...";
            const blob = new Blob([logText], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a'); a.href = url; a.download = 'GodMode_Log.txt'; a.click(); URL.revokeObjectURL(url);
        }

        function renderSkeletons() {
            const skelTemplate = `<div class="format-btn skeleton"><div style="display:flex; flex-direction:column; align-items:center; gap:4px; width:100%;"><div style="display:flex; align-items:baseline; justify-content:center; gap:6px; flex-wrap:wrap;"><span class="f-label">HQ</span><span class="f-size">(0.00 MB)</span></div><div class="b-rate"><web-icon name="bitrate"></web-icon> 0 kbps</div></div></div>`;
            const skelBlock = skelTemplate.repeat(6);
            document.getElementById('mp4Grid').innerHTML = skelBlock; document.getElementById('webmGrid').innerHTML = skelBlock;
            const skelAudioTemplate = `<div class="format-btn compact skeleton"><div style="display:flex; flex-direction:column; align-items:center; gap:4px; width:100%;"><div style="display:flex; align-items:baseline; justify-content:center; gap:6px; flex-wrap:wrap;"><span class="f-label">AUDIO</span><span class="f-size">(0.00 MB)</span></div><div class="b-rate"><web-icon name="bitrate"></web-icon> 0 kbps</div></div></div>`;
            document.getElementById('audioGrid').innerHTML = skelAudioTemplate.repeat(4);
        }
        
        function isYouTubeLink(url) { return /^(https?:\/\/)?(www\.|m\.)?(youtube\.com\/(watch\?.*v=|shorts\/|live\/|playlist\?list=)|youtu\.be\/)[a-zA-Z0-9_-]+/i.test(url); }
        function cleanYouTubeUrl(url) {
            try { let urlObj = new URL(url); if (!isPlaylistMode) urlObj.searchParams.delete('list'); urlObj.searchParams.delete('si'); urlObj.searchParams.delete('start_radio'); urlObj.searchParams.delete('index'); return urlObj.toString(); } 
            catch(e) { return url; }
        }

        function debounceTrigger() { clearTimeout(timeout); timeout = setTimeout(() => { const url = document.getElementById('ytLink').value.trim(); if(isYouTubeLink(url)) runScan(); }, 600); }

        async function pasteAndScan() {
            try {
                const text = await navigator.clipboard.readText();
                if(text) { 
                    document.getElementById('ytLink').value = ''; await new Promise(r => setTimeout(r, 50)); document.getElementById('ytLink').value = text; 
                    if(isYouTubeLink(text)) runScan(); 
                    else { document.getElementById('status').innerText = "INVALID LINK"; document.getElementById('status').style.color = "var(--danger)"; }
                }
            } catch (err) { document.getElementById('status').innerText = "PASTE MANUALLY"; document.getElementById('status').style.color = "var(--danger)"; }
        }

        function clearUrl() {
            document.getElementById('ytLink').value = ''; document.getElementById('trimStart').value = ''; document.getElementById('trimEnd').value = '';
            document.getElementById('status').innerText = 'CORE ENGINE STANDBY'; document.getElementById('status').style.color = "var(--accent)";
            document.getElementById('mTitle').value = 'AWAITING MEDIA STREAM...'; document.getElementById('mTitle').setAttribute('readonly', 'true');
            document.getElementById('mDuration').innerText = 'Duration: 00:00';
            document.getElementById('mThumb').src = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='500' height='281' style='background:%2327272a'%3E%3Cpath fill='%2352525b' d='M250 105c-20 0-38 18-38 38s18 38 38 38 38-18 38-38-18-38-38-38zm-12 52v-28l28 14-28 14z'/%3E%3C/svg%3E";
            renderSkeletons();
        }

        async function runScan() {
            let val = document.getElementById('ytLink').value.trim();
            if(!val) return;
            if(!isYouTubeLink(val)) { document.getElementById('status').innerText = "INVALID LINK"; return; }
            val = cleanYouTubeUrl(val); document.getElementById('ytLink').value = val;
            
            const statusEl = document.getElementById('status'); statusEl.innerText = "FETCHING META..."; statusEl.style.color = "var(--accent)";
            
            try {
                const fetchUrl = '/api/scan?url=' + encodeURIComponent(val) + '&playlist=' + (isPlaylistMode ? '1' : '0');
                const res = await fetch(fetchUrl); const data = await res.json();
                if(data.error) throw new Error(data.error);

                document.getElementById('mTitle').value = data.title; document.getElementById('mTitle').removeAttribute('readonly');
                document.getElementById('mThumb').src = data.thumbnail; document.getElementById('mDuration').innerText = "Duration: " + data.duration;
                globalDurationSec = data.duration_sec || 0;

                buildGrid('mp4Grid', data.mp4, 'video'); buildGrid('webmGrid', data.webm, 'video'); buildAudioGrid();
                statusEl.innerText = "SYSTEM ARMED";
            } catch (e) { statusEl.innerText = "BAN DETECTED / ERROR"; statusEl.style.color = "var(--danger)"; }
        }

        function buildGrid(id, list, type) {
            const grid = document.getElementById(id); grid.innerHTML = "";
            list.forEach(item => {
                const btn = document.createElement('div'); btn.className = 'format-btn';
                let sizeStr = "N/A";
                if (item.size) { let sizeMB = item.size / (1024 * 1024); sizeStr = sizeMB >= 1024 ? (sizeMB / 1024).toFixed(2) + " GB" : sizeMB.toFixed(2) + " MB"; }
                const bitrate = item.bitrate || "AUTO VBR";
                let badge = "";
                if(item.res === '720p' || item.res === '1080p') badge = " <span class='res-badge'>HD</span>"; else if(item.res === '1440p') badge = " <span class='res-badge'>2K</span>"; else if(item.res === '2160p') badge = " <span class='res-badge'>4K</span>";

                btn.innerHTML = `<div style="display:flex; flex-direction:column; align-items:center; gap:4px; width:100%;"><div style="display:flex; align-items:baseline; justify-content:center; gap:6px; flex-wrap:wrap;"><span class="f-label">${item.res}${badge}</span><span class="f-size">(${sizeStr})</span></div><div class="b-rate"><web-icon name="bitrate"></web-icon> ${bitrate}</div></div>`;
                btn.onclick = () => startExtraction(item.f_id, item.ext, '0', item.res); grid.appendChild(btn);
            });
        }

        function buildAudioGrid() {
            const grid = document.getElementById('audioGrid'); grid.innerHTML = "";
            const audioOpts = [ { label: '48K (mp3)', ext: 'mp3', br: '48' }, { label: '128K (m4a)', ext: 'm4a', br: '128' }, { label: '128K (mp3)', ext: 'mp3', br: '128' }, { label: '256K (mp3)', ext: 'mp3', br: '256' } ];
            audioOpts.forEach(opt => {
                const btn = document.createElement('div'); btn.className = 'format-btn compact';
                let sizeStr = "N/A";
                if(globalDurationSec > 0) { let sizeMB = (parseInt(opt.br) * globalDurationSec) / 8192; sizeStr = sizeMB >= 1024 ? (sizeMB / 1024).toFixed(2) + " GB" : sizeMB.toFixed(2) + " MB"; }
                btn.innerHTML = `<div style="display:flex; flex-direction:column; align-items:center; gap:4px; width:100%;"><div style="display:flex; align-items:baseline; justify-content:center; gap:6px; flex-wrap:wrap;"><span class="f-label">${opt.label}</span><span class="f-size">(${sizeStr})</span></div><div class="b-rate"><web-icon name="bitrate"></web-icon> ${opt.br} kbps</div></div>`;
                btn.onclick = () => startExtraction('bestaudio', opt.ext, opt.br, opt.br + 'kbps'); grid.appendChild(btn);
            });
        }

        async function trackProgress(taskId) {
            if (globalActiveTaskId !== taskId) return; 
            try {
                const res = await fetch('/api/progress?task_id=' + taskId); const data = await res.json();
                const statusEl = document.getElementById('status');
                if (data.status === 'downloading') { statusEl.innerText = `${data.percent} ( ${data.downloaded} )`; statusEl.style.color = "var(--accent)"; } 
                else if (data.status === 'muxing') { statusEl.innerText = "MERGING A/V & METADATA..."; statusEl.style.color = "#f59e0b"; }
            } catch (e) {}
        }

        async function startExtraction(fid, ext, bitrate, quality_tag) {
            const cleanTitle = document.getElementById('mTitle').value.trim();
            const trimStart = document.getElementById('trimStart').value.trim();
            const trimEnd = document.getElementById('trimEnd').value.trim();
            
            const statusEl = document.getElementById('status');
            statusEl.style.color = "#f59e0b"; statusEl.style.borderColor = "#f59e0b";
            statusEl.innerText = "STARTING CLOUD DOWNLOAD...";
            
            const taskId = Date.now().toString() + Math.floor(Math.random()*1000);
            globalActiveTaskId = taskId; const localPollTimer = setInterval(() => trackProgress(taskId), 800);

            try {
                const resp = await fetch('/api/download', {
                    method: 'POST', headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ url: document.getElementById('ytLink').value, fid, title: cleanTitle, ext, bitrate, quality_tag, task_id: taskId, trim_start: trimStart, trim_end: trimEnd, is_playlist: isPlaylistMode, fast_dl: isFastDL })
                });
                
                clearInterval(localPollTimer); const res = await resp.json();
                
                if (globalActiveTaskId === taskId) {
                    if(res.status === "success") { 
                        statusEl.innerText = "TRANSFERRING TO PC..."; statusEl.style.color = "var(--accent)"; 
                        window.location.href = '/api/serve?filepath=' + encodeURIComponent(res.path);
                        setTimeout(() => { statusEl.innerText = "DOWNLOAD COMPLETE"; }, 3000);
                    } else { statusEl.innerText = res.message || "ERROR"; statusEl.style.color = "var(--danger)"; }
                }
            } catch(e) { 
                clearInterval(localPollTimer); 
                if (globalActiveTaskId === taskId) { statusEl.innerText = "CRITICAL FAILURE"; statusEl.style.color = "var(--danger)"; }
            }
        }
    </script>
</body>
</html>
"""

# ------------------------------------------------------------------------------
# BACKEND: API ENDPOINTS (NAT COLLISION FIXED)
# ------------------------------------------------------------------------------

@app.route('/api/logs')
def logs_api(): return jsonify(system_logs)

@app.route('/api/syscheck')
def syscheck_api(): return jsonify({"status": "ok"})

@app.route('/')
def home(): return render_template_string(HTML_UI)

@app.route('/api/scan')
def scan_api():
    url = request.args.get('url')
    is_playlist = request.args.get('playlist') == '1'
    
    ydl_opts = {
        'logger': GodModeLogger(), 'quiet': False, 'no_warnings': False,      
        'ignoreerrors': True, 'extract_flat': False, 'noplaylist': not is_playlist, 
        'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36'},
        'restrictfilenames': False, 'geo_bypass': True,
        # [NAT FIX]: Removed 'source_address' completely to allow Docker NAT to route packets properly
        'force_ipv4': True,
        'legacyserverconnect': True
    } 
    
    if os.path.exists('cookies.txt'): ydl_opts['cookiefile'] = 'cookies.txt'
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info: return jsonify({"error": "No data returned. Check Terminal."}), 500

            parse_target = info['entries'][0] if (is_playlist and 'entries' in info and len(info['entries']) > 0) else info
            raw_title = info.get('title', parse_target.get('title', 'Unknown Title'))
            clean_safe_title = re.sub(r'[\\/*?:"<>|]', '', raw_title)
            duration_sec = parse_target.get('duration', 0)

            mp4_list, webm_list = [], []
            for f in parse_target.get('formats', []):
                h = f.get('height')
                ext = f.get('ext')
                
                if h is not None and h >= 144:
                    audio_query = "bestaudio[ext=m4a]/bestaudio" if ext == 'mp4' else "bestaudio[ext=webm]/bestaudio" 
                    vbr = f.get('vbr') or f.get('tbr') or 0
                    bitrate_str = f"{int(vbr)} kbps" if vbr > 0 else "AUTO VBR"
                    
                    file_size = f.get('filesize') or f.get('filesize_approx')
                    if not file_size and vbr > 0 and duration_sec > 0: file_size = (vbr * 1024 / 8) * duration_sec
                    
                    vid_data = { "f_id": f"{f['format_id']}+{audio_query}", "res": f"{h}p", "size": file_size, "ext": ext, "bitrate": bitrate_str }
                    if ext == 'mp4': mp4_list.append(vid_data)
                    elif ext == 'webm': webm_list.append(vid_data)

            def unique_res(v_list):
                seen = set(); res = []
                for v in v_list:
                    if v['res'] not in seen: seen.add(v['res']); res.append(v)
                return res

            return jsonify({
                "title": clean_safe_title, "thumbnail": parse_target.get('thumbnail', info.get('thumbnail', '')), 
                "duration": parse_target.get('duration_string', '00:00'), "duration_sec": duration_sec, 
                "mp4": unique_res(sorted(mp4_list, key=lambda x: int(x['res'][:-1]))),
                "webm": unique_res(sorted(webm_list, key=lambda x: int(x['res'][:-1])))
            })
    except Exception as e: return jsonify({"error": str(e)}), 500


@app.route('/api/progress')
def progress_api():
    task_id = request.args.get('task_id', 'default')
    return jsonify(download_states.get(task_id, {"status": "idle", "percent": "0.0%", "downloaded": "0.0 MB", "total": "0.0 MB"}))

def get_progress_hook(task_id):
    def hook(d):
        if task_id not in download_states: download_states[task_id] = {"status": "idle", "percent": "0.0%", "downloaded": "0.0 MB", "total": "0.0 MB"}
        state = download_states[task_id]
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            down = d.get('downloaded_bytes', 0)
            if total > 0:
                state['percent'] = f"{(down / total) * 100:.1f}%"
                state['downloaded'] = f"{down / (1024*1024):.2f} MB"
                state['total'] = f"{total / (1024*1024):.2f} MB"
                state['status'] = 'downloading'
        elif d['status'] == 'finished': state['status'] = 'muxing'
    return hook

def parse_time_to_seconds(time_str):
    if not time_str or not str(time_str).strip(): return None
    parts = str(time_str).strip().split(':')
    try:
        if len(parts) == 3: return int(parts[0])*3600 + int(parts[1])*60 + float(parts[2])
        elif len(parts) == 2: return int(parts[0])*60 + float(parts[1])
        elif len(parts) == 1: return float(parts[0])
    except: return None
    return None

@app.route('/api/download', methods=['POST'])
def download_api():
    data = request.json
    task_id = data.get('task_id', 'default')
    is_playlist = data.get('is_playlist', False)
    fast_dl = data.get('fast_dl', False)
    
    download_states[task_id] = {"status": "idle", "percent": "0.0%", "downloaded": "0.0 MB", "total": "0.0 MB"}
    save_dir = os.path.join(os.getcwd(), "cloud_downloads")
    try: os.makedirs(save_dir, exist_ok=True)
    except Exception as e: return jsonify({"status": "error", "message": f"CLOUD DIR ERROR: {str(e)}"}), 500
        
    safe_title = re.sub(r'[\\/*?:"<>|]', '', data['title']).strip()
    quality_tag = data.get('quality_tag', '')
    
    if is_playlist:
        tmpl_str = f"%(playlist_title)s/%(title)s_{quality_tag}.{data['ext']}" if quality_tag else f"%(playlist_title)s/%(title)s.{data['ext']}"
        path = os.path.join(save_dir, tmpl_str)
    else:
        if quality_tag: safe_title = f"{safe_title}_{quality_tag}"
        path = os.path.join(save_dir, f"{safe_title}.{data['ext']}")
    
    postprocessors = []
    writethumbnail = False
    if data['ext'] in ['mp3', 'm4a']:
        writethumbnail = True
        postprocessors.extend([
            {'key': 'FFmpegExtractAudio', 'preferredcodec': data['ext'], 'preferredquality': data.get('bitrate', '192')},
            {'key': 'FFmpegMetadata', 'add_metadata': True},
            {'key': 'EmbedThumbnail', 'already_have_thumbnail': False}
        ])

    ydl_opts = {
        'logger': GodModeLogger(), 'format': data['fid'], 'outtmpl': path, 'quiet': False, 'no_warnings': False,
        'noprogress': True, 'progress_hooks': [get_progress_hook(task_id)], 'noplaylist': not is_playlist, 
        'writethumbnail': writethumbnail, 'continuedl': True, 'retries': 10, 'fragment_retries': 10,    
        'postprocessors': postprocessors, 'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36'},
        'restrictfilenames': False, 'geo_bypass': True,
        # [NAT FIX]: Removed 'source_address' here too
        'force_ipv4': True,
        'legacyserverconnect': True
    }
    
    if os.path.exists('cookies.txt'): ydl_opts['cookiefile'] = 'cookies.txt'
    
    if fast_dl:
        ydl_opts['concurrent_fragment_downloads'] = 15
        ydl_opts['sleep_interval_requests'] = 0.0
        ydl_opts['max_sleep_interval_requests'] = 0.0
    else:
        ydl_opts['concurrent_fragment_downloads'] = 5
        ydl_opts['sleep_interval_requests'] = 2.1
        ydl_opts['max_sleep_interval_requests'] = 3.5
    
    t_start = parse_time_to_seconds(data.get('trim_start'))
    t_end = parse_time_to_seconds(data.get('trim_end'))
    if t_start is not None or t_end is not None:
        s = t_start if t_start is not None else 0
        e = t_end if t_end is not None else 9999999
        ydl_opts['download_ranges'] = download_range_func(None, [(s, e)])
        ydl_opts['force_keyframes_at_cuts'] = True 
    
    if data['ext'] in ['mp4', 'webm']: ydl_opts['merge_output_format'] = data['ext']
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl: ydl.download([data['url']])
        gc.collect()
        return jsonify({"status": "success", "path": save_dir if is_playlist else path})
    except Exception as e: return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/serve')
def serve_file():
    filepath = request.args.get('filepath')
    if os.path.exists(filepath): return send_file(filepath, as_attachment=True)
    return "File missing on server", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860, debug=False)
