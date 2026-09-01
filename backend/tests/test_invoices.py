from app.models.invoice import Invoice, InvoiceItem


def test_invoice_totals():
    invoice = Invoice(
        reference_code="INV-001",
        total_subtotal=100.0,
        total_tax=19.0,
        total_discount=0.0,
        total_amount=119.0,
    )
    assert invoice.total_amount == 119.0


def test_invoice_item_calculations():
    item = InvoiceItem(
        code_reference="PROD-1",
        name="Product",
        quantity=2,
        price=50.0,
        unit_measure_code="94",
        standard_code="999",
        discount_rate=0.0,
        tax_rate=19.0,
        tax_code="01",
        subtotal=100.0,
        tax_amount=19.0,
        total=119.0,
    )
    assert item.total == 119.0
