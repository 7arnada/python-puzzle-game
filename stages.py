STAGES = [

    # ==================================================
    # STAGE 1
    #
    # goalは最初からclear
    #
    # ball = you
    # ball_x += 2
    #
    # ↓
    #
    # clear goalに重なる
    # ==================================================

    {
        "name": "STAGE 1",

        "player_pos": (
            2,
            0
        ),

        "goal_pos": (
            2,
            2
        ),


        # goalは最初からclear
        "initial_clear": [
            "goal"
        ],

        "blocks": [

            "ball",

            "ball_x",

            "ball_y",

            "+=",

            "2",
        ],

        "initial_slots": {
            0: "ball",
        },

        "allowed_rules": [

            "ball_is_you",

            "move_ball_right",

            "move_ball_wrong",
        ],
    },


    # ==================================================
    # STAGE 2
    #
    # ball = you
    # ball = clear
    #
    # ↓
    #
    # YOU自身がclear
    # ==================================================

    {
        "name": "STAGE 2",

        "player_pos": (
            2,
            0
        ),

        "goal_pos": (
            0,
            1
        ),

        "default_you":
            "ball",

        "you_options": [
            "ball",
            "goal"
        ],

        "initial_clear": [],

        "blocks": [

            "ball",

            "ball",

            "+=",

            "clear",
        ],

        "initial_slots": {
            0: "ball",
        },        

        "allowed_rules": [

            "ball_is_you",

            "ball_is_clear",

            "clear_is_ball",

            "clear_is_you",
        ],
    },


    # ==================================================
    # STAGE 3
    #
    # 例1
    #
    # ball = you
    # goal = clear
    # for ball in range(9):
    #
    # ↓
    #
    # ballがclear goalに重なる
    #
    #
    # 例2
    #
    # goal = you
    # ball = clear
    # for goal in range(9):
    #
    # ↓
    #
    # goalがclear ballに重なる
    # ==================================================

    {
        "name": "STAGE 3",

        "player_pos": (
            2,
            0
        ),

        "goal_pos": (
            0,
            2
        ),

        "initial_slots": {
            0: "ball",
        },

        "initial_clear": [],

        "blocks": [

            "goal",

            "goal",

            "+=",

            "clear",

            "for",

            "ball",

            "ball",

            "in range(9):",
        ],

        "allowed_rules": [

            "ball_is_you",

            "goal_is_you",

            "ball_is_clear",

            "goal_is_clear",

            "clear_is_ball",

            "clear_is_goal",

            "clear_is_you",

            "for_ball",

            "for_goal",

            "for_clear",
        ],
    },
]