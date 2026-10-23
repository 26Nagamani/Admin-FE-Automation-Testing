from playwright.sync_api import Page, expect


class OrderDetailsPage:

    def __init__(self, page: Page):
        self.page = page

    def verify_modal_open(self):
        expect(
            self.page.get_by_text("Order Information")
        ).to_be_visible()

    def close_modal(self):
        self.page.keyboard.press("Escape")