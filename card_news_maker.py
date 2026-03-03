"""
카드뉴스 메이커 - Pillow 기반 카드뉴스 이미지 생성기
사용법: python card_news_maker.py [content.json] [--theme THEME] [--output OUTPUT_DIR]
"""

import json
import os
import sys
import argparse
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ─── 상수 ───────────────────────────────────────────────────────────────────
CARD_SIZE = (1080, 1080)
FONT_DIR = Path("C:/Windows/Fonts")

# 폰트 경로
FONTS = {
    "regular": FONT_DIR / "malgun.ttf",
    "bold": FONT_DIR / "malgunbd.ttf",
    "light": FONT_DIR / "malgunsl.ttf",
}

# 컬러 테마 정의
THEMES = {
    "blue": {
        "cover_bg": [(15, 32, 80), (30, 90, 180)],
        "cover_accent": (100, 180, 255),
        "cover_text": (255, 255, 255),
        "content_bg": (248, 250, 255),
        "content_text": (30, 40, 60),
        "content_title": (15, 60, 150),
        "content_accent": (30, 100, 220),
        "quote_bg": [(15, 50, 120), (30, 90, 180)],
        "quote_text": (255, 255, 255),
        "end_bg": (15, 32, 80),
        "end_text": (255, 255, 255),
        "end_accent": (100, 180, 255),
        "tag_bg": (30, 100, 220),
        "tag_text": (255, 255, 255),
    },
    "coral": {
        "cover_bg": [(180, 50, 50), (230, 100, 80)],
        "cover_accent": (255, 200, 160),
        "cover_text": (255, 255, 255),
        "content_bg": (255, 250, 248),
        "content_text": (60, 30, 30),
        "content_title": (200, 60, 60),
        "content_accent": (220, 80, 80),
        "quote_bg": [(180, 60, 50), (220, 100, 80)],
        "quote_text": (255, 255, 255),
        "end_bg": (200, 60, 60),
        "end_text": (255, 255, 255),
        "end_accent": (255, 200, 160),
        "tag_bg": (220, 80, 80),
        "tag_text": (255, 255, 255),
    },
    "green": {
        "cover_bg": [(20, 80, 50), (40, 160, 80)],
        "cover_accent": (150, 255, 180),
        "cover_text": (255, 255, 255),
        "content_bg": (245, 255, 248),
        "content_text": (20, 50, 30),
        "content_title": (30, 120, 60),
        "content_accent": (40, 150, 80),
        "quote_bg": [(20, 80, 50), (40, 150, 80)],
        "quote_text": (255, 255, 255),
        "end_bg": (20, 80, 50),
        "end_text": (255, 255, 255),
        "end_accent": (150, 255, 180),
        "tag_bg": (40, 150, 80),
        "tag_text": (255, 255, 255),
    },
    "purple": {
        "cover_bg": [(60, 20, 120), (120, 60, 200)],
        "cover_accent": (220, 180, 255),
        "cover_text": (255, 255, 255),
        "content_bg": (252, 248, 255),
        "content_text": (40, 20, 60),
        "content_title": (100, 40, 180),
        "content_accent": (120, 60, 200),
        "quote_bg": [(60, 20, 120), (120, 60, 200)],
        "quote_text": (255, 255, 255),
        "end_bg": (60, 20, 120),
        "end_text": (255, 255, 255),
        "end_accent": (220, 180, 255),
        "tag_bg": (120, 60, 200),
        "tag_text": (255, 255, 255),
    },
    "dark": {
        "cover_bg": [(20, 20, 25), (45, 45, 55)],
        "cover_accent": (200, 200, 220),
        "cover_text": (255, 255, 255),
        "content_bg": (28, 28, 35),
        "content_text": (220, 220, 230),
        "content_title": (180, 200, 255),
        "content_accent": (120, 150, 255),
        "quote_bg": [(25, 25, 35), (45, 45, 60)],
        "quote_text": (240, 240, 255),
        "end_bg": (20, 20, 25),
        "end_text": (255, 255, 255),
        "end_accent": (120, 150, 255),
        "tag_bg": (80, 100, 200),
        "tag_text": (255, 255, 255),
    },
    "white": {
        "cover_bg": [(240, 245, 255), (255, 255, 255)],
        "cover_accent": (80, 120, 200),
        "cover_text": (30, 40, 80),
        "content_bg": (255, 255, 255),
        "content_text": (40, 40, 60),
        "content_title": (60, 80, 160),
        "content_accent": (80, 120, 200),
        "quote_bg": [(235, 240, 255), (245, 250, 255)],
        "quote_text": (40, 60, 120),
        "end_bg": (240, 245, 255),
        "end_text": (30, 40, 80),
        "end_accent": (80, 120, 200),
        "tag_bg": (80, 120, 200),
        "tag_text": (255, 255, 255),
    },
}


# ─── 유틸리티 함수 ────────────────────────────────────────────────────────────

def load_font(style="regular", size=40):
    """폰트 로드 (실패시 기본 폰트 사용)"""
    try:
        return ImageFont.truetype(str(FONTS.get(style, FONTS["regular"])), size)
    except (OSError, IOError):
        return ImageFont.load_default()


def draw_gradient(img, color_start, color_end, direction="vertical"):
    """그라디언트 배경 그리기"""
    w, h = img.size
    draw = ImageDraw.Draw(img)
    for i in range(h if direction == "vertical" else w):
        ratio = i / (h if direction == "vertical" else w)
        r = int(color_start[0] + (color_end[0] - color_start[0]) * ratio)
        g = int(color_start[1] + (color_end[1] - color_start[1]) * ratio)
        b = int(color_start[2] + (color_end[2] - color_start[2]) * ratio)
        if direction == "vertical":
            draw.line([(0, i), (w, i)], fill=(r, g, b))
        else:
            draw.line([(i, 0), (i, h)], fill=(r, g, b))


def wrap_text(text, font, max_width, draw):
    """텍스트를 max_width에 맞게 줄바꿈"""
    lines = []
    for paragraph in text.split('\n'):
        if not paragraph.strip():
            lines.append('')
            continue
        words = list(paragraph)  # 한글은 글자 단위로 처리
        # 단어 기반 처리 (영어 포함)
        current_line = ''
        for char in paragraph:
            test_line = current_line + char
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = char
        if current_line:
            lines.append(current_line)
    return lines


def get_text_height(lines, font, line_spacing=1.4):
    """여러 줄 텍스트의 총 높이 계산"""
    if not lines:
        return 0
    bbox = ImageDraw.Draw(Image.new('RGB', (1, 1))).textbbox((0, 0), "가", font=font)
    line_height = bbox[3] - bbox[1]
    return int(line_height * line_spacing * len(lines))


def draw_multiline_text(draw, lines, x, y, font, fill, line_spacing=1.4, align="left", max_width=None):
    """여러 줄 텍스트 그리기"""
    bbox = draw.textbbox((0, 0), "가", font=font)
    line_height = int((bbox[3] - bbox[1]) * line_spacing)
    for i, line in enumerate(lines):
        if not line:
            y += line_height
            continue
        if align == "center" and max_width:
            lbbox = draw.textbbox((0, 0), line, font=font)
            lw = lbbox[2] - lbbox[0]
            lx = x + (max_width - lw) // 2
        elif align == "right" and max_width:
            lbbox = draw.textbbox((0, 0), line, font=font)
            lw = lbbox[2] - lbbox[0]
            lx = x + max_width - lw
        else:
            lx = x
        draw.text((lx, y), line, font=font, fill=fill)
        y += line_height
    return y


def draw_rounded_rect(draw, xy, radius, fill=None, outline=None, width=1):
    """둥근 모서리 사각형"""
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle([x1, y1, x2, y2], radius=radius, fill=fill, outline=outline, width=width)


def add_page_indicator(draw, current, total, theme, y_pos=1020, size=8, spacing=20):
    """페이지 인디케이터 (점) 추가"""
    total_width = total * size + (total - 1) * spacing
    start_x = (CARD_SIZE[0] - total_width) // 2
    for i in range(total):
        cx = start_x + i * (size + spacing) + size // 2
        if i == current:
            draw.ellipse([cx - size, y_pos - size, cx + size, y_pos + size],
                         fill=theme["cover_accent"])
        else:
            draw.ellipse([cx - size // 2, y_pos - size // 2, cx + size // 2, y_pos + size // 2],
                         fill=(*theme["cover_accent"][:3], 100))


# ─── 카드 렌더러 ──────────────────────────────────────────────────────────────

class CardRenderer:
    def __init__(self, theme_name="blue", brand="", total_cards=1):
        self.theme = THEMES.get(theme_name, THEMES["blue"])
        self.brand = brand
        self.total_cards = total_cards
        self.W, self.H = CARD_SIZE

    def _base_image(self):
        return Image.new("RGB", CARD_SIZE, (255, 255, 255))

    def render_cover(self, card_data, card_index):
        """커버 카드 렌더링"""
        img = self._base_image()
        draw_gradient(img, self.theme["cover_bg"][0], self.theme["cover_bg"][1])
        draw = ImageDraw.Draw(img)

        # 장식 원
        draw.ellipse([-100, -100, 300, 300], fill=(*self.theme["cover_accent"][:3], 30))
        draw.ellipse([800, 700, 1200, 1200], fill=(*self.theme["cover_accent"][:3], 20))
        draw.ellipse([700, -50, 1100, 350], fill=(*self.theme["cover_accent"][:3], 15))

        # 브랜드 태그
        if self.brand:
            brand_font = load_font("bold", 28)
            bx, by = 60, 60
            bbox = draw.textbbox((0, 0), self.brand, font=brand_font)
            bw = bbox[2] - bbox[0] + 24
            bh = bbox[3] - bbox[1] + 12
            draw_rounded_rect(draw, [bx, by, bx + bw, by + bh], radius=8,
                               fill=self.theme["tag_bg"])
            draw.text((bx + 12, by + 6), self.brand, font=brand_font,
                      fill=self.theme["tag_text"])

        # 시리즈 번호 (있을 경우)
        series = card_data.get("series", "")
        if series:
            s_font = load_font("regular", 32)
            draw.text((60, 130), series, font=s_font,
                      fill=(*self.theme["cover_accent"][:3],))

        # 제목
        title = card_data.get("title", "")
        title_font = load_font("bold", 80)
        max_w = self.W - 120
        title_lines = wrap_text(title, title_font, max_w, draw)

        # 제목 Y 위치 계산 (세로 중앙)
        title_h = get_text_height(title_lines, title_font, 1.2)
        subtitle = card_data.get("subtitle", "")
        sub_font = load_font("regular", 40)
        sub_lines = wrap_text(subtitle, sub_font, max_w, draw) if subtitle else []
        sub_h = get_text_height(sub_lines, sub_font, 1.4) if sub_lines else 0
        gap = 40 if subtitle else 0

        total_h = title_h + gap + sub_h
        start_y = (self.H - total_h) // 2

        y = draw_multiline_text(draw, title_lines, 60, start_y,
                                title_font, self.theme["cover_text"], 1.2)

        if sub_lines:
            y += gap
            draw_multiline_text(draw, sub_lines, 60, y, sub_font,
                                (*self.theme["cover_accent"],), 1.4)

        # 구분선
        line_y = start_y - 30
        draw.line([(60, line_y), (180, line_y)], fill=self.theme["cover_accent"], width=4)

        # 페이지 인디케이터
        add_page_indicator(draw, card_index, self.total_cards, self.theme)

        return img

    def render_content(self, card_data, card_index):
        """일반 내용 카드 렌더링"""
        img = self._base_image()
        img.paste(self.theme["content_bg"], [0, 0, self.W, self.H])
        draw = ImageDraw.Draw(img)

        # 상단 액센트 바
        draw.rectangle([0, 0, self.W, 8], fill=self.theme["content_accent"])

        # 카드 번호 뱃지
        num_font = load_font("bold", 28)
        num_text = f"{card_index + 1:02d}"
        nx, ny = 60, 50
        nbbox = draw.textbbox((0, 0), num_text, font=num_font)
        nw = nbbox[2] - nbbox[0] + 20
        nh = nbbox[3] - nbbox[1] + 10
        draw_rounded_rect(draw, [nx, ny, nx + nw, ny + nh], radius=6,
                           fill=self.theme["content_accent"])
        draw.text((nx + 10, ny + 5), num_text, font=num_font,
                  fill=(255, 255, 255))

        # 태그
        tags = card_data.get("tags", [])
        tag_x = nx + nw + 16
        for tag in tags[:3]:
            t_font = load_font("regular", 26)
            tbbox = draw.textbbox((0, 0), f"#{tag}", font=t_font)
            tw = tbbox[2] - tbbox[0] + 16
            th = tbbox[3] - tbbox[1] + 8
            draw_rounded_rect(draw, [tag_x, ny, tag_x + tw, ny + th], radius=6,
                               fill=(*self.theme["content_accent"][:3], 30))
            draw.text((tag_x + 8, ny + 4), f"#{tag}", font=t_font,
                      fill=self.theme["content_accent"])
            tag_x += tw + 8

        # 제목
        title = card_data.get("title", "")
        title_font = load_font("bold", 58)
        max_w = self.W - 120
        title_lines = wrap_text(title, title_font, max_w, draw)
        title_y = ny + nh + 50
        y = draw_multiline_text(draw, title_lines, 60, title_y,
                                title_font, self.theme["content_title"], 1.2)

        # 구분선
        y += 30
        draw.line([(60, y), (60 + 80, y)], fill=self.theme["content_accent"], width=3)
        y += 40

        # 본문
        body = card_data.get("body", "")
        body_font = load_font("regular", 38)
        body_lines = wrap_text(body, body_font, max_w, draw)
        y = draw_multiline_text(draw, body_lines, 60, y,
                                body_font, self.theme["content_text"], 1.6)

        # 핵심 포인트 (있을 경우)
        points = card_data.get("points", [])
        if points:
            y += 30
            p_font = load_font("regular", 36)
            for pt in points:
                # 불릿 포인트
                draw.ellipse([60, y + 10, 76, y + 26],
                              fill=self.theme["content_accent"])
                pt_lines = wrap_text(pt, p_font, max_w - 40, draw)
                y = draw_multiline_text(draw, pt_lines, 92, y,
                                        p_font, self.theme["content_text"], 1.5)
                y += 10

        # 하단 장식
        draw.rectangle([0, self.H - 6, self.W, self.H], fill=self.theme["content_accent"])

        # 페이지 인디케이터
        add_page_indicator(draw, card_index, self.total_cards, self.theme,
                           y_pos=self.H - 30)

        return img

    def render_quote(self, card_data, card_index):
        """인용구 카드 렌더링"""
        img = self._base_image()
        draw_gradient(img, self.theme["quote_bg"][0], self.theme["quote_bg"][1], "diagonal"
                      if False else "vertical")
        draw = ImageDraw.Draw(img)

        # 큰 따옴표 장식
        q_font = load_font("bold", 220)
        draw.text((40, -30), "\"", font=q_font,
                  fill=(*self.theme["cover_accent"][:3], 40))

        # 인용 텍스트
        quote = card_data.get("text", "")
        q_font2 = load_font("bold", 54)
        max_w = self.W - 160
        q_lines = wrap_text(quote, q_font2, max_w, draw)
        q_h = get_text_height(q_lines, q_font2, 1.5)

        # 출처
        source = card_data.get("source", "")
        s_font = load_font("regular", 34)
        s_h = 50 if source else 0

        total_h = q_h + s_h + 40
        start_y = (self.H - total_h) // 2

        y = draw_multiline_text(draw, q_lines, 80, start_y,
                                q_font2, self.theme["quote_text"], 1.5,
                                align="center", max_width=max_w)

        if source:
            y += 40
            draw.line([(self.W // 2 - 60, y), (self.W // 2 + 60, y)],
                      fill=(*self.theme["cover_accent"][:3],), width=2)
            y += 20
            s_bbox = draw.textbbox((0, 0), source, font=s_font)
            sw = s_bbox[2] - s_bbox[0]
            draw.text(((self.W - sw) // 2, y), source, font=s_font,
                      fill=(*self.theme["cover_accent"][:3],))

        # 페이지 인디케이터
        add_page_indicator(draw, card_index, self.total_cards, self.theme)

        return img

    def render_stat(self, card_data, card_index):
        """통계/수치 강조 카드"""
        img = self._base_image()
        img.paste(self.theme["content_bg"], [0, 0, self.W, self.H])
        draw = ImageDraw.Draw(img)

        draw.rectangle([0, 0, self.W, 8], fill=self.theme["content_accent"])

        # 제목
        title = card_data.get("title", "")
        t_font = load_font("bold", 50)
        max_w = self.W - 120
        t_lines = wrap_text(title, t_font, max_w, draw)
        y = 80
        y = draw_multiline_text(draw, t_lines, 60, y, t_font,
                                self.theme["content_title"], 1.3)
        y += 50

        # 통계 항목들
        stats = card_data.get("stats", [])
        s_per_row = 2 if len(stats) > 2 else 1
        box_w = (self.W - 120 - 20 * (s_per_row - 1)) // s_per_row
        box_h = 220

        for i, stat in enumerate(stats[:4]):
            row = i // s_per_row
            col = i % s_per_row
            bx = 60 + col * (box_w + 20)
            by = y + row * (box_h + 20)

            # 박스
            draw_rounded_rect(draw, [bx, by, bx + box_w, by + box_h], radius=16,
                               fill=(255, 255, 255) if self.theme["content_bg"] != (255, 255, 255)
                               else (240, 244, 255))

            # 수치
            num_text = stat.get("value", "")
            n_font = load_font("bold", 72)
            nbbox = draw.textbbox((0, 0), num_text, font=n_font)
            nw = nbbox[2] - nbbox[0]
            draw.text((bx + (box_w - nw) // 2, by + 30),
                      num_text, font=n_font, fill=self.theme["content_accent"])

            # 단위/설명
            label = stat.get("label", "")
            l_font = load_font("regular", 32)
            lbbox = draw.textbbox((0, 0), label, font=l_font)
            lw = lbbox[2] - lbbox[0]
            draw.text((bx + (box_w - lw) // 2, by + 120),
                      label, font=l_font, fill=self.theme["content_text"])

            # 변화율 (있으면)
            change = stat.get("change", "")
            if change:
                c_font = load_font("regular", 28)
                c_color = (80, 180, 100) if change.startswith("+") else (220, 80, 80)
                cbbox = draw.textbbox((0, 0), change, font=c_font)
                cw = cbbox[2] - cbbox[0]
                draw.text((bx + (box_w - cw) // 2, by + 165),
                          change, font=c_font, fill=c_color)

        draw.rectangle([0, self.H - 6, self.W, self.H], fill=self.theme["content_accent"])
        add_page_indicator(draw, card_index, self.total_cards, self.theme,
                           y_pos=self.H - 30)
        return img

    def render_list(self, card_data, card_index):
        """리스트 카드 - 번호 붙은 목록"""
        img = self._base_image()
        img.paste(self.theme["content_bg"], [0, 0, self.W, self.H])
        draw = ImageDraw.Draw(img)

        draw.rectangle([0, 0, self.W, 8], fill=self.theme["content_accent"])

        # 제목
        title = card_data.get("title", "")
        t_font = load_font("bold", 56)
        max_w = self.W - 120
        t_lines = wrap_text(title, t_font, max_w, draw)
        y = 70
        y = draw_multiline_text(draw, t_lines, 60, y, t_font,
                                self.theme["content_title"], 1.2)
        y += 20
        draw.line([(60, y), (140, y)], fill=self.theme["content_accent"], width=3)
        y += 40

        # 리스트 아이템
        items = card_data.get("items", [])
        i_font = load_font("regular", 36)
        n_font = load_font("bold", 32)

        for idx, item in enumerate(items):
            # 번호 원
            cx, cy = 84, y + 20
            draw.ellipse([cx - 22, cy - 22, cx + 22, cy + 22],
                          fill=self.theme["content_accent"])
            num_str = str(idx + 1)
            nbbox = draw.textbbox((0, 0), num_str, font=n_font)
            nw = nbbox[2] - nbbox[0]
            nh = nbbox[3] - nbbox[1]
            draw.text((cx - nw // 2, cy - nh // 2), num_str,
                      font=n_font, fill=(255, 255, 255))

            # 아이템 텍스트
            item_lines = wrap_text(str(item), i_font, max_w - 70, draw)
            y = draw_multiline_text(draw, item_lines, 120, y,
                                    i_font, self.theme["content_text"], 1.5)
            y += 16

        draw.rectangle([0, self.H - 6, self.W, self.H], fill=self.theme["content_accent"])
        add_page_indicator(draw, card_index, self.total_cards, self.theme,
                           y_pos=self.H - 30)
        return img

    def render_end(self, card_data, card_index):
        """마지막 카드 (CTA)"""
        img = self._base_image()
        img.paste(self.theme["end_bg"], [0, 0, self.W, self.H])
        draw = ImageDraw.Draw(img)

        # 장식
        draw.ellipse([-80, self.H - 300, 280, self.H + 80],
                      fill=(*self.theme["end_accent"][:3], 25))
        draw.ellipse([self.W - 200, -80, self.W + 80, 250],
                      fill=(*self.theme["end_accent"][:3], 20))

        # 아이콘 / 체크 원
        cx, cy = self.W // 2, self.H // 2 - 160
        r = 80
        draw.ellipse([cx - r, cy - r, cx + r, cy + r],
                      fill=self.theme["end_accent"])
        # 체크마크
        check_pts = [(cx - 30, cy), (cx - 5, cy + 28), (cx + 35, cy - 25)]
        draw.line(check_pts, fill=self.theme["end_bg"], width=8, joint="curve")

        # 제목
        title = card_data.get("title", "감사합니다")
        t_font = load_font("bold", 72)
        max_w = self.W - 160
        t_lines = wrap_text(title, t_font, max_w, draw)
        t_h = get_text_height(t_lines, t_font, 1.2)
        y = cy + r + 50
        y = draw_multiline_text(draw, t_lines, 80, y, t_font,
                                self.theme["end_text"], 1.2,
                                align="center", max_width=max_w)

        # CTA 텍스트
        cta = card_data.get("cta", "")
        if cta:
            y += 30
            c_font = load_font("regular", 36)
            c_lines = wrap_text(cta, c_font, max_w, draw)
            y = draw_multiline_text(draw, c_lines, 80, y, c_font,
                                    self.theme["end_accent"], 1.4,
                                    align="center", max_width=max_w)

        # 브랜드
        if self.brand:
            b_font = load_font("bold", 30)
            bbbox = draw.textbbox((0, 0), self.brand, font=b_font)
            bw = bbbox[2] - bbbox[0]
            draw.text(((self.W - bw) // 2, self.H - 100),
                      self.brand, font=b_font,
                      fill=(*self.theme["end_accent"][:3],))

        add_page_indicator(draw, card_index, self.total_cards, self.theme)
        return img

    def render_card(self, card_data, card_index):
        """카드 타입에 따라 적절한 렌더러 호출"""
        card_type = card_data.get("type", "content")
        if card_type == "cover":
            return self.render_cover(card_data, card_index)
        elif card_type == "quote":
            return self.render_quote(card_data, card_index)
        elif card_type == "stat":
            return self.render_stat(card_data, card_index)
        elif card_type == "list":
            return self.render_list(card_data, card_index)
        elif card_type == "end":
            return self.render_end(card_data, card_index)
        else:
            return self.render_content(card_data, card_index)


# ─── 메인 생성기 ──────────────────────────────────────────────────────────────

def make_card_news(content_path, theme_override=None, output_dir=None):
    """카드뉴스 생성 메인 함수"""
    # 콘텐츠 로드
    with open(content_path, encoding="utf-8") as f:
        data = json.load(f)

    theme_name = theme_override or data.get("theme", "blue")
    brand = data.get("brand", "")
    cards = data.get("cards", [])
    series_title = data.get("title", "card_news")

    if not cards:
        print("[오류] 카드 데이터가 없습니다.")
        return

    # 출력 디렉토리 설정
    if output_dir is None:
        safe_title = "".join(c for c in series_title if c.isalnum() or c in "_ -")[:30]
        output_dir = Path(content_path).parent / f"output_{safe_title}"
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    renderer = CardRenderer(theme_name, brand, total_cards=len(cards))

    print(f"\n[카드뉴스 생성 시작]")
    print(f"   테마: {theme_name} | 카드 수: {len(cards)}장")
    print(f"   출력: {output_dir}\n")

    generated = []
    for i, card in enumerate(cards):
        img = renderer.render_card(card, i)
        filename = f"card_{i+1:02d}_{card.get('type', 'content')}.png"
        out_path = output_dir / filename
        img.save(out_path, "PNG", quality=95)
        generated.append(out_path)
        print(f"   OK [{i+1}/{len(cards)}] {filename}")

    print(f"\n완료! {len(generated)}장 생성됨 -> {output_dir}")
    return generated


# ─── CLI ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="카드뉴스 메이커 - JSON 설정으로 카드뉴스 이미지 생성",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  python card_news_maker.py example_content.json
  python card_news_maker.py content.json --theme purple
  python card_news_maker.py content.json --theme dark --output ./my_cards

사용 가능한 테마: blue, coral, green, purple, dark, white
카드 타입: cover, content, quote, stat, list, end
        """
    )
    parser.add_argument("content", nargs="?", default="example_content.json",
                        help="콘텐츠 JSON 파일 경로 (기본값: example_content.json)")
    parser.add_argument("--theme", choices=list(THEMES.keys()),
                        help="테마 색상 (JSON 설정 오버라이드)")
    parser.add_argument("--output", "-o",
                        help="출력 디렉토리 경로")
    parser.add_argument("--list-themes", action="store_true",
                        help="사용 가능한 테마 목록 출력")

    args = parser.parse_args()

    if args.list_themes:
        print("사용 가능한 테마:")
        for t in THEMES:
            print(f"  - {t}")
        return

    if not Path(args.content).exists():
        print(f"[오류] 파일을 찾을 수 없습니다: {args.content}")
        print("   example_content.json 파일을 먼저 생성하거나 올바른 경로를 지정하세요.")
        sys.exit(1)

    make_card_news(args.content, args.theme, args.output)


if __name__ == "__main__":
    main()
