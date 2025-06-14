#!/usr/bin/env python3

import json
import yaml
import requests
import tempfile
import os
from flask import Flask, request, jsonify, send_file
from datetime import datetime
import time

app = Flask(__name__)

with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

def get_embed_color(severity):
    color_map = {
        "info": 5814783,
        "notice": 3447003,
        "warning": 16776960,
        "error": 16711680,
        "unknown": 9807270
    }
    return color_map.get(severity, 9807270)

def format_discord_payload(data, hostname):
    title = data.get('title', 'Proxmox Notification')
    message = data.get('message', '')
    severity = data.get('severity', 'unknown').lower()
    timestamp = data.get('timestamp', '')
    if timestamp and str(timestamp).isdigit():
        try:
            ts = int(timestamp)
        except:
            ts = int(time.mktime(datetime.now().timetuple()))
    else:
        ts = int(time.mktime(datetime.now().timetuple()))
    color = get_embed_color(severity)
    embed = {
        "title": f"{get_severity_emoji(severity)} {severity.upper()} - {title}",
        "description": message if len(message) < 1000 else "",
        "color": color,
        "footer": {"text": hostname},
        "timestamp": datetime.utcfromtimestamp(ts).replace(microsecond=0).isoformat() + "Z"
    }
    payload = {
        "content": None,
        "embeds": [embed]
    }
    if len(message) >= 1000:
        payload["attachments"] = []
    else:
        payload["attachments"] = []
    return payload

def get_severity_emoji(severity):
    return {
        "info": "ℹ️",
        "notice": "📢",
        "warning": "⚠️",
        "error": "❌",
        "unknown": "❔"
    }.get(severity, "📋")

def send_to_discord(webhook_url, payload, message, use_file):
    headers = {"Content-Type": "application/json"}
    if use_file:
        with open("notification-content.txt", "w") as f:
            f.write(message)
        with open("notification-content.txt", "rb") as f:
            files = {'file': ("notification-content.txt", f, 'text/plain')}
            response = requests.post(webhook_url, data={"payload_json": json.dumps(payload)}, files=files, timeout=10)
        os.remove("notification-content.txt")
        return response.status_code in (200, 204)
    else:
        response = requests.post(webhook_url, json=payload, headers=headers, timeout=10)
        return response.status_code in (200, 204)

@app.route('/')
def info():
    return {"service": "Proxmox to Discord Forwarder", "status": "running", "version": "2.1"}

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if not data:
        return {"error": "No JSON data provided"}, 400
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ',' in client_ip:
        client_ip = client_ip.split(',')[0].strip()
    severity = data.get('severity', 'unknown').lower()
    title = data.get('title', 'Proxmox Notification')
    message = data.get('message', '')
    timestamp = data.get('timestamp', '')
    hostname = os.uname().nodename if hasattr(os, 'uname') else 'unknown'
    print(f"Received notification: severity={severity}, source={client_ip}, title={title}")
    use_file = len(message) >= 1000
    payload = format_discord_payload(data, hostname)
    sent_count = 0
    for webhook in config.get('webhooks', []):
        webhook_severities = webhook.get('severity', ['any'])
        if webhook_severities != ['any'] and severity not in webhook_severities:
            continue
        webhook_sources = webhook.get('source', ['any'])
        if webhook_sources != ['any'] and client_ip not in webhook_sources:
            continue
        if send_to_discord(webhook['url'], payload, message, use_file):
            sent_count += 1
            print(f"Sent to Discord webhook (severity filter: {webhook_severities}, source filter: {webhook_sources})")
        else:
            print(f"Failed to send to Discord webhook")
    return {
        "status": "success",
        "sent": sent_count,
        "severity": severity,
        "source": client_ip,
        "title": title
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
