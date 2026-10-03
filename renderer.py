import pygame

from settings import (
    BASE_WIDTH,
    CELL_SIZE,
    BOARD_X,
    BOARD_Y,
    PLAYER_POS,
    GOAL_POS
)

from messages import RESULT_MESSAGES


# =========================
# 盤面
# =========================

def draw_board(surface):

    for row in range(3):

        for col in range(3):

            x = (
                BOARD_X
                + col * CELL_SIZE
            )

            y = (
                BOARD_Y
                + row * CELL_SIZE
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


# =========================
# ball
# =========================

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
        (x, y),
        30
    )


# =========================
# goal
# =========================

def draw_goal(
    surface,
    row,
    col
):

    x = (
        BOARD_X
        + col * CELL_SIZE
    )

    y = (
        BOARD_Y
        + row * CELL_SIZE
    )

    # 棒
    pygame.draw.line(
        surface,
        "black",
        (x + 45, y + 30),
        (x + 45, y + 90),
        4
    )

    # 旗
    pygame.draw.polygon(
        surface,
        "red",
        [
            (x + 45, y + 30),
            (x + 85, y + 45),
            (x + 45, y + 60)
        ]
    )


# =========================
# 文字を9マス表示
# =========================

def draw_word_grid(
    surface,
    word,
    font
):

    for index in range(9):

        row = index // 3
        col = index % 3

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

        text = font.render(
            word,
            True,
            "black"
        )

        text_rect = text.get_rect(
            center=(x, y)
        )

        surface.blit(
            text,
            text_rect
        )


# =========================
# 通常状態
# =========================

def draw_default_state(surface):

    draw_ball(
        surface,
        PLAYER_POS[0],
        PLAYER_POS[1]
    )

    draw_goal(
        surface,
        GOAL_POS[0],
        GOAL_POS[1]
    )


# =========================
# 実行結果を描画
# =========================

def draw_game_state(
    surface,
    rule,
    font
):

    # まだRUNしていない
    if rule is None:

        draw_default_state(
            surface
        )

        return

    effect = rule["effect"]

    effect_type = effect["type"]


    # ---------------------------------
    # ball = clear
    # ---------------------------------

    if effect_type == "ball_removed":

        draw_goal(
            surface,
            GOAL_POS[0],
            GOAL_POS[1]
        )

        draw_ball(
            surface,
            PLAYER_POS[0],
            PLAYER_POS[1]
        )

    # ---------------------------------
    # goal = clear
    # ball = goal
    # ---------------------------------

    elif effect_type == "ball_to_goal":

        draw_goal(
            surface,
            GOAL_POS[0],
            GOAL_POS[1]
        )

        draw_goal(
            surface,
            PLAYER_POS[0],
            PLAYER_POS[1]
        )

    # ---------------------------------
    # for goal in range(9)
    # ---------------------------------

    elif effect_type == "goal_grid":

        # 元ball
        draw_ball(
            surface,
            PLAYER_POS[0],
            PLAYER_POS[1]
        )

        for goal in range(9):

            row = goal // 3
            col = goal % 3

            draw_goal(
                surface,
                row,
                col
            )


    # ---------------------------------
    # for ball in range(9)
    # ---------------------------------

    elif effect_type == "ball_grid":

        # 元goal
        draw_goal(
            surface,
            GOAL_POS[0],
            GOAL_POS[1]
        )

        for ball in range(9):

            row = ball // 3
            col = ball % 3

            draw_ball(
                surface,
                row,
                col
            )


    # ---------------------------------
    # goal = ball
    # ---------------------------------

    elif effect_type == "goal_to_ball":

        draw_ball(
            surface,
            PLAYER_POS[0],
            PLAYER_POS[1]
        )

        draw_ball(
            surface,
            GOAL_POS[0],
            GOAL_POS[1]
        )

    # ---------------------------------
    # 文字を9個
    # ---------------------------------

    elif effect_type == "word_grid":

        draw_default_state(
            surface
        )

        draw_word_grid(
            surface,
            effect["word"],
            font
        )

    # ---------------------------------
    # Syntax Error
    # ---------------------------------

    else:

        draw_default_state(
            surface
        )


# =========================
# CLEAR / FAILED表示
# =========================

def draw_result_message(
    surface,
    rule,
    font
):

    if rule is None:
        return

    status = rule["status"]

    # ルール個別のmessageがあれば優先
    message = rule.get(
        "message",
        RESULT_MESSAGES.get(
            status,
            ""
        )
    )

    if not message:
        return

    if status == "clear":

        text_color = "green"

    elif status in [
        "failed",
        "syntax"
    ]:

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
            440
        )
    )

    surface.blit(
        text,
        rect
    )


# =========================
# UI
# =========================

def draw_ui(
    surface,
    blocks,
    slots,
    button_rect,
    font,
    small_font
):

    # Code Blocks
    label = small_font.render(
        "Code Blocks",
        True,
        "black"
    )

    surface.blit(
        label,
        (20, 470)
    )

    # Build Code
    label = small_font.render(
        "Build Code",
        True,
        "gray"
    )

    surface.blit(
        label,
        (40, 655)
    )

    # スロット
    for slot in slots:

        pygame.draw.rect(
            surface,
            "gray",
            slot,
            3,
            border_radius=8
        )

    # ブロック
    for block in blocks:

        pygame.draw.rect(
            surface,
            "lightgreen",
            block["rect"],
            border_radius=8
        )

        text = font.render(
            block["text"],
            True,
            "black"
        )

        text_rect = text.get_rect(
            center=block["rect"].center
        )

        surface.blit(
            text,
            text_rect
        )

    # RUN
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

    text_rect = text.get_rect(
        center=button_rect.center
    )

    surface.blit(
        text,
        text_rect
    )