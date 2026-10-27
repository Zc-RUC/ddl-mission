**[中文](README.md) | English**

# DDL.MISSION

A pixel-space-inspired deadline manager: a single-file web app, local sync server, macOS desktop widget, and GitHub Pages online version.

The default theme is inspired by [careers.kimi.com](https://careers.kimi.com), with three additional one-click themes: **Engineering (Linear) / Cream (Anthropic) / Minimal (Vercel)**.

![screenshot](./screenshot.jpg)

**[Live Demo](https://zc-ruc.github.io/ddl-mission/)**

## Features

- **Real-time countdowns**: an independently updating `T-2d 03:22:42` display for every task; inverted colors under 24 hours and a flashing inverted state for overdue tasks.
- **Eclipse countdown ring**: the ring around the moon represents the elapsed-time ratio of the most urgent task, rendered with Canvas, Bayer ordered dithering, and a slowly rotating pixel moon.
- **Natural-language input**: examples include `明天23:59 交报告` (submit a report tomorrow at 23:59), `每周五 18:00 实习周报` (weekly internship report every Friday at 18:00), `3天后 还书` (return a book in three days), and `12月31日 跨年` (New Year's Eve on December 31). Automatically detects the time, recurrence, category (course/work), and priority (urgent → high).
- **Recurring tasks**: daily, weekly, or monthly; completing a task automatically schedules the next occurrence.
- **Native macOS notifications**: T-24h, T-1h, and overdue reminders from the resident server, **even when the browser is closed**.
- **Four synchronized themes**: Pixel, Engineering, Cream, and Minimal, synchronized across clients through the server.
- **Multi-device real-time sync**: desktop widget, browsers, and LAN devices share the same data within five seconds.
- **Desktop widget**: a compact 300px countdown view with draggable positioning, position memory, and task rows that open the web app.

## Quick Start

```bash
git clone https://github.com/Zc-RUC/ddl-mission.git
cd ddl-mission
python3 server.py            # Start the sync and notification server on 0.0.0.0:8791
open http://127.0.0.1:8791   # Open the web app on macOS
```

No server is required for basic use: **open `index.html` directly**. The pixel font is embedded and works offline. Data falls back to browser localStorage and migrates back to server synchronization when the server becomes available.

## Desktop Widget (macOS, Optional)

1. Install [Übersicht](https://tracesof.net/uebersicht/) (free and open source).
2. Install the widget with one command, which creates the directory and downloads the widget:

```bash
mkdir -p ~/Library/Application\ Support/Übersicht/widgets/ddl-mission.widget && \
curl -L https://raw.githubusercontent.com/Zc-RUC/ddl-mission/main/ubersicht-widget-index.jsx \
  -o ~/Library/Application\ Support/Übersicht/widgets/ddl-mission.widget/index.jsx
```

3. In the Übersicht menu bar icon, choose **Refresh All Widgets**.

Drag the widget with the `···` handle at the top. The bottom bar cycles through themes. Clicking a task row opens the web app in the default browser through Übersicht's built-in `/run/` endpoint.

## Multi-Device Access on a LAN

The server listens on `0.0.0.0:8791` by default. On the same Wi-Fi network, open `http://<your-Mac-name>.local:8791` (or `http://<your-Mac-IP>:8791`) on a phone, iPad, or another computer to synchronize with the Mac widget and web app.

## GitHub Pages

Enable **Settings → Pages → Deploy from a branch → main** to publish the app at `https://<username>.github.io/ddl-mission/`.

The online version stores data in browser localStorage. When accessed on the same Mac that runs the server, it can also synchronize with the server after Chrome's **Local Network** permission is allowed.

## Data & Privacy

- Data is stored locally in `tasks.json` and `settings.json`, both excluded by `.gitignore`; no task data is uploaded to a cloud service.
- The server uses a CORS allowlist limited to `file://`, `127.0.0.1`/`localhost`, and this repository's GitHub Pages origin, plus PNA response headers.
- **Security note**: the server listens on all network interfaces. On an untrusted network, other devices on the same network may access your task list. Add authentication if this is a concern.

## Themes & Development

Add a theme in two steps:

1. In `index.html`, add a variable group following the existing blocks: `body[data-theme="xxx"] { --bg: ...; --fg: ...; --accent: ...; --font: ...; }`. Add the corresponding block to `widget.html` as well.
2. Register the new theme in the `#themes` navigation and in the widget's `THEME_ORDER`.

Tasks and themes synchronize through `GET/PUT /api/tasks` and `GET/PUT /api/settings`, with five-second polling.

## Tech Stack

- Vanilla HTML/CSS/JavaScript with zero runtime dependencies and no build step; single-file `index.html` with the embedded Fusion Pixel 12px Mono font (SIL OFL).
- `server.py`: Python standard library only (`http.server`), providing static hosting, JSON storage, and notification monitoring.
- `widget.html`: compact widget view; `ubersicht-widget-index.jsx`: Übersicht wrapper for dragging, adaptive height, and web-app navigation.

## License

MIT. The `fusion-pixel.otf` font is licensed separately under the SIL Open Font License.
