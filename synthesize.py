#!/usr/bin/env python3
"""自有语音库合成入口（GPT-SoVITS zero-shot）。

前置：API 服务已启动（python3 serve.py，或直接跑 GPT-SoVITS/api_v2.py）。

用法：
    python3 synthesize.py --voice diandian --text "同学们好" --out out.wav
    python3 synthesize.py --voice xiaohu --text "Hello!" --lang en --out out.wav
    python3 synthesize.py --list
"""
import argparse
import os
import sys
import sys

import requests
import yaml

LIB = os.path.dirname(os.path.abspath(__file__))
API = os.environ.get("SOVITS_API", "http://127.0.0.1:9880")


def load_voice(voice_id: str) -> dict:
    d = os.path.join(LIB, "voices", voice_id)
    meta = os.path.join(d, "meta.yaml")
    if not os.path.exists(meta):
        raise SystemExit(f"未知音色 '{voice_id}'，可用：{list_voices()}")
    with open(meta, encoding="utf-8") as f:
        m = yaml.safe_load(f)
    ref_txt = os.path.join(d, "ref.txt")
    with open(ref_txt, encoding="utf-8") as f:
        m["ref_text"] = f.read().strip()
    m["ref_audio"] = os.path.join(d, m["ref_audio"])
    return m


def list_voices() -> list:
    vdir = os.path.join(LIB, "voices")
    return sorted(d for d in os.listdir(vdir)
                  if os.path.exists(os.path.join(vdir, d, "meta.yaml")))


def synthesize(voice_id: str, text: str, out: str, lang: str = "zh",
               speed: float = 1.0) -> str:
    m = load_voice(voice_id)
    payload = {
        "text": text,
        "text_lang": lang,
        "ref_audio_path": m["ref_audio"],
        "prompt_text": m["ref_text"],
        "prompt_lang": m.get("lang", "zh"),
        "media_type": "wav",
        "speed_factor": speed,
        "streaming_mode": False,
    }
    r = requests.post(f"{API}/tts", json=payload, timeout=600)
    r.raise_for_status()
    with open(out, "wb") as f:
        f.write(r.content)
    if os.path.getsize(out) < 1024:
        raise RuntimeError("合成返回空音频")
    return out


def main():
    ap = argparse.ArgumentParser(description="自有语音库合成")
    ap.add_argument("--voice", default="", help="音色 id")
    ap.add_argument("--text", default="", help="合成文本")
    ap.add_argument("--text-stdin", action="store_true", help="从 stdin 读取合成文本")
    ap.add_argument("--out", default="", help="输出 wav 路径")
    ap.add_argument("--lang", default="zh", help="zh|en|ja")
    ap.add_argument("--speed", type=float, default=1.0)
    ap.add_argument("--list", action="store_true", help="列出所有音色")
    args = ap.parse_args()

    if args.list:
        for v in list_voices():
            m = load_voice(v)
            print(f"{v:12} {m['name']:8} {m['role']}")
        return
    text = sys.stdin.read() if args.text_stdin else args.text
    if not args.voice or not text.strip() or not args.out:
        ap.error("--voice/--text(--text-stdin)/--out 必填")
    out = synthesize(args.voice, text, args.out, args.lang, args.speed)
    print(f"OK: {out} ({os.path.getsize(out)//1024}KB)")


if __name__ == "__main__":
    main()
