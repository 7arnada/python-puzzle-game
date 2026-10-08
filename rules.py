from collections import Counter


# ==================================================
# RULES
#
# 1文 = 1ルール
# ==================================================

RULES = [

    # ==================================================
    # YOU設定
    # ==================================================

    {
        "name": "ball_is_you",

        "program": [
            "ball",
            "=",
            "you"
        ],

        "effect": {
            "type": "set_you",
            "target": "ball"
        }
    },


    {
        "name": "goal_is_you",

        "program": [
            "goal",
            "=",
            "you"
        ],

        "effect": {
            "type": "set_you",
            "target": "goal"
        }
    },


    # ==================================================
    # CLEAR設定
    # ==================================================

    {
        "name": "ball_is_clear",

        "program": [
            "ball",
            "+=",
            "clear"
        ],

        "effect": {
            "type": "mark_clear",
            "target": "ball"
        }
    },


    {
        "name": "goal_is_clear",

        "program": [
            "goal",
            "+=",
            "clear"
        ],

        "effect": {
            "type": "mark_clear",
            "target": "goal"
        }
    },


    # ==================================================
    # clear = ball
    # ==================================================

    {
        "name": "clear_is_ball",

        "program": [
            "clear",
            "+=",
            "ball"
        ],

        "message_key": "ball!",

        "effect": {
            "type": "none"
        }
    },


    # ==================================================
    # clear = goal
    # ==================================================

    {
        "name": "clear_is_goal",

        "program": [
            "clear",
            "+=",
            "goal"
        ],

        "message_key": "goal!",

        "effect": {
            "type": "none"
        }
    },

    # ==================================================
    # clear = you
    # ==================================================

    {
        "name": "clear_is_you",

        "program": [
            "clear",
            "=",
            "you"
        ],

        "message_key": "YOU!",

        "effect": {
            "type": "none"
        }
    },

    # ==================================================
    # ball = goal
    # ==================================================

    {
        "name": "ball_is_goal",

        "program": [
            "ball",
            "=",
            "goal"
        ],

        "effect": {
            "type": "ball_to_goal"
        }
    },


    # ==================================================
    # goal = ball
    # ==================================================

    {
        "name": "goal_is_ball",

        "program": [
            "goal",
            "=",
            "ball"
        ],

        "effect": {
            "type": "goal_to_ball"
        }
    },


    # ==================================================
    # for ball in range(9):
    # ==================================================

    {
        "name": "for_ball",

        "program": [
            "for",
            "ball",
            "in range(9):"
        ],

        "effect": {
            "type": "ball_grid"
        }
    },


    # ==================================================
    # for goal in range(9):
    # ==================================================

    {
        "name": "for_goal",

        "program": [
            "for",
            "goal",
            "in range(9):"
        ],

        "effect": {
            "type": "goal_grid"
        }
    },


    # ==================================================
    # for clear in range(9):
    # ==================================================

    {
        "name": "for_clear",

        "program": [
            "for",
            "clear",
            "in range(9):"
        ],

        "message_key": "clear?",

        "effect": {
            "type": "none"
        }
    },


    # ==================================================
    # ball_x += 2
    # ==================================================

    {
        "name": "move_ball_right",

        "program": [
            "ball_x",
            "+=",
            "2"
        ],

        "effect": {
            "type": "move_ball",
            "x": 2,
            "y": 0
        }
    },


    # ==================================================
    # ball_y += 2
    # ==================================================

    {
        "name": "move_ball_wrong",

        "program": [
            "ball_y",
            "+=",
            "2"
        ],

        "effect": {
            "type": "move_ball",
            "x": 0,
            "y": 2
        }
    },
]


# ==================================================
# Build Code
# ↓
# program
# ==================================================

def build_program(
    slot_contents
):

    program = []


    # 3スロットずつ読む
    for start in range(
        0,
        len(slot_contents),
        3
    ):

        row = slot_contents[
            start:start + 3
        ]


        # 完全な空行なら無視
        if not any(row):
            continue


        line = []


        for block in row:

            if block is None:
                continue

            line.append(
                block["text"]
            )


        if line:

            program.append(
                line
            )


    return program


# ==================================================
# 1文のルールを探す
# ==================================================

def find_rule(
    line,
    allowed_rule_names
):

    for rule in RULES:

        if (
            rule["name"]
            not in allowed_rule_names
        ):

            continue


        if (
            rule["program"]
            == line
        ):

            return rule


    return None


# ==================================================
# 9マス座標
# ==================================================

def create_full_grid():

    return [

        (
            index // 3,
            index % 3
        )

        for index in range(9)
    ]


# ==================================================
# ルールを実際に実行して
# 盤面状態を作る
#
# elapsed_ms=None
# ↓
# 論理判定用
# 即座に全部実行
#
# elapsed_msあり
# ↓
# renderer用
# for文にdelayを付けられる
# ==================================================

def simulate_state(
    stage,
    rules,
    elapsed_ms=None,
    grid_delay=500
):

    player_pos = (
        stage["player_pos"]
    )

    goal_pos = (
        stage["goal_pos"]
    )


    # ==================================================
    # 初期状態
    # ==================================================

    ball_positions = [
        player_pos
    ]

    goal_positions = [
        goal_pos
    ]


    # YOU
    you_target = stage.get(
        "default_you",
        "ball"
    )


    # CLEAR状態
    clear_targets = set(
        stage.get(
            "initial_clear",
            []
        )
    )


    word_grids = []


    # ==================================================
    # 上から実行
    # ==================================================

    for rule in rules:

        effect = rule.get(
            "effect",
            {}
        )

        effect_type = effect.get(
            "type",
            "none"
        )


        # ==================================================
        # ○○ = you
        # ==================================================

        if effect_type == "set_you":

            you_target = effect.get(
                "target"
            )


        # ==================================================
        # ○○ = clear
        # ==================================================

        elif effect_type == "mark_clear":

            target = effect.get(
                "target"
            )

            if target:

                clear_targets.add(
                    target
                )


        # ==================================================
        # ball移動
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


            ball_positions = [

                (
                    row + move_y,
                    col + move_x
                )

                for row, col
                in ball_positions

            ]


        # ==================================================
        # for ball
        # ==================================================

        elif effect_type == "ball_grid":

            # 判定時は即座
            # 描画時だけdelay
            if (
                elapsed_ms is None
                or elapsed_ms >= grid_delay
            ):

                ball_positions = (
                    create_full_grid()
                )


        # ==================================================
        # for goal
        # ==================================================

        elif effect_type == "goal_grid":

            if (
                elapsed_ms is None
                or elapsed_ms >= grid_delay
            ):

                goal_positions = (
                    create_full_grid()
                )


        # ==================================================
        # ball = goal
        # ==================================================

        elif effect_type == "ball_to_goal":

            for position in ball_positions:

                if (
                    position
                    not in goal_positions
                ):

                    goal_positions.append(
                        position
                    )


            ball_positions = []


        # ==================================================
        # goal = ball
        # ==================================================

        elif effect_type == "goal_to_ball":

            for position in goal_positions:

                if (
                    position
                    not in ball_positions
                ):

                    ball_positions.append(
                        position
                    )


            goal_positions = []


        # ==================================================
        # 文字
        # ==================================================

        elif effect_type == "word_grid":

            word = effect.get(
                "word",
                ""
            )

            if word:

                word_grids.append(
                    word
                )


        elif effect_type == "none":

            pass


    return {

        "ball_positions":
            ball_positions,

        "goal_positions":
            goal_positions,

        "you_target":
            you_target,

        "clear_targets":
            clear_targets,

        "word_grids":
            word_grids,
    }


# ==================================================
# YOUがCLEARしたか
#
# 条件1:
# YOU自身がclear
#
# 条件2:
# YOUとclear対象が重なる
# ==================================================

def is_you_clear(
    state
):

    you_target = state[
        "you_target"
    ]

    clear_targets = state[
        "clear_targets"
    ]


    # ==================================================
    # 自分自身がclear
    # ==================================================

    if (
        you_target
        in clear_targets
    ):

        return True


    # ==================================================
    # YOUの座標
    # ==================================================

    if you_target == "ball":

        you_positions = set(
            state[
                "ball_positions"
            ]
        )

    elif you_target == "goal":

        you_positions = set(
            state[
                "goal_positions"
            ]
        )

    else:

        return False


    # ==================================================
    # clear対象との接触判定
    # ==================================================

    for target in clear_targets:


        if target == "ball":

            clear_positions = set(
                state[
                    "ball_positions"
                ]
            )


        elif target == "goal":

            clear_positions = set(
                state[
                    "goal_positions"
                ]
            )


        else:

            continue


        # 1マスでも重なっている
        if (
            you_positions
            & clear_positions
        ):

            return True


    return False


# ==================================================
# 旧clear_patternsも
# 一応使用可能
# ==================================================

def matches_clear_pattern(
    matched_names,
    clear_patterns
):

    matched_counter = Counter(
        matched_names
    )


    for pattern in clear_patterns:

        if (
            matched_counter
            == Counter(pattern)
        ):

            return True


    return False


# ==================================================
# 判定
# ==================================================

def judge_code(
    program,
    stage
):

    allowed_rule_names = stage.get(
        "allowed_rules",
        []
    )


    matched_rules = []


    # ==================================================
    # 1行ずつ読む
    # ==================================================

    for line in program:

        rule = find_rule(
            line,
            allowed_rule_names
        )


        # 一致しない行は無視
        if rule is None:

            continue


        matched_rules.append(
            rule
        )


    # ==================================================
    # YOU設定以外のルール
    # ==================================================

    action_rules = [

        rule

        for rule in matched_rules

        if rule.get(
            "effect",
            {}
        ).get(
            "type"
        ) != "set_you"

    ]


    # ==================================================
    # 2・3行目にコードがあるのに
    # 1文も意味がない
    #
    # → Syntax Error
    # ==================================================

    action_input_exists = (
        len(program) >= 2
    )


    if (
        action_input_exists
        and not action_rules
    ):

        return {

            "syntax_error": True,

            "status": "syntax",

            "rules": matched_rules,
        }


    # ==================================================
    # 最終状態
    # ==================================================

    state = simulate_state(
        stage,
        matched_rules
    )


    # ==================================================
    # YOU / CLEARルール
    # ==================================================

    dynamic_clear = (
        is_you_clear(
            state
        )
    )


    # ==================================================
    # 旧clear_patterns
    # ==================================================

    action_names = [

        rule["name"]

        for rule in action_rules

    ]


    pattern_clear = (
        matches_clear_pattern(

            action_names,

            stage.get(
                "clear_patterns",
                []
            )
        )
    )


    # ==================================================
    # 最終CLEAR
    # ==================================================

    is_clear = (
        dynamic_clear
        or pattern_clear
    )


    return {

        "syntax_error": False,

        "status": (
            "clear"
            if is_clear
            else "failed"
        ),

        "rules": matched_rules,

        "state": state,
    }