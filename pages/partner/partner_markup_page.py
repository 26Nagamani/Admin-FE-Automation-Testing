from playwright.sync_api import Page, expect

from config.config import BASE_URL


class PartnerMarkupPage:

    def __init__(self, page: Page):
        self.page = page

    def navigate(self):
        self.page.goto(f"{BASE_URL}partners/markup")
        self.page.wait_for_load_state("networkidle")

    def select_dropdown(self, testid: str, value: str):
        wrapper = self.page.get_by_test_id(testid)
        wrapper.wait_for(state="visible", timeout=10000)
        control = wrapper.locator(".react-select__control")
        if control.count() == 0:
            expect(wrapper.get_by_display_value(value)).to_be_visible(timeout=10000)
            return

        control.click()
        self.page.keyboard.type(value)
        self.page.wait_for_timeout(500)
        self.page.keyboard.press("ArrowDown")
        self.page.keyboard.press("Enter")
        self.page.wait_for_load_state("networkidle")

    def select_branch(self, branch_name: str):
        self.select_dropdown("markup-branch-select", branch_name)

    def select_partner(self, partner_name: str):
        self.select_dropdown("markup-partner-select", partner_name)

    def verify_markup_loaded(self):
        expect(self.page.get_by_test_id("markup-tab")).to_be_visible(timeout=10000)
        expect(self.page.get_by_test_id("set-markup-btn")).to_be_visible(timeout=10000)
        self.page.wait_for_load_state("networkidle")

    def open_set_markup_modal(self):
        button = self.page.get_by_test_id("set-markup-btn")
        button.wait_for(state="visible", timeout=10000)
        button.click()
        self.page.wait_for_selector("text=Configure bulk markup rules.", timeout=10000)

    def close_set_markup_modal(self):
        self.page.get_by_test_id("markup-setup-close-btn").click()
        self.page.wait_for_selector("text=Configure bulk markup rules.", state="hidden", timeout=10000)

    def switch_to_charges_tab(self):
        self.page.get_by_test_id("charges-tab").click()
        self.page.wait_for_load_state("networkidle")

    def verify_charges_loaded(self):
        expect(self.page.get_by_test_id("charges-tab")).to_have_attribute(
            "aria-selected",
            "true",
            timeout=10000
        )
        self.page.wait_for_load_state("networkidle")
