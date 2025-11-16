import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import os

def load_recorded_games():
    """Load previously recorded games from Records/RecordsGamesEmails file"""
    records_file = os.path.join(os.path.dirname(__file__), '..', '..', 'Records', 'RecordsGamesEmails')
    try:
        if os.path.exists(records_file) and os.path.getsize(records_file) > 0:
            with open(records_file, 'r') as f:
                return json.load(f)
        return {}
    except Exception as e:
        print(f"Error loading records: {e}")
        return {}

def save_recorded_games(records):
    """Save recorded games to Records/RecordsGamesEmails file"""
    records_file = os.path.join(os.path.dirname(__file__), '..', '..', 'Records', 'RecordsGamesEmails')
    try:
        with open(records_file, 'w') as f:
            json.dump(records, f, indent=2)
    except Exception as e:
        print(f"Error saving records: {e}")

def filter_new_deals(games_list, recipient_emails=None):
    """Filter out games that have the same discount as previously recorded for each recipient"""
    if not games_list:
        return {}
    
    # Load existing records
    recorded_games = load_recorded_games()
    
    # Determine which category to check
    if not recipient_emails or len(recipient_emails) == 0:
        # No email recipients - store under "No email search"
        category = "No email search"
        
        # Ensure category exists
        if category not in recorded_games:
            recorded_games[category] = {}
        
        new_deals = []
        for game in games_list:
            game_title = game['title']
            game_discount = game['discount']
            
            # Check if game exists with same discount in "No email search"
            if game_title in recorded_games[category]:
                if recorded_games[category][game_title]['discount'] == game_discount:
                    continue
            
            # New game or changed discount
            new_deals.append(game)
            
            # Update records
            recorded_games[category][game_title] = {
                'discount': game_discount,
                'url': game['url']
            }
        
        # Save updated records
        save_recorded_games(recorded_games)
        
        # Return empty dict since no emails to send
        return {}
    else:
        # Has email recipients - check each recipient separately
        recipient_new_deals = {}
        
        for recipient_email in recipient_emails:
            # Ensure category exists for this email
            if recipient_email not in recorded_games:
                recorded_games[recipient_email] = {}
            
            new_deals = []
            for game in games_list:
                game_title = game['title']
                game_discount = game['discount']
                
                # Check if game exists with same discount for this recipient
                if game_title in recorded_games[recipient_email]:
                    if recorded_games[recipient_email][game_title]['discount'] == game_discount:
                        continue
                
                # New game or changed discount for this recipient
                new_deals.append(game)
                
                # Update records for this recipient
                recorded_games[recipient_email][game_title] = {
                    'discount': game_discount,
                    'url': game['url']
                }
            
            # Store new deals for this recipient
            if new_deals:
                recipient_new_deals[recipient_email] = new_deals
        
        # Save updated records
        save_recorded_games(recorded_games)
        
        return recipient_new_deals

def send_email(games_list=None, recipient_emails=None, sender_email=None, sender_password=None):
    # Validate sender credentials
    if not sender_email or not sender_password:
        print("Error: Sender email and password are required")
        return
    
    # Use provided recipients
    if not recipient_emails:
        recipient_emails = []
    
    # Filter out games with same discount as before - returns dict of {email: [new_deals]}
    recipient_new_deals = filter_new_deals(games_list, recipient_emails)
    
    # If no new deals for anyone, don't send email
    if not recipient_new_deals:
        print("No new or updated deals found. Email not sent.")
        return
    
    try:
        # Connect to Gmail's SMTP server
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        
        # Send email to each recipient with their specific new deals
        for recipient_email, new_deals in recipient_new_deals.items():
            if not new_deals:
                continue
                
            # Email content for this recipient
            subject = f"Steam Deals - {len(new_deals)} New Games on Sale!"
            body = "Here are the NEW Steam deals (games with changed discounts):\n\n"
            
            for i, game in enumerate(new_deals, 1):
                body += f"{i}. {game['title']}\n"
                body += f"   💰 Discount: {game['discount']}% OFF\n"
                body += f"   💵 Price: {game['original_price']} → {game['final_price']}\n"
                body += f"   🔗 Link: {game['url']}\n\n"
            
            body += "\nHappy gaming! 🎮"
            
            # Create message for this recipient
            message = MIMEMultipart()
            message["From"] = sender_email
            message["To"] = recipient_email
            message["Subject"] = subject
            message.attach(MIMEText(body, "plain"))
            
            # Send email
            server.send_message(message)
            print(f"Email sent successfully to {recipient_email} with {len(new_deals)} new deals")
        
        server.quit()
    except Exception as e:
        print(f"Error sending email: {e}")

def send_email_and_get_count(games_list=None, recipient_emails=None, sender_email=None, sender_password=None):
    """Send email and return the count of new deals sent"""
    # Filter out games with same discount as before FIRST - returns dict of {email: [new_deals]}
    recipient_new_deals = filter_new_deals(games_list, recipient_emails)
    
    # If no new deals for anyone, return immediately without connecting to SMTP
    if not recipient_new_deals:
        print("No new or updated deals found. Email not sent.")
        return 0
    
    # Validate sender credentials
    if not sender_email or not sender_password:
        print("Error: Sender email and password are required")
        return 0
    
    # Use provided recipients
    if not recipient_emails:
        recipient_emails = []
    
    total_sent = 0
    
    try:
        # Connect to Gmail's SMTP server
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        
        # Send email to each recipient with their specific new deals
        for recipient_email, new_deals in recipient_new_deals.items():
            if not new_deals:
                continue
            
            # Email content for this recipient
            subject = f"Steam Deals - {len(new_deals)} New Games on Sale!"
            body = "Here are the NEW Steam deals (games with changed discounts):\n\n"
            
            for i, game in enumerate(new_deals, 1):
                body += f"{i}. {game['title']}\n"
                body += f"   💰 Discount: {game['discount']}% OFF\n"
                body += f"   💵 Price: {game['original_price']} → {game['final_price']}\n"
                body += f"   🔗 Link: {game['url']}\n\n"
            
            body += "\nHappy gaming! 🎮"
            
            # Create message for this recipient
            message = MIMEMultipart()
            message["From"] = sender_email
            message["To"] = recipient_email
            message["Subject"] = subject
            message.attach(MIMEText(body, "plain"))
            
            # Send email
            server.send_message(message)
            print(f"Email sent successfully to {recipient_email} with {len(new_deals)} new deals")
            total_sent += len(new_deals)
        
        server.quit()
        return total_sent
    except Exception as e:
        print(f"Error sending email: {e}")
        return 0

if __name__ == "__main__":
    send_email()