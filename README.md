# 自有语音库 · voice_library/

用 GPT-SoVITS zero-shot v2 克隆的专属角色音色，后续配音不再依赖外部 API。
2026-10-13 已验证：9 个音色全部合成成功（4 种子音色 + 3 变调角色音色 + 2 方言特色音色）。

## 结构

```
voice_library/
├── venv/               # Python 虚拟环境（torch CPU + GPT-SoVITS 依赖）
├── serve.py            # 启动推理 API（python3 serve.py）
├── synthesize.py       # 合成入口（支持 --text-stdin）
├── api.log             # 服务日志
├── voices/
│   ├── narrator/       # 旁白（种子 avocado_v2:casper）
│   ├── diandian/       # 电电老师（种子 avocado_v2:MAI_01）
│   ├── xiaohu/         # 小糊（种子 avocado_v2:rumi）
│   ├── lele/           # 乐乐（由 diandian +5 半音变调设计，阳光小男孩）
│   ├── mia/            # 米娅（由 v1narrator +3 半音变调设计，好奇小女孩）
│   ├── drhoot/         # 睿博士（由 narrator -4 半音变调设计，睿智长者）
│   ├── v1narrator/     # 微课旁白（种子 avocado_v2:MAI_03）
│   ├── sichuan/        # 四川话博主（YouTube四川话段子截取，方言口音普通话）
│   └── canto/          # 粤语说书人（YouTube粤语讲古截取，真粤语 lang=yue）
│       ├── ref.wav     # 参考音频（3~10 秒，API 硬性要求；32kHz 单声道）
│       ├── ref.txt     # 参考音频逐字稿（必须与音频逐字对应！）
│       └── meta.yaml   # 音色元数据
└── README.md
```

## 使用

```bash
# 1. 启动 API 服务（systemd 常驻，VM 重启自动拉起；CPU 加载模型约 40 秒）
sudo systemctl enable --now voice-library-api.service
# 查看状态 / 日志：
systemctl status voice-library-api.service
tail -f ~/workspace/voice_library/api.log
# 手动单次启动（调试用）：
cd ~/workspace/voice_library && python3 serve.py

# 2. 合成
venv/bin/python synthesize.py --voice diandian --text "同学们好" --out out.wav

# 3. 查看所有音色
venv/bin/python synthesize.py --list
```

## 新增音色（三步）

1. 准备 **3~10 秒**清晰参考音频（无背景音乐、无杂音），存为 `voices/<id>/ref.wav`
  （32kHz 单声道；超 10 秒 API 会直接拒绝）。
2. 写准逐字稿 `ref.txt`（必须和音频逐字对应，错一个字都会影响克隆质量）。
3. 写 `meta.yaml`（参考现有），然后 `synthesize.py --list` 确认。

## GitHub 备份

代码与音色元数据直接在 [Wisely88/voice-library](https://github.com/Wisely88/voice-library)
备份。参考音频（mp3 二进制）以 base64 文本形式存为 `voices/<id>/ref.mp3.b64`
（MCP 通道传不了二进制），还原：

```bash
base64 -d voices/diandian/ref.mp3.b64 > voices/diandian/ref.mp3
ffmpeg -y -i voices/diandian/ref.mp3 -ar 32000 -ac 1 voices/diandian/ref.wav
```

## 接入视频管线

`pipeline` 的 `lesson.yaml` 里：

```yaml
voices:
  电电老师: "library:diandian"   # library: 前缀走自有语音库
```

`pipeline/src/tts.py` 已支持：`library:` 前缀自动路由到本地 API，
`avocado_v2:*` 仍走云端；混合对白逐行合成后拼接。API 不可用时报错会提示启动命令。

## 注意事项

- 本机无 GPU，CPU 推理约 15 秒/句，4 分钟配音约需 8~20 分钟，适合批量离线跑。
- 参考音频质量决定克隆上限：最好用真人干净录音；当前 4 个音色是用 API 音色做种子，保证和现有视频 continuity。
- 模型在 `~/workspace/vendor/GPT-SoVITS/GPT_SoVITS/pretrained_models/`（v2 + bert + hubert + G2PW + fast_langdetect，约 3.2GB）。
- 依赖安装曾踩坑：pip 需 `TMPDIR`/`PIP_CACHE_DIR` 指向 workspace（/tmp 只有 512MB）；
  另需 `torchcodec`、`resampy`（新版 torchaudio 要求），NLTK 数据 `cmudict` /
  `averaged_perceptron_tagger_eng` 需从 GitHub 镜像手动放 `~/nltk_data/`（官方源被墙）。
- `wget -c` 续传 LFS 指针文件会在文件头留下 134 字节指针残留——大文件下载用 `curl -L -o` 全量重下。
