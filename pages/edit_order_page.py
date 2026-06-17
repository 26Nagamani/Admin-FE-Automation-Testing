from playwright.sync_api import Page, expect


class EditOrderPage:

    def __init__(self, page: Page):
        self.page = page

    # -------------------------
    # Helpers (IMPORTANT FIX)
    # -------------------------

    def wait_for_overlay_to_close(self):
        """Wait until modal overlay is gone"""
        overlay = self.page.locator(".fixed.inset-0.z-50")
        try:
            overlay.wait_for(state="detached", timeout=5000)
        except:
            pass  # overlay might not exist sometimes

    def safe_click(self, locator):
        expect(locator).to_be_visible()
        expect(locator).to_be_enabled()
        locator.click()

    # -------------------------
    # Form Actions
    # -------------------------

    def update_currency_amount(self, value):
        self.page.get_by_test_id("currency-amount-input").fill(str(value))

    def update_buyer_rate(self, value):
        self.page.get_by_test_id("buyer-rate-input").fill(str(value))

    def update_service_charge(self, value):
        self.page.get_by_test_id("service-charge-input").fill(str(value))

    def update_gst(self, value):
        self.page.get_by_test_id("gst-input").fill(str(value))

    def select_payment_status(self, value):
        wrapper = self.page.get_by_test_id("payment-status-select")

        self.safe_click(wrapper)

        # React-select input inside dropdown
        self.page.keyboard.type(value)
        self.page.wait_for_timeout(300)
        self.page.keyboard.press("ArrowDown")
        self.page.keyboard.press("Enter")

        self.wait_for_overlay_to_close()

    # -------------------------
    # Navigation Actions
    # -------------------------

    def click_edit(self):
        btn = self.page.get_by_role("button", name="Edit", exact=True)
        self.safe_click(btn)

    # -------------------------
    # SAVE FLOW (FIXED)
    # -------------------------

    def save(self):
        # Step 1: Click Save (opens modal)
        save_btn = self.page.get_by_test_id("save-order-btn")
        self.safe_click(save_btn)

        # Step 2: Wait for modal properly
        confirm_modal = self.page.get_by_text("Confirm Changes")
        confirm_modal.wait_for(state="visible", timeout=5000)

        self.page.wait_for_timeout(300)  # allow animation settle

        # Step 3: Click Apply safely
        apply_btn = self.page.get_by_test_id("confirm-apply-btn")
        self.safe_click(apply_btn)

        # Step 4: WAIT for modal to close (CRITICAL FIX)
        self.wait_for_overlay_to_close()

        self.page.wait_for_load_state("networkidle")

    # -------------------------
    # Full Edit Flow
    # -------------------------

    def edit_order(
        self,
        currency_amount=None,
        buyer_rate=None,
        service_charge=None,
        gst=None,
        payment_status=None,
    ):
        if currency_amount:
            self.update_currency_amount(currency_amount)

        if buyer_rate:
            self.update_buyer_rate(buyer_rate)

        if service_charge:
            self.update_service_charge(service_charge)

        if gst:
            self.update_gst(gst)

        if payment_status:
            self.select_payment_status(payment_status)