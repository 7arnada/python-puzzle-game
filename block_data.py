import pygame


# =========================
# コードブロック一覧
# =========================

BLOCK_SPECS = [
    {
        "text": "for",
        "rect": (20, 500, 70, 55)
    },

    {
        "text": "ball",
        "rect": (100, 500, 80, 55)
    },

    {
        "text": "ball",
        "rect": (190, 500, 80, 55)
    },

    {
        "text": "goal",
        "rect": (280, 500, 80, 55)
    },

    {
        "text": "goal",
        "rect": (370, 500, 80, 55)
    },

    {
        "text": "=",
        "rect": (20, 570, 60, 55)
    },

    {
        "text": "=",
        "rect": (90, 570, 60, 55)
    },

    {
        "text": "clear",
        "rect": (160, 570, 90, 55)
    },

    {
        "text": "clear",
        "rect": (260, 570, 90, 55)
    },

    {
        "text": "in range(9):",
        "rect": (360, 570, 220, 55)
    }
]


# =========================
# Build Codeのスロット
# =========================

SLOT_SPECS = [
    # 1行目
    (40, 690, 160, 55),
    (220, 690, 160, 55),
    (400, 690, 220, 55),

    # 2行目
    (40, 755, 160, 55),
    (220, 755, 160, 55),
    (400, 755, 220, 55)
]


# =========================
# ブロック生成
# =========================

def create_blocks():

    blocks = []

    for index, spec in enumerate(BLOCK_SPECS):

        rect = pygame.Rect(
            *spec["rect"]
        )

        blocks.append(
            {
                "id": index,
                "text": spec["text"],
                "rect": rect,
                "start": rect.topleft,
                "slot": None
            }
        )

    return blocks


# =========================
# スロット生成
# =========================

def create_slots():

    return [
        pygame.Rect(*spec)
        for spec in SLOT_SPECS
    ]