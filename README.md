# Pi Social Poster — Raspberry Pi Social Media Automation Hub

![Platforms](https://img.shields.io/badge/Platforms-Mastodon%20%7C%20Bluesky%20%7C%20Telegram%20%7C%20LinkedIn%20%7C%20Facebook-blue)
![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-5-red)
![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Maintenance](https://img.shields.io/badge/Maintained-Yes-green)
![Self Hosted](https://img.shields.io/badge/Self%20Hosted-Yes-purple)
![GitHub issues](https://img.shields.io/github/issues/your_username/social-poster)

## 📊 Statistics
![GitHub stars](https://img.shields.io/github/stars/your_username/social-poster)
![GitHub forks](https://img.shields.io/github/forks/your_username/social-poster)
![GitHub license](https://img.shields.io/github/license/your_username/social-poster)

**🎯 Write once, post everywhere — from your own hardware, on your own terms.**
Built with ❤️ for privacy, reliability, and full ownership of your social media workflow.

[⭐ Star this repo](https://github.com/your_username/social-poster) if it saved you time!

---

A self-hosted cross-posting hub built on a Raspberry Pi 5 that simultaneously publishes to Mastodon, Bluesky, Telegram, LinkedIn, and Facebook from a single web dashboard.

---

## Table of Contents

- [Hardware](#hardware)
- [About the Pironman 5 Max](#about-the-pironman-5-max)
- [OS Installation](#os-installation)
- [Pironman 5 Software](#pironman-5-software)
- [Overclocking](#overclocking)
- [Application Setup](#application-setup)
- [NVMe Boot Migration](#nvme-boot-migration)
- [Data Drive Setup](#data-drive-setup)
- [Platform Credentials](#platform-credentials)
- [Security Hardening](#security-hardening)
- [Tailscale Remote Access](#tailscale-remote-access)
- [Dashboard Login](#dashboard-login)
- [Maintenance](#maintenance)

---

## Hardware

- Raspberry Pi 5 (8GB recommended)
- SunFounder Pironman 5 Max case
- 2x NVMe M.2 SSDs (any size — 1TB recommended)
- 27W USB-C power supply (official Raspberry Pi or SunFounder)

**Compatible SSDs:** Raspberry Pi branded SSD, Samsung 980, Crucial P3. Avoid SSDs with Phison controllers — WD SN350 and SN570 prevent boot entirely.

---

## About the Pironman 5 Max

The [SunFounder Pironman 5 Max](https://www.sunfounder.com/products/pironman-5-max) is an aluminum mini PC enclosure designed specifically for the Raspberry Pi 5. It transforms a bare Pi into a compact, fully featured desktop-style machine with serious cooling, storage expansion, and built-in monitoring.

### What it does

- **Dual NVMe M.2 slots** — supports 2230/2242/2260/2280 drives via a PCIe Gen2 switch, with RAID 0/1 support for NAS setups. This guide uses one drive for the OS and one for data.
- **Tower cooler + dual RGB fans** — keeps the Pi 5 at around 39°C under full load in a 25°C room, making it suitable for always-on workloads and overclocking.
- **0.96" OLED display** — shows real-time CPU usage, RAM, temperature, IP address, and disk status. Tap-to-wake via built-in vibration sensor.
- **Safe shutdown button** — a retro-style metal power button that gracefully shuts down the OS rather than cutting power.
- **Dual full-size HDMI ports** — replaces the Pi's micro-HDMI connectors with standard-size outputs.
- **External GPIO extender** — labeled 40-pin header accessible from the outside of the case.
- **IR receiver** — for media remote control.
- **RTC battery support** — keeps time accurate without network access.
- **Customizable RGB lighting** — four addressable WS2812 LEDs with software control.

### Where to buy

| Retailer | Link |
|---|---|
| SunFounder (official) | https://www.sunfounder.com/products/pironman-5-max |
| Amazon | Search "Pironman 5 Max" |
| AliExpress | Available for Russia and South America |

**Price:** approximately $94.99 USD (Raspberry Pi not included). Bundles with Pi 5, SSDs, and accessories are available from SunFounder directly.

### Pironman 5 lineup

SunFounder makes several variants — choose based on your needs:

| Model | Key difference | Best for |
|---|---|---|
| **Pironman 5** | Single NVMe slot | Single SSD builds |
| **Pironman 5 Max** | Dual NVMe, RAID support | This guide — OS + data drive split |
| **Pironman 5 Mini** | Compact, fewer features, easier assembly | Minimal builds, tighter budgets |
| **Pironman 5 Pro Max** | Adds 4.3" touchscreen, camera, mic, speakers | Interactive AI / desktop use |

### Running this project on other hardware

This application is not tied to the Pironman case. It will run on any hardware that can run Raspberry Pi OS or a Debian-based Linux distribution. Some alternative setups:

| Hardware | Notes |
|---|---|
| Bare Raspberry Pi 5 with official active cooler | Works fine for the app — just no OLED or dual NVMe. Use a single SSD via a PCIe HAT. |
| Raspberry Pi 4 | Supported — no PCIe slot, so NVMe requires a USB adapter. Performance is lower but adequate for API-based posting. |
| Any Debian/Ubuntu x86 machine | The application runs without modification. Ignore the Pironman and overclocking sections. |
| Docker | The FastAPI app can be containerised. A Dockerfile is not included in this repo but the app has no platform-specific dependencies beyond aiosqlite. |
| Proxmox LXC | Run as a lightweight container on an existing Proxmox node. Use `network_mode: host` equivalent to preserve LAN access if needed. |

> **Note on overclocking:** The overclock settings in this guide are safe specifically because the Pironman 5 Max provides substantial active cooling. **Do not apply these settings on a Pi without adequate cooling** — the official active cooler is the minimum requirement. A bare Pi 5 with only a heatsink should not be overclocked beyond 2600MHz. Always stress test after any overclock change and monitor temperatures.

---

## About the Pironman 5 Max

The **SunFounder Pironman 5 Max** is a premium tower enclosure that transforms a bare Raspberry Pi 5 into a compact mini PC. It is the case used in this guide and the reason the dual NVMe setup and overclocking sections exist — the case provides the cooling headroom that makes both possible.

### What it does

- **Dual NVMe M.2 slots** — supports two SSDs (2230, 2242, 2260, or 2280) via a PCIe Gen2 switch, with RAID 0/1 support. One slot can alternatively hold a Hailo-8L AI accelerator instead of a second SSD.
- **Tower cooler + dual RGB fans** — passive heatsink tower combined with two active RGB fans keeps the Pi 5 cool even under sustained load and overclocking.
- **0.96" OLED display** — shows CPU usage, RAM, temperature, IP address, and disk status in real time. Tap-to-wake via a built-in vibration sensor.
- **Safe shutdown button** — metal power button that triggers a clean OS shutdown rather than cutting power.
- **Full-size HDMI ports** — two standard HDMI outputs replacing the Pi 5's micro-HDMI connectors.
- **External GPIO header** — labeled 40-pin header accessible on the outside of the case.
- **RTC battery support** — maintains system time without network connectivity.
- **Customizable RGB lighting** — addressable LEDs on the fans, controllable via the pironman5 service.

### Where to buy

| Retailer | Link |
|---|---|
| SunFounder (official) | https://www.sunfounder.com/products/pironman-5-max |
| Amazon | Search "Pironman 5 MAX" |
| AliExpress | Search "Pironman 5 MAX SunFounder" |

**Price:** approximately $94.99 USD (case only, Raspberry Pi not included). US duties and EU VAT are included in the SunFounder store price.

### Pironman 5 model lineup

| Model | NVMe slots | OLED | Notable difference |
|---|---|---|---|
| Pironman 5 | 1 | Yes | Original model, single SSD, ~$79.99 |
| Pironman 5 Max | 2 | Yes (tap-to-wake) | Dual SSD, used in this guide, ~$94.99 |
| Pironman 5 Mini | 1 | No | Budget option, single fan, ~$45 |
| Pironman 5 Pro Max | 2 | Yes | Adds 4.3" touchscreen, camera, mic, speaker |

### This project without the Pironman 5

The application itself has no dependency on the Pironman 5 case. It runs on any hardware that can run Raspberry Pi OS or Ubuntu. The case-specific sections (Pironman software, overclocking, dual NVMe setup) are optional enhancements. Alternatives that work well:

| Option | Notes |
|---|---|
| Any Raspberry Pi 5 with official Active Cooler | Cheapest path — no NVMe, SD card only, no overclock needed |
| Pi 5 + Argon ONE V3 case | Single NVMe slot, good cooling, clean aluminum design |
| Pi 5 + Waveshare PCIe to M.2 HAT | Single NVMe, no case extras, very low cost |
| Any x86 mini PC or old laptop | Run the app on any Linux machine — no Pi required |
| VPS or cloud VM | Fully headless deployment, no hardware at all |

The only sections that require the Pironman 5 specifically are [Pironman 5 Software](#pironman-5-software) and the dual-drive [NVMe Boot Migration](#nvme-boot-migration) / [Data Drive Setup](#data-drive-setup). Everything else is standard Raspberry Pi OS setup.

---

## OS Installation

Flash **Raspberry Pi OS Lite 64-bit (Bookworm)** using Raspberry Pi Imager.

1. Download Raspberry Pi Imager: https://www.raspberrypi.com/software/
2. Select:
   - **Device:** Raspberry Pi 5
   - **OS:** Raspberry Pi OS (other) → Raspberry Pi OS Lite (64-bit)
   - **Storage:** your SD card
3. Click the settings gear and pre-configure:

```
Hostname:   your-hostname
Username:   your_username
SSH:        enabled
Timezone:   Your/Timezone
```

4. Write the image and boot the Pi.
5. SSH in:

```bash
ssh your_username@your-hostname.local
```

6. Update the system:

```bash
sudo apt update && sudo apt full-upgrade -y
```

---

## Pironman 5 Software

The Pironman service controls the OLED display, RGB fans, and safe shutdown button. Use the `max` branch for the dual M.2 model.

```bash
sudo apt install git python3 python3-pip python3-setuptools -y
cd ~
git clone -b max https://github.com/sunfounder/pironman5.git --depth 1
cd ~/pironman5
sudo python3 install.py
sudo reboot
```

After reboot the OLED, RGB fans, and safe shutdown button will be active.

---

## Overclocking

> **Warning:** Overclocking increases heat output significantly. Only attempt this with adequate active cooling — a heatsink alone is not sufficient. The settings below are tuned for the Pironman 5 Max with its tower cooler and dual RGB fans. If you are using a different case or cooler, start at `arm_freq=2600` and work up gradually while monitoring temperature. Do not overclock without a fan.

Safe overclock for the Pironman 5 Max with its tower cooler and dual RGB fans.

```bash
sudo nano /boot/firmware/config.txt
```

Add to the `[pi5]` section at the bottom:

```ini
[pi5]
over_voltage_delta=50000
arm_freq=2800
gpu_freq=933
```

Reboot and verify:

```bash
sudo reboot
vcgencmd measure_clock arm
vcgencmd get_throttled     # should return 0x0
vcgencmd measure_temp      # should stay under 70C under load
```

Run a stress test to confirm stability:

```bash
sudo apt install stress-ng -y
stress-ng --cpu 4 --timeout 300
```

---

## Application Setup

### 1. Create the project

```bash
cd ~
mkdir social-poster && cd social-poster

mkdir -p app/connectors app/formatters app/dashboard/templates \
         app/dashboard/static migrations logs media/uploads systemd

python3 -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
cat > requirements.txt << 'EOF'
fastapi==0.111.1
uvicorn[standard]==0.30.1
httpx==0.27.0
python-dotenv==1.0.1
pydantic-settings==2.3.4
aiosqlite==0.20.0
APScheduler==3.10.4
jinja2==3.1.4
python-multipart==0.0.20
atproto==0.0.65
Mastodon.py==1.8.1
python-jose[cryptography]
passlib[bcrypt]
Pillow
EOF

pip install -r requirements.txt
```

### 3. Create the .env file

```bash
cat > ~/.env << 'EOF'
APP_HOST=0.0.0.0
APP_PORT=8080
DATABASE_URL=sqlite+aiosqlite:///./app.db
DRY_RUN=true

MASTODON_INSTANCE_URL=https://mastodon.social
MASTODON_ACCESS_TOKEN=

BLUESKY_HANDLE=yourhandle.bsky.social
BLUESKY_APP_PASSWORD=

TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=

LINKEDIN_CLIENT_ID=
LINKEDIN_CLIENT_SECRET=
LINKEDIN_REDIRECT_URI=http://localhost:8080/auth/linkedin/callback
LINKEDIN_ACCESS_TOKEN=
LINKEDIN_PERSON_URN=
LINKEDIN_PAGE_URN=

FACEBOOK_PAGE_ID=
FACEBOOK_PAGE_ACCESS_TOKEN=

INSTAGRAM_ACCOUNT_ID=
INSTAGRAM_ACCESS_TOKEN=

DASHBOARD_USERNAME=your_username
DASHBOARD_PASSWORD=your_strong_password
SECRET_KEY=
EOF
```

Generate a secret key and add it:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
# paste output as SECRET_KEY value
```

Copy to project and secure:

```bash
cp ~/.env ~/social-poster/.env
chmod 600 ~/social-poster/.env
```

### 4. Build the application files

The full application source code is in this repository. After cloning, the structure is:

```
social-poster/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── dispatcher.py
│   ├── queue.py
│   ├── scheduler.py
│   ├── schemas.py
│   ├── models.py
│   ├── connectors/
│   │   ├── base.py
│   │   ├── mastodon.py
│   │   ├── bluesky.py
│   │   ├── telegram.py
│   │   ├── linkedin.py
│   │   └── facebook.py
│   ├── formatters/
│   │   ├── base.py
│   │   ├── mastodon.py
│   │   ├── bluesky.py
│   │   ├── telegram.py
│   │   ├── linkedin.py
│   │   └── facebook.py
│   └── dashboard/
│       ├── templates/
│       │   ├── index.html
│       │   └── logs.html
│       └── static/
│           └── style.css
├── migrations/
│   └── 001_init.sql
├── systemd/
│   └── social-poster.service
├── .env.example
└── requirements.txt
```

### 5. Test the application

```bash
cd ~/social-poster
source venv/bin/activate

# Verify database initialises cleanly
python3 -c "from app.config import settings; from app.database import init_db; import asyncio; asyncio.run(init_db()); print('OK')"

# Start the server
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

Visit `http://your-hostname.local:8080` — you should see the login page.

### 6. Install the systemd service

```bash
cat > systemd/social-poster.service << 'EOF'
[Unit]
Description=Social Media Poster
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/home/your_username/social-poster
EnvironmentFile=/home/your_username/social-poster/.env
ExecStart=/home/your_username/social-poster/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8080
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

sudo cp systemd/social-poster.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable social-poster
sudo systemctl start social-poster
sudo systemctl status social-poster
```

---

## NVMe Boot Migration

Boot the OS from SSD 1 for performance and SD card longevity.

### 1. Enable PCIe Gen 3

```bash
echo 'dtparam=pciex1_gen=3' | sudo tee -a /boot/firmware/config.txt
```

### 2. Verify both SSDs are visible

```bash
lsblk
# Should show nvme0n1 and nvme1n1
```

### 3. Clone SD card to NVMe

```bash
sudo systemctl stop social-poster
sudo dd if=/dev/mmcblk0 of=/dev/nvme0n1 bs=4M status=progress
sudo sync
```

### 4. Expand the partition to full SSD size

```bash
sudo growpart /dev/nvme0n1 2
sudo e2fsck -f /dev/nvme0n1p2
sudo resize2fs /dev/nvme0n1p2
```

### 5. Set NVMe as boot device

```bash
sudo raspi-config nonint do_boot_order B2
sudo rpi-eeprom-config --edit
```

Find `BOOT_ORDER` and change it to:

```
BOOT_ORDER=0xf416
```

Save and reboot:

```bash
sudo reboot
```

### 6. Verify NVMe boot

```bash
lsblk
findmnt /
# Should show /dev/nvme0n1p2 mounted as /
```

---

## Data Drive Setup

Mount SSD 2 as a dedicated data volume for the database, media, and logs.

```bash
# Format SSD 2
sudo mkfs.ext4 /dev/nvme1n1
sudo mkdir -p /mnt/data
sudo mount /dev/nvme1n1 /mnt/data

# Auto-mount on boot
echo "$(sudo blkid -s UUID -o value /dev/nvme1n1) /mnt/data ext4 defaults,noatime 0 2" | sudo tee -a /etc/fstab

# Create directory structure
sudo mkdir -p /mnt/data/poster/{db,media,logs}
sudo chown -R your_username:your_username /mnt/data/poster

# Stop service and migrate data
sudo systemctl stop social-poster
cp ~/social-poster/app.db /mnt/data/poster/db/

# Update paths in app (edit these files)
# app/database.py: DB_PATH = Path("/mnt/data/poster/db/app.db")
# app/main.py: MEDIA_UPLOAD_DIR = Path("/mnt/data/poster/media")

sudo systemctl start social-poster
```

---

## Platform Credentials

### Mastodon

1. Log into your instance → Settings → Development → New Application
2. App name: `social-poster`
3. Scopes: check only `write:statuses` and `write:media`
4. Submit and copy the **Access Token**
5. Add to `.env`:

```
MASTODON_INSTANCE_URL=https://your.instance
MASTODON_ACCESS_TOKEN=your_token
```

### Bluesky

1. Settings → Privacy and Security → App Passwords → Add App Password
2. Add to `.env`:

```
BLUESKY_HANDLE=yourhandle.bsky.social
BLUESKY_APP_PASSWORD=your_app_password
```

### Telegram

1. Message `@BotFather` → `/newbot` → follow prompts → copy token
2. Add bot to your channel
3. Get chat ID from `@userinfobot`
4. Add to `.env`:

```
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHAT_ID=your_chat_id
```

### LinkedIn

1. Create app at https://developer.linkedin.com/apps
2. Add product: **Share on LinkedIn**
3. Add redirect URI: `http://localhost:8080/auth/linkedin/callback`
4. Add Client ID and Secret to `.env`
5. SSH tunnel for OAuth:

```bash
# On your local machine
ssh -L 8080:localhost:8080 your_username@your-hostname.local
```

6. Visit `http://localhost:8080/auth/linkedin` in your browser
7. Authorize and copy the token and person URN shown on screen
8. Add to `.env`:

```
LINKEDIN_ACCESS_TOKEN=your_token
LINKEDIN_PERSON_URN=urn:li:person:xxxxxxxx
```

### Facebook Page

1. Create app at https://developers.facebook.com
2. Add use cases: **Manage everything on your Page**
3. Add permissions: `pages_manage_posts`, `pages_read_engagement`
4. Go to Tools → Graph API Explorer
5. Generate Access Token with those permissions
6. Get Page Access Token (never expires):

```bash
curl -s "https://graph.facebook.com/v25.0/me/accounts?access_token=YOUR_USER_TOKEN"
```

Copy `data[0].access_token` — this is your permanent Page token.

7. Add to `.env`:

```
FACEBOOK_PAGE_ID=your_page_id
FACEBOOK_PAGE_ACCESS_TOKEN=your_page_token
```

---

## Security Hardening

### Firewall

```bash
sudo apt install ufw -y
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 8080/tcp
sudo ufw enable
```

### Fail2ban

```bash
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### Automatic security updates

```bash
sudo apt install unattended-upgrades -y
sudo dpkg-reconfigure -plow unattended-upgrades
# Select Yes when prompted
```

### DNS stability (prevents transient failures)

```bash
echo "$(dig +short api.telegram.org | head -1) api.telegram.org" | sudo tee -a /etc/hosts
echo "$(dig +short mastodon.social | head -1) mastodon.social" | sudo tee -a /etc/hosts
echo "$(dig +short graph.facebook.com | head -1) graph.facebook.com" | sudo tee -a /etc/hosts
```

### Lock down port 8080 to local network and Tailscale only

```bash
sudo ufw delete allow 8080/tcp
sudo ufw allow in on tailscale0 to any port 8080
sudo ufw allow in on eth0 to any port 8080
```

---

## Tailscale Remote Access

```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
sudo systemctl enable tailscaled
tailscale ip -4
```

Authorize via the URL shown. Once connected access the dashboard from anywhere at:

```
http://your-hostname:8080
```

Install Tailscale on your phone and laptop from https://tailscale.com/download and log in with the same account.

---

## Dashboard Login

The dashboard is protected by a login page. Set your credentials in `.env`:

```
DASHBOARD_USERNAME=your_username
DASHBOARD_PASSWORD=your_strong_password
SECRET_KEY=your_generated_hex_key
```

Generate the secret key:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

After updating `.env` restart the service:

```bash
cp ~/.env ~/social-poster/.env
chmod 600 ~/social-poster/.env
sudo systemctl restart social-poster
```

---

## Maintenance

### Service management

```bash
sudo systemctl status social-poster
sudo systemctl restart social-poster
sudo systemctl stop social-poster
journalctl -u social-poster --no-pager | tail -30
```

### Check for throttling after overclock changes

```bash
vcgencmd get_throttled     # 0x0 = no throttling
vcgencmd measure_temp
vcgencmd measure_clock arm
```

### Verify Facebook token is permanent

```bash
APP_ID="your_app_id"
APP_SECRET="your_app_secret"
FB_TOKEN=$(grep FACEBOOK_PAGE_ACCESS_TOKEN ~/social-poster/.env | cut -d= -f2)

curl -s "https://graph.facebook.com/debug_token?input_token=${FB_TOKEN}&access_token=${APP_ID}%7C${APP_SECRET}" | python3 -m json.tool
# Look for "type": "PAGE" and "expires_at": 0
```

### Dry run mode

Keep `DRY_RUN=true` in `.env` while testing. Set to `false` to go live. Restart the service after any `.env` change:

```bash
sudo systemctl restart social-poster
```

---

## Pending / Future

- **Instagram** — requires Instagram Business account properly linked to Facebook Page via Meta Business Suite
- **LinkedIn Company Page** — requires Marketing Developer Platform approval (submit request in LinkedIn Developer Portal)
- **Scheduled posts UI** — `scheduled_at` field exists in the database schema, UI not yet built
- **Post templates** — for recurring content formats
- **Grafana dashboard** — SQLite datasource over the `post_events` table

---

## Access

| Method | URL |
|---|---|
| Local network | `http://your-hostname.local:8080` |
| Tailscale (anywhere) | `http://your-hostname:8080` |
| Tailscale IP | `http://100.x.x.x:8080` |

---

## License

MIT
