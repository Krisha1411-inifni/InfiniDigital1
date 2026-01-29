import zipfile
from pathlib import Path
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Product

@receiver(post_save, sender=Product)
def extract_demo_zip(sender, instance, created, **kwargs):
    # Only process if ProductFile exists and DemoFolder is empty
    if not instance.ProductFile:
        return
    if instance.DemoFolder:
        return  # already extracted

    # Unique folder name for demo
    demo_folder_name = f"product_{instance.id}"

    # Full path where the demo will live
    demo_path = settings.BASE_DIR / "products" / "template_demo" / demo_folder_name
    demo_path.mkdir(parents=True, exist_ok=True)

    zip_path = Path(instance.ProductFile.path)

    # Extract zip (flatten top-level folder)
    if zip_path.suffix.lower() == ".zip":
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for member in zip_ref.namelist():
                # Remove the top-level folder if it exists
                parts = member.split('/', 1)
                target_path = demo_path / (parts[1] if len(parts) > 1 else parts[0])

                if member.endswith('/'):
                    # It's a folder
                    target_path.mkdir(parents=True, exist_ok=True)
                else:
                    # It's a file
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    with zip_ref.open(member) as source, open(target_path, 'wb') as target:
                        target.write(source.read())

        # Save the demo folder name to the DB
        instance.DemoFolder = demo_folder_name
        instance.save(update_fields=["DemoFolder"])
