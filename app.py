import requests
from bs4 import BeautifulSoup
import re
import csv
from datetime import datetime
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def clean_price(price):
    # Remove the currency symbol and any non-numeric characters
    price = re.sub(r'[^0-9.]', '', price)  # Keep only digits and the decimal point
    
    # Split the price at the decimal point and take the integer part only
    if price:
        return price.split('.')[0]  # Take the part before the decimal
    else:
        return "Price not found"

def store_price(date, time, price):
    # Check if the file exists to determine if we need to add the header
    file_exists = os.path.isfile("prices.csv")
    
    # Open the CSV file in append mode and store the price along with the date and time
    with open("prices.csv", "a", newline="") as file:
        writer = csv.writer(file)
        
        # If the file doesn't exist, write the header
        if not file_exists:
            writer.writerow(["Date", "Time", "Price"])  # Header only once
        
        # Write the date, time, and price
        writer.writerow([date, time, price])

def send_email(price):
    # Sender email credentials (your Gmail credentials)
    sender_email = "akshayalva030303@gmail.com"
    sender_password = "cttg ivqm vdns epxa"  # Or use an app password if 2FA is enabled
    receiver_email = "akshayalva030303@gmail.com"
    
    # Set up the email content
    subject = f"Product Price Update DUNKS - ₹{price}"
    body = f"The current price of the product is: ₹{price}"
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    
    # Attach the body with the msg instance
    msg.attach(MIMEText(body, 'plain'))
    
    # Setup the SMTP server
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    
    try:
        # Login to the email account
        server.login(sender_email, sender_password)
        
        # Send the email
        server.sendmail(sender_email, receiver_email, msg.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")
    finally:
        # Quit the server
        server.quit()

def get_price(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Locate the price element (adjust this to the actual price tag)
        price_tag = soup.find("span", {"class": "nds-text mr2-sm css-tbgmka e1yhcai00 text-align-start appearance-body1Strong color-primary display-inline weight-regular"})
        
        if price_tag:
            # Get the raw text of the price
            price_text = price_tag.text.strip()
            # Clean the price and return it
            return clean_price(price_text)
        else:
            return "Price element not found on the page"
    else:
        return f"Failed to retrieve page: {response.status_code}"

# URL of the product
product_url = "https://www.nike.com/in/t/dunk-low-retro-berlin-shoes-cxX6mF"

# Get the price
price = get_price(product_url)

# Get current date and time
now = datetime.now()
date = now.strftime('%Y-%m-%d')  # Date in YYYY-MM-DD format
time = now.strftime('%H:%M')  # Time in HH:MM format (only hour and minute)

# Store the price, date, and time in a CSV file
store_price(date, time, price)

# Send the price via email
send_email(price)

print(f"The current price of the product is: {price}")
