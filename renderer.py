import pygame

from settings import (
    BASE_WIDTH,
    CELL_SIZE,
    BOARD_X,
    BOARD_Y,
)

from messages import RESULT_MESSAGES


# ==================================================
# 盤面
# ==================================================

def draw_board(surface):

    for row in range(3):
        for col in range(3):

            x = BOARD_X + col * CELL_SIZE
            y = BOARD_Y + row * CELL_SIZE

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
        (x, y),
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
        + col * CELL_SIZE
    )

    y = (
        BOARD_Y
        + row * CELL_SIZE
    )

    # 旗の棒
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


# ==================================================
# 文字を9マスに表示
# ==================================================

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


# ==================================================
# RUN前
# ==================================================

def draw_default_state(
    surface,
    player_pos,
    goal_pos
):

    draw_ball(
        surface,
        player_pos[0],
        player_pos[1]
    )

    draw_goal(
        surface,
        goal_pos[0],
        goal_pos[1]
    )


# ==================================================
# 9マス分の座標を作成
# ==================================================

def create_grid_positions():

    return [
        (
            index // 3,
            index % 3
        )
        for index in range(9)
    ]


# ==================================================
# RUN後の盤面
#
# result["rules"] を
# 上から1つずつ実行する
# ==================================================

def draw_game_state(
    surface,
    result,
    font,
    stage
):

    player_pos = stage["player_pos"]
    goal_pos = stage["goal_pos"]


    # ==================================================
    # RUN前
    # ==================================================

    if result is None:

        draw_default_state(
            surface,
            player_pos,
            goal_pos
        )

        return


    # ==================================================
    # Syntax Error
    #
    # 一致した命令が1個もない場合
    # ==================================================

    if result.get(
        "syntax_error",
        False
    ):

        draw_default_state(
            surface,
            player_pos,
            goal_pos
        )

        return


    # ==================================================
    # 現在の盤面状態
    #
    # 最初は
    # ball 1個
    # goal 1個
    # ==================================================

    ball_positions = [
        player_pos
    ]

    goal_positions = [
        goal_pos
    ]

    # 文字表示
    word_grids = []


    # ==================================================
    # コードを1文ずつ実行
    # ==================================================

    for rule in result["rules"]:

        effect = rule.get(
            "effect",
            {}
        )

        effect_type = effect.get(
            "type",
            "none"
        )


        # ==================================================
        # ball = clear
        #
        # ballを全部消す
        # ==================================================

        if effect_type == "ball_removed":

            ball_positions = []


        # ==================================================
        # goal = clear
        #
        # goalを全部消す
        # ==================================================

        elif effect_type == "goal_removed":

            goal_positions = []


        # ==================================================
        # ball = goal
        #
        # ballがgoalになる
        # 元のgoalは残る
        # ==================================================

        elif effect_type == "ball_to_goal":

            for position in ball_positions:

                if position not in goal_positions:

                    goal_positions.append(
                        position
                    )

            ball_positions = []


        # ==================================================
        # goal = ball
        #
        # goalがballになる
        # 元のballは残る
        # ==================================================

        elif effect_type == "goal_to_ball":

            for position in goal_positions:

                if position not in ball_positions:

                    ball_positions.append(
                        position
                    )

            goal_positions = []


        # ==================================================
        # for ball in range(9):
        #
        # ballを9マス配置
        # ==================================================

        elif effect_type == "ball_grid":

            ball_positions = (
                create_grid_positions()
            )


        # ==================================================
        # for goal in range(9):
        #
        # goalを9マス配置
        # ==================================================

        elif effect_type == "goal_grid":

            goal_positions = (
                create_grid_positions()
            )


        # ==================================================
        # 過去ルール互換
        #
        # goal = clear
        # for ball in range(9)
        # ==================================================

        elif effect_type == "ball_grid_goal_hidden":

            goal_positions = []

            ball_positions = (
                create_grid_positions()
            )


        # ==================================================
        # 過去ルール互換
        #
        # ball = clear
        # goal = ball
        # ==================================================

        elif effect_type == "goal_to_ball_only":

            ball_positions = list(
                goal_positions
            )

            goal_positions = []


        # ==================================================
        # ball_x += ○
        # ball_y += ○
        #
        # ballを移動
        # ==================================================

        elif effect_type == "move_ball":

            move_x = effect.get(
                "x",
                0
            )

            move_y = effect.get(
                "y",
                0
            )

            moved_positions = []

            for row, col in ball_positions:

                new_row = (
                    row
                    + move_y
                )

                new_col = (
                    col
                    + move_x
                )

                moved_positions.append(
                    (
                        new_row,
                        new_col
                    )
                )

            ball_positions = (
                moved_positions
            )


        # ==================================================
        # 文字を9マスに表示
        #
        # 例：
        # for clear in range(9)
        #
        # clear = ball の場合なども
        # rules.py側でwordを変えられる
        # ==================================================

        elif effect_type == "word_grid":

            word_grids.append(
                effect.get(
                    "word",
                    ""
                )
            )


        # ==================================================
        # 何もしない
        # ==================================================

        elif effect_type == "none":

            pass


        # ==================================================
        # 未登録effect
        # ==================================================

        else:

            pass


    # ==================================================
    # 最終状態を描画
    #
    # コードを全部実行してから
    # 最後にまとめて描画
    # ==================================================


    # goal
    for row, col in goal_positions:

        draw_goal(
            surface,
            row,
            col
        )


    # ball
    for row, col in ball_positions:

        draw_ball(
            surface,
            row,
            col
        )


    # 文字
    for word in word_grids:

        draw_word_grid(
            surface,
            word,
            font
        )


# ==================================================
# 実行結果メッセージ
# ==================================================

def draw_result_message(
    surface,
    result,
    font
):

    if result is None:
        return


    # ==================================================
    # Syntax Error
    # ==================================================

    if result.get(
        "syntax_error",
        False
    ):

        status = "syntax"

        message = RESULT_MESSAGES.get(
            "syntax",
            "Syntax Error!"
        )


    # ==================================================
    # 1つ以上ルールが実行された
    # ==================================================

    else:

        rules = result.get(
            "rules",
            []
        )

        if not rules:
            return


        # ----------------------------------------------
        # 最後に実行されたルールを
        # メッセージの基準にする
        # ----------------------------------------------

        last_rule = rules[-1]

        status = last_rule.get(
            "status",
            "failed"
        )

        # 個別messageを優先
        message = last_rule.get(
            "message",
            RESULT_MESSAGES.get(
                status,
                ""
            )
        )


    if not message:
        return


    # ==================================================
    # 色
    # ==================================================

    if status == "clear":

        text_color = "green"

    elif status in [
        "failed",
        "syntax"
    ]:

        text_color = "red"

    else:

        text_color = "black"


    # ==================================================
    # 改行
    # ==================================================

    lines = message.split(
        "\n"
    )

    start_y = 420
    line_height = 38

    for index, line in enumerate(
        lines
    ):

        text = font.render(
            line,
            True,
            text_color
        )

        rect = text.get_rect(
            center=(
                BASE_WIDTH // 2,
                start_y
                + index * line_height
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
        (20, 470)
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
        (40, 655)
    )


    # ==================================================
    # スロット
    # ==================================================

    for slot in slots:

        pygame.draw.rect(
            surface,
            "gray",
            slot,
            3,
            border_radius=8
        )


    # ==================================================
    # コードブロック
    # ==================================================

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

    text_rect = text.get_rect(
        center=button_rect.center
    )

    surface.blit(
        text,
        text_rect
    )