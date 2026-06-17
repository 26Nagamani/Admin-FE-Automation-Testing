import time

from pages.partner_list_page import PartnerListPage
from utils.excel_service import ExcelService


def test_partner_list(logged_in_page):

    page = logged_in_page
    list_page = PartnerListPage(page)
    start_time = time.time()
    result, error_message = "FAIL", ""

    try:
        list_page.navigate()

        list_page.click_pending_tab()
        pending_count = list_page.get_pending_count()
        print(f"Pending partners: {pending_count}")

        list_page.click_approved_tab()
        print("Approved tab loaded")

        result = "PASS"

    except Exception as e:
        error_message = str(e)
        print(f"TC001 Error: {error_message}")

    finally:
        duration = round(time.time() - start_time, 2)
        try:
            ExcelService.write_result(
                module_name="PartnerList",
                test_id="TC001",
                data_test_id="partner-list",
                result=result,
                error_message=error_message,
                duration=duration,
            )
            print(f"TC001 : {result} | Excel saved to D:\\AutomationReports\\PartnerList\\")
        except Exception as excel_err:
            print(f"TC001 : {result} | Excel write failed: {excel_err}")