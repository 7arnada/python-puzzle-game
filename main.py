import sys
import pygame

from settings import BASE_WIDTH

try:
    from settings import BASE_HEIGHT
except ImportError:
    BASE_HEIGHT = 950


from stages import STAGES

from block_data import (
    create_blocks,
    create_slots,
)

from rules import (
    judge_code,
    build_program,
)

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


# ==================================================
# 表示倍率
# ==================================================

DISPLAY_SCALE = 0.75


# ==================================================
# ブロックを初期位置へ戻す
# ==================================================

def return_block_home(block):

    start = block.get("start")

    if start is not None:
        block["rect"].topleft = start

    block["slot"] = None


# ==================================================
# ステージ読み込み
# ==================================================

def load_stage(stage_index):

    stage = STAGES[stage_index]


    # ==================================================
    # 通常ブロック作成
    # ==================================================

    new_blocks = create_blocks(
        stage.get(
            "blocks",
            []
        )
    )


    # ==================================================
    # 3行 × 3列
    # ==================================================

    new_slots = create_slots()


    new_slot_contents = [
        None
        for _ in new_slots
    ]


    # ==================================================
    # 固定スロット
    #
    # 1行目
    #
    # [ ??? ][ = ][ you ]
    #
    # = と you は動かせない
    # ==================================================

    new_slot_contents[1] = {
        "text": "=",
        "slot": 1,
        "fixed": True,
    }


    new_slot_contents[2] = {
        "text": "you",
        "slot": 2,
        "fixed": True,
    }


    # ==================================================
    # stages.pyから初期配置を取得
    #
    # 例:
    #
    # "initial_slots": {
    #     0: "ball"
    # }
    # ==================================================

    initial_slots = stage.get(
        "initial_slots",
        {}
    )


    # ==================================================
    # 初期配置
    # ==================================================

    for slot_index, block_text in initial_slots.items():

        # ----------------------------------------------
        # 不正なスロット番号なら無視
        # ----------------------------------------------

        if not (
            0 <= slot_index < len(new_slots)
        ):
            continue


        # ----------------------------------------------
        # 固定スロットには置かない
        # ----------------------------------------------

        if slot_index in (1, 2):
            continue


        # ----------------------------------------------
        # blocksから該当ブロックを探す
        #
        # まだ他のスロットに使われていないものだけ
        # ----------------------------------------------

        target_block = next(
            (
                block
                for block in new_blocks

                if (
                    block["text"] == block_text
                    and block.get("slot") is None
                )
            ),
            None
        )


        # ----------------------------------------------
        # 見つからなければ無視
        # ----------------------------------------------

        if target_block is None:
            continue


        # ----------------------------------------------
        # スロットへ配置
        # ----------------------------------------------

        new_slot_contents[
            slot_index
        ] = target_block


        target_block[
            "slot"
        ] = slot_index


        target_block[
            "rect"
        ].center = (
            new_slots[
                slot_index
            ].center
        )


    return (
        stage,
        new_blocks,
        new_slots,
        new_slot_contents,
    )


# ==================================================
# ウィンドウ座標
# ↓
# ゲーム内部座標
# ==================================================

def get_game_mouse_pos(
    pos,
    window_size,
):

    window_width, window_height = window_size


    if (
        window_width <= 0
        or window_height <= 0
    ):
        return pos


    x = (
        pos[0]
        * BASE_WIDTH
        / window_width
    )


    y = (
        pos[1]
        * BASE_HEIGHT
        / window_height
    )


    return (
        int(x),
        int(y),
    )


# ==================================================
# Pygameイベントの座標変換
# ==================================================

def make_game_event(
    event,
    window_size,
):

    if not hasattr(
        event,
        "pos"
    ):
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
# ブロックをスロットへ置く
# ==================================================

def put_block_in_slot(
    block,
    slot_index,
    slots,
    slot_contents,
):

    # ==================================================
    # 1行目の
    #
    # slot1 = "="
    # slot2 = "you"
    #
    # は固定
    # ==================================================

    if slot_index in (1, 2):

        return_block_home(block)
        return


    # ==================================================
    # 配置先にすでに何かあるか
    # ==================================================

    old_block = slot_contents[
        slot_index
    ]


    # ==================================================
    # 別ブロックが入っている場合
    # ==================================================

    if (
        old_block is not None
        and old_block is not block
    ):

        # 固定ブロックなら交換不可
        if old_block.get(
            "fixed",
            False
        ):
            return_block_home(block)
            return


        # 既存ブロックをホームへ戻す
        return_block_home(
            old_block
        )


    # ==================================================
    # 新しいブロックを配置
    # ==================================================

    slot_contents[
        slot_index
    ] = block


    block["slot"] = slot_index


    block["rect"].center = (
        slots[
            slot_index
        ].center
    )


# ==================================================
# RESULT Popup用status
# ==================================================

def get_result_status(result):

    if result is None:
        return None


    status = result.get(
        "status",
        "failed"
    )


    # PopupとしてはFAILED扱い
    # 表示文字だけSyntax Error
    if status == "syntax":
        return "failed"


    return status


# ==================================================
# RESULTメッセージ
# ==================================================

def get_result_message(result):

    if result is None:
        return ""


    status = result.get(
        "status",
        "failed"
    )


    # ==================================================
    # CLEAR
    # ==================================================

    if status == "clear":

        return RESULT_MESSAGES.get(
            "clear",
            "CLEAR!"
        )


    # ==================================================
    # Syntax
    # ==================================================

    if status == "syntax":

        return RESULT_MESSAGES.get(
            "syntax",
            "Syntax Error!"
        )


    # ==================================================
    # 特殊FAILEDメッセージ
    # ==================================================

    rules = result.get(
        "rules",
        []
    )


    for rule in reversed(rules):

        message_key = rule.get(
            "message_key"
        )


        if message_key:

            return RESULT_MESSAGES.get(
                message_key,
                RESULT_MESSAGES.get(
                    "failed",
                    "FAILED!"
                )
            )


    # ==================================================
    # 通常FAILED
    # ==================================================

    return RESULT_MESSAGES.get(
        "failed",
        "FAILED!"
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
        (
            12,
            15
        ),
    )


# ==================================================
# ゲーム画面
# ==================================================

def draw_game_screen(
    surface,
    current_stage_index,
    current_stage,
    blocks,
    slots,
    slot_contents,
    run_button_rect,
    current_result,
    font,
    small_font,
):

    surface.fill(
        "white"
    )


    # ==================================================
    # STAGE
    # ==================================================

    draw_stage_title(
        surface,
        current_stage_index,
        font,
    )


    # ==================================================
    # 盤面
    # ==================================================

    draw_board(
        surface
    )


    # ==================================================
    # ゲーム状態
    # ==================================================

    draw_game_state(
        surface,
        current_result,
        font,
        current_stage,
    )


    # ==================================================
    # コードUI
    # ==================================================

    draw_ui(
        surface,
        blocks,
        slots,
        slot_contents,
        run_button_rect,
        font,
        small_font,
    )


# ==================================================
# MAIN
# ==================================================

def main():

    pygame.init()


    # ==================================================
    # ウィンドウ
    # ==================================================

    window_width = int(
        BASE_WIDTH
        * DISPLAY_SCALE
    )


    window_height = int(
        BASE_HEIGHT
        * DISPLAY_SCALE
    )


    screen = pygame.display.set_mode(
        (
            window_width,
            window_height,
        ),
        pygame.RESIZABLE,
    )


    pygame.display.set_caption(
        "Python Puzzle Game"
    )


    # ==================================================
    # 内部描画Surface
    # ==================================================

    game_surface = pygame.Surface(
        (
            BASE_WIDTH,
            BASE_HEIGHT,
        )
    )


    clock = pygame.time.Clock()


    # ==================================================
    # フォント
    # ==================================================

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


    # ==================================================
    # RUNボタン
    # ==================================================

    run_button_rect = pygame.Rect(
        0,
        0,
        165,
        62,
    )


    run_button_rect.center = (
        BASE_WIDTH // 2,
        875,
    )


    # ==================================================
    # 初期画面
    # ==================================================

    screen_state = (
        SCREEN_TITLE
    )


    # ==================================================
    # ステージ
    # ==================================================

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


    # ==================================================
    # ドラッグ
    # ==================================================

    dragging_block = None


    drag_offset = (
        0,
        0
    )


    # ==================================================
    # Result
    # ==================================================

    result_popup = ResultPopup()


    # ==================================================
    # TITLE / STAGE SELECT用
    # ==================================================

    title_start_rect = None

    stage_buttons = []

    stage_back_rect = None


    # ==================================================
    # メインループ
    # ==================================================

    running = True


    while running:


        # ==================================================
        # イベント
        # ==================================================

        for event in pygame.event.get():


            # ==============================================
            # 終了
            # ==============================================

            if event.type == pygame.QUIT:

                running = False
                continue


            # ==============================================
            # 内部座標へ変換
            # ==============================================

            game_event = make_game_event(
                event,
                screen.get_size(),
            )


            # ==============================================
            # TITLE
            # ==============================================

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


            # ==============================================
            # STAGE SELECT
            # ==============================================

            if (
                screen_state
                == SCREEN_STAGE_SELECT
            ):

                if stage_back_rect is None:
                    continue


                action = (
                    handle_stage_select_event(
                        game_event,
                        stage_buttons,
                        stage_back_rect,
                    )
                )


                if action is None:
                    continue


                action_name, value = action


                # ------------------------------------------
                # TITLEへ戻る
                # ------------------------------------------

                if action_name == "title":

                    screen_state = (
                        SCREEN_TITLE
                    )


                # ------------------------------------------
                # STAGE開始
                # ------------------------------------------

                elif action_name == "stage":

                    current_stage_index = (
                        value
                    )


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


                    screen_state = (
                        SCREEN_GAME
                    )


                continue


            # ==============================================
            # RESULT
            # ==============================================

            if screen_state == SCREEN_RESULT:

                action = (
                    result_popup.handle_event(
                        game_event
                    )
                )


                # ------------------------------------------
                # RETRY
                # ------------------------------------------

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


                    screen_state = (
                        SCREEN_GAME
                    )


                # ------------------------------------------
                # TITLE
                # ------------------------------------------

                elif action == "title":

                    current_result = None
                    dragging_block = None

                    result_popup.close()


                    screen_state = (
                        SCREEN_TITLE
                    )


                # ------------------------------------------
                # NEXT
                # ------------------------------------------

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


                        screen_state = (
                            SCREEN_GAME
                        )


                continue


            # ==============================================
            # GAME以外ならここまで
            # ==============================================

            if screen_state != SCREEN_GAME:
                continue


            # ==============================================
            # マウス位置
            # ==============================================

            if hasattr(
                game_event,
                "pos"
            ):

                mouse_pos = (
                    game_event.pos
                )

            else:

                mouse_pos = None


            # ==============================================
            # 左クリック
            # ==============================================

            if (
                game_event.type
                == pygame.MOUSEBUTTONDOWN

                and game_event.button
                == 1
            ):


                # ==========================================
                # RUN
                # ==========================================

                if (
                    mouse_pos is not None

                    and run_button_rect.collidepoint(
                        mouse_pos
                    )
                ):

                    # --------------------------------------
                    # 3行をコード化
                    #
                    # 例:
                    #
                    # ball = you
                    # ball += clear
                    # ball_x += 2
                    # --------------------------------------

                    program = build_program(
                        slot_contents
                    )


                    # --------------------------------------
                    # 判定
                    # --------------------------------------

                    current_result = judge_code(
                        program,
                        current_stage
                    )


                    # --------------------------------------
                    # RUN開始時間
                    # --------------------------------------

                    current_result[
                        "started_at"
                    ] = (
                        pygame.time.get_ticks()
                    )


                    # --------------------------------------
                    # Result Popup
                    # --------------------------------------

                    status = get_result_status(
                        current_result
                    )


                    result_message = (
                        get_result_message(
                            current_result
                        )
                    )


                    result_popup.open(
                        status,
                        (
                            current_stage_index
                            < len(STAGES) - 1
                        ),
                        result_message,
                    )


                    screen_state = (
                        SCREEN_RESULT
                    )


                    continue


                # ==========================================
                # ブロックを掴む
                # ==========================================

                for block in reversed(
                    blocks
                ):

                    if (
                        mouse_pos is not None

                        and block[
                            "rect"
                        ].collidepoint(
                            mouse_pos
                        )
                    ):

                        dragging_block = block


                        # ----------------------------------
                        # 元スロットから外す
                        # ----------------------------------

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
                                ] is block
                            ):

                                slot_contents[
                                    old_slot
                                ] = None


                            block[
                                "slot"
                            ] = None


                        # ----------------------------------
                        # ドラッグ位置
                        # ----------------------------------

                        drag_offset = (

                            block[
                                "rect"
                            ].x
                            - mouse_pos[0],

                            block[
                                "rect"
                            ].y
                            - mouse_pos[1],
                        )


                        # ----------------------------------
                        # 一番前へ
                        # ----------------------------------

                        blocks.remove(
                            block
                        )

                        blocks.append(
                            block
                        )


                        break


            # ==============================================
            # ドラッグ中
            # ==============================================

            elif (
                game_event.type
                == pygame.MOUSEMOTION

                and dragging_block
                is not None

                and mouse_pos
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


            # ==============================================
            # ドロップ
            # ==============================================

            elif (
                game_event.type
                == pygame.MOUSEBUTTONUP

                and game_event.button
                == 1

                and dragging_block
                is not None
            ):

                target_slot = None


                # ------------------------------------------
                # ドロップ先を探す
                # ------------------------------------------

                if mouse_pos is not None:

                    for index, slot in enumerate(
                        slots
                    ):

                        if slot.collidepoint(
                            mouse_pos
                        ):

                            target_slot = index
                            break


                # ------------------------------------------
                # スロット外
                # ------------------------------------------

                if target_slot is None:

                    return_block_home(
                        dragging_block
                    )


                # ------------------------------------------
                # スロット内
                # ------------------------------------------

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

        # ==============================================
        # TITLE
        # ==============================================

        if screen_state == SCREEN_TITLE:

            title_start_rect = (
                draw_title_screen(
                    game_surface,
                    title_font,
                    button_font,
                    small_font,
                )
            )


        # ==============================================
        # STAGE SELECT
        # ==============================================

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


        # ==============================================
        # GAME / RESULT
        # ==============================================

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
                slot_contents,
                run_button_rect,
                current_result,
                font,
                small_font,
            )


            # ==========================================
            # RESULT Popup
            # ==========================================

            if screen_state == SCREEN_RESULT:

                result_popup.draw(
                    game_surface,
                    big_font,
                    button_font,
                    small_font,
                )


        # ==================================================
        # 実ウィンドウへ拡大縮小
        # ==================================================

        scaled_surface = (
            pygame.transform.smoothscale(
                game_surface,
                screen.get_size(),
            )
        )


        screen.blit(
            scaled_surface,
            (
                0,
                0
            ),
        )


        pygame.display.flip()


        clock.tick(
            60
        )


    # ==================================================
    # 終了
    # ==================================================

    pygame.quit()
    sys.exit()


# ==================================================
# 起動
# ==================================================

if __name__ == "__main__":
    main()