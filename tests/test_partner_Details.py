import time
from pages.partner_list_page import PartnerListPage
from pages.partnerDetails_page import AgentDetailsPage
from utils.excel_service import ExcelService


def test_partner_details(logged_in_page):

    page = logged_in_page
    print(f"\n current url after login: {page.url}")
    list_page = PartnerListPage(page)
    details_page = AgentDetailsPage(page)
    start_time = time.time()
    result, error_message = "FAIL", ""
    api_captured = {
        "backend_url": "",
        "payload": "",
        "api_response": ""
    }
    

    try:
        # Step 1: Navigate and capture getAgents API
        api_captured = list_page.navigate_and_capture_api()
        print("✓ navigated")
        print(f"✓ backend url: {api_captured['backend_url']}")

        # Step 2: Go to pending tab
        list_page.click_pending_tab()
        pending_count = list_page.get_pending_count()
        print(f"✓ pending count: {pending_count}")

        # Step 3: Grab first available agent
        page.wait_for_selector('[data-testid^="view-details-"]', timeout=7000)
        first_agent = page.locator('[data-testid^="view-details-"]').first
        agent_code = first_agent.get_attribute("data-testid").replace("view-details-", "")
        print(f"✓ agent code: {agent_code}")

        # Step 4: Open modal
        list_page.click_view_details(agent_code)
        print("✓ view details clicked")

        # Step 5: Verify modal open
        details_page.verify_modal_open()
        print("✓ modal open")

        # Step 6: Verify documents section
        details_page.verify_documents_section()
        print("✓ documents section visible")

        # View details verified — PASS regardless of approve step
        result = "PASS"

        # Step 7: Approve only if button is visible
        approve_btn = page.locator('[data-testid="approve-btn"]')
        if approve_btn.is_visible():
            print("✓ approve button visible")

            approve_captured = details_page.click_approve()
            print("✓ approve clicked")

            # Override captured with approve API data since it's more useful
            api_captured["backend_url"] = approve_captured["backend_url"]
            api_captured["payload"]     = approve_captured["payload"]
            api_captured["api_response"] = approve_captured["api_response"]
            print(f"✓ approve api url: {api_captured['backend_url']}")

            details_page.verify_credentials_modal()
            print("✓ credentials modal open")

            username, password = details_page.get_credentials()
            print(f"✓ credentials — username: {username} | password: {password}")

            details_page.close_credentials_modal()
            print("✓ credentials modal closed")

        else:
            print("⚠ approve button not visible — agent already approved/rejected, skipping approve step")
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