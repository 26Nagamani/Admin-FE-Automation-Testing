from openpyxl import Workbook, load_workbook
from datetime import datetime
import os
import json


class ExcelService:

    ROOT_FOLDER = r"D:\AutomationReports"

    @staticmethod
    def write_result(
        module_name,
        test_id,
        data_test_id,
        result,
        error_message="",
        backend_url="",
        api_response="",
        duration="",
        payload=""
    ):

        # Convert payload dict → JSON string (important for readability)
        if isinstance(payload, dict):
            payload = json.dumps(payload, indent=2)

        current_date = datetime.now().strftime("%Y-%m-%d")

        module_folder = os.path.join(
            ExcelService.ROOT_FOLDER,
            module_name
        )

        os.makedirs(module_folder, exist_ok=True)

        excel_file = os.path.join(
            module_folder,
            f"{current_date}.xlsx"
        )

        # Load or create workbook
        if os.path.exists(excel_file):
            workbook = load_workbook(excel_file)
            sheet = workbook.active
        else:
            workbook = Workbook()
            sheet = workbook.active

            # Header row
            sheet.append([
                "Test ID",
                "Module Name",
                "Data Test ID",
                "Result",
                "Error Message",
                "Backend URL Hit",
                "API Response",
                "Duration",
                "Payload",
                "Execution Time"
            ])

        # Data row
        sheet.append([
            test_id,
            module_name,
            data_test_id,
            result,
            error_message,
            backend_url,
            api_response,
            duration,
            payload,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ])
        print(f"[ExcelService] Saving to: {excel_file}")
        workbook.save(excel_file)
        print(f"[ExcelService] Saved successfully") 