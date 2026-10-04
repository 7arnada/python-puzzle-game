import pygame


# =========================
# ブロックのサイズ
# =========================

BLOCK_WIDTHS = {
    "for": 70,
    "ball": 80,
    "goal": 80,
    "=": 60,
    "clear": 90,
    "in range(9):": 220,
    "ball_x": 100,
    "ball_y": 100,
    "+=": 70,
    "2": 60
}


# =========================
# ステージ用ブロック生成
# =========================

def create_blocks(block_texts):

    blocks = []

    x = 20
    y = 500

    gap = 10

    for index, text in enumerate(block_texts):

        width = BLOCK_WIDTHS.get(
            text,
            100
        )

        # 右端を超えそうなら次の段へ
        if x + width > 680:

            x = 20
            y += 70

        rect = pygame.Rect(
            x,
            y,
            width,
            55
        )

        blocks.append(
            {
                "id": index,
                "text": text,
                "rect": rect,
                "start": rect.topleft,
                "slot": None
            }
        )

        x += width + gap

    return blocks


# =========================
# Build Code
# =========================

def create_slots():

    return [
        # 1行目
        pygame.Rect(
            40,
            690,
            160,
            55
        ),

        pygame.Rect(
            220,
            690,
            160,
            55
        ),

        pygame.Rect(
            400,
            690,
            220,
            55
        ),

        # 2行目
        pygame.Rect(
            40,
            755,
            160,
            55
        ),

        pygame.Rect(
            220,
            755,
            160,
            55
        ),

        pygame.Rect(
            400,
            755,
            220,
            55
        )
    ]