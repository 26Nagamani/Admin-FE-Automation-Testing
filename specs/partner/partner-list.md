# Partner List

## Preconditions
- User is authenticated.
- Partner list page is reachable at the configured `BASE_URL`.

## Flow
1. Open the partner list.
2. Switch to the Pending tab and read the count.
3. Switch to the Approved tab.
4. Record the test result in the Excel report.

## Maintenance Notes
- Partner list selectors belong in `pages/partner/partner_list_page.py`.
- Keep test scenarios in `tests/partner/test_partner_list.py`.
- Add reusable cross-test list operations to a workflow only when they are shared by multiple tests.
