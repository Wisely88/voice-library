# 自有语音库 · voice_library/

用 GPT-SoVITS zero-shot v2 克隆的专属角色音色，后续配音不再依赖外部 API。
2026-10-13 已验证：4 个音色全部合成成功。

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
│   └── v1narrator/     # 微课旁白（种子 avocado_v2:MAI_03）
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
