# from app import create_app, db
# from app.models import Product
# import random

# app = create_app()

# categories = ['Electronics', 'Clothing', 'Books', 'Home', 'Toys', 'Sports']

# with app.app_context():
#     # Clear existing products
#     Product.query.delete()

#     for i in range(1, 101):
#         product = Product(
#             name=f'Product {i}',
#             category=random.choice(categories),
#             price=round(random.uniform(10.0, 500.0), 2),
#             rating=round(random.uniform(1.0, 5.0), 1),
#             description=f'This is the description for product {i}.'
#         )
#         db.session.add(product)

#     db.session.commit()
#     print("Inserted 100 mock products")

import random
from faker import Faker
from app import create_app, db
from app.models import Product

fake = Faker()
app = create_app()

# Realistic product names (at least 100)
product_names = [
    "Wireless Headphones", "Bluetooth Speaker", "Smartphone Case", "Laptop Stand",
    "Noise Cancelling Earbuds", "4K Monitor", "Mechanical Keyboard", "Gaming Mouse",
    "USB-C Hub", "Smartwatch", "Wireless Charger", "Portable SSD", "Bluetooth Earbuds",
    "Wireless Gaming Controller", "Power Bank", "LED Desk Lamp", "Laptop Cooling Pad",
    "VR Headset", "External Hard Drive", "Smart Light Bulb", "Fitness Tracker", "WiFi Router",
    "Smart Doorbell", "Portable Projector", "Dash Cam", "Smart Thermostat", "Robot Vacuum",
    "Home Security Camera", "Streaming Stick", "Smart Plug", "Wireless HDMI Transmitter",
    "Laptop Backpack", "Tablet Stand", "Ergonomic Office Chair", "Graphic Tablet",
    "Digital Drawing Pad", "Noise Cancelling Headphones", "Phone Tripod", "DSLR Camera",
    "Camera Lens", "Bluetooth Selfie Stick", "Smart Glasses", "Smart Speaker", "Gaming Laptop",
    "Mini PC", "Wireless Presentation Remote", "Smart Alarm Clock", "Screen Cleaner Kit",
    "Laptop Sleeve", "HD Webcam", "Microphone", "Streaming Microphone", "Tripod Stand",
    "Ring Light", "Wireless Key Finder", "Tablet Keyboard Case", "Smart Air Purifier",
    "E-Reader", "Wireless Thermometer", "Bluetooth Tracker", "Digital Photo Frame",
    "Kids Smartwatch", "3D Printer", "Smart Coffee Maker", "Portable Fan", "Cable Organizer",
    "Noise-Isolating Earphones", "Laptop Docking Station", "Wireless Barcode Scanner",
    "Digital Weight Scale", "Portable Bluetooth Keyboard", "Rechargeable Batteries",
    "WiFi Extender", "Smart Ceiling Fan", "Smart Lock", "LED Strip Lights", "Mini Projector",
    "Smart Humidifier", "HDMI Splitter", "USB Fan", "Bluetooth Transmitter", "Laptop Table",
    "Gaming Monitor", "Smart TV Box", "Smart Water Bottle", "Phone Sanitizer", "Bike Computer",
    "Bluetooth Beanie", "Wireless Shower Speaker", "Smart Mirror", "Wireless Keyboard",
    "Fingerprint Padlock", "Wireless Charging Stand", "Bluetooth Mouse", "Desktop Speakers",
    "AI Voice Assistant Device", "Electric Toothbrush", "Massage Gun", "Neck Massager",
    "Hand Warmer", "Mobile Gimbal", "Smart Ring"
]

with app.app_context():
    print("[*] Clearing existing products...")
    Product.query.delete()
    db.session.commit()

    print("[*] Inserting mock products...")
    for name in product_names:
        product = Product(
            name=name,
            description=fake.text(50),
            price=round(random.uniform(10.0, 500.0), 2),
            rating=round(random.uniform(3.0, 5.0), 1),
            category=random.choice(['Electronics', 'Accessories', 'Wearables', 'Smart Devices'])
        )
        db.session.add(product)

    db.session.commit()
    print(f"[✓] Inserted {len(product_names)} products.")
