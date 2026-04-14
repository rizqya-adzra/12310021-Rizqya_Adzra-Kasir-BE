from django.utils import timezone

def generate_invoice(model_class):
    today = timezone.now().strftime('%Y%m%d') 
    prefix = f"INV-{today}-"

    last_report = model_class.objects.filter(
        invoice__icontains=prefix
    ).order_by('-invoice').first()

    if not last_report:
        new_number = "0001"
    else:
        last_number = int(last_report.invoice.split('-')[-1])
        new_number = f"{last_number + 1:04d}" 

    return f"{prefix}{new_number}"