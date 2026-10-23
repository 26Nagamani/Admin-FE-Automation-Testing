# Partner Details

## Preconditions
- User is authenticated.
- At least one partner detail action is available from the Pending tab.

## Flow
1. Open the partner list and capture the backend list API response metadata.
2. Switch to the Pending tab.
3. Open the first available partner details modal.
4. Verify the modal and documents section.
5. Approve the partner when the approval button is visible.
6. Capture approval API metadata and close the credentials modal.

## Maintenance Notes
- Modal selectors belong in `pages/partner/partner_details_page.py`.
- Review and approval sequence belongs in `workflows/partner/review_partner_workflow.py`.
- Keep result reporting in `tests/partner/test_partner_details.py`.
