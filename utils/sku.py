from django.utils import timezone

def generate_sku(model_class):
    today = timezone.now().strftime('%Y%m%d') 
    prefix = f"PRD-{today}-"

    last_product = model_class.objects.filter(
        sku__icontains=prefix
    ).order_by('-sku').first()

    if not last_product:
        new_number = "0001"
    else:
        last_number = int(last_product.sku.split('-')[-1])
        new_number = f"{last_number + 1:04d}" 

    return f"{prefix}{new_number}"