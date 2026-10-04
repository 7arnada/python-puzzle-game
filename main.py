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

from stages import STAGES


# =========================
# Pygame初期化
# =========================

pygame.init()


# =========================
# 最初のウィンドウサイズ
# =========================

display_info = pygame.display.Info()

desktop_width = display_info.current_w
desktop_height = display_info.current_h

max_window_width = int(
    desktop_width * 0.8
)

max_window_height = int(
    desktop_height * 0.8
)

initial_scale = min(
    max_window_width / BASE_WIDTH,
    max_window_height / BASE_HEIGHT,
    1.0
)

window_width = int(
    BASE_WIDTH * initial_scale
)

window_height = int(
    BASE_HEIGHT * initial_scale
)


screen = pygame.display.set_mode(
    (
        window_width,
        window_height
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
# RUNボタン
# =========================

button_rect = pygame.Rect(
    *RUN_BUTTON_RECT
)


# =========================
# NEXT STAGEボタン
# =========================

next_button_rect = pygame.Rect(
    460,
    845,
    200,
    60
)


# =========================
# ステージ
# =========================

current_stage_index = 0


def load_stage(stage_index):

    stage = STAGES[
        stage_index
    ]

    new_blocks = create_blocks(
        stage["blocks"]
    )

    new_slots = create_slots()

    new_slot_contents = [
        None
        for _ in new_slots
    ]

    return (
        stage,
        new_blocks,
        new_slots,
        new_slot_contents
    )


(
    current_stage,
    blocks,
    slots,
    slot_contents
) = load_stage(
    current_stage_index
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

        return (
            -9999,
            -9999
        )

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
# クリア済みか
# =========================

def stage_is_clear():

    # まだRUNしていない
    if current_rule is None:
        return False

    # Syntax Error
    if current_rule.get(
        "syntax_error",
        False
    ):
        return False

    # 実行されたルールを確認
    rules = current_rule.get(
        "rules",
        []
    )

    # clearのルールが1つでもあればクリア
    for rule in rules:

        if rule.get("status") == "clear":
            return True

    return False


# =========================
# メインループ
# =========================

while running:

    # =====================
    # イベント処理
    # =====================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False


        # =====================
        # マウス押下
        # =====================

        if event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1:

                mouse_pos = (
                    get_game_mouse_pos(
                        event.pos
                    )
                )

                block_clicked = False


                # =====================
                # ブロック
                # =====================

                for block in reversed(
                    blocks
                ):

                    if block[
                        "rect"
                    ].collidepoint(
                        mouse_pos
                    ):

                        block_clicked = True

                        dragging_block = block

                        # 編集したら結果解除
                        current_rule = None

                        # スロットから外す
                        if block[
                            "slot"
                        ] is not None:

                            old_slot = (
                                block["slot"]
                            )

                            slot_contents[
                                old_slot
                            ] = None

                            block[
                                "slot"
                            ] = None

                        drag_offset_x = (
                            mouse_pos[0]
                            - block["rect"].x
                        )

                        drag_offset_y = (
                            mouse_pos[1]
                            - block["rect"].y
                        )

                        break


                # =====================
                # RUN
                # =====================

                if not block_clicked:

                    if button_rect.collidepoint(
                        mouse_pos
                    ):

                        program = (
                            build_program(
                                slot_contents
                            )
                        )

                        allowed_rules = (
                            current_stage.get("clear_rules", [])
                            + current_stage.get("failed_rules", [])
                        )

                        current_rule = judge_code(
                            program,
                            allowed_rules
                        )


                # =====================
                # NEXT STAGE
                # =====================

                if (
                    stage_is_clear()
                    and
                    current_stage_index
                    < len(STAGES) - 1
                ):

                    if next_button_rect.collidepoint(
                        mouse_pos
                    ):

                        current_stage_index += 1

                        (
                            current_stage,
                            blocks,
                            slots,
                            slot_contents
                        ) = load_stage(
                            current_stage_index
                        )

                        current_rule = None

                        dragging_block = None


        # =====================
        # ドラッグ
        # =====================

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


        # =====================
        # ドロップ
        # =====================

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

                        # 既存ブロックを戻す
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


                # スロット以外
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


    # =====================
    # ステージ名
    # =====================

    stage_text = font.render(
        current_stage["name"],
        True,
        "black"
    )

    game_surface.blit(
        stage_text,
        (
            20,
            20
        )
    )


    # =====================
    # 盤面
    # =====================

    draw_board(
        game_surface
    )


    # =====================
    # ゲーム状態
    # =====================

    draw_game_state(
    game_surface,
    current_rule,
    font,
    current_stage
    )


    # =====================
    # CLEAR / ERROR
    # =====================

    draw_result_message(
        game_surface,
        current_rule,
        font
    )


    # =====================
    # コードUI
    # =====================

    draw_ui(
        game_surface,
        blocks,
        slots,
        button_rect,
        font,
        small_font
    )


    # =====================
    # NEXT STAGE
    # =====================

    if (
        stage_is_clear()
        and
        current_stage_index
        < len(STAGES) - 1
    ):

        pygame.draw.rect(
            game_surface,
            "lightgreen",
            next_button_rect,
            border_radius=8
        )

        next_text = small_font.render(
            "NEXT STAGE",
            True,
            "black"
        )

        next_rect = (
            next_text.get_rect(
                center=next_button_rect.center
            )
        )

        game_surface.blit(
            next_text,
            next_rect
        )


    # =====================
    # 最終ステージCLEAR
    # =====================

    if (
        stage_is_clear()
        and
        current_stage_index
        == len(STAGES) - 1
    ):

        finish_text = small_font.render(
            "ALL STAGES CLEAR!",
            True,
            "green"
        )

        finish_rect = (
            finish_text.get_rect(
                center=(
                    560,
                    875
                )
            )
        )

        game_surface.blit(
            finish_text,
            finish_rect
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