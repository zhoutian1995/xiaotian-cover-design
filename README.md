# xiaotian-cover-design · 小天说FDE 封面 Skill

把「两行标题 + 本人照片」变成抖音短视频封面，一次生成四个画幅（9:16 / 3:4 / 16:9 / 4:3）。

## 风格（v6 定版，2026-11 验收）

- **标题**：两行大字从上往下自然连读——第一行白色粗黑体（铺垫/问句），第二行金黄更粗更大（结论/钩子），带黑色投影
- **人物**：本人照片「贴纸抠图」效果（一圈白色描边），胸部以上近景，写实照片感
- **背景**：真实场景虚化（办公室/街头/展会…），无海报特效
- 防裁字（中央安全区）+ 四边无黑边，已内建到提示词模板

## 快速开始

```bash
pip install requests pillow

export OPENAI_API_KEY=sk-xxx        # 你的 OpenAI 兼容 API Key
export OPENAI_BASE_URL=https://xxx  # 你的 OpenAI 兼容接口地址

python3 scripts/make_cover.py \
  --l1 "会自己赚钱的AI" \
  --l2 "才是懂事的AI" \
  --out ~/Desktop/新封面
```

可选参数：`--ref` 换参考照片（默认 `assets/身份参考/本人单照-墨镜皮衣.jpg`）、`--pose` 姿势、`--scene` 场景。

输出：`标题-9比16.png / 3比4.png / 16比9.png / 4比3.png`（1080×1920 / 1080×1440 / 1920×1080 / 1440×1080）。

## 说明

- `assets/身份参考/` 内为作者（小天说FDE）本人照片，**仅限生成作者本人封面使用**，不得移作他人或训练用途
- 生成走 `gpt-image-2` 图片编辑接口（照片换装、保真人五官）；密钥只放环境变量，不进仓库
- 完整设计规范、提示词模板与 7 项审查清单见 [SKILL.md](SKILL.md)
- 历史版本见 [CHANGELOG.md](CHANGELOG.md)
