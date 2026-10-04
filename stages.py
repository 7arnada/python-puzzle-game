STAGES = [
    {
        "name": "STAGE 1",

        # 初期位置
        "player_pos": (2, 0),
        "goal_pos": (2, 2),


        "blocks": [
            "ball_x",
            "ball_y",
            "+=",
            "2"
        ],

        "clear_rules": [
            "move_ball_right"
        ],

        "failed_rules": [
        "move_ball_wrong"
        ]
    },

    {
        "name": "STAGE 2",

        # 初期位置
        "player_pos": (2, 0),
        "goal_pos": (0, 1),

        # このステージで使えるブロック
        "blocks": [
            "ball",
            "=",
            "clear"
        ],

        # rules.py にあるルール名
        "clear_rules": [
            "clear_ball"
        ],

        "failed_rules": [
            "clear_is_ball"
        ]
    },

    {
        "name": "STAGE 3",

        # 初期位置
        "player_pos": (2, 0),
        "goal_pos": (0, 2),

        "blocks": [
            "goal",
            "=",
            "clear",
            "for",
            "ball",
            "in range(9):"
        ],

        "clear_rules": [
            "ball_grid",
            "clear_ball"
        ],

        "failed_rules": [
            "clear_is_ball",
            "clear_is_goal",
            "for_goal",
            "for_ball",
        ]
    }
]