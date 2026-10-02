import pygame
import sys

# Pygameを初期化
pygame.init()

# 画面サイズ
WIDTH = 600
HEIGHT = 800

# ゲーム画面を作成
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Python Puzzle Game")

# マスの大きさ
CELL_SIZE = 120

# 3×3の盤面の開始位置
BOARD_X = 120
BOARD_Y = 50

# キャラクターの位置（行, 列）,ゴールの位置（行, 列）
player_pos = (2, 0)
goal_pos = (0, 1)

# フォント
font = pygame.font.Font(None, 36)

# 実行ボタン
button_rect = pygame.Rect(220, 500, 160, 60)

# 実行されたかどうか
executed = False

# コードブロック
code_block = pygame.Rect(50, 450, 220, 60)

# コードブロックの初期位置
code_block_start = (50, 450)

# 実行エリア
execution_area = pygame.Rect(300, 430, 250, 120)

# ドラッグ中かどうか
dragging = False

# コードが実行エリアに置かれたか
code_placed = False

# ゲームを動かし続ける
running = True

while running:

    # ×ボタンが押されたか確認
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if event.type == pygame.MOUSEBUTTONDOWN:
        if button_rect.collidepoint(event.pos):
            executed = True

    # 背景を白にする
    screen.fill("white")

    # 3×3のマスを描画
    for row in range(3):
        for col in range(3):

            x = BOARD_X + col * CELL_SIZE
            y = BOARD_Y + row * CELL_SIZE

            pygame.draw.rect(
                screen,
                "black",
                (x, y, CELL_SIZE, CELL_SIZE),
                2
            )

    # キャラクターを描画
    player_row, player_col = player_pos

    player_x = BOARD_X + player_col * CELL_SIZE + CELL_SIZE // 2
    player_y = BOARD_Y + player_row * CELL_SIZE + CELL_SIZE // 2

    pygame.draw.circle(
        screen,
        "gold",
        (player_x, player_y),
        30
    )

    # ゴールを描画
    goal_row, goal_col = goal_pos

    goal_x = BOARD_X + goal_col * CELL_SIZE
    goal_y = BOARD_Y + goal_row * CELL_SIZE

    # 旗の棒
    pygame.draw.line(
        screen,
        "black",
        (goal_x + 45, goal_y + 30),
        (goal_x + 45, goal_y + 90),
        4
    )

    # 旗
    pygame.draw.polygon(
        screen,
        "red",
        [
            (goal_x + 45, goal_y + 30),
            (goal_x + 85, goal_y + 45),
            (goal_x + 45, goal_y + 60)
        ]
    )
    # RUNが押されたら、for文で9マスにキャラクターを増やす
    if executed:

        for i in range(9):

            row = i // 3
            col = i % 3

            x = BOARD_X + col * CELL_SIZE + CELL_SIZE // 2
            y = BOARD_Y + row * CELL_SIZE + CELL_SIZE // 2

            pygame.draw.circle(
                screen,
                "gold",
                (x, y),
                30
            )
        # ゴールに到達したのでCLEAR
        clear_text = font.render("CLEAR!", True, "green")

        screen.blit(
            clear_text,
            (250, 460)
        )

    # 実行ボタンを描画
    pygame.draw.rect(
        screen,
        "lightblue",
        button_rect
    )

    button_text = font.render("RUN", True, "black")

    screen.blit(
        button_text,
        (button_rect.x + 50, button_rect.y + 15)
    )
    # コードブロック
    pygame.draw.rect(
        screen,
        "lightgreen",
        code_block,
        border_radius=8
    )

    code_text = font.render(
        "for i in range(9):",
        True,
        "black"
    )

    screen.blit(
        code_text,
        (code_block.x + 10, code_block.y + 15)
    )


    # 実行エリア
    pygame.draw.rect(
        screen,
        "gray",
        execution_area,
        3,
        border_radius=8
    )

    # 画面を更新
    pygame.display.flip()


pygame.quit()
sys.exit()