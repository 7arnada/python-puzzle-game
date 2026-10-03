STAGES = [
    {
        "name": "STAGE 1",

        # このステージで使えるブロック
        "blocks": [
            "ball",
            "=",
            "clear"
        ],

        # rules.py にあるルール名
        "clear_rules": [
            "clear_ball"
        ]
    },

    {
        "name": "STAGE 2",

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
        ]
    }
]