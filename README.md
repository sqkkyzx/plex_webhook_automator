# PLEX WEBHOOK AUTOMATOR
该程序为 PLEX 服务器的 WEBHOOK 通知提供一个通知接收后端。通过接收
到的 WEBHOOK 消息，可以和 PLEX 实现联动各类自动化功能。

    ⚠ 项目正在开发中，功能尚不完善，仅少量功能可用。

# 功能

功能目录以 PLEX WEBHOOK 通知的 12 种事件排序，请参考下文：

### LIBARTY.NEW
    添加了一个新项目到用户有权访问的库中。该事件附有一张海报。
- [x] 自动更新为拼音排序
- [x] 自动汉化标签
- [ ] 自动刮削电影版本
- [ ] 通知到企微机器人/飞书机器人

### LIBRARY.ON.DECK
    添加了一个新项目到用户的 On Deck 中。该事件附有一张海报。

### MEDIA.SCROBBLE
    媒体已被观看（播放进度超过 90% ）。
- [ ] 自动发送微博动态
- [ ] 同步标记已看到'豆瓣'

### MEDIA.RATE
    用户对媒体评级。该事件附有一张海报。
- [ ] 同步评分到'豆瓣'

### MEDIA.PLAY
    媒体开始播放。该事件附有一张海报。
- [ ] 链接 Home Assistant 关灯、关窗帘。

### MEDIA.PAUSE
    媒体播放暂停。

### MEDIA.RESUME
    媒体播放恢复。

### MEDIA.STOP
    媒体播放停止。

### ADMIN.DATABASE.BACKUP
    通过计划任务成功完成数据库备份。
- [ ] 复制最近的数据库备份到其他位置

### ADMIN.DATABASE.CORRUPTED
    在服务器数据库中检测到损坏。
- [ ] 通知到企微机器人/飞书机器人

### DEVICE.NEW
    一台新的设备访问了服务器（仅意味着登录并连接服务器，不代表浏览或播放）。

### PLAYBACK.STARTED
    服务器的共享用户播放了媒体。该事件附有一张海报。