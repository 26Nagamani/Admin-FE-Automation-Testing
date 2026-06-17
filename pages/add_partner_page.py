from playwright.sync_api import Page


class AddPartnerPage:

    def __init__(self, page: Page):
        self.page = page

    # ---------- DROPDOWNS ----------

    def select_dropdown(self, testid: str, value: str):
        wrapper = self.page.get_by_test_id(testid)
        wrapper.wait_for(state="visible", timeout=10000)
        wrapper.locator(".react-select__control").click()
        self.page.keyboard.type(value)
        self.page.wait_for_timeout(500)
        self.page.keyboard.press("ArrowDown")
        self.page.keyboard.press("Enter")

    # ---------- STEP 1 ----------

    def fill_partner_details(self, data):

        self.select_dropdown("partner-type-select", data["partner_type"])
        self.select_dropdown("branch-select", data["branch"])
        self.select_dropdown("partner-channel-select", data["partner_channel"])
        self.select_dropdown("referral-source-select", data["referral_source"])

        self.page.get_by_test_id("partner-name-input").fill(data["partner_name"])
        self.page.get_by_placeholder("Enter registered business name").fill(data["business_name"])
        self.page.get_by_test_id("email-input").fill(data["email"])
        self.page.get_by_test_id("phone-input").fill(data["phone"])
        self.page.get_by_test_id("pan-input").fill(data["pan_number"])
        self.page.get_by_test_id("account-holder-input").fill(data["account_holder_name"])
        self.page.get_by_test_id("ifsc-input").fill(data["ifsc"])
        self.page.get_by_test_id("account-number-input").fill(data["bank_account_number"])
        self.page.get_by_test_id("gst-input").fill(data["gst_number"])

    # ---------- VERIFY ACTIONS ----------

    def verify_pan(self):
        self.page.get_by_test_id("verify-pan-btn").click()

    def verify_bank(self):
        self.page.get_by_test_id("verify-bank-btn").click()

    def verify_gst(self):
        self.page.get_by_test_id("verify-gst-btn").click()

    # ---------- CREATE PARTNER ----------

    def click_create_partner(self):
        self.page.get_by_test_id("create-partner-btn").click()
        # IMPORTANT: removed hard wait_for_selector here — handled in test with debug
        self.page.wait_for_load_state("networkidle")

    # ---------- STEP 2 DOCUMENTS ----------

    def upload_document(self, document_code, file_path):
        self.page.get_by_test_id(f"upload-{document_code}").set_input_files(file_path)

    def click_upload(self):
        self.page.get_by_test_id("upload-btn").click()

    # ---------- NAVIGATION ----------

    def click_back(self):
        self.page.get_by_test_id("back-btn").click()

    def click_cancel(self):
        self.page.get_by_test_id("cancel-btn").click()