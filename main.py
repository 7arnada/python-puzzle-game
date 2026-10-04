import sys

import pygame

from settings import BASE_WIDTH
try:
    from settings import BASE_HEIGHT
except ImportError:
    BASE_HEIGHT = 950

from stages import STAGES
from block_data import create_blocks, create_slots
from rules import judge_code
from messages import RESULT_MESSAGES

from renderer import (
    draw_board,
    draw_game_state,
    draw_ui,
)

from title_screen import (
    draw_title_screen,
    handle_title_event,
)

from stage_select_screen import (
    draw_stage_select,
    handle_stage_select_event,
)

from result_popup import ResultPopup


# ==================================================
# 画面状態
# ==================================================

SCREEN_TITLE = "title"
SCREEN_STAGE_SELECT = "stage_select"
SCREEN_GAME = "game"
SCREEN_RESULT = "result"

SLOTS_PER_LINE = 3

# 実際に表示するウィンドウ倍率
# 0.75 = ゲーム内部サイズの75%
DISPLAY_SCALE = 0.75


# ==================================================
# ステージ読み込み
# ==================================================

def load_stage(stage_index):
    """
    stages.py のステージ情報から
    そのステージ用のブロック・スロットを作り直す。
    """

    stage = STAGES[stage_index]

    new_blocks = create_blocks(
        stage["blocks"]
    )

    new_slots = create_slots()

    # 各スロットに入っている block を保持
    new_slot_contents = [
        None
        for _ in new_slots
    ]

    return (
        stage,
        new_blocks,
        new_slots,
        new_slot_contents,
    )


# ==================================================
# ウィンドウ座標 → ゲーム座標
# ==================================================

def get_game_mouse_pos(pos, window_size):
    """
    game_surface は BASE_WIDTH x BASE_HEIGHT 固定。
    ウィンドウを拡大縮小しても、
    マウス位置をゲーム内座標へ変換する。
    """

    window_width, window_height = window_size

    if window_width <= 0 or window_height <= 0:
        return pos

    x = pos[0] * BASE_WIDTH / window_width
    y = pos[1] * BASE_HEIGHT / window_height

    return (
        int(x),
        int(y),
    )


def make_game_event(event, window_size):
    """
    TITLE / STAGE SELECT / RESULT のクリック判定でも
    BASEサイズの座標を使えるようにする。
    """

    if not hasattr(event, "pos"):
        return event

    data = event.dict.copy()
    data["pos"] = get_game_mouse_pos(
        event.pos,
        window_size,
    )

    return pygame.event.Event(
        event.type,
        data,
    )


# ==================================================
# ブロックを初期位置へ戻す
# ==================================================

def return_block_home(block):
    start = block.get("start")

    if start is not None:
        block["rect"].topleft = start

    block["slot"] = None


# ==================================================
# ブロックをスロットへ置く
# ==================================================

def put_block_in_slot(
    block,
    slot_index,
    slots,
    slot_contents,
):
    """
    target slot に既に別ブロックがある場合は
    そのブロックを初期位置へ戻す。
    """

    old_block = slot_contents[slot_index]

    if (
        old_block is not None
        and old_block is not block
    ):
        return_block_home(old_block)

    slot_contents[slot_index] = block

    block["slot"] = slot_index
    block["rect"].center = (
        slots[slot_index].center
    )


# ==================================================
# Build Code → judge_code用 program
# ==================================================

def build_program(
    slot_contents,
):
    """
    3スロット = 1行として program を作る。

    例:
        goal | = | clear
        for  | goal | in range(9):

    ↓

    [
        ["goal", "=", "clear"],
        ["for", "goal", "in range(9):"]
    ]
    """

    program = []

    for start in range(
        0,
        len(slot_contents),
        SLOTS_PER_LINE,
    ):

        row = slot_contents[
            start:start + SLOTS_PER_LINE
        ]

        # 1個も置かれていない行は無視
        if not any(row):
            continue

        line = []

        for block in row:
            if block is not None:
                line.append(
                    block["text"]
                )

        program.append(line)

    return program


# ==================================================
# judge_codeの結果から
# リザルト判定
# ==================================================

def get_result_status(result):
    """
    clear / failed を返す。

    result_rule を使う新しい形式にも、
    rules だけを返す現在の形式にも対応。
    """

    if result is None:
        return None

    if result.get(
        "syntax_error",
        False,
    ):
        return "failed"

    result_rule = result.get(
        "result_rule"
    )

    if result_rule is not None:
        return result_rule.get(
            "status",
            "failed",
        )

    rules = result.get(
        "rules",
        [],
    )

    for rule in rules:
        if rule.get("status") == "clear":
            return "clear"

    return "failed"



# ==================================================
# judge_codeの結果から
# ルール固有メッセージを取得
# ==================================================

def get_result_message(result):
    """
    以前 draw_result_message() で表示していた
    rule["message"] をリザルト画面へ渡す。

    例:
        "BALL!"
        "GOAL!"
        "Syntax Error"
    """

    if result is None:
        return ""

    # Syntax Error
    if result.get(
        "syntax_error",
        False,
    ):
        return RESULT_MESSAGES.get(
            "syntax",
            "Syntax Error"
        )

    # 2行ルールなど result_rule がある形式
    result_rule = result.get(
        "result_rule"
    )

    if result_rule is not None:

        status = result_rule.get(
            "status",
            "failed"
        )

        return result_rule.get(
            "message",
            RESULT_MESSAGES.get(
                status,
                ""
            )
        )

    # 現在の rules 形式
    rules = result.get(
        "rules",
        []
    )

    if not rules:
        return ""

    # CLEARルールが含まれていたら
    # そのメッセージを最優先
    selected_rule = None

    for rule in rules:

        if rule.get("status") == "clear":
            selected_rule = rule
            break

    # CLEARがなければ最後に成立したルール
    if selected_rule is None:
        selected_rule = rules[-1]

    status = selected_rule.get(
        "status",
        "failed"
    )

    return selected_rule.get(
        "message",
        RESULT_MESSAGES.get(
            status,
            ""
        )
    )


# ==================================================
# ステージタイトル
# ==================================================

def draw_stage_title(
    surface,
    stage_index,
    font,
):
    text = font.render(
        f"STAGE {stage_index + 1}",
        True,
        "black",
    )

    surface.blit(
        text,
        (12, 15),
    )


# ==================================================
# ゲーム画面描画
# ==================================================

def draw_game_screen(
    surface,
    current_stage_index,
    current_stage,
    blocks,
    slots,
    run_button_rect,
    current_result,
    font,
    small_font,
):
    surface.fill("white")

    draw_stage_title(
        surface,
        current_stage_index,
        font,
    )

    draw_board(
        surface
    )

    # RUN前は None
    # RUN後は judge_code の result
    draw_game_state(
        surface,
        current_result,
        font,
        current_stage,
    )

    draw_ui(
        surface,
        blocks,
        slots,
        run_button_rect,
        font,
        small_font,
    )


# ==================================================
# main
# ==================================================

def main():

    pygame.init()

    # ------------------------------
    # ウィンドウ
    # ------------------------------

    window_width = int(
        BASE_WIDTH * DISPLAY_SCALE
    )

    window_height = int(
        BASE_HEIGHT * DISPLAY_SCALE
    )

    screen = pygame.display.set_mode(
        (
            window_width,
            window_height,
        )
    )

    pygame.display.set_caption(
        "Python Puzzle Game"
    )

    game_surface = pygame.Surface(
        (
            BASE_WIDTH,
            BASE_HEIGHT,
        )
    )

    clock = pygame.time.Clock()

    # ------------------------------
    # フォント
    # ------------------------------

    font = pygame.font.SysFont(
        "arial",
        30,
        bold=True,
    )

    small_font = pygame.font.SysFont(
        "arial",
        22,
        bold=True,
    )

    button_font = pygame.font.SysFont(
        "arial",
        32,
        bold=True,
    )

    big_font = pygame.font.SysFont(
        "arial",
        58,
        bold=True,
    )

    title_font = pygame.font.SysFont(
        "arial",
        68,
        bold=True,
    )

    # ------------------------------
    # RUNボタン
    # ------------------------------

    run_button_rect = pygame.Rect(
        0,
        0,
        165,
        62,
    )

    run_button_rect.center = (
        BASE_WIDTH // 2,
        885,
    )

    # ------------------------------
    # 画面状態
    # ------------------------------

    screen_state = SCREEN_TITLE

    # ------------------------------
    # 現在ステージ
    # ------------------------------

    current_stage_index = 0

    (
        current_stage,
        blocks,
        slots,
        slot_contents,
    ) = load_stage(
        current_stage_index
    )

    current_result = None

    # ------------------------------
    # ドラッグ状態
    # ------------------------------

    dragging_block = None

    drag_offset = (
        0,
        0,
    )

    # ------------------------------
    # リザルト
    # ------------------------------

    result_popup = ResultPopup()

    # ------------------------------
    # 各画面のクリック領域
    # ------------------------------

    title_start_rect = None

    stage_buttons = []
    stage_back_rect = None

    running = True

    # ==================================================
    # メインループ
    # ==================================================

    while running:

        window_size = screen.get_size()

        # ==================================================
        # イベント
        # ==================================================

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False
                continue

            game_event = make_game_event(
                event,
                screen.get_size(),
            )

            # ==================================================
            # TITLE
            # ==================================================

            if screen_state == SCREEN_TITLE:

                if title_start_rect is None:
                    continue

                action = handle_title_event(
                    game_event,
                    title_start_rect,
                )

                if action == "start":
                    screen_state = (
                        SCREEN_STAGE_SELECT
                    )

                continue

            # ==================================================
            # STAGE SELECT
            # ==================================================

            if (
                screen_state
                == SCREEN_STAGE_SELECT
            ):

                if stage_back_rect is None:
                    continue

                action = handle_stage_select_event(
                    game_event,
                    stage_buttons,
                    stage_back_rect,
                )

                if action is None:
                    continue

                action_name, value = action

                if action_name == "title":

                    screen_state = SCREEN_TITLE

                elif action_name == "stage":

                    current_stage_index = value

                    (
                        current_stage,
                        blocks,
                        slots,
                        slot_contents,
                    ) = load_stage(
                        current_stage_index
                    )

                    current_result = None

                    dragging_block = None

                    result_popup.close()

                    screen_state = SCREEN_GAME

                continue

            # ==================================================
            # RESULT
            # ==================================================

            if screen_state == SCREEN_RESULT:

                action = result_popup.handle_event(
                    game_event
                )

                # --------------------------
                # やり直し
                # --------------------------

                if action == "retry":

                    (
                        current_stage,
                        blocks,
                        slots,
                        slot_contents,
                    ) = load_stage(
                        current_stage_index
                    )

                    current_result = None

                    dragging_block = None

                    result_popup.close()

                    screen_state = SCREEN_GAME

                # --------------------------
                # タイトル
                # --------------------------

                elif action == "title":

                    current_result = None

                    dragging_block = None

                    result_popup.close()

                    screen_state = SCREEN_TITLE

                # --------------------------
                # 次のステージ
                # --------------------------

                elif action == "next":

                    if (
                        current_stage_index
                        < len(STAGES) - 1
                    ):

                        current_stage_index += 1

                        (
                            current_stage,
                            blocks,
                            slots,
                            slot_contents,
                        ) = load_stage(
                            current_stage_index
                        )

                        current_result = None

                        dragging_block = None

                        result_popup.close()

                        screen_state = SCREEN_GAME

                continue

            # ==================================================
            # GAME
            # ==================================================

            if screen_state != SCREEN_GAME:
                continue

            # ゲーム座標
            if hasattr(
                game_event,
                "pos",
            ):
                mouse_pos = game_event.pos
            else:
                mouse_pos = None

            # ------------------------------------------
            # 左クリック開始
            # ------------------------------------------

            if (
                game_event.type
                == pygame.MOUSEBUTTONDOWN
                and game_event.button == 1
            ):

                # ==============================
                # RUN
                # ==============================

                if (
                    run_button_rect.collidepoint(
                        mouse_pos
                    )
                ):

                    program = build_program(
                        slot_contents
                    )

                    allowed_rules = (
                        current_stage.get(
                            "clear_rules",
                            [],
                        )
                        + current_stage.get(
                            "failed_rules",
                            [],
                        )
                    )

                    current_result = judge_code(
                        program,
                        allowed_rules,
                    )

                    status = get_result_status(
                        current_result
                    )

                    result_message = get_result_message(
                        current_result
                    )

                    result_popup.open(
                        status,
                        (
                            current_stage_index
                            < len(STAGES) - 1
                        ),
                        result_message,
                    )

                    # RESULTへ切り替えるが、
                    # 背景にはGAME画面をそのまま描く
                    screen_state = SCREEN_RESULT

                    continue

                # ==============================
                # ブロックを掴む
                # ==============================

                for block in reversed(
                    blocks
                ):

                    if block[
                        "rect"
                    ].collidepoint(
                        mouse_pos
                    ):

                        dragging_block = block

                        # スロットから取り出す
                        old_slot = block.get(
                            "slot"
                        )

                        if old_slot is not None:

                            if (
                                0
                                <= old_slot
                                < len(
                                    slot_contents
                                )
                                and slot_contents[
                                    old_slot
                                ]
                                is block
                            ):
                                slot_contents[
                                    old_slot
                                ] = None

                            block["slot"] = None

                        drag_offset = (
                            block["rect"].x
                            - mouse_pos[0],
                            block["rect"].y
                            - mouse_pos[1],
                        )

                        # 描画順を一番上へ
                        blocks.remove(block)
                        blocks.append(block)

                        break

            # ------------------------------------------
            # ドラッグ中
            # ------------------------------------------

            elif (
                game_event.type
                == pygame.MOUSEMOTION
                and dragging_block
                is not None
            ):

                dragging_block[
                    "rect"
                ].topleft = (
                    mouse_pos[0]
                    + drag_offset[0],
                    mouse_pos[1]
                    + drag_offset[1],
                )

            # ------------------------------------------
            # ドロップ
            # ------------------------------------------

            elif (
                game_event.type
                == pygame.MOUSEBUTTONUP
                and game_event.button == 1
                and dragging_block
                is not None
            ):

                target_slot = None

                # マウス位置が入っている
                # スロットを探す
                for index, slot in enumerate(
                    slots
                ):

                    if slot.collidepoint(
                        mouse_pos
                    ):
                        target_slot = index
                        break

                if target_slot is None:

                    return_block_home(
                        dragging_block
                    )

                else:

                    put_block_in_slot(
                        dragging_block,
                        target_slot,
                        slots,
                        slot_contents,
                    )

                dragging_block = None

        # ==================================================
        # 描画
        # ==================================================

        if screen_state == SCREEN_TITLE:

            title_start_rect = (
                draw_title_screen(
                    game_surface,
                    title_font,
                    button_font,
                    small_font,
                )
            )

        elif (
            screen_state
            == SCREEN_STAGE_SELECT
        ):

            (
                stage_buttons,
                stage_back_rect,
            ) = draw_stage_select(
                game_surface,
                len(STAGES),
                title_font,
                button_font,
                small_font,
            )

        elif screen_state in (
            SCREEN_GAME,
            SCREEN_RESULT,
        ):

            draw_game_screen(
                game_surface,
                current_stage_index,
                current_stage,
                blocks,
                slots,
                run_button_rect,
                current_result,
                font,
                small_font,
            )

            # RESULT時のみ
            # GAME画面の上へポップアップ
            if (
                screen_state
                == SCREEN_RESULT
            ):

                result_popup.draw(
                    game_surface,
                    big_font,
                    button_font,
                    small_font,
                )

        # ==================================================
        # 固定サイズ画面を
        # 現在ウィンドウサイズへ拡大縮小
        # ==================================================

        scaled_surface = (
            pygame.transform.smoothscale(
                game_surface,
                screen.get_size(),
            )
        )

        screen.blit(
            scaled_surface,
            (0, 0),
        )

        pygame.display.flip()

        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
