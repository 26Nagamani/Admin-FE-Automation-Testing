import re
import time

from playwright.sync_api import Page, expect

from workflows.partner.partner_requirements import COMMON_FIELD_ALIASES, get_document_file_name


def normalize_key(value: str) -> str:
    return "".join(ch for ch in str(value or "").lower() if ch.isalnum())


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
        self.page.wait_for_load_state("networkidle")

    def field_locator(self, field_code: str):
        locators = {
            "partner_name": self.page.get_by_test_id("partner-name-input"),
            "email": self.page.get_by_test_id("email-input"),
            "phone_number": self.page.get_by_test_id("phone-input"),
            "pan_number": self.page.get_by_test_id("pan-input"),
            "account_holder_name": self.page.get_by_test_id("account-holder-input"),
            "ifsc_code": self.page.get_by_test_id("ifsc-input"),
            "bank_account_number": self.page.get_by_test_id("account-number-input"),
            "confirm_bank_account_number": self.page.get_by_test_id("confirm-account-number-input"),
            "gst_number": self.page.get_by_test_id("gst-input"),
            "buisness_name": self.page.get_by_test_id("dynamic-input-buisness_name"),
            "business_name": self.page.get_by_test_id("dynamic-input-buisness_name"),
            "address": self.page.get_by_test_id("dynamic-input-address"),
            "cin_llpin": self.page.get_by_test_id("dynamic-input-cin_llpin"),
            "referral_code": self.page.get_by_test_id("referral-code-input"),
        }
        return locators.get(field_code, self.page.get_by_test_id(f"dynamic-input-{field_code}"))

    def fill_if_visible(self, field_code: str, value):
        if value in (None, ""):
            return

        locator = self.field_locator(field_code)
        if locator.count() == 0 or not locator.first.is_visible():
            return

        locator.first.fill(str(value))

    def verify_required_fields(self, field_codes):
        missing_fields = []
        for field_code in field_codes:
            canonical = COMMON_FIELD_ALIASES.get(field_code, field_code)
            locator = self.field_locator(canonical)
            if locator.count() == 0 or not locator.first.is_visible():
                missing_fields.append(canonical)

        if missing_fields:
            raise AssertionError(f"Missing required partner fields: {missing_fields}")

    def verify_required_documents(self, document_names):
        missing_documents = []
        rendered_documents = self.rendered_document_keys()
        print(f"📄 rendered upload documents: {rendered_documents}")

        for document_name in document_names:
            upload_card = self.page.get_by_test_id(f"upload-card-{document_name}")
            upload_input = self.page.get_by_test_id(f"upload-{document_name}")
            try:
                if upload_card.count() > 0:
                    expect(upload_card.first).to_be_visible(timeout=10000)
                else:
                    expect(upload_input.first).to_be_attached(timeout=10000)
            except Exception:
                missing_documents.append(document_name)

        if missing_documents:
            raise AssertionError(f"Missing required partner documents: {missing_documents}")

    def rendered_document_keys(self):
        upload_cards = self.page.locator('[data-testid^="upload-card-"]')
        document_keys = []
        for index in range(upload_cards.count()):
            testid = upload_cards.nth(index).get_attribute("data-testid") or ""
            document_keys.append(testid.replace("upload-card-", ""))
        return document_keys

    # ---------- STEP 1 ----------

    def fill_partner_details(self, data):

        self.select_dropdown("partner-type-select", data["partner_type"])
        self.select_dropdown("branch-select", data["branch"])
        self.select_dropdown("partner-channel-select", data["partner_channel"])
        self.select_dropdown("referral-source-select", data["referral_source"])

        self.fill_if_visible("partner_name", data.get("partner_name"))
        self.fill_if_visible("buisness_name", data.get("business_name"))
        self.fill_if_visible("email", data.get("email"))
        self.fill_if_visible("phone_number", data.get("phone") or data.get("registered_mobile"))
        self.fill_if_visible("pan_number", data.get("pan_number"))
        self.fill_if_visible("account_holder_name", data.get("account_holder_name"))
        self.fill_if_visible("ifsc_code", data.get("ifsc") or data.get("ifsc_code"))
        self.fill_if_visible("bank_account_number", data.get("bank_account_number"))
        self.fill_if_visible("confirm_bank_account_number", data.get("bank_account_number"))
        self.fill_if_visible("gst_number", data.get("gst_number"))
        self.fill_if_visible("address", data.get("address"))
        self.fill_if_visible("cin_llpin", data.get("cin_llpin"))
        self.fill_if_visible("referral_code", data.get("referral_code"))

    # ---------- VERIFY ACTIONS ----------

    def verify_pan(self):
        button = self.page.get_by_test_id("verify-pan-btn")
        if button.count() > 0 and button.is_visible() and button.is_enabled():
            button.click()

    def verify_bank(self):
        button = self.page.get_by_test_id("verify-bank-btn")
        if button.count() > 0 and button.is_visible() and button.is_enabled():
            button.click()

    def verify_gst(self):
        button = self.page.get_by_test_id("verify-gst-btn")
        if button.count() > 0 and button.is_visible() and button.is_enabled():
            button.click()

    def handle_name_mismatch(self, action):
        normalized_action = str(action or "yes").strip().lower()
        yes_button = self.page.get_by_test_id("mismatch-yes-btn")
        no_button = self.page.get_by_test_id("mismatch-no-btn")

        try:
            yes_button.wait_for(state="visible", timeout=2000)
        except Exception:
            return

        if normalized_action in {"yes", "y", "true", "1", "update"}:
            yes_button.click()
            print("✓ mismatch handled: yes")
        else:
            no_button.click()
            print("✓ mismatch handled: no")

    # ---------- CREATE PARTNER ----------

    def click_create_partner(self):
        self.page.get_by_test_id("create-partner-btn").click()
        # IMPORTANT: removed hard wait_for_selector here — handled in test with debug
        self.page.wait_for_load_state("networkidle")

    # ---------- STEP 2 DOCUMENTS ----------

    def upload_document(self, document_code, file_path):
        input_locator = self.page.get_by_test_id(f"upload-{document_code}")
        input_locator.set_input_files(str(file_path))
        expect(input_locator).to_have_value(re.compile(r".+"), timeout=5000)

    def upload_configured_documents(self, document_files):
        upload_cards = self.page.locator('[data-testid^="upload-card-"]')
        count = upload_cards.count()
        if count == 0:
            raise Exception(f"No document upload cards rendered. URL: {self.page.url}")

        file_paths = list(document_files.values()) if isinstance(document_files, dict) else list(document_files)
        file_lookup = {normalize_key(file_path.stem): file_path for file_path in file_paths}
        uploaded_documents = []
        missing_config = []

        print(f"📄 document upload source: test_data/docs")
        print(f"📄 document upload labels/docKeys from UI cards: {self.rendered_document_keys()}")
        print(f"📄 document upload started | cards found: {count} | files available: {len(file_paths)}")

        for index in range(count):
            upload_card = upload_cards.nth(index)
            card_testid = upload_card.get_attribute("data-testid") or ""
            doc_key = card_testid.replace("upload-card-", "")
            normalized_doc_key = normalize_key(doc_key)
            input_locator = upload_card.locator('input[type="file"]').first
            input_testid = input_locator.get_attribute("data-testid") or ""

            print(f"📄 [{index + 1}/{count}] resolving document upload | docKey={doc_key} | card={card_testid}")

            file_path = file_lookup.get(normalized_doc_key)
            if not file_path:
                for configured_doc_key, configured_file_path in file_lookup.items():
                    if (
                        normalized_doc_key in configured_doc_key
                        or configured_doc_key in normalized_doc_key
                    ):
                        file_path = configured_file_path
                        break

            if not file_path:
                configured_file_name = get_document_file_name(doc_key)
                if configured_file_name:
                    file_path = next(
                        (
                            candidate_path
                            for candidate_path in file_paths
                            if candidate_path.name == configured_file_name
                        ),
                        None,
                    )

            if not file_path:
                for file_stem, candidate_path in file_lookup.items():
                    if normalized_doc_key in file_stem or file_stem in normalized_doc_key:
                        file_path = candidate_path
                        break

            if not file_path:
                missing_config.append(doc_key or f"input #{index + 1}")
                print(f"✗ [{index + 1}/{count}] no file matched for docKey={doc_key}")
                continue

            print(f"📄 [{index + 1}/{count}] matched file | docKey={doc_key} | file={file_path.name}")
            input_locator.set_input_files(str(file_path))
            expect(input_locator).to_have_value(re.compile(r".+"), timeout=5000)
            uploaded_documents.append(doc_key)
            print(f"✓ [{index + 1}/{count}] uploaded | docKey={doc_key} | input={input_testid} | file={file_path}")

        if missing_config:
            raise Exception(f"No configured upload file for rendered documents: {missing_config}")

        if len(uploaded_documents) < count:
            raise Exception(f"Uploaded {len(uploaded_documents)} of {count} rendered documents")

        print(f"✓ document upload completed | uploaded {len(uploaded_documents)} of {count}: {uploaded_documents}")
        return uploaded_documents

    def upload_visible_documents(self, file_paths):
        upload_files = {
            path.stem: path
            for path in file_paths
        }
        self.upload_configured_documents(upload_files)

    def verify_upload_step_visible(self):
        expect(self.page.get_by_text("Upload Documents", exact=True)).to_be_visible(timeout=10000)
        expect(self.page.get_by_text(re.compile(r"^click to upload$", re.I)).first).to_be_visible(timeout=10000)

    def click_upload(self, expected_upload_count=0):
        captured = {
            "backend_url": "",
            "api_response": "",
            "responses": [],
            "upload_response_count": 0,
        }

        def handle_response(response):
            if (
                "localhost:5173" not in response.url
                and response.request.method in {"POST", "PUT", "PATCH"}
            ):
                response_item = {
                    "method": response.request.method,
                    "status": response.status,
                    "url": response.url,
                    "body": "",
                }
                try:
                    response_item["body"] = str(response.json())[:500]
                except Exception:
                    response_item["body"] = "Could not parse response"

                captured["responses"].append(response_item)
                captured["backend_url"] = " | ".join(item["url"] for item in captured["responses"])
                captured["api_response"] = " | ".join(
                    f"{item['method']} {item['status']} {item['url']} => {item['body']}"
                    for item in captured["responses"]
                )

        self.page.on("response", handle_response)
        try:
            self.page.get_by_test_id("upload-btn").click()
            deadline = time.monotonic() + 60
            while time.monotonic() < deadline:
                upload_response_count = len([
                    response for response in captured["responses"]
                    if "/upload-document/" in response.get("url", "")
                ])
                captured["upload_response_count"] = upload_response_count
                if upload_response_count >= expected_upload_count:
                    break
                self.page.wait_for_timeout(500)

            self.page.wait_for_load_state("networkidle")
        finally:
            self.page.remove_listener("response", handle_response)

        return captured

    # ---------- NAVIGATION ----------

    def click_back(self):
        self.page.get_by_test_id("back-btn").click()

    def click_cancel(self):
        self.page.get_by_test_id("cancel-btn").click()
