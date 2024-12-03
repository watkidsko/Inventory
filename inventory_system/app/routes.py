from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from app.models import db, Product
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import qrcode
from io import BytesIO
import base64
import barcode
from barcode.writer import ImageWriter
import random
import string

main = Blueprint('main', __name__)

@main.route('/')
def index():
    products = Product.query.all()
    return render_template('inventory.html', products=products)

@main.route('/sync_ebay')
def sync_ebay():
    try:
        # Launch browser for eBay login
        driver = webdriver.Chrome()  # or webdriver.Firefox()
        driver.get('https://www.ebay.com/sh/lst/active')
        
        # Wait for user to log in manually and for the page to load
        WebDriverWait(driver, 300).until(
            EC.presence_of_element_located((By.CLASS_NAME, "srp-controls__count-heading"))
        )
        
        # Get listing data
        listings = driver.find_elements(By.CLASS_NAME, "s-item")
        
        for listing in listings:
            try:
                title = listing.find_element(By.CLASS_NAME, "s-item__title").text
                quantity = listing.find_element(By.CLASS_NAME, "s-item__quantity").text
                quantity = int(quantity.split()[0])
                sku = listing.get_attribute("data-item-id")
                
                product = Product.query.filter_by(ebay_id=sku).first()
                if not product:
                    product = Product(
                        ebay_id=sku,
                        name=title,
                        sku=sku,
                        quantity=quantity
                    )
                    db.session.add(product)
                else:
                    product.quantity = quantity
            except Exception as e:
                print(f"Error processing listing: {e}")
                
        db.session.commit()
        driver.quit()
        return jsonify({'success': True})
        
    except Exception as e:
        if 'driver' in locals():
            driver.quit()
        return jsonify({'error': str(e)}), 500

@main.route('/generate_qr/<sku>')
def generate_qr(sku):
    img = qrcode.make(sku)
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return jsonify({'qr_code': img_str})

@main.route('/update_stock', methods=['POST'])
def update_stock():
    data = request.json
    sku = data.get('sku')
    action = data.get('action')
    
    product = Product.query.filter_by(sku=sku).first()
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    if action == 'add':
        product.quantity += 1
    elif action == 'remove':
        if product.quantity > 0:
            product.quantity -= 1
    
    db.session.commit()
    return jsonify({'success': True, 'new_quantity': product.quantity})

@main.route('/scanner')
def scanner():
    return render_template('scanner.html')

@main.route('/scan', methods=['POST'])
def scan():
    # Get the scanned code from the form
    sku = request.form.get('scan_input')
    if not sku:
        return jsonify({'error': 'No SKU provided'}), 400
    
    # Find the product
    product = Product.query.filter_by(sku=sku).first()
    if not product:
        return jsonify({'error': 'Product not found'}), 404
        
    return jsonify({
        'success': True,
        'product': {
            'name': product.name,
            'sku': product.sku,
            'quantity': product.quantity
        }
    })

@main.route('/generate_barcode/<sku>')
def generate_barcode(sku):
    # Generate barcode using the correct method
    EAN = barcode.get_barcode_class('code128')
    my_barcode = EAN(sku, writer=ImageWriter())
    buffered = BytesIO()
    my_barcode.write(buffered)
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return jsonify({'barcode': img_str})

@main.route('/generate_new_sku')
def generate_new_sku():
    # Generate a random SKU number (you can modify this format)
    sku = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return jsonify({'sku': sku})