#!/usr/bin/env python3
"""启动 GPT-SoVITS 推理 API 服务（供 synthesize.py 调用）。

用法：python3 serve.py [--port 9880]
前置：venv 依赖已装，预训练模型已放到 GPT_SoVITS/pretrained_models/。
"""
import argparse
import os
import subprocess
import sys

LIB = os.path.dirname(os.path.abspath(__file__))
SOVITS = os.path.expanduser("~/workspace/vendor/GPT-SoVITS")
VENV_PY = os.path.join(LIB, "venv", "bin", "python")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=9880)
    args = ap.parse_args()
    if not os.path.exists(VENV_PY):
        sys.exit("venv 不存在，先跑环境安装")
    env = dict(os.environ)
    env["DEVICE"] = env.get("DEVICE", "cpu")
    print(f"启动 GPT-SoVITS API :{args.port} ...", flush=True)
    subprocess.run(
        [VENV_PY, "api_v2.py", "-a", "127.0.0.1", "-p", str(args.port)],
        cwd=SOVITS, env=env,
    )


if __name__ == "__main__":
    main()
