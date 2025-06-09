import re
import os
import requests
import json
import time
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import ChatSession, Message, Product
from .. import db
from datetime import datetime
import uuid

chat_bp = Blueprint('chat', __name__)


# def parse_user_query_with_gemini(user_query: str):
#     api_url = "https://openrouter.ai/api/v1/chat/completions"
#     api_key = os.getenv("GEMINI_API_KEY")
#     if not api_key:
#         raise RuntimeError("GEMINI_API_KEY environment variable not set")

#     headers = {
#         "Authorization": f"Bearer {api_key}",
#         "Content-Type": "application/json",
#     }

#     prompt = (
#         f"You are an assistant that extracts product search filters from a user query.\n"
#         f"User query: \"{user_query}\"\n\n"
#         "Respond ONLY with a valid JSON object containing zero or more of the following keys:\n"
#         "  - name (string)\n"
#         "  - category (string)\n"
#         "  - max_price (number)\n"
#         "  - min_rating (number)\n"
#         "Do NOT include any other text, explanations, or markdown formatting.\n"
#         "If a value is missing or not applicable, omit that key.\n"
#         "Your response must be a single JSON object only."
#     )

#     data = {
#         "model": "deepseek/deepseek-r1-0528-qwen3-8b:free",
#         "messages": [
#             {
#                 "role": "user",
#                 "content": [{"type": "text", "text": prompt}]
#             }
#         ],
#         "temperature": 0
#     }

#     max_retries = 3
#     backoff = 1  # seconds

#     for attempt in range(max_retries):
#         try:
#             print(f"Sending to OpenRouter API (attempt {attempt+1}): {json.dumps(data, indent=2)}")
#             response = requests.post(api_url, headers=headers, data=json.dumps(data))
#             response.raise_for_status()
#             res_json = response.json()
#             print("Raw API response:", json.dumps(res_json, indent=2))

#             text_response = res_json["choices"][0]["message"]["content"].strip()
#             print("API text response:", text_response)

#             # 🛠 Remove backticks / extract JSON block safely
#             json_match = re.search(r"\{[\s\S]*\}", text_response)
#             if json_match:
#                 clean_json = json_match.group(0)
#             else:
#                 clean_json = text_response  # fallback if no braces found

#             try:
#                 filters = json.loads(clean_json)
#             except Exception as e:
#                 print("Error parsing JSON response:", e)
#                 filters = {}

#             print("Parsed filters:", filters)
#             return filters

#         except requests.exceptions.HTTPError as http_err:
#             if response.status_code == 429:
#                 print(f"Received 429 Too Many Requests. Backing off for {backoff} seconds...")
#                 time.sleep(backoff)
#                 backoff *= 2
#             else:
#                 print(f"HTTP error occurred: {http_err}")
#                 raise
#         except Exception as e:
#             print(f"Unexpected error occurred: {e}")
#             raise

#     print("Failed to get valid response after retries.")
#     return {}

PRODUCT_NAMES = [
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

CATEGORIES = ['Electronics', 'Accessories', 'Wearables', 'Smart Devices']


def extract_json_from_text(text):
    """
    Extract JSON substring from a larger text response,
    by locating first '{' and last '}'.
    """
    try:
        start = text.index('{')
        end = text.rindex('}') + 1
        return text[start:end]
    except ValueError:
        # fallback: return original text if no braces found
        return text


def parse_user_query_with_gemini(user_query: str):
    api_url = "https://openrouter.ai/api/v1/chat/completions"
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY environment variable not set")

    # Build prompt with product names and categories context for better extraction
    prompt = (
        f"You are an assistant that extracts product search filters from a user query.\n"
        f"Available product names include: {', '.join(PRODUCT_NAMES[:30])}, and more.\n"
        f"Available categories are: {', '.join(CATEGORIES)}.\n"
        f"User query: \"{user_query}\"\n\n"
        "Respond ONLY with a valid JSON object containing zero or more of the following keys:\n"
        "  - name (string — must be one of the available product names)\n"
        "  - category (string — must be one of the available categories)\n"
        "  - max_price (number)\n"
        "  - min_rating (number)\n"
        "Do NOT include any other text, explanations, or markdown formatting.\n"
        "If a value is missing or not applicable, omit that key.\n"
        "Your response must be a single JSON object only."
    )

    data = {
        "model": "deepseek/deepseek-r1-0528-qwen3-8b:free",
        "messages": [
            {
                "role": "user",
                "content": [{"type": "text", "text": prompt}]
            }
        ],
        "temperature": 0
    }

    max_retries = 3
    backoff = 1  # seconds

    for attempt in range(max_retries):
        try:
            print(f"Sending to OpenRouter API (attempt {attempt + 1}): {json.dumps(data, indent=2)}")
            response = requests.post(api_url, headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }, data=json.dumps(data))
            response.raise_for_status()
            res_json = response.json()
            print("Raw API response:", json.dumps(res_json, indent=2))

            text_response = res_json["choices"][0]["message"]["content"].strip()
            print("API text response:", text_response)

            # Extract JSON safely
            clean_json = extract_json_from_text(text_response)

            try:
                filters = json.loads(clean_json)
            except Exception as e:
                print("Error parsing JSON response:", e)
                filters = {}

            print("Parsed filters:", filters)
            return filters

        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 429:
                print(f"Received 429 Too Many Requests. Backing off for {backoff} seconds...")
                time.sleep(backoff)
                backoff *= 2
            else:
                print(f"HTTP error occurred: {http_err}")
                raise
        except Exception as e:
            print(f"Unexpected error occurred: {e}")
            raise

    print("Failed to get valid response after retries.")
    return {}

@chat_bp.route('/sessions', methods=['POST'])
@jwt_required()
def start_chat_session():
    user_id = get_jwt_identity()
    session_id = str(uuid.uuid4())
    chat_session = ChatSession(session_id=session_id, user_id=user_id)
    db.session.add(chat_session)
    db.session.commit()
    return jsonify({
        'sessionId': session_id,
        'userId': user_id,
        'startTime': chat_session.start_time.isoformat() + 'Z'
    }), 201


@chat_bp.route('/messages', methods=['POST'])
@jwt_required()
def add_message():
    data = request.get_json()
    session_id = data.get('sessionId')
    content = data.get('content')
    sender = data.get('sender')
    timestamp = data.get('timestamp')

    if not all([session_id, content, sender]):
        return jsonify({'error': 'Missing required fields'}), 400

    chat_session = ChatSession.query.filter_by(session_id=session_id).first()
    if not chat_session:
        return jsonify({'error': 'Invalid session ID'}), 404

    try:
        ts = datetime.fromisoformat(timestamp.replace('Z', '+00:00')) if timestamp else datetime.utcnow()
    except:
        ts = datetime.utcnow()

    # Extract filters from user message content using Gemini API
    try:
        filters = parse_user_query_with_gemini(content)
    except Exception as e:
        print("Error calling Gemini API:", e)
        filters = {}

    print("Filters extracted from user query:", filters)

    query = Product.query
    if 'name' in filters and filters['name']:
       query = query.filter(Product.name.ilike(f"%{filters['name']}%"))
    if 'category' in filters and filters['category']:
        query = query.filter(Product.category.ilike(f"%{filters['category']}%"))
    if 'max_price' in filters and filters['max_price'] is not None:
        query = query.filter(Product.price <= filters['max_price'])
    if 'min_rating' in filters and filters['min_rating'] is not None:
        query = query.filter(Product.rating >= filters['min_rating'])

    matched_products = query.limit(20).all()
    print(f"Filter query: category={filters.get('category')}, max_price={filters.get('max_price')}, min_rating={filters.get('min_rating')}")
    print(f"Number of matched products: {len(matched_products)}")

    products_data = [{
        'id': p.id,
        'name': p.name,
        'category': p.category,
        'price': p.price,
        'rating': p.rating,
        'description': p.description
    } for p in matched_products]
    
    message = Message(
        session_id=session_id,
        content=content,
        sender=sender,
        timestamp=ts,
        products=products_data
    )
    db.session.add(message)

    chat_session.message_count += 1
    db.session.commit()

    return jsonify({
        'messageId': message.id,
        'products': products_data
    }), 201
