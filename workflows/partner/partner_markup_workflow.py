from pages.partner.partner_markup_page import PartnerMarkupPage


class PartnerMarkupWorkflow:

    def __init__(self, page):
        self.page = page
        self.markup_page = PartnerMarkupPage(page)

    def open_markup_for_partner(self, data):
        self.markup_page.navigate()
        print("✓ partner markup page opened")

        self.markup_page.select_branch(data["branch"])
        print(f"✓ branch selected: {data['branch']}")

        self.markup_page.select_partner(data["partner_name"])
        print(f"✓ partner selected: {data['partner_name']}")

        self.markup_page.verify_markup_loaded()
        print("✓ markup page loaded")

    def verify_set_markup_modal(self):
        self.markup_page.open_set_markup_modal()
        print("✓ set markup modal opened")
        self.markup_page.close_set_markup_modal()
        print("✓ set markup modal closed")

    def verify_charges_tab(self):
        self.markup_page.switch_to_charges_tab()
        self.markup_page.verify_charges_loaded()
        print("✓ charges tab loaded")
