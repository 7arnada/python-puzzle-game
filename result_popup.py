import pygame


RESULT_DELAY = 1500
RESULT_ANIMATION = 280


class ResultPopup:

    def __init__(self):
        self.active = False
        self.status = None
        self.started_at = 0
        self.has_next_stage = False
        self.message = ""

        self.retry_rect = None
        self.title_rect = None
        self.next_rect = None

        # 手描きの矢印ではなく文字記号を使う。
        # Windowsでは Segoe UI Symbol が優先される。
        icon_font_path = pygame.font.match_font(
            "segoeuisymbol,seguisym,arial,dejavusans"
        )

        if icon_font_path:
            self.retry_icon_font = pygame.font.Font(
                icon_font_path,
                42
            )
        else:
            self.retry_icon_font = pygame.font.Font(
                None,
                42
            )

    def open(
        self,
        status,
        has_next_stage,
        message=""
    ):
        self.active = True
        self.status = status
        self.started_at = pygame.time.get_ticks()
        self.has_next_stage = has_next_stage
        self.message = message

        self.retry_rect = None
        self.title_rect = None
        self.next_rect = None

    def close(self):
        self.active = False
        self.status = None
        self.message = ""

        self.retry_rect = None
        self.title_rect = None
        self.next_rect = None

    def get_progress(self):
        if not self.active:
            return None

        now = pygame.time.get_ticks()

        elapsed = (
            now
            - self.started_at
        )

        if elapsed < RESULT_DELAY:
            return None

        animation_elapsed = (
            elapsed
            - RESULT_DELAY
        )

        return min(
            animation_elapsed
            / RESULT_ANIMATION,
            1.0
        )

    def ease_out_back(
        self,
        x
    ):
        c1 = 1.70158
        c3 = c1 + 1

        return (
            1
            + c3 * (x - 1) ** 3
            + c1 * (x - 1) ** 2
        )

    def draw(
        self,
        surface,
        big_font,
        button_font,
        small_font
    ):
        progress = self.get_progress()

        if progress is None:
            return

        screen_width = surface.get_width()
        screen_height = surface.get_height()

        overlay = pygame.Surface(
            (
                screen_width,
                screen_height
            ),
            pygame.SRCALPHA
        )

        overlay.fill(
            (0, 0, 0, 130)
        )

        surface.blit(
            overlay,
            (0, 0)
        )

        eased = self.ease_out_back(
            progress
        )

        scale = (
            0.78
            + 0.22 * eased
        )

        base_width = 520
        base_height = 370

        popup_width = int(
            base_width * scale
        )

        popup_height = int(
            base_height * scale
        )

        popup_rect = pygame.Rect(
            0,
            0,
            popup_width,
            popup_height
        )

        popup_rect.center = (
            screen_width // 2,
            screen_height // 2
        )

        pygame.draw.rect(
            surface,
            (32, 35, 46),
            popup_rect,
            border_radius=22
        )

        if self.status == "clear":
            accent_color = (
                80,
                220,
                140
            )
        else:
            accent_color = (
                245,
                90,
                100
            )

        # rules.py の message があれば、
        # CLEAR! / FAILED! の代わりにそのまま表示する
        #
        # 例:
        # "message": "BALL!"  -> BALL!
        # "message": "GOAL!"  -> GOAL!
        if self.message:
            result_text = self.message
        elif self.status == "clear":
            result_text = "CLEAR!"
        else:
            result_text = "FAILED!"

        pygame.draw.rect(
            surface,
            accent_color,
            popup_rect,
            width=4,
            border_radius=22
        )

        if progress < 0.75:
            return

        result_surface = big_font.render(
            result_text,
            True,
            accent_color
        )

        result_rect = result_surface.get_rect(
            center=(
                popup_rect.centerx,
                popup_rect.top + 70
            )
        )

        surface.blit(
            result_surface,
            result_rect
        )

        self.retry_rect = pygame.Rect(
            popup_rect.left + 60,
            popup_rect.top + 135,
            popup_rect.width - 120,
            55
        )

        self.draw_button(
            surface,
            self.retry_rect,
            "RETRY",
            button_font
        )

        self.draw_retry_icon(
            surface,
            (
                self.retry_rect.left + 42,
                self.retry_rect.centery
            )
        )

        self.title_rect = pygame.Rect(
            popup_rect.left + 60,
            popup_rect.top + 205,
            popup_rect.width - 120,
            55
        )

        self.draw_button(
            surface,
            self.title_rect,
            "TITLE",
            button_font
        )

        self.next_rect = None

        if (
            self.status == "clear"
            and self.has_next_stage
        ):
            self.next_rect = pygame.Rect(
                popup_rect.left + 60,
                popup_rect.top + 275,
                popup_rect.width - 120,
                55
            )

            self.draw_button(
                surface,
                self.next_rect,
                "NEXT STAGE  >",
                button_font,
                accent=True
            )

    def draw_button(
        self,
        surface,
        rect,
        text,
        font,
        accent=False
    ):
        mouse_pos = pygame.mouse.get_pos()

        hover = rect.collidepoint(
            mouse_pos
        )

        if accent:
            if hover:
                color = (
                    70,
                    190,
                    125
                )
            else:
                color = (
                    55,
                    155,
                    105
                )
        else:
            if hover:
                color = (
                    70,
                    75,
                    95
                )
            else:
                color = (
                    50,
                    54,
                    70
                )

        pygame.draw.rect(
            surface,
            color,
            rect,
            border_radius=10
        )

        text_surface = font.render(
            text,
            True,
            "white"
        )

        surface.blit(
            text_surface,
            text_surface.get_rect(
                center=rect.center
            )
        )

    def draw_retry_icon(
        self,
        surface,
        center
    ):
        """
        やり直しアイコン。
        手描きのarcではなく ↻ を使うので、
        縮小表示しても形が崩れにくい。
        """

        icon = self.retry_icon_font.render(
            "↻",
            True,
            "white"
        )

        icon_rect = icon.get_rect(
            center=center
        )

        surface.blit(
            icon,
            icon_rect
        )


    def handle_event(
        self,
        event
    ):
        if not self.active:
            return None

        progress = self.get_progress()

        if (
            progress is None
            or progress < 1.0
        ):
            return None

        if (
            event.type
            != pygame.MOUSEBUTTONDOWN
        ):
            return None

        if event.button != 1:
            return None

        if (
            self.retry_rect
            and self.retry_rect.collidepoint(
                event.pos
            )
        ):
            return "retry"

        if (
            self.title_rect
            and self.title_rect.collidepoint(
                event.pos
            )
        ):
            return "title"

        if (
            self.next_rect
            and self.next_rect.collidepoint(
                event.pos
            )
        ):
            return "next"

        return None
