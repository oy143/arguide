# 音频文件夹

多点位模板默认引用以下文件：

```text
spot0.mp3
spot1.mp3
spot2.mp3
spot3.mp3
spot4.mp3
```

学生可以用 Edge TTS、剪映、Audacity 或手机录音生成 MP3 文件，并按上面的名称放入本文件夹。

如果暂时没有音频，可以先删除 `spots` 数组中的 `audioFile` 字段。多点位模板也内置了浏览器 TTS 降级逻辑：音频文件播放失败时，会自动朗读该点位标题和介绍。
