# Proxmox to Discord Webhook Forwarder 🚀

A lightweight Docker service that receives webhook notifications from Proxmox and forwards them to Discord channels with smart filtering and beautiful formatting.

## ✨ Features

- 🎯 **Smart Filtering**: Route notifications by severity and source IP
- 📝 **Beautiful Messages**: Clean Discord formatting with emojis and embeds
- 📎 **Long Message Support**: Auto-converts long messages to file attachments
- 🐳 **Docker Ready**: Easy deployment with Docker Compose
- ⚙️ **Simple Config**: YAML-based configuration

## 🚀 Quick Start

```bash
git clone https://github.com/JakronIT/Proxmox-to-Discord.git
cd Proxmox-to-Discord
```

Edit `config.yaml` and set your Discord webhook URLs.

**Structure of `config.yaml`:**

- `webhooks`: a list of Discord webhooks to which notifications will be sent
    - `url`: Discord webhook URL
    - `severity`: list of severity levels to be forwarded to this webhook (`any` or e.g. `["warning", "error"]`)
    - `source`: list of IP addresses from which notifications should be forwarded (`any` or specific IPs)

Example:

```yaml
webhooks:
  - url: "https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN"
    severity: ["any"]
    source: ["any"]
  # - url: "https://discord.com/api/webhooks/ANOTHER_WEBHOOK_ID/ANOTHER_WEBHOOK_TOKEN"
  #   severity: ["warning", "error", "critical"]
  #   source: ["192.168.1.10"]
```

Start the service:

```bash
docker compose up -d
```

The service will be available at `http://localhost:5000`

## 🗝️ How to Get Your Discord Webhook URL

1. Open your Discord server and go to the channel where you want to receive notifications.
2. Click the gear icon next to the channel name to open **Edit Channel**.
3. Go to the **Integrations** tab and click **Webhooks**.
4. Click **New Webhook** (or select an existing one).
5. Set a name and (optionally) an avatar for your webhook.
6. Click **Copy Webhook URL** – this is the URL you need for the `url` field in your config.
7. Paste this URL into your `config.yaml` as shown in the example above.

## 🔧 Proxmox Configuration

Configure Proxmox to send webhook notifications:

1. In Proxmox web interface: **Datacenter** → **Notifications** → **Endpoints**
2. Click **Add** → **Webhook**
3. Configure:
   - **Name**: `discord-forwarder`
   - **URL**: `http://YOUR_SERVER_IP:5000/webhook`
   - **Method**: `POST`
   - **Header**: `Content-Type: application/json`
   - **Body**:

```json
{
    "title": "{{ title }}",
    "message": "{{ escape message }}",
    "severity": "{{ severity }}",
    "timestamp": {{ timestamp }}
}
```

4. Save and test the endpoint from Proxmox.

## 📊 Severity Levels

Supported severity levels (compatible with Proxmox):

- info
- notice
- warning
- error
- unknown
