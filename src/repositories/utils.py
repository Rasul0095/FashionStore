import uuid
from datetime import datetime

def generate_sku(product_type: str, brand_id: int, category_id: int) -> str:
    # Пример: CLOTH-NIKE-123-20241217-ABC123
    timestamp = datetime.now().strftime("%Y%m%d")
    unique = str(uuid.uuid4())[:6].upper()
    return f"{product_type[:5].upper()}-{brand_id}-{category_id}-{timestamp}-{unique}"