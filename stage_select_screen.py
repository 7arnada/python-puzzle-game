import pygame


def draw_stage_select(
    surface,
    stage_count,
    title_font,
    button_font,
    small_font
):

    width = surface.get_width()
    height = surface.get_height()

    surface.fill(
        (22, 24, 32)
    )

    # =========================
    # タイトル
    # =========================

    title = title_font.render(
        "SELECT STAGE",
        True,
        (245, 245, 250)
    )

    surface.blit(
        title,
        title.get_rect(
            center=(
                width // 2,
                80
            )
        )
    )

    # =========================
    # ステージボタン
    # =========================

    buttons = []

    button_width = 180
    button_height = 100

    columns = 3

    gap_x = 30
    gap_y = 30

    total_width = (
        button_width * columns
        + gap_x * (columns - 1)
    )

    start_x = (
        width - total_width
    ) // 2

    start_y = 170

    mouse_pos = pygame.mouse.get_pos()

    for index in range(stage_count):

        row = index // columns
        col = index % columns

        x = (
            start_x
            + col * (
                button_width
                + gap_x
            )
        )

        y = (
            start_y
            + row * (
                button_height
                + gap_y
            )
        )

        rect = pygame.Rect(
            x,
            y,
            button_width,
            button_height
        )

        if rect.collidepoint(mouse_pos):
            color = (75, 90, 190)
        else:
            color = (45, 50, 70)

        pygame.draw.rect(
            surface,
            color,
            rect,
            border_radius=12
        )

        pygame.draw.rect(
            surface,
            (100, 110, 150),
            rect,
            width=2,
            border_radius=12
        )

        number_text = button_font.render(
            f"STAGE {index + 1}",
            True,
            "white"
        )

        surface.blit(
            number_text,
            number_text.get_rect(
                center=rect.center
            )
        )

        buttons.append(
            (
                rect,
                index
            )
        )

    # =========================
    # タイトルへ戻る
    # =========================

    back_rect = pygame.Rect(
        30,
        height - 70,
        150,
        45
    )

    pygame.draw.rect(
        surface,
        (45, 50, 70),
        back_rect,
        border_radius=8
    )

    back_text = small_font.render(
        "TITLE",
        True,
        "white"
    )

    surface.blit(
        back_text,
        back_text.get_rect(
            center=back_rect.center
        )
    )

    return (
        buttons,
        back_rect
    )


def handle_stage_select_event(
    event,
    buttons,
    back_rect
):

    if event.type != pygame.MOUSEBUTTONDOWN:
        return None

    if event.button != 1:
        return None

    # ステージ選択
    for rect, index in buttons:

        if rect.collidepoint(
            event.pos
        ):

            return (
                "stage",
                index
            )

    # TITLEへ戻る
    if back_rect.collidepoint(
        event.pos
    ):

        return (
            "title",
            None
        )

    return None