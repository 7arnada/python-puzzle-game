import pygame


def draw_title_screen(
    surface,
    title_font,
    button_font,
    small_font
):

    width = surface.get_width()
    height = surface.get_height()

    # 背景
    surface.fill((22, 24, 32))

    # =========================
    # タイトル
    # =========================

    title = title_font.render(
        "CODE PUZZLE",
        True,
        (245, 245, 250)
    )

    title_rect = title.get_rect(
        center=(width // 2, height // 2 - 120)
    )

    surface.blit(
        title,
        title_rect
    )

    # =========================
    # サブタイトル
    # =========================

    subtitle = small_font.render(
        "Build the code. Reach the goal.",
        True,
        (160, 165, 180)
    )

    subtitle_rect = subtitle.get_rect(
        center=(width // 2, height // 2 - 65)
    )

    surface.blit(
        subtitle,
        subtitle_rect
    )

    # =========================
    # STARTボタン
    # =========================

    start_rect = pygame.Rect(
        0,
        0,
        210,
        55
    )

    start_rect.center = (
        width // 2,
        height // 2 + 50
    )

    mouse_pos = pygame.mouse.get_pos()

    if start_rect.collidepoint(mouse_pos):
        button_color = (85, 105, 255)
    else:
        button_color = (65, 80, 210)

    pygame.draw.rect(
        surface,
        button_color,
        start_rect,
        border_radius=14
    )

    start_text = button_font.render(
        "START",
        True,
        "white"
    )

    surface.blit(
        start_text,
        start_text.get_rect(
            center=start_rect.center
        )
    )

    return start_rect


def handle_title_event(
    event,
    start_rect
):

    if event.type == pygame.MOUSEBUTTONDOWN:

        if event.button == 1:

            if start_rect.collidepoint(
                event.pos
            ):

                return "start"

    return None