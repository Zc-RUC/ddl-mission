# DDL.MISSION 控制舱

像素太空风的截止日期（DDL）管理器，风格致敬 [careers.kimi.com](https://careers.kimi.com)。
单文件网页应用 + 本地同步服务器 + macOS 桌面小组件。

![style](https://img.shields.io/badge/style-careers.kimi-black) ![font](https://img.shields.io/badge/font-Fusion%20Pixel%20(OFL)-black)

## 功能

- **实时倒计时**：`T-2d 04:12:33` 秒级刷新；<24h 反色、逾期反色闪烁
- **日食倒计时环**：绕月光环显示最紧急任务的时间流逝比，月球缓慢自转（Canvas + Bayer 有序抖动渲染）
- **自然语言输入**：`明天23:59 交报告`、`每周五 18:00 实习周报`、`3天后 还书`，自动识别时间/循环/分类/优先级
- **循环任务**：每天 / 每周 / 每月，勾选自动续期
- **macOS 原生通知**：T-24h / T-1h / 已逾期三档提醒，浏览器关了也能收到（由常驻服务器发出）
- **三端同步**：桌面小组件、浏览器、双击本地文件，读写同一份数据（5 秒轮询）
- **桌面小组件**：Übersicht 驱动，300px 精简提醒视图，可拖动、位置记忆、高度自适应
- 像素字体：[Fusion Pixel 12px Mono](https://github.com/TakWolf/fusion-pixel-font)（SIL OFL 协议）

## 使用

```bash
# 启动本地服务器（同步 + 通知）
python3 server.py
# 打开网页版
open http://127.0.0.1:8791
```

- 双击 `index.html` 也能用（字体已内嵌，离线可用，数据自动降级为浏览器本地存储；服务器在线时自动同步）
- 桌面小组件：安装 [Übersicht](https://tracesof.net/uebersicht/)，把 `index.jsx` 风格的 iframe widget 指向 `http://127.0.0.1:8791/widget.html`（仓库中未含，见 wiki/后续补充）
- 数据保存在 `tasks.json`（.gitignore 已排除）

## 在线版

GitHub Pages 静态托管：<https://zc-ruc.github.io/ddl-mission/>
（在本机且本地服务器运行时，在线版同样与服务器同步；离线时为空初始状态）
