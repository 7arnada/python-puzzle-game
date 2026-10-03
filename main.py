import pygame
import sys

from settings import (
    BASE_WIDTH,
    BASE_HEIGHT,
    RUN_BUTTON_RECT
)

from block_data import (
    create_blocks,
    create_slots
)

from rules import (
    build_program,
    judge_code
)

from renderer import (
    draw_board,
    draw_game_state,
    draw_result_message,
    draw_ui
)


# =========================
# Pygame初期化
# =========================

pygame.init()

screen = pygame.display.set_mode(
    (
        BASE_WIDTH,
        BASE_HEIGHT
    ),
    pygame.RESIZABLE
)

pygame.display.set_caption(
    "Python Puzzle Game"
)

game_surface = pygame.Surface(
    (
        BASE_WIDTH,
        BASE_HEIGHT
    )
)

clock = pygame.time.Clock()

font = pygame.font.Font(
    None,
    34
)

small_font = pygame.font.Font(
    None,
    26
)


# =========================
# ブロック・スロット
# =========================

blocks = create_blocks()

slots = create_slots()

slot_contents = [
    None
    for _ in slots
]

button_rect = pygame.Rect(
    *RUN_BUTTON_RECT
)


# =========================
# 状態
# =========================

dragging_block = None

drag_offset_x = 0
drag_offset_y = 0

current_rule = None

running = True


# =========================
# マウス座標変換
# =========================

def get_game_mouse_pos(pos):

    window_width, window_height = (
        screen.get_size()
    )

    scale = min(
        window_width / BASE_WIDTH,
        window_height / BASE_HEIGHT
    )

    if scale <= 0:

        return -9999, -9999

    scaled_width = (
        BASE_WIDTH * scale
    )

    scaled_height = (
        BASE_HEIGHT * scale
    )

    offset_x = (
        window_width
        - scaled_width
    ) / 2

    offset_y = (
        window_height
        - scaled_height
    ) / 2

    game_x = (
        pos[0]
        - offset_x
    ) / scale

    game_y = (
        pos[1]
        - offset_y
    ) / scale

    return (
        int(game_x),
        int(game_y)
    )


# =========================
# メインループ
# =========================

while running:

    # =====================
    # イベント
    # =====================

    for event in pygame.event.get():

        # -----------------
        # 終了
        # -----------------

        if event.type == pygame.QUIT:

            running = False


        # -----------------
        # マウス押下
        # -----------------

        if event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1:

                mouse_pos = (
                    get_game_mouse_pos(
                        event.pos
                    )
                )

                block_clicked = False

                # ブロック判定
                for block in reversed(blocks):

                    if block[
                        "rect"
                    ].collidepoint(
                        mouse_pos
                    ):

                        block_clicked = True

                        dragging_block = block

                        # 編集したら結果解除
                        current_rule = None

                        # スロットから取り外す
                        if block[
                            "slot"
                        ] is not None:

                            old_slot = (
                                block["slot"]
                            )

                            slot_contents[
                                old_slot
                            ] = None

                            block["slot"] = None

                        drag_offset_x = (
                            mouse_pos[0]
                            - block["rect"].x
                        )

                        drag_offset_y = (
                            mouse_pos[1]
                            - block["rect"].y
                        )

                        break

                # -----------------
                # RUN
                # -----------------

                if not block_clicked:

                    if button_rect.collidepoint(
                        mouse_pos
                    ):

                        program = (
                            build_program(
                                slot_contents
                            )
                        )

                        current_rule = (
                            judge_code(
                                program
                            )
                        )


        # -----------------
        # ドラッグ
        # -----------------

        if event.type == pygame.MOUSEMOTION:

            if dragging_block is not None:

                mouse_pos = (
                    get_game_mouse_pos(
                        event.pos
                    )
                )

                dragging_block[
                    "rect"
                ].x = (
                    mouse_pos[0]
                    - drag_offset_x
                )

                dragging_block[
                    "rect"
                ].y = (
                    mouse_pos[1]
                    - drag_offset_y
                )


        # -----------------
        # ドロップ
        # -----------------

        if event.type == pygame.MOUSEBUTTONUP:

            if (
                event.button == 1
                and
                dragging_block is not None
            ):

                placed = False

                for index, slot in enumerate(
                    slots
                ):

                    if slot.colliderect(
                        dragging_block[
                            "rect"
                        ]
                    ):

                        old_block = (
                            slot_contents[
                                index
                            ]
                        )

                        # 既にブロックがある
                        if old_block is not None:

                            old_block[
                                "rect"
                            ].topleft = (
                                old_block[
                                    "start"
                                ]
                            )

                            old_block[
                                "slot"
                            ] = None

                        # 新しいブロックを配置
                        dragging_block[
                            "rect"
                        ].center = (
                            slot.center
                        )

                        dragging_block[
                            "slot"
                        ] = index

                        slot_contents[
                            index
                        ] = dragging_block

                        placed = True

                        break

                # スロット外
                if not placed:

                    dragging_block[
                        "rect"
                    ].topleft = (
                        dragging_block[
                            "start"
                        ]
                    )

                    dragging_block[
                        "slot"
                    ] = None

                dragging_block = None


    # =====================
    # 描画
    # =====================

    game_surface.fill(
        "white"
    )

    # 盤面
    draw_board(
        game_surface
    )

    # ball / goal / 実行結果
    draw_game_state(
        game_surface,
        current_rule,
        font
    )

    # CLEAR / FAILED
    draw_result_message(
        game_surface,
        current_rule,
        font
    )

    # ブロックUI
    draw_ui(
        game_surface,
        blocks,
        slots,
        button_rect,
        font,
        small_font
    )


    # =====================
    # 自動リサイズ
    # =====================

    window_width, window_height = (
        screen.get_size()
    )

    scale = min(
        window_width / BASE_WIDTH,
        window_height / BASE_HEIGHT
    )

    scaled_width = max(
        1,
        int(
            BASE_WIDTH * scale
        )
    )

    scaled_height = max(
        1,
        int(
            BASE_HEIGHT * scale
        )
    )

    scaled_surface = (
        pygame.transform.smoothscale(
            game_surface,
            (
                scaled_width,
                scaled_height
            )
        )
    )

    screen.fill(
        "black"
    )

    offset_x = (
        window_width
        - scaled_width
    ) // 2

    offset_y = (
        window_height
        - scaled_height
    ) // 2

    screen.blit(
        scaled_surface,
        (
            offset_x,
            offset_y
        )
    )

    pygame.display.flip()

    clock.tick(60)


pygame.quit()
sys.exit()