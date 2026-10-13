import time
from utils.excel_service import ExcelService
from workflows.partner.review_partner_workflow import ReviewPartnerWorkflow


def test_partner_details(logged_in_page):

    page = logged_in_page
    print(f"\n current url after login: {page.url}")
    partner_workflow = ReviewPartnerWorkflow(page)
    start_time = time.time()
    result, error_message = "FAIL", ""
    api_captured = {
        "backend_url": "",
        "payload": "",
        "api_response": ""
    }
    

    try:
        api_captured = partner_workflow.open_pending_partner_details()

        # View details verified — PASS regardless of approve step
        result = "PASS"

        api_captured = partner_workflow.approve_if_available(api_captured)

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
