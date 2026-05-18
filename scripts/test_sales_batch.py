import os
import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ecommerce_backend.settings")

import django
django.setup()

from store.services.sales.batch_processing import trigger_daily_sales_batch
from store.models.sales_report import DailySalesReport

def run():
    print("Triggering the Daily Sales Batch Job manually...")
    
    from django.utils import timezone
    from datetime import timedelta
    target_date_str = timezone.now().date().strftime('%Y-%m-%d')
    
    result = trigger_daily_sales_batch.delay(custom_date=target_date_str)
    report_id = result.get()
    print(f"Task dispatched! Master Report ID: {report_id}")
    
    print("Wait a few seconds, then refresh your Dashboard to see the progress!")

if __name__ == "__main__":
    run()
