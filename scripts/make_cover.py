#!/usr/bin/env python3
"""小天说FDE 封面生成器（跨机器便携版）。

输入标题两行 + 本人参考照，产出四画幅封面（9:16 / 3:4 / 16:9 / 4:3）。
依赖: pip install requests pillow；环境变量 OPENAI_API_KEY + OPENAI_BASE_URL。

用法:
  python3 make_cover.py --l1 "会自己赚钱的AI" --l2 "才是懂事的AI" --out ~/Desktop/新封面
  # 可选: --ref 自定义参考照 --pose 姿势 --scene 场景 --api-key xxx --base-url xxx
"""
import argparse
import base64
import os
import sys
from pathlib import Path

import requests
from PIL import Image

HERE = Path(__file__).resolve().parent
DEFAULT_REF = HERE.parent / "assets" / "身份参考" / "本人单照-墨镜皮衣.jpg"

TITLE_RULE = """第一行白色粗黑体大字：「{l1}」；第二行金黄色（饱和金黄，与第一行白色形成白黄对比，这是本图核心设计，缺一不可）更粗更大字：「{l2}」。两行均带黑色投影。两行从上往下自然连读。"""

NO_BLACK = "重要：画面任何区域不得出现纯黑、深黑条带或黑色边框；所有区域都是连续的虚化真实场景，边缘自然过渡。"

PERSON = "人物：照片中这个男子（黑色墨镜、黑色皮衣、写实、五官不变）以贴纸抠图形式呈现，人物边缘有一圈清晰的白色描边，胸部以上近景，禁止全身照。"

PROMPT_V = """制作竖版抖音封面。硬性排版规则——所有文字必须完整落在画面正中央60%宽的竖向安全区内，任何字的任何笔画不得越过安全区、不得碰到画面左右边缘，每个字完整可见：
{title}
两行占画面上半部。{person}姿势：{pose}，人物放在画面下半部正中央、整体保持在中央60%安全区内。背景：{scene}。{no_black}
除标题外不得出现任何其他文字水印。禁止漫画插画3D。"""

PROMPT_H = """制作横版抖音封面（最终从画面中央裁一条水平横带）。硬性构图：所有内容集中在画面正中央50%高度的水平带内，上下留白区域必须是与人像连续的虚化真实场景背景：
水平带内布局：左侧两行大标题从上往下连读——{title} 文字占横带宽度55%、垂直居中；右侧{person}面向左侧身，姿势：{pose}，人物占横带高度约90%。
文字任何笔画不得被裁切或贴边。背景：{scene}。{no_black}
除标题外不得出现任何其他文字水印。禁止漫画插画3D。"""


def gen_image(prompt: str, ref: Path, api_key: str, base_url: str, out: Path, retries: int = 3) -> None:
    import time
    for attempt in range(1, retries + 1):
        try:
            with open(ref, "rb") as f:
                resp = requests.post(
                    f"{base_url.rstrip('/')}/images/edits",
                    headers={"Authorization": f"Bearer {api_key}"},
                    files={"image": (ref.name, f, "image/jpeg")},
                    data={"model": "gpt-image-2", "prompt": prompt, "n": 1},
                    timeout=300,
                )
            if resp.status_code == 200:
                payload = resp.json()
                item = payload["data"][0]
                if item.get("b64_json"):
                    out.write_bytes(base64.b64decode(item["b64_json"]))
                    return
                if item.get("url"):
                    img = requests.get(item["url"], timeout=120)
                    out.write_bytes(img.content)
                    return
            print(f"  attempt {attempt}: HTTP {resp.status_code} {resp.text[:200]}", file=sys.stderr)
        except Exception as exc:
            print(f"  attempt {attempt}: {type(exc).__name__}: {exc}", file=sys.stderr)
        time.sleep(8 * attempt)
    raise SystemExit("生成失败，请检查 API Key / 网络后重试")


def crops(raw: Path, outdir: Path, stem: str) -> None:
    im = Image.open(raw).convert("RGB")
    w, h = im.size
    outdir.mkdir(parents=True, exist_ok=True)
    if h >= w:
        tw = int(h * 9 / 16); x0 = (w - tw) // 2
        im.crop((x0, 0, x0 + tw, h)).resize((1080, 1920), Image.LANCZOS).save(outdir / f"{stem}-9比16.png")
        tw = int(h * 3 / 4); x0 = (w - tw) // 2
        im.crop((x0, 0, x0 + tw, h)).resize((1080, 1440), Image.LANCZOS).save(outdir / f"{stem}-3比4.png")
    else:
        ch = int(w * 9 / 16); y0 = (h - ch) // 2
        im.crop((0, y0, w, y0 + ch)).resize((1920, 1080), Image.LANCZOS).save(outdir / f"{stem}-16比9.png")
        cw = int(ch * 4 / 3); x0 = (w - cw) // 2  # 4:3 从内容带内裁，避开上下黑条
        im.crop((x0, y0, x0 + cw, y0 + ch)).resize((1440, 1080), Image.LANCZOS).save(outdir / f"{stem}-4比3.png")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--l1", required=True, help="第一行(白色，铺垫/问句)")
    ap.add_argument("--l2", required=True, help="第二行(金黄，结论/钩子)")
    ap.add_argument("--ref", default=str(DEFAULT_REF), help="本人参考照片路径")
    ap.add_argument("--pose", default="抱臂冷脸，直视镜头")
    ap.add_argument("--scene", default="现代办公室窗边，午后暖光，浅景深虚化")
    ap.add_argument("--out", default=".", help="输出目录")
    ap.add_argument("--api-key", default=os.environ.get("OPENAI_API_KEY", ""))
    ap.add_argument("--base-url", default=os.environ.get("OPENAI_BASE_URL", ""))
    args = ap.parse_args()
    if not args.api_key or not args.base_url:
        raise SystemExit("需要 OPENAI_API_KEY 和 OPENAI_BASE_URL（环境变量或参数）")

    title = TITLE_RULE.format(l1=args.l1, l2=args.l2)
    ref = Path(args.ref).expanduser()
    outdir = Path(args.out).expanduser()
    stem = f"{args.l1}{args.l2}"[:24]
    work = outdir / "_raw"
    work.mkdir(parents=True, exist_ok=True)

    print("[1/2] 生成竖版母图…")
    v_raw = work / "v.png"
    gen_image(PROMPT_V.format(title=title, person=PERSON, pose=args.pose, scene=args.scene, no_black=NO_BLACK), ref, args.api_key, args.base_url, v_raw)
    crops(v_raw, outdir, stem)
    print("[2/2] 生成横版母图…")
    h_raw = work / "h.png"
    gen_image(PROMPT_H.format(title=title, person=PERSON, pose=args.pose, scene=args.scene, no_black=NO_BLACK), ref, args.api_key, args.base_url, h_raw)
    crops(h_raw, outdir, stem)
    print(f"完成 → {outdir}/  ({stem}-9比16/3比4/16比9/4比3.png)")


if __name__ == "__main__":
    main()
