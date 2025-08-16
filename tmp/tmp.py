from matplotlib.font_manager import fontManager
found_fonts = set()

for font in fontManager.ttflist:
    found_fonts.add(font.name)

if not found_fonts:
    print("没有找到任何字体")
else:
    # 排序后打印，方便查看
    for i, font_name in enumerate(sorted(list(found_fonts))):
        print(f"{i+1}. {font_name}")

if "Noto Sans CJK SC" in found_fonts:
    print("正确，已找到 Noto Sans CJK SC 字体")
else:
    print("错误，未找到 Noto Sans CJK SC 字体")