import sys
import time
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from config.conftest import logged_in_page, page
from pages.partner.partner_list_page import PartnerListPage
from pages.partner.partner_markup_page import PartnerMarkupPage
from utils.excel_reader import read_excel
from utils.excel_service import ExcelService


PARTNER_MARKUP_DATA_FILE = REPO_ROOT / "test_data" / "partner" / "PartnerMarkupData.xlsx"


def markup_data():
    rows = read_excel(str(PARTNER_MARKUP_DATA_FILE), "PartnerMarkupData")
    if not rows:
        raise AssertionError(f"No partner markup test data found in {PARTNER_MARKUP_DATA_FILE}")
    return rows[0]


def run_markup_test(test_id, flow):
    started_at = time.time()
    result = "FAIL"
    error_message = ""
    captured = {}
    try:
        captured = flow()
        result = "PASS"
    except Exception as exc:
        error_message = str(exc)
        raise
    finally:
        try:
            ExcelService.write_result(
                module_name="PartnerMarkup",
                test_id=test_id,
                data_test_id="partner-markup",
                result=result,
                error_message=error_message,
                backend_url=captured.get("backend_url", ""),
                api_response=captured.get("api_response", ""),
                duration=round(time.time() - started_at, 2),
            )
            print(f"{test_id} : {result}")
        except Exception as report_error:
            print(f"{test_id} : {result} | Excel write failed: {report_error}")


def run_direct_partner_markup(page, data):
    """Apply markup to the supplied partner in the current browser context."""
    markup_page = PartnerMarkupPage(page)
    set_markup_button = page.get_by_test_id("set-markup-btn")

    # Approval redirects to this partner's markup page. Reuse that selection
    # when available; otherwise open the page and select it explicitly.
    if "/partners/markup" not in page.url or set_markup_button.count() == 0:
        markup_page.navigate()
        markup_page.select_branch(data["branch"])
        markup_page.select_partner(data["partner_name"])

    markup_page.verify_markup_loaded()
    return markup_page.create_markup()


def test_apply_markup_from_approved_partner_listing(logged_in_page):
    """Choose an approved partner showing Apply Markup and configure markup."""
    list_page = PartnerListPage(logged_in_page)
    markup_page = PartnerMarkupPage(logged_in_page)

    def flow():
        list_page.open_first_partner_without_markup()
        markup_page.verify_markup_loaded()
        return markup_page.create_markup()

    run_markup_test("TC004-LISTING", flow)


def test_apply_markup_directly_for_branch_partner(logged_in_page):
    """Open markup directly, select a branch and partner, then configure markup."""
    data = markup_data()
    def flow():
        return run_direct_partner_markup(logged_in_page, data)

    run_markup_test("TC004-DIRECT", flow)
