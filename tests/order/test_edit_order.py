import time
from pages.order.edit_order_page import EditOrderPage
from pages.order.reports_page import ReportsListPage
from utils.excel_reader import read_excel
from utils.excel_service import ExcelService

edit_data = read_excel("test_data/EditOrderData.xlsx", "EditOrderData")


def test_edit_order(logged_in_page):

    page = logged_in_page
    reports_page = ReportsListPage(page)
    edit_page = EditOrderPage(page)

    for row in edit_data:

        start_time = time.time()
        result = "FAIL"
        error_message = ""

        try:

            # Step 2: Open first order's details modal
            reports_page.view_first_order()
            print("✓ order details modal open")

            # Step 3: Click Edit button inside modal
            edit_page.click_edit()
            print("✓ edit mode enabled")

            # Step 4: Fill fields
            edit_page.edit_order(
                currency_amount=row.get("currency_amount"),
                buyer_rate=row.get("buyer_rate"),
                service_charge=row.get("service_charge"),
                gst=row.get("gst"),
                payment_status=row.get("payment_status"),
            )
            print(f"✓ filled: {row}")

            # Step 5: Save
            edit_page.save()
            print("✓ saved")

            result = "PASS"

        except Exception as e:
            error_message = str(e)
            print(f"✗ FAILED: {error_message}")

        finally:
            duration = round(time.time() - start_time, 2)
            ExcelService.write_result(
                module_name="EditOrder",
                test_id="TC007",
                data_test_id="edit-order",
                result=result,
                error_message=error_message,
                duration=duration,
            )
            print(f"TC007 : {result}")
