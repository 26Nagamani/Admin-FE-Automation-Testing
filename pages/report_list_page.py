from playwright.sync_api import Page


class ReportsListPage:

    def __init__(self, page: Page):
        self.page = page

    def get_row_count(self):
        return self.page.locator("tbody tr").count()

    def click_first_view_order(self):
        self.page.locator(
            "[data-testid^='view-order-']"
        ).first.click()