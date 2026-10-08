import math

import pygame


from settings import (
    BASE_WIDTH,
    CELL_SIZE,
    BOARD_X,
    BOARD_Y,
)

from messages import RESULT_MESSAGES

from rules import simulate_state


# ==================================================
# 盤面
# ==================================================

def draw_board(
    surface
):

    for row in range(3):

        for col in range(3):

            x = (
                BOARD_X
                + col
                * CELL_SIZE
            )

            y = (
                BOARD_Y
                + row
                * CELL_SIZE
            )


            pygame.draw.rect(

                surface,

                "black",

                (
                    x,
                    y,
                    CELL_SIZE,
                    CELL_SIZE
                ),

                2
            )


# ==================================================
# ball
# ==================================================

def draw_ball(
    surface,
    row,
    col
):

    x = (
        BOARD_X
        + col * CELL_SIZE
        + CELL_SIZE // 2
    )

    y = (
        BOARD_Y
        + row * CELL_SIZE
        + CELL_SIZE // 2
    )


    pygame.draw.circle(

        surface,

        "gold",

        (
            x,
            y
        ),

        30
    )


# ==================================================
# goal
# ==================================================

def draw_goal(
    surface,
    row,
    col
):

    x = (
        BOARD_X
        + col
        * CELL_SIZE
    )

    y = (
        BOARD_Y
        + row
        * CELL_SIZE
    )


    # 棒
    pygame.draw.line(

        surface,

        "black",

        (
            x + 45,
            y + 30
        ),

        (
            x + 45,
            y + 90
        ),

        4
    )


    # 旗
    pygame.draw.polygon(

        surface,

        "red",

        [

            (
                x + 45,
                y + 30
            ),

            (
                x + 85,
                y + 45
            ),

            (
                x + 45,
                y + 60
            ),
        ]
    )


# ==================================================
# CLEARキラキラ
# ==================================================

def draw_clear_sparkle(
    surface,
    row,
    col
):

    center_x = (

        BOARD_X

        + col
        * CELL_SIZE

        + CELL_SIZE // 2
    )


    center_y = (

        BOARD_Y

        + row
        * CELL_SIZE

        + CELL_SIZE // 2
    )


    time = (
        pygame.time.get_ticks()
        / 180
    )


    sparkles = [

        (-38, -35, 0),

        (38, -28, 1),

        (-38, 30, 2),

        (38, 36, 3),

        (0, -48, 4),

        (0, 48, 5),
    ]


    for (
        dx,
        dy,
        phase
    ) in sparkles:


        pulse = (

            math.sin(
                time + phase
            )

            + 1

        ) / 2


        size = int(

            3

            + pulse
            * 7
        )


        x = (
            center_x
            + dx
        )

        y = (
            center_y
            + dy
        )


        pygame.draw.line(

            surface,

            "gold",

            (
                x - size,
                y
            ),

            (
                x + size,
                y
            ),

            3
        )


        pygame.draw.line(

            surface,

            "gold",

            (
                x,
                y - size
            ),

            (
                x,
                y + size
            ),

            3
        )


# ==================================================
# 文字を9マス
# ==================================================

def draw_word_grid(
    surface,
    word,
    font
):

    for index in range(9):

        row = (
            index // 3
        )

        col = (
            index % 3
        )


        x = (

            BOARD_X

            + col
            * CELL_SIZE

            + CELL_SIZE // 2
        )


        y = (

            BOARD_Y

            + row
            * CELL_SIZE

            + CELL_SIZE // 2
        )


        text = font.render(

            word,

            True,

            "black"
        )


        rect = text.get_rect(

            center=(
                x,
                y
            )
        )


        surface.blit(

            text,

            rect
        )


# ==================================================
# 状態を描画
# ==================================================

def draw_state(
    surface,
    state,
    font
):

    ball_positions = state[
        "ball_positions"
    ]

    goal_positions = state[
        "goal_positions"
    ]

    clear_targets = state[
        "clear_targets"
    ]

    word_grids = state[
        "word_grids"
    ]


    # ==================================================
    # ballを先に描く
    # ==================================================

    for row, col in ball_positions:

        draw_ball(

            surface,

            row,

            col
        )


    # ==================================================
    # goalを後から描く
    #
    # → goalが前面
    # ==================================================

    for row, col in goal_positions:

        draw_goal(

            surface,

            row,

            col
        )


    # ==================================================
    # 文字
    # ==================================================

    for word in word_grids:

        draw_word_grid(

            surface,

            word,

            font
        )


    # ==================================================
    # CLEARエフェクト
    # ==================================================

    if (
        "ball"
        in clear_targets
    ):

        for row, col in ball_positions:

            draw_clear_sparkle(

                surface,

                row,

                col
            )


    if (
        "goal"
        in clear_targets
    ):

        for row, col in goal_positions:

            draw_clear_sparkle(

                surface,

                row,

                col
            )


# ==================================================
# RUN前 / RUN後
# ==================================================

def draw_game_state(
    surface,
    result,
    font,
    stage
):

    # ==================================================
    # RUN前
    # ==================================================

    if result is None:

        state = simulate_state(

            stage,

            []
        )


        draw_state(

            surface,

            state,

            font
        )


        return


    # ==================================================
    # RUNからの時間
    # ==================================================

    started_at = result.get(
        "started_at"
    )


    elapsed_ms = None


    if started_at is not None:

        elapsed_ms = (

            pygame.time.get_ticks()

            - started_at
        )


    # ==================================================
    # アニメーション込み状態
    # ==================================================

    state = simulate_state(

        stage,

        result.get(
            "rules",
            []
        ),

        elapsed_ms=elapsed_ms,

        grid_delay=500
    )


    draw_state(

        surface,

        state,

        font
    )


# ==================================================
# リザルトメッセージ
# ==================================================

def draw_result_message(
    surface,
    result,
    font
):

    if result is None:
        return


    status = result.get(
        "status",
        "failed"
    )


    message = RESULT_MESSAGES.get(
        status,
        ""
    )


    if not message:
        return


    if status == "clear":

        text_color = "green"

    elif status in (
        "failed",
        "syntax"
    ):

        text_color = "red"

    else:

        text_color = "black"


    text = font.render(

        message,

        True,

        text_color
    )


    rect = text.get_rect(

        center=(

            BASE_WIDTH // 2,

            420
        )
    )


    surface.blit(

        text,

        rect
    )


# ==================================================
# UI
# ==================================================

def draw_ui(
    surface,
    blocks,
    slots,
    slot_contents,
    button_rect,
    font,
    small_font
):

    # ==================================================
    # Code Blocks
    # ==================================================

    label = small_font.render(

        "Code Blocks",

        True,

        "black"
    )


    surface.blit(

        label,

        (
            20,
            455
        )
    )


    # ==================================================
    # Build Code
    # ==================================================

    label = small_font.render(

        "Build Code",

        True,

        "gray"
    )


    surface.blit(

        label,

        (
            40,
            595
        )
    )


    # ==================================================
    # スロット
    # ==================================================

    for index, slot in enumerate(
        slots
    ):


        pygame.draw.rect(

            surface,

            "gray",

            slot,

            3,

            border_radius=8
        )


        # ==================================================
        # 固定スロット
        # "="
        # "you"
        # ==================================================

        content = slot_contents[
            index
        ]


        if (
            content is not None

            and content.get(
                "fixed",
                False
            )
        ):

            inner = slot.inflate(
                -8,
                -8
            )


            pygame.draw.rect(

                surface,

                "lightgray",

                inner,

                border_radius=6
            )


            text = font.render(

                content[
                    "text"
                ],

                True,

                "black"
            )


            text_rect = text.get_rect(

                center=(
                    slot.center
                )
            )


            surface.blit(

                text,

                text_rect
            )


    # ==================================================
    # 可動ブロック
    # ==================================================

    for block in blocks:

        pygame.draw.rect(

            surface,

            "lightgreen",

            block[
                "rect"
            ],

            border_radius=8
        )


        text = font.render(

            block[
                "text"
            ],

            True,

            "black"
        )


        rect = text.get_rect(

            center=(
                block[
                    "rect"
                ].center
            )
        )


        surface.blit(

            text,

            rect
        )


    # ==================================================
    # RUN
    # ==================================================

    pygame.draw.rect(

        surface,

        "lightblue",

        button_rect,

        border_radius=8
    )


    text = font.render(

        "RUN",

        True,

        "black"
    )


    rect = text.get_rect(

        center=(
            button_rect.center
        )
    )


    surface.blit(

        text,

        rect
    )