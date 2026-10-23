import time
from pages.partner.partner_details_page import PartnerDetailsPage
from pages.partner.partner_list_page import PartnerListPage
from utils.excel_service import ExcelService


def test_partner_details(logged_in_page):

    page = logged_in_page
    print(f"\n current url after login: {page.url}")
    list_page = PartnerListPage(page)
    details_page = PartnerDetailsPage(page)
    start_time = time.time()
    result, error_message = "FAIL", ""
    api_captured = {
        "backend_url": "",
        "payload": "",
        "api_response": ""
    }
    

    try:
        api_captured = list_page.navigate_pending_and_capture_api()
        list_page.open_partner_details_from_current_results()
        details_page.verify_modal_open()
        details_page.verify_documents_section()

        # View details verified only. Approval is covered by test_partner_approval.py.
        result = "PASS"
        details_page.close_modal()

    except Exception as e:
        error_message = str(e)
        print(f"✗ FAILED AT STEP: {error_message}")

    finally:
        duration = round(time.time() - start_time, 2)
        try:
            ExcelService.write_result(
                module_name="AgentDetails",
                test_id="TC002",
                data_test_id="agent-details",
                result=result,
                error_message=error_message,
                backend_url=api_captured["backend_url"],
                duration=duration,
            )
            print(f"TC002 : {result}")
        except Exception as excel_err:
            print(f"TC002 : {result} | Excel write failed: {excel_err}")
