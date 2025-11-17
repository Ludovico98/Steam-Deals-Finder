import customtkinter 
import sys
import os
import webbrowser
import threading

# Add scripts directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Email'))

from steam_search import SteamSearcher
from SendEmail import send_email

customtkinter.set_appearance_mode("light")  # Modes: "system" (default), "light", "dark"
customtkinter.set_default_color_theme("green")  # Themes: "blue" (default), "green", "dark-blue"

class SteamDealsUI:
    def __init__(self):
        self.root = customtkinter.CTk()
        self.root.geometry("1000x800")
        self.root.title("Steam Deals Finder")
        
        # Configure root window to be resizable
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        self.searcher = SteamSearcher()
        self.min_discount = 0
        self.search_results = []
        self.scheduled_task = None
        self.is_scheduled_active = False
        self.email_recipients = []  # List of email addresses
        
        self.setup_ui()
        
        # Enable mouse wheel scrolling for all scrollable frames
        self.bind_mousewheel()
    
    def bind_mousewheel(self):
        """Bind mouse wheel scrolling to all scrollable frames"""
        def _on_mousewheel(event):
            # Find which widget the mouse is over
            widget = event.widget.winfo_containing(event.x_root, event.y_root)
            
            # Check if we're over a scrollable frame
            while widget:
                if isinstance(widget, customtkinter.CTkScrollableFrame):
                    # Scroll the frame
                    if event.delta:
                        widget._parent_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
                    break
                widget = widget.master
        
        # Bind to the root window
        self.root.bind_all("<MouseWheel>", _on_mousewheel)  # Windows/MacOS
        self.root.bind_all("<Button-4>", lambda e: _on_mousewheel(type('obj', (object,), {'delta': 120, 'widget': e.widget, 'x_root': e.x_root, 'y_root': e.y_root})()))  # Linux scroll up
        self.root.bind_all("<Button-5>", lambda e: _on_mousewheel(type('obj', (object,), {'delta': -120, 'widget': e.widget, 'x_root': e.x_root, 'y_root': e.y_root})()))  # Linux scroll down
    
    def setup_ui(self):
        # Main frame - use grid for better control
        main_frame = customtkinter.CTkFrame(master=self.root)
        main_frame.grid(row=0, column=0, pady=20, padx=20, sticky="nsew")
        main_frame.rowconfigure(2, weight=1)  # Controls frame expands
        main_frame.columnconfigure(0, weight=1)

        # Title
        title_label = customtkinter.CTkLabel(
            master=main_frame, 
            text="Steam Deals Finder", 
            font=("Arial", 32, "bold")
        )
        title_label.grid(row=0, column=0, pady=20, padx=30, sticky="ew")

        # Controls frame
        controls_frame = customtkinter.CTkFrame(master=main_frame)
        controls_frame.grid(row=2, column=0, pady=10, padx=20, sticky="nsew")
        controls_frame.rowconfigure(0, weight=1)
        controls_frame.columnconfigure(0, weight=1)
        controls_frame.columnconfigure(1, weight=1)

        # Create two columns: left for controls, right for scheduler
        left_controls = customtkinter.CTkFrame(master=controls_frame)
        left_controls.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        left_controls.rowconfigure(4, weight=1)  # Results frame expands (row 4, not row 3)
        left_controls.columnconfigure(0, weight=1)

        right_scheduler = customtkinter.CTkFrame(master=controls_frame)
        right_scheduler.grid(row=0, column=1, padx=(10, 0), sticky="nsew")
        right_scheduler.rowconfigure(2, weight=1)  # Email list frame expands
        right_scheduler.columnconfigure(0, weight=1)

        # === LEFT SIDE - Main Controls ===
        
        # Discount slider section
        discount_label = customtkinter.CTkLabel(
            master=left_controls, 
            text="Minimum Discount Percentage:", 
            font=("Arial", 16)
        )
        discount_label.grid(row=0, column=0, pady=(10, 5), padx=10, sticky="ew")

        self.discount_slider = customtkinter.CTkSlider(
            master=left_controls,
            from_=0,
            to=100,
            number_of_steps=20,
            command=self.update_discount_value,
            height=20
        )
        self.discount_slider.grid(row=1, column=0, pady=5, padx=20, sticky="ew")
        self.discount_slider.set(0)
        
        self.discount_value_label = customtkinter.CTkLabel(
            master=left_controls,
            text="0%",
            font=("Arial", 16, "bold")
        )
        self.discount_value_label.grid(row=2, column=0, pady=(5, 15), sticky="ew")

        # Search and Send button
        self.search_send_button = customtkinter.CTkButton(
            master=left_controls,
            text="🔍📧 Search & Send Email",
            command=self.search_and_send_email,
            height=50,
            font=("Arial", 18, "bold"),
            fg_color="#FF6B35"
        )
        self.search_send_button.grid(row=3, column=0, pady=15, padx=20, sticky="ew")

        # Results frame with scrollbar (inside left_controls)
        self.results_frame = customtkinter.CTkScrollableFrame(
            master=left_controls,
            label_text="Search Results"
        )
        self.results_frame.grid(row=4, column=0, pady=10, padx=10, sticky="nsew")

        # === RIGHT SIDE - Scheduler ===
        scheduler_title = customtkinter.CTkLabel(
            master=right_scheduler,
            text="⏰ Schedule Auto Send",
            font=("Arial", 20, "bold")
        )
        scheduler_title.grid(row=0, column=0, pady=(10, 15), padx=10, sticky="ew")

        # Email credentials section
        credentials_section = customtkinter.CTkFrame(master=right_scheduler)
        credentials_section.grid(row=1, column=0, pady=10, padx=10, sticky="ew")
        credentials_section.columnconfigure(0, weight=1)

        credentials_title = customtkinter.CTkLabel(
            master=credentials_section,
            text="🔐 Sender Email Credentials",
            font=("Arial", 14, "bold")
        )
        credentials_title.grid(row=0, column=0, pady=(5, 5), sticky="ew")

        # Sender email input
        self.sender_email_entry = customtkinter.CTkEntry(
            master=credentials_section,
            placeholder_text="Sender email address",
            font=("Arial", 11)
        )
        self.sender_email_entry.grid(row=1, column=0, pady=3, padx=5, sticky="ew")

        # Sender password input with toggle visibility button
        password_frame = customtkinter.CTkFrame(master=credentials_section)
        password_frame.grid(row=2, column=0, pady=3, padx=5, sticky="ew")
        password_frame.columnconfigure(0, weight=1)

        self.sender_password_entry = customtkinter.CTkEntry(
            master=password_frame,
            placeholder_text="App password (not regular password)",
            font=("Arial", 11),
            show="•"
        )
        self.sender_password_entry.grid(row=0, column=0, padx=(0, 5), sticky="ew")

        self.password_visible = False
        self.toggle_password_button = customtkinter.CTkButton(
            master=password_frame,
            text="👁️",
            command=self.toggle_password_visibility,
            width=40,
            height=28,
            font=("Arial", 14)
        )
        self.toggle_password_button.grid(row=0, column=1, sticky="e")

        # Email recipients section
        email_section = customtkinter.CTkFrame(master=right_scheduler)
        email_section.grid(row=2, column=0, pady=10, padx=10, sticky="nsew")
        email_section.rowconfigure(2, weight=1)  # Email list expands
        email_section.columnconfigure(0, weight=1)

        email_title = customtkinter.CTkLabel(
            master=email_section,
            text="📧 Email Recipients",
            font=("Arial", 14, "bold")
        )
        email_title.grid(row=0, column=0, pady=(5, 5), sticky="ew")

        # Email input frame
        email_input_frame = customtkinter.CTkFrame(master=email_section)
        email_input_frame.grid(row=1, column=0, pady=5, padx=5, sticky="ew")
        email_input_frame.columnconfigure(0, weight=1)

        self.email_entry = customtkinter.CTkEntry(
            master=email_input_frame,
            placeholder_text="Enter email address",
            font=("Arial", 12)
        )
        self.email_entry.grid(row=0, column=0, padx=5, sticky="ew")

        add_email_button = customtkinter.CTkButton(
            master=email_input_frame,
            text="➕ Add",
            command=self.add_email,
            width=60,
            height=30,
            font=("Arial", 12, "bold"),
            fg_color="#28a745"
        )
        add_email_button.grid(row=0, column=1, padx=5, sticky="e")

        # Email list frame (scrollable)
        self.email_list_frame = customtkinter.CTkScrollableFrame(
            master=email_section,
            label_text="Recipients List"
        )
        self.email_list_frame.grid(row=2, column=0, pady=5, padx=5, sticky="nsew")

        # Time input section
        time_frame = customtkinter.CTkFrame(master=right_scheduler)
        time_frame.grid(row=3, column=0, pady=10, padx=10, sticky="ew")
        time_frame.columnconfigure(0, weight=1)

        time_label = customtkinter.CTkLabel(
            master=time_frame,
            text="Set Time (HH:MM):",
            font=("Arial", 14)
        )
        time_label.grid(row=0, column=0, pady=5, sticky="ew")

        # Hour and minute inputs
        time_input_frame = customtkinter.CTkFrame(master=time_frame)
        time_input_frame.grid(row=1, column=0, pady=5)

        self.hour_entry = customtkinter.CTkEntry(
            master=time_input_frame,
            placeholder_text="HH",
            width=60,
            font=("Arial", 16)
        )
        self.hour_entry.pack(side="left", padx=5)
        
        colon_label = customtkinter.CTkLabel(
            master=time_input_frame,
            text=":",
            font=("Arial", 20, "bold")
        )
        colon_label.pack(side="left", padx=2)
        
        self.minute_entry = customtkinter.CTkEntry(
            master=time_input_frame,
            placeholder_text="MM",
            width=60,
            font=("Arial", 16)
        )
        self.minute_entry.pack(side="left", padx=5)
        
        # Activate/Deactivate toggle button
        self.schedule_toggle_button = customtkinter.CTkButton(
            master=right_scheduler,
            text="✅ Activate",
            command=self.toggle_schedule,
            height=50,
            font=("Arial", 18, "bold"),
            fg_color="#28a745"
        )
        self.schedule_toggle_button.grid(row=4, column=0, pady=15, padx=10, sticky="ew")

        # Schedule status label
        self.schedule_status_label = customtkinter.CTkLabel(
            master=right_scheduler,
            text="No task scheduled",
            font=("Arial", 12),
            text_color="gray"
        )
        self.schedule_status_label.grid(row=5, column=0, pady=10, sticky="ew")

        # Status label (at bottom of main frame)
        self.status_label = customtkinter.CTkLabel(
            master=main_frame,
            text="Ready to search Steam deals",
            font=("Arial", 14)
        )
        self.status_label.grid(row=3, column=0, pady=10, sticky="ew")

    def update_discount_value(self, value):
        """Update the discount percentage display"""
        self.min_discount = int(value)
        self.discount_value_label.configure(text=f"{self.min_discount}%")
    
    def toggle_password_visibility(self):
        """Toggle password visibility between hidden and visible"""
        if self.password_visible:
            # Hide password
            self.sender_password_entry.configure(show="•")
            self.toggle_password_button.configure(text="👁️")
            self.password_visible = False
        else:
            # Show password
            self.sender_password_entry.configure(show="")
            self.toggle_password_button.configure(text="🙈")
            self.password_visible = True
    
    def add_email(self):
        """Add an email address to the recipients list"""
        email = self.email_entry.get().strip()
        
        if not email:
            return
        
        # Basic email validation
        if '@' not in email or '.' not in email.split('@')[-1]:
            self.status_label.configure(text="⚠️ Please enter a valid email address")
            return
        
        # Check if email already exists
        if email in self.email_recipients:
            self.status_label.configure(text="⚠️ Email already added")
            return
        
        # Add to list
        self.email_recipients.append(email)
        
        # Clear entry
        self.email_entry.delete(0, 'end')
        
        # Update display
        self.refresh_email_list()
        self.status_label.configure(text=f"✅ Added {email} to recipients")
    
    def remove_email(self, email):
        """Remove an email address from the recipients list"""
        if email in self.email_recipients:
            self.email_recipients.remove(email)
            self.refresh_email_list()
            self.status_label.configure(text=f"🗑️ Removed {email} from recipients")
    
    def refresh_email_list(self):
        """Refresh the display of email recipients"""
        # Clear current display
        for widget in self.email_list_frame.winfo_children():
            widget.destroy()
        
        # Display each email with remove button
        if not self.email_recipients:
            no_emails_label = customtkinter.CTkLabel(
                master=self.email_list_frame,
                text="No recipients added yet",
                font=("Arial", 11),
                text_color="gray"
            )
            no_emails_label.pack(pady=10, fill="x")
        else:
            for email in self.email_recipients:
                email_frame = customtkinter.CTkFrame(master=self.email_list_frame)
                email_frame.pack(pady=3, padx=5, fill="x", expand=True)

                email_label = customtkinter.CTkLabel(
                    master=email_frame,
                    text=email,
                    font=("Arial", 11),
                    anchor="w"
                )
                email_label.pack(side="left", padx=10, fill="x", expand=True)
                
                remove_button = customtkinter.CTkButton(
                    master=email_frame,
                    text="❌",
                    command=lambda e=email: self.remove_email(e),
                    width=30,
                    height=25,
                    font=("Arial", 12),
                    fg_color="#dc3545"
                )
                remove_button.pack(side="right", padx=5)
        
    def start_search(self):
        """Start the search in a separate thread"""
        
        # Show loading status
        self.status_label.configure(text="Searching for Steam deals...")
        
        # Clear previous results
        self.clear_results()
        
        # Start search in separate thread to prevent UI freezing
        thread = threading.Thread(target=self.perform_search)
        thread.daemon = True
        thread.start()
    
    def perform_search(self):
        """Perform the actual search"""
        try:
            # Get featured deals with minimum discount from slider
            results = self.searcher.get_featured_deals(min_discount=self.min_discount)
            
            # Update UI in main thread
            self.root.after(0, self.display_results, results)
            
        except Exception as e:
            self.root.after(0, self.show_error, f"Search error: {str(e)}")
    
    def display_results(self, results):
        """Display search results in the UI"""
        self.search_results = results
        
        if not results:
            self.status_label.configure(text="No games found matching your criteria")
            no_results_label = customtkinter.CTkLabel(
                master=self.results_frame,
                text=f"No games found with {self.min_discount}%+ discount. Try lowering the discount percentage.",
                font=("Arial", 14)
            )
            no_results_label.pack(pady=20)
            return
        
        self.status_label.configure(text=f"Found {len(results)} games with {self.min_discount}%+ discount")
        
        # Display each game
        for i, game in enumerate(results):
            self.create_game_entry(game, i)
    
    def create_game_entry(self, game, index):
        """Create a UI entry for a single game"""
        # Game frame
        game_frame = customtkinter.CTkFrame(master=self.results_frame)
        game_frame.pack(pady=5, padx=10, fill="both", expand=True)

        # Game title
        title_label = customtkinter.CTkLabel(
            master=game_frame,
            text=game['title'],
            font=("Arial", 16, "bold"),
            anchor="w",
            wraplength=600
        )
        title_label.pack(pady=(10, 5), padx=15, anchor="w", fill="x")

        # Game info frame
        info_frame = customtkinter.CTkFrame(master=game_frame)
        info_frame.pack(pady=5, padx=15, fill="x", expand=True)

        # Discount percentage
        discount_label = customtkinter.CTkLabel(
            master=info_frame,
            text=f"🏷️ {game['discount']}% OFF",
            font=("Arial", 14, "bold"),
            text_color="red"
        )
        discount_label.pack(side="left", padx=(10, 20))
        
        # Prices
        if game['original_price'] != "N/A" and game['final_price'] != "N/A":
            price_text = f"💰 {game['original_price']} → {game['final_price']}"
        elif game['final_price'] != "N/A":
            price_text = f"💰 {game['final_price']}"
        else:
            price_text = "💰 Price available on Steam"
            
        price_label = customtkinter.CTkLabel(
            master=info_frame,
            text=price_text,
            font=("Arial", 12)
        )
        price_label.pack(side="left", padx=10, fill="x", expand=True)

        # Steam link button
        steam_button = customtkinter.CTkButton(
            master=game_frame,
            text="🎮 View on Steam",
            command=lambda url=game['url']: self.open_steam_link(url),
            width=150,
            height=35,
            font=("Arial", 12, "bold")
        )
        steam_button.pack(pady=10, padx=15, anchor="e")
    
    def open_steam_link(self, url):
        """Open Steam game page in web browser"""
        try:
            webbrowser.open(url)
            print(f"Opening Steam page: {url}")
        except Exception as e:
            print(f"Error opening Steam link: {e}")
    
    def clear_results(self):
        """Clear all result widgets"""
        for widget in self.results_frame.winfo_children():
            widget.destroy()
    
    def show_error(self, error_message):
        """Show an error message"""
        self.status_label.configure(text=error_message)
        
        error_label = customtkinter.CTkLabel(
            master=self.results_frame,
            text=f"Error: {error_message}",
            font=("Arial", 14),
            text_color="red"
        )
        error_label.pack(pady=20)
    
    def send_test_email(self):
        """Send a test email"""
        # Check if we have search results
        if not self.search_results:
            self.status_label.configure(text="⚠️ Please search for deals first before sending email")
            return
        
        # Show status
        self.status_label.configure(text="Sending email with game deals...")
        
        # Send email in separate thread
        thread = threading.Thread(target=self.perform_email_send)
        thread.daemon = True
        thread.start()
    
    def perform_email_send(self):
        """Perform the email sending"""
        try:
            # Check if we have recipients
            if not self.email_recipients:
                self.root.after(0, lambda: self.status_label.configure(text="⚠️ No email recipients added. Please add at least one email address."))
                self.root.after(0, lambda: self.search_send_button.configure(state="normal", text="🔍📧 Search & Send Email"))
                return
            
            # Get credentials
            sender_email = self.sender_email_entry.get().strip()
            sender_password = self.sender_password_entry.get().strip()
            
            # Validate credentials
            if not sender_email or not sender_password:
                self.root.after(0, lambda: self.status_label.configure(text="⚠️ Please enter sender email and password in the credentials section."))
                self.root.after(0, lambda: self.search_send_button.configure(state="normal", text="🔍📧 Search & Send Email"))
                return
            
            send_email(self.search_results, self.email_recipients, sender_email, sender_password)
            self.root.after(0, self.email_sent_success)
        except Exception as e:
            self.root.after(0, self.email_sent_error, str(e))
    
    def email_sent_success(self):
        """Update UI after successful email send"""
        self.status_label.configure(text=f"✅ Email sent with {len(self.search_results)} game deals!")
    
    def email_sent_error(self, error_msg):
        """Update UI after email send error"""
        self.search_send_button.configure(state="normal", text="🔍📧 Search & Send Email")
        self.status_label.configure(text=f"❌ Email error: {error_msg}")
    
    def search_and_send_email(self):
        """Search for deals and automatically send email when done"""
        # Check if we have recipients first
        if not self.email_recipients:
            self.status_label.configure(text="⚠️ Please add at least 1 email to the list. Search will continue but no email will be sent.")
        
        # Disable button
        self.search_send_button.configure(state="disabled", text="Searching...")
        if self.email_recipients:
            self.status_label.configure(text="Searching for Steam deals...")
        
        # Clear previous results
        self.clear_results()
        
        # Start search and send in separate thread
        thread = threading.Thread(target=self.perform_search_and_send)
        thread.daemon = True
        thread.start()
    
    def perform_search_and_send(self):
        """Perform search and then send email"""
        try:
            from datetime import datetime
            
            # Get featured deals with minimum discount from slider
            results = self.searcher.get_featured_deals(min_discount=self.min_discount)
            
            # Update UI in main thread
            self.root.after(0, self.display_results, results)
            
            # Wait a moment for UI to update
            import time
            time.sleep(0.5)
            
            # Send email if we have results
            if results:
                # Always filter and record the deals (even without email recipients)
                from SendEmail import send_email_and_get_count
                
                # Get credentials
                sender_email = self.sender_email_entry.get().strip()
                sender_password = self.sender_password_entry.get().strip()
                
                # Check if we have recipients
                if not self.email_recipients:
                    # No recipients - but still record the games under "No email search"
                    new_deals_count = send_email_and_get_count(results, [], sender_email, sender_password)
                    search_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self.root.after(0, lambda: self.status_label.configure(text=f"🔍 Search completed at {search_date} - Found {len(results)} games but no email sent (no recipients)."))
                    self.root.after(0, lambda: self.search_send_button.configure(state="normal", text="🔍📧 Search & Send Email"))
                    return
                
                # Validate credentials before sending
                if not sender_email or not sender_password:
                    self.root.after(0, lambda: self.status_label.configure(text="⚠️ Please enter sender email and password in the credentials section."))
                    self.root.after(0, lambda: self.search_send_button.configure(state="normal", text="🔍📧 Search & Send Email"))
                    return
                
                self.root.after(0, lambda: self.status_label.configure(text="Sending email with game deals..."))
                self.root.after(0, lambda: self.search_send_button.configure(text="Sending Email..."))
                
                # Send email - it will check for new deals internally and return the count
                new_deals_count = send_email_and_get_count(results, self.email_recipients, sender_email, sender_password)
                
                if new_deals_count > 0:
                    self.root.after(0, self.search_and_send_success, new_deals_count)
                else:
                    # No new deals found
                    search_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self.root.after(0, self.search_and_send_no_new_deals, search_date, len(results))
            else:
                self.root.after(0, self.search_and_send_no_results)
            
        except Exception as e:
            self.root.after(0, self.search_and_send_error, str(e))
    
    def search_and_send_success(self, num_games):
        """Update UI after successful search and send"""
        self.search_send_button.configure(state="normal", text="🔍📧 Search & Send Email")
        self.status_label.configure(text=f"✅ Found {num_games} new games and sent email successfully!")
    
    def search_and_send_no_results(self):
        """Update UI when no results found"""
        self.search_send_button.configure(state="normal", text="🔍📧 Search & Send Email")
        self.status_label.configure(text=f"⚠️ No games found with {self.min_discount}%+ discount. Email not sent.")
    
    def search_and_send_no_new_deals(self, search_date, total_games):
        """Update UI when search found games but no new deals"""
        self.search_send_button.configure(state="normal", text="🔍📧 Search & Send Email")
        self.status_label.configure(text=f"🔍 Search completed at {search_date} - Found {total_games} games but no new deals. Email not sent.")
    
    def search_and_send_error(self, error_msg):
        """Update UI after search and send error"""
        self.search_send_button.configure(state="normal", text="🔍📧 Search & Send Email")
        self.status_label.configure(text=f"❌ Error: {error_msg}")
    
    def toggle_schedule(self):
        """Toggle daily scheduled task on/off"""
        if self.is_scheduled_active:
            # Deactivate
            if self.scheduled_task:
                self.root.after_cancel(self.scheduled_task)
                self.scheduled_task = None
            
            self.is_scheduled_active = False
            self.schedule_toggle_button.configure(text="✅ Activate", fg_color="#28a745")
            self.schedule_status_label.configure(text="⏸️ Daily task deactivated", text_color="orange")
        else:
            # Activate
            try:
                hour = int(self.hour_entry.get())
                minute = int(self.minute_entry.get())
                
                if not (0 <= hour <= 23 and 0 <= minute <= 59):
                    self.schedule_status_label.configure(text="⚠️ Invalid time! Use 00-23 for hours, 00-59 for minutes", text_color="red")
                    return
                
                # Schedule first execution
                self.schedule_daily_task(hour, minute)
                
                self.is_scheduled_active = True
                self.schedule_toggle_button.configure(text="❌ Deactivate", fg_color="#dc3545")
                
            except ValueError:
                self.schedule_status_label.configure(text="⚠️ Please enter valid numbers for time", text_color="red")
    
    def schedule_daily_task(self, hour, minute):
        """Schedule the next daily task execution"""
        from datetime import datetime, timedelta
        now = datetime.now()
        scheduled_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        # If the time has passed today, schedule for tomorrow
        if scheduled_time <= now:
            scheduled_time += timedelta(days=1)
        
        time_diff = (scheduled_time - now).total_seconds()
        
        # Cancel any existing scheduled task
        if self.scheduled_task:
            self.root.after_cancel(self.scheduled_task)
        
        # Schedule the task
        self.scheduled_task = self.root.after(int(time_diff * 1000), lambda: self.execute_daily_task(hour, minute))
        
        # Update UI
        self.schedule_status_label.configure(
            text=f"🔄 Active - Next run: {scheduled_time.strftime('%Y-%m-%d %H:%M')}\n(Repeats daily)",
            text_color="green"
        )
    
    def execute_daily_task(self, hour, minute):
        """Execute the scheduled task and reschedule for next day"""
        self.schedule_status_label.configure(text="🔄 Executing daily task...", text_color="blue")
        
        # Execute search and send
        self.search_and_send_email()
        
        # Reschedule for tomorrow at the same time if still active
        if self.is_scheduled_active:
            self.schedule_daily_task(hour, minute)
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = SteamDealsUI()
    app.run()
