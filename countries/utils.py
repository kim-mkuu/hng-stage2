import requests
import random
from decimal import Decimal
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
import os

def fetch_countries():
    """Fetch country data from restcountries API"""
    url = "https://restcountries.com/v2/all?fields=name,capital,region,population,flag,currencies"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise Exception(f"Could not fetch data from restcountries.com: {str(e)}")

def fetch_exchange_rates():
    """Fetch exchange rates from open.er-api.com"""
    url = "https://open.er-api.com/v6/latest/USD"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json().get('rates', {})
    except requests.RequestException as e:
        raise Exception(f"Could not fetch data from open.er-api.com: {str(e)}")

def calculate_estimated_gdp(population, exchange_rate):
    """Calculate estimated GDP"""
    if not exchange_rate or exchange_rate == 0:
        return None
    random_multiplier = random.uniform(1000, 2000)
    return Decimal(population) * Decimal(random_multiplier) / Decimal(exchange_rate)

def generate_summary_image(total_countries, top_countries, timestamp):
    """Generate summary image with country statistics"""
    # Create image
    width, height = 800, 600
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)

    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
        font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
    except:
        font_large = font_medium = font_small = ImageFont.load_default()
        
    # Title
    draw.text((50, 30), "Country Data Summary", fill='black', font=font_large)
    
    # Total countries
    draw.text((50, 100), f"Total Countries: {total_countries}", fill='black', font=font_medium)
    
    # Top 5 countries by GDP
    draw.text((50, 150), "Top 5 Countries by Estimated GDP:", fill='black', font=font_medium)
    
    y_position = 200
    for i, country in enumerate(top_countries[:5], 1):
        gdp_formatted = f"{country.estimated_gdp:,.2f}" if country.estimated_gdp else "N/A"
        text = f"{i}. {country.name}: ${gdp_formatted}"
        draw.text((70, y_position), text, fill='black', font=font_small)
        y_position += 40
    
    # Timestamp
    timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S UTC") if timestamp else "N/A"
    draw.text((50, 520), f"Last Refreshed: {timestamp_str}", fill='gray', font=font_small)
    
    # Save image
    cache_dir = os.path.join(settings.BASE_DIR, 'cache')
    os.makedirs(cache_dir, exist_ok=True)
    image_path = os.path.join(cache_dir, 'summary.png')
    img.save(image_path)
    
    return image_path