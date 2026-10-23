from playwright.sync_api import Page


class ReportsFilterPage:

    def __init__(self, page: Page):
        self.page = page

    # =========================
    # Buttons
    # =========================

    def toggle_filters(self):
        self.page.get_by_test_id(
            "toggle-filters-btn"
        ).click()

    def clear_filters(self):
        self.page.get_by_test_id(
            "clear-filters-btn"
        ).click()

    # =========================
    # Text Inputs
    # =========================

    def enter_order_code(self, value):
        self.page.get_by_test_id(
            "order-code-input"
        ).fill(value)

    def enter_phone_number(self, value):
        self.page.get_by_test_id(
            "phone-number-input"
        ).fill(value)

    def enter_from_date(self, value):
        self.page.get_by_test_id(
            "date-from-input"
        ).fill(value)

    def enter_to_date(self, value):
        self.page.get_by_test_id(
            "date-to-input"
        ).fill(value)

    # =========================
    # Dropdowns
    # =========================

    def select_branch(self, value):
        self.page.get_by_test_id(
            "branch-filter-select"
        ).click()

        self.page.get_by_role(
            "option",
            name=value,
            exact=True
        ).click()

    def select_status(self, value):
        self.page.get_by_test_id(
            "status-filter-select"
        ).click()

        self.page.get_by_role(
            "option",
            name=value,
            exact=True
        ).click()

    def select_order_type(self, value):
        self.page.get_by_test_id(
            "order-type-filter-select"
        ).click()

        self.page.get_by_role(
            "option",
            name=value
        ).click()

    def select_city(self, value):
        self.page.get_by_test_id(
            "city-filter-select"
        ).click()

        self.page.get_by_role(
            "option",
            name=value,
            exact=True
        ).click()

    def select_currency(self, value):
        self.page.get_by_test_id(
            "currency-filter-select"
        ).click()

        self.page.get_by_role(
            "option",
            name=value
        ).click()

    def select_product(self, value):
        self.page.get_by_test_id(
            "product-filter-select"
        ).click()

        self.page.get_by_role(
            "option",
            name=value,
            exact=True
        ).click()

    # =========================
    # Combined Action
    # =========================

    def set_filters(
        self,
        order_code,
        phone_number,
        from_date,
        to_date,
        branch,
        status,
        order_type,
        city,
        currency,
        product
    ):
        self.enter_order_code(order_code)
        self.enter_phone_number(phone_number)
        self.enter_from_date(from_date)
        self.enter_to_date(to_date)

        self.select_branch(branch)
        self.select_status(status)
        self.select_order_type(order_type)
        self.select_city(city)
        self.select_currency(currency)
        self.select_product(product)

    # =========================
    # Getters
    # =========================

    def get_order_code(self):
        return self.page.get_by_test_id(
            "order-code-input"
        ).input_value()

    def get_phone_number(self):
        return self.page.get_by_test_id(
            "phone-number-input"
        ).input_value()

    def get_from_date(self):
        return self.page.get_by_test_id(
            "date-from-input"
        ).input_value()

    def get_to_date(self):
        return self.page.get_by_test_id(
            "date-to-input"
        ).input_value()