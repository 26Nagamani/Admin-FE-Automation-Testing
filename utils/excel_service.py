from openpyxl import Workbook, load_workbook
from datetime import datetime
import os
import json
from pathlib import Path


class ExcelService:

    ROOT_FOLDER = r"D:\AutomationReports"

    RESULT_HEADERS = [
        "Test ID",
        "Module Name",
        "Data Test ID",
        "Result",
        "Error Message",
        "Backend URL Hit",
        "API Response",
        "Duration",
        "Payload",
        "Screenshot Path",
        # "Video Path",
        "Execution Time",
    ]

    @staticmethod
    def _current_pytest_test_name():
        current_test = os.environ.get("PYTEST_CURRENT_TEST", "")
        if not current_test:
            return ""

        test_id = current_test.split(" ", 1)[0]
        test_name = test_id.rsplit("::", 1)[-1]
        return test_name.replace("/", "_").replace("\\", "_")

    @staticmethod
    def _current_screenshot_path():
        test_name = ExcelService._current_pytest_test_name()
        if not test_name:
            return ""

        screenshot_path = Path("reports/screenshots") / f"{test_name}.png"
        return str(screenshot_path)

    @staticmethod
    def _find_result_row(sheet, headers, test_id, data_test_id):
        test_id_column = headers.index("Test ID") + 1
        data_test_id_column = headers.index("Data Test ID") + 1

        for row_number in range(2, sheet.max_row + 1):
            row_test_id = str(sheet.cell(row=row_number, column=test_id_column).value or "")
            row_data_test_id = str(sheet.cell(row=row_number, column=data_test_id_column).value or "")
            if row_test_id == str(test_id) and row_data_test_id == str(data_test_id):
                return row_number

        return sheet.max_row + 1

    @staticmethod
    def _ensure_headers(sheet):
        existing_headers = [cell.value for cell in sheet[1]]

        if not any(existing_headers):
            for column_index, header in enumerate(ExcelService.RESULT_HEADERS, start=1):
                sheet.cell(row=1, column=column_index).value = header
            return ExcelService.RESULT_HEADERS

        for header in ExcelService.RESULT_HEADERS:
            if header not in existing_headers:
                sheet.cell(row=1, column=len(existing_headers) + 1).value = header
                existing_headers.append(header)

        return existing_headers

    @staticmethod
    def clear_module_results(module_name):
        current_date = datetime.now().strftime("%Y-%m-%d")
        module_folder = os.path.join(
            ExcelService.ROOT_FOLDER,
            module_name
        )
        excel_file = os.path.join(
            module_folder,
            f"{current_date}.xlsx"
        )

        os.makedirs(module_folder, exist_ok=True)

        workbook = Workbook()
        sheet = workbook.active
        for column_index, header in enumerate(ExcelService.RESULT_HEADERS, start=1):
            sheet.cell(row=1, column=column_index).value = header

        print(f"[ExcelService] Clearing previous results: {excel_file}")
        workbook.save(excel_file)
        print("[ExcelService] Previous results cleared")

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
        payload="",
        screenshot_path="",
        # video_path=""
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

        headers = ExcelService._ensure_headers(sheet)

        if str(result).upper() == "FAIL":
            screenshot_path = screenshot_path or ExcelService._current_screenshot_path()
        else:
            screenshot_path = ""
        # video_path = ""

        row_values = {
            "Test ID": test_id,
            "Module Name": module_name,
            "Data Test ID": data_test_id,
            "Result": result,
            "Error Message": error_message,
            "Backend URL Hit": backend_url,
            "API Response": api_response,
            "Duration": duration,
            "Payload": payload,
            "Screenshot Path": screenshot_path,
            # "Video Path": video_path,
            "Execution Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        # Upsert result row for this test case instead of appending duplicates.
        target_row = ExcelService._find_result_row(sheet, headers, test_id, data_test_id)
        for column_index, header in enumerate(headers, start=1):
            sheet.cell(row=target_row, column=column_index).value = row_values.get(header, "")

        print(f"[ExcelService] Saving to: {excel_file}")
        workbook.save(excel_file)
        print(f"[ExcelService] Saved successfully") 

    @staticmethod
    def update_data_row(file_path, sheet_name, match_column, match_value, updates):
        workbook = load_workbook(file_path)
        sheet = workbook[sheet_name]

        headers = [cell.value for cell in sheet[1]]

        for column_name in updates:
            if column_name not in headers:
                sheet.cell(row=1, column=len(headers) + 1).value = column_name
                headers.append(column_name)

        if match_column not in headers:
            raise ValueError(f"Column not found: {match_column}")

        match_column_index = headers.index(match_column) + 1

        target_row = None
        for row_number in range(2, sheet.max_row + 1):
            if str(sheet.cell(row=row_number, column=match_column_index).value or "") == str(match_value):
                target_row = row_number
                break

        if target_row is None:
            raise ValueError(f"No row found for {match_column}={match_value}")

        for column_name, value in updates.items():
            column_index = headers.index(column_name) + 1
            sheet.cell(row=target_row, column=column_index).value = value

        workbook.save(file_path)
