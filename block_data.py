import pygame


# ==================================================
# ブロック幅
# ==================================================

BLOCK_WIDTHS = {

    "for": 70,

    "ball": 80,
    "goal": 80,

    "=": 60,
    "+=": 70,

    "clear": 90,
    "you": 80,

    "ball_x": 100,
    "ball_y": 100,

    "2": 60,

    "in range(9):": 220,
}


# ==================================================
# コードブロック作成
# ==================================================

def create_blocks(
    block_texts
):

    blocks = []

    x = 20
    y = 485

    gap = 10
    row_gap = 65


    for index, text in enumerate(
        block_texts
    ):

        width = BLOCK_WIDTHS.get(
            text,
            100
        )


        # 横幅を超えたら次の行
        if (
            x + width
            > 680
        ):

            x = 20
            y += row_gap


        rect = pygame.Rect(
            x,
            y,
            width,
            55
        )


        blocks.append({

            "id": index,

            "text": text,

            "rect": rect,

            "start": rect.topleft,

            "slot": None,

            "fixed": False,

            # 後でmain.pyから設定
            "you_selector": False,
        })


        x += (
            width
            + gap
        )


    return blocks


# ==================================================
# Build Code
#
# 常に3行 × 3列
# ==================================================

def create_slots():

    return [

        # ==============================
        # 1行目
        # YOU設定
        # ==============================

        pygame.Rect(
            40,
            625,
            160,
            55
        ),

        pygame.Rect(
            220,
            625,
            160,
            55
        ),

        pygame.Rect(
            400,
            625,
            220,
            55
        ),


        # ==============================
        # 2行目
        # ==============================

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


        # ==============================
        # 3行目
        # ==============================

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
        ),
    ]