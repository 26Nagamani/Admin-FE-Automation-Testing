# Add Partner

## Preconditions
- User is authenticated.
- Partner test data exists in `test_data/partner/AddPartnerData.xlsx`.
- Upload documents exist in `test_data/partner/docs/`.

## Flow
1. Open the partner list.
2. Click Add Partner.
3. Fill partner details from the Excel data row.
4. Verify PAN, bank, and GST.
5. Create the partner and wait for document upload fields.
6. Upload all required documents.
7. Submit the upload step.

## Maintenance Notes
- Page selectors belong in `pages/partner/add_partner_page.py`.
- Business sequence belongs in `workflows/partner/create_partner_workflow.py`.
- Test assertions and result reporting belong in `tests/partner/test_add_partner.py`.
- Upload document paths should come from `workflows/partner/partner_paths.py`.
