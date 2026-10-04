from collections import Counter


# =========================
# ゲームルール
# =========================

RULES = [

    # ---------------------------------
    # CLEAR 1
    #
    # goal = clear
    # for ball in range(9):
    # ---------------------------------

    {
        "name": "ball_grid",

        "program": [
            ["goal", "=", "clear"],
            ["for", "ball", "in range(9):"]
        ],

        "status": "clear",

        "effect": {
            "type": "ball_grid"
        }
    },


    # ---------------------------------
    # CLEAR 2
    #
    # ball = clear
    # ---------------------------------

    {
        "name": "clear_ball",

        "program": [
            ["ball", "=", "clear"]
        ],

        "status": "clear",

        "effect": {
            "type": "none"
        }
    },


    # ---------------------------------
    # CLEAR 3
    #
    # goal = clear
    # ball = goal
    # ---------------------------------

    {
        "name": "ball_becomes_goal",

        "program": [
            ["goal", "=", "clear"],
            ["ball", "=", "goal"]
        ],

        "status": "clear",

        "effect": {
            "type": "ball_to_goal"
        }
    },


    # ---------------------------------
    # CLEAR 4
    #
    # goal = clear
    # for goal in range(9):
    # ---------------------------------

    {
        "name": "goal_grid",

        "program": [
            ["goal", "=", "clear"],
            ["for", "goal", "in range(9):"]
        ],

        "status": "clear",

        "effect": {
            "type": "goal_grid"
        }
    },


    # ---------------------------------
    # CLEAR 5
    #
    # ball = clear
    # goal = ball
    # ---------------------------------

    {
        "name": "goal_becomes_ball",

        "program": [
            ["ball", "=", "clear"],
            ["goal", "=", "ball"]
        ],

        "status": "clear",

        "effect": {
            "type": "goal_to_ball"
        }
    },

    # ---------------------------------
    # CLEAR 6
    #
    # ball_x += 2
    # ---------------------------------

    {
        "name": "move_ball_right",

        "program": [
            ["ball_x", "+=", "2"]
        ],

        "status": "clear",

        "effect": {
            "type": "move_ball",
            "x": 2,
            "y": 0
        }
    },


    # ---------------------------------
    # FAILED
    #
    # goal = ball
    # ---------------------------------

    {
        "name": "fail_goal_ball",

        "program": [
            ["goal", "=", "ball"]
        ],

        "status": "failed",

        "effect": {
            "type": "goal_to_ball"
        }
    },

        # ---------------------------------
    # FAILED
    #
    # ball = goal
    # ---------------------------------

    {
        "name": "fail_ball_goal",

        "program": [
            ["ball", "=", "goal"]
        ],

        "status": "failed",

        "effect": {
            "type": "ball_to_goal"
        }
    },


    # ---------------------------------
    # FAILED
    #
    # for clear in range(9):
    # ---------------------------------

    {
        "name": "for_clear",

        "program": [
            ["for", "clear", "in range(9):"]
        ],

        "status": "clear?",

        "effect": {
            "type": "none",
        }
    },

    # ---------------------------------
    # failed
    #
    # for goal in range(9):
    # ---------------------------------

    {
        "name": "for_goal",

        "program": [
            ["for", "goal", "in range(9):"]
        ],

        "status": "failed",

        "effect": {
            "type": "goal_grid"
        }
    },

    # ---------------------------------
    # failed
    #
    # for ball in range(9):
    # ---------------------------------

    {
        "name": "for_ball",

        "program": [
            ["for", "ball", "in range(9):"]
        ],

        "effect": {
            "type": "ball_grid"
        }
    },

    # ---------------------------------
    # FAILED
    #
    # ball_y += 2
    # ---------------------------------
    
    {
        "name": "move_ball_wrong",

        "program": [
            ["ball_y", "+=", "2"]
        ],

        "status": "failed",

        "effect": {
            "type": "move_ball",
            "x": 0,
            "y": -2
        }
    },

    # ---------------------------------
    # FAILED
    #
    # clear = ball
    # ---------------------------------

        {
        "name": "clear_is_ball",

        "program": [
            ["clear", "=", "ball"]
        ],

        "status": "ball!",

        "effect": {
            "type": "none",
        }
    },

    # ---------------------------------
    # FAILED
    #
    # clear = goal
    # ---------------------------------

        {
        "name": "clear_is_goal",

        "program": [
            ["clear", "=", "goal"]
        ],

        "status": "goal!",

        "effect": {
            "type": "none",
        }
    },
]


# =========================
# Build Codeからプログラム取得
# =========================

def build_program(slot_contents):

    line1 = []

    line2 = []

    # 1行目
    for block in slot_contents[0:3]:

        if block is not None:

            line1.append(
                block["text"]
            )

    # 2行目
    for block in slot_contents[3:6]:

        if block is not None:

            line2.append(
                block["text"]
            )

    lines = []

    if line1:
        lines.append(line1)

    if line2:
        lines.append(line2)

    return lines


# =========================
# プログラム比較
#
# 1行目と2行目の上下は無視
# =========================

def program_matches(
    actual_program,
    expected_program
):

    actual = Counter(
        tuple(line)
        for line in actual_program
    )

    expected = Counter(
        tuple(line)
        for line in expected_program
    )

    return actual == expected


# =========================
# コード判定
# =========================

def judge_code(
    program,
    allowed_rule_names=None
):

    # =========================
    # ① まず2行ルールを判定
    # =========================

    if len(program) == 2:

        for rule in RULES:

            # -------------------------
            # このステージで
            # 使用可能なルールか確認
            # -------------------------

            if allowed_rule_names is not None:

                if rule["name"] not in allowed_rule_names:
                    continue

            # -------------------------
            # 2行ルールだけ確認
            # -------------------------

            if len(rule["program"]) != 2:
                continue

            # -------------------------
            # 順番を無視して比較
            # -------------------------

            rule_program = sorted(
                tuple(line) for line in rule["program"]
            )

            input_program = sorted(
                tuple(line) for line in program
            )

            if rule_program == input_program:

                return {
                    "syntax_error": False,
                    "rules": [rule]
                }


    # =========================
    # ② 2行ルールに一致しなかった場合
    #    1行ずつ読む
    # =========================

    matched_rules = []

    for line in program:

        matched_rule = None

        # 登録されているルールを確認
        for rule in RULES:

            # -------------------------
            # このステージで
            # 使用可能なルールか確認
            # -------------------------

            if allowed_rule_names is not None:

                if rule["name"] not in allowed_rule_names:
                    continue

            # -------------------------
            # 1行ルールだけ確認
            # -------------------------

            if len(rule["program"]) != 1:
                continue

            # -------------------------
            # 1行がルールと一致するか
            # -------------------------

            if rule["program"] == [line]:

                matched_rule = rule
                break

        # -------------------------
        # 一致した場合だけ追加
        # 一致しない行は無視
        # -------------------------

        if matched_rule is not None:

            matched_rules.append(
                matched_rule
            )


    # =========================
    # ③ 1つも一致しなかった
    #
    # → Syntax Error
    # =========================

    if len(matched_rules) == 0:

        return {
            "syntax_error": True,
            "rules": []
        }


    # =========================
    # ④ 1つ以上一致した
    # =========================

    return {
        "syntax_error": False,
        "rules": matched_rules
    }