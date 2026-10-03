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
            "type": "ball_removed"
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

        "status": "failed",

        "effect": {
            "type": "ball_grid"
        }
    },


    # ---------------------------------
    # FAILED
    #
    # clear = ball
    # for clear in range(9):
    # ---------------------------------

    {
        "name": "clear_equals_ball",

        "program": [
            ["clear", "=", "ball"],
            ["for", "clear", "in range(9):"]
        ],

        "status": "failed",

        "effect": {
            "type": "word_grid",
            "word": "ball"
        }
    },


    # ---------------------------------
    # FAILED
    #
    # clear = goal
    # for clear in range(9):
    # ---------------------------------

    {
        "name": "clear_equals_goal",

        "program": [
            ["clear", "=", "goal"],
            ["for", "clear", "in range(9):"]
        ],

        "status": "failed",

        "effect": {
            "type": "word_grid",
            "word": "goal"
        }
    }
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

    for rule in RULES:

        # ステージで使用できないルールは無視
        if allowed_rule_names is not None:

            if rule["name"] not in allowed_rule_names:

                continue

        if program_matches(
            program,
            rule["program"]
        ):

            return rule

    return {
        "name": "syntax_error",

        "status": "syntax",

        "effect": {
            "type": "none"
        }
    }