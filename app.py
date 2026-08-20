from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import csv
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
import os
import re
import requests
import webbrowser


class LeadGenUI:
    def __init__(self, root):
        self.root = root
        self.root.title("NexX Spark - Google Maps Lead Generator")
        self.root.geometry("1100x900")
        self.root.resizable(True, True)
        
        self.driver = None
        self.is_running = False
        self.results = []
        self.filtered_results = []
        
        self.create_ui()
        self.show_branding_popup()
    
    def create_ui(self):
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for responsiveness
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="🗺️ Google Maps Lead Generator", 
                                font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # === CREATE NOTEBOOK (TABS) ===
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Create three tabs
        self.tab1 = ttk.Frame(self.notebook, padding="10")
        self.tab2 = ttk.Frame(self.notebook, padding="10")
        self.tab3 = ttk.Frame(self.notebook, padding="10")
        
        self.notebook.add(self.tab1, text="🔍 Search & Scrape")
        self.notebook.add(self.tab2, text="🎯 Filter & Clean")
        self.notebook.add(self.tab3, text="📊 Results & Export")
        
        # Configure tab layouts
        self.tab1.columnconfigure(0, weight=1)
        self.tab2.columnconfigure(0, weight=1)
        self.tab3.columnconfigure(0, weight=1)
        self.tab2.rowconfigure(2, weight=1)
        self.tab3.rowconfigure(1, weight=1)
        
        # ==================== TAB 1: SEARCH & SCRAPE ====================
        self.create_search_tab()
        
        # ==================== TAB 2: FILTER & CLEAN ====================
        self.create_filter_tab()
        
        # ==================== TAB 3: RESULTS & EXPORT ====================
        self.create_results_tab()
        
        # === STATUS & PROGRESS (BOTTOM) ===
        status_frame = ttk.LabelFrame(main_frame, text="Status & Progress", padding="10")
        status_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        status_frame.columnconfigure(0, weight=1)
        
        self.status_label = ttk.Label(status_frame, text="Ready to start", foreground="green")
        self.status_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(status_frame, variable=self.progress_var, 
                                             maximum=100, mode='determinate')
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
    
    def create_search_tab(self):
        """Create the Search & Scrape tab content"""
        # === SEARCH CONFIGURATION SECTION ===
        config_frame = ttk.LabelFrame(self.tab1, text="Search Configuration", padding="10")
        config_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        config_frame.columnconfigure(1, weight=1)
        
        # Business Type / Category
        ttk.Label(config_frame, text="Business Type:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.business_type_var = tk.StringVar(value="cafe")
        business_combo = ttk.Combobox(config_frame, textvariable=self.business_type_var, 
                                       values=["cafe", "restaurant", "toystore", "hotel", 
                                              "gym", "salon", "pharmacy", "bakery", 
                                              "grocery", "custom"])
        business_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # Custom Business Type Entry
        ttk.Label(config_frame, text="Custom Type:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.custom_business_var = tk.StringVar()
        self.custom_entry = ttk.Entry(config_frame, textvariable=self.custom_business_var)
        self.custom_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # Location
        ttk.Label(config_frame, text="Location:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.location_var = tk.StringVar(value="Tamilnadu")
        location_entry = ttk.Entry(config_frame, textvariable=self.location_var)
        location_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # Max Scrolls - removed from UI, will auto-scroll to end
        self.max_scrolls_var = tk.IntVar(value=500)  # High limit, will stop when no new results
        
        # Headless Mode
        self.headless_var = tk.BooleanVar(value=False)
        headless_check = ttk.Checkbutton(config_frame, text="Run in headless mode (hidden browser)", 
                                          variable=self.headless_var)
        headless_check.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # === CSV CONFIGURATION SECTION ===
        csv_frame = ttk.LabelFrame(self.tab1, text="CSV Configuration & Headers", padding="10")
        csv_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        csv_frame.columnconfigure(1, weight=1)
        
        # Output Filename
        ttk.Label(csv_frame, text="Output Filename:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.filename_var = tk.StringVar(value="google_maps_data.csv")
        filename_entry = ttk.Entry(csv_frame, textvariable=self.filename_var)
        filename_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Button(csv_frame, text="Browse", command=self.browse_save_location).grid(row=0, column=2, padx=5)
        
        # Column Headers
        ttk.Label(csv_frame, text="CSV Columns:").grid(row=1, column=0, sticky=tk.W, pady=5)
        
        # Checkboxes for optional fields
        self.include_name_var = tk.BooleanVar(value=True)
        self.include_phone_var = tk.BooleanVar(value=True)
        self.include_website_var = tk.BooleanVar(value=True)
        self.include_address_var = tk.BooleanVar(value=True)
        self.include_rating_var = tk.BooleanVar(value=True)
        self.include_rating_count_var = tk.BooleanVar(value=True)
        self.include_hours_var = tk.BooleanVar(value=True)
        
        fields_frame = ttk.Frame(csv_frame)
        fields_frame.grid(row=1, column=1, sticky=tk.W, padx=5)
        
        ttk.Checkbutton(fields_frame, text="Name", variable=self.include_name_var).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(fields_frame, text="Phone", variable=self.include_phone_var).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(fields_frame, text="Website", variable=self.include_website_var).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(fields_frame, text="Address", variable=self.include_address_var).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(fields_frame, text="Rating", variable=self.include_rating_var).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(fields_frame, text="Rating Count", variable=self.include_rating_count_var).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(fields_frame, text="Hours", variable=self.include_hours_var).pack(side=tk.LEFT, padx=5)
        
        # === CONTROL BUTTONS ===
        button_frame = ttk.Frame(self.tab1)
        button_frame.grid(row=2, column=0, pady=15)
        
        self.start_button = ttk.Button(button_frame, text="▶ Start Scraping", 
                                        command=self.start_scraping, style="Accent.TButton")
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="⏹ Stop", 
                                       command=self.stop_scraping, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # === CONSOLE OUTPUT IN TAB 1 ===
        console_frame = ttk.LabelFrame(self.tab1, text="Console Output", padding="5")
        console_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        console_frame.columnconfigure(0, weight=1)
        console_frame.rowconfigure(0, weight=1)
        self.tab1.rowconfigure(3, weight=1)
        
        self.console_text = scrolledtext.ScrolledText(console_frame, height=12, wrap=tk.WORD)
        self.console_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    def create_filter_tab(self):
        """Create the Filter & Clean tab content"""
        # Info Label
        info_label = ttk.Label(self.tab2, text="🎯 Apply filters to clean your scraped data and keep only high-quality contactable leads", 
                              font=("Arial", 10), foreground="blue")
        info_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 15))
        
        # === DATA FILTER SECTION ===
        filter_frame = ttk.LabelFrame(self.tab2, text="🔍 Filter Options", padding="15")
        filter_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        filter_frame.columnconfigure(0, weight=1)
        
        # Filter checkboxes
        self.filter_no_phone_var = tk.BooleanVar(value=True)
        self.filter_no_website_var = tk.BooleanVar(value=False)
        self.filter_low_rating_var = tk.BooleanVar(value=False)
        self.filter_five_star_only_var = tk.BooleanVar(value=False)
        self.filter_whatsapp_only_var = tk.BooleanVar(value=False)
        self.min_rating_var = tk.DoubleVar(value=4.2)
        self.min_rating_count_var = tk.IntVar(value=10)
        
        ttk.Checkbutton(filter_frame, text="❌ Remove leads without phone number (mandatory)", 
                       variable=self.filter_no_phone_var).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        ttk.Checkbutton(filter_frame, text="🌐 Remove leads without website", 
                       variable=self.filter_no_website_var).grid(row=1, column=0, sticky=tk.W, pady=5)
        
        rating_frame = ttk.Frame(filter_frame)
        rating_frame.grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Checkbutton(rating_frame, text="⭐ Remove low rating (below ", 
                       variable=self.filter_low_rating_var).pack(side=tk.LEFT)
        ttk.Spinbox(rating_frame, from_=1.0, to=5.0, increment=0.1, 
                   textvariable=self.min_rating_var, width=5).pack(side=tk.LEFT, padx=2)
        ttk.Label(rating_frame, text=")").pack(side=tk.LEFT)
        
        five_star_frame = ttk.Frame(filter_frame)
        five_star_frame.grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Checkbutton(five_star_frame, text="🌟 Keep only 5-star ratings with min ", 
                       variable=self.filter_five_star_only_var).pack(side=tk.LEFT)
        ttk.Spinbox(five_star_frame, from_=1, to=1000, increment=1, 
                   textvariable=self.min_rating_count_var, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Label(five_star_frame, text=" reviews").pack(side=tk.LEFT)
        
        ttk.Checkbutton(filter_frame, text="📱 Keep only WhatsApp numbers", 
                       variable=self.filter_whatsapp_only_var).grid(row=4, column=0, sticky=tk.W, pady=5)
        
        # Filter buttons
        filter_button_frame = ttk.Frame(filter_frame)
        filter_button_frame.grid(row=5, column=0, pady=15)
        ttk.Button(filter_button_frame, text="✅ Apply Filters", 
                  command=self.apply_filters, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(filter_button_frame, text="🔄 Clear Filters", 
                  command=self.clear_filters, width=20).pack(side=tk.LEFT, padx=5)
        
        # Filter status
        self.filter_status_label = ttk.Label(self.tab2, text="", foreground="blue", font=("Arial", 10))
        self.filter_status_label.grid(row=2, column=0, sticky=tk.W, pady=10)
        
        # Next button
        next_button = ttk.Button(self.tab2, text="Next: View Results →", 
                                command=lambda: self.notebook.select(self.tab3), width=30)
        next_button.grid(row=3, column=0, pady=20)
    
    def create_results_tab(self):
        """Create the Results & Export tab content"""
        # Info Label
        info_label = ttk.Label(self.tab3, text="📊 View and export your filtered high-quality leads", 
                              font=("Arial", 10), foreground="blue")
        info_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        # === RESULTS TABLE ===
        results_frame = ttk.LabelFrame(self.tab3, text="📋 Filtered Results Preview", padding="5")
        results_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        # Treeview with scrollbars
        tree_scroll_y = ttk.Scrollbar(results_frame)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        tree_scroll_x = ttk.Scrollbar(results_frame, orient=tk.HORIZONTAL)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.results_tree = ttk.Treeview(results_frame, 
                                         yscrollcommand=tree_scroll_y.set,
                                         xscrollcommand=tree_scroll_x.set,
                                         show='headings', height=15)
        self.results_tree.pack(fill=tk.BOTH, expand=True)
        
        tree_scroll_y.config(command=self.results_tree.yview)
        tree_scroll_x.config(command=self.results_tree.xview)
        
        # Initialize with default columns
        self.results_tree['columns'] = ('Name', 'Phone', 'Website', 'Rating')
        for col in self.results_tree['columns']:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=150)
        
        # === EXPORT BUTTONS ===
        export_frame = ttk.Frame(self.tab3)
        export_frame.grid(row=2, column=0, pady=20)
        
        ttk.Button(export_frame, text="💾 Export Filtered CSV", 
                  command=self.export_results, width=25).pack(side=tk.LEFT, padx=5)
        ttk.Button(export_frame, text="🗑️ Clear All Results", 
                  command=self.clear_results, width=25).pack(side=tk.LEFT, padx=5)
        
    def browse_save_location(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=self.filename_var.get()
        )
        if filename:
            self.filename_var.set(filename)
    
    def log(self, message):
        self.console_text.insert(tk.END, message + "\n")
        self.console_text.see(tk.END)
        self.root.update_idletasks()
    
    def update_status(self, message, color="black"):
        self.status_label.config(text=message, foreground=color)
        self.root.update_idletasks()
    
    def is_whatsapp_number(self, phone):
        """Check if phone number is likely a WhatsApp number"""
        if not phone or phone == "NaN":
            return False
        # Remove common formatting
        cleaned = re.sub(r'[^\d+]', '', phone)
        # WhatsApp numbers typically have country code and 10+ digits
        # Indian numbers: +91 followed by 10 digits
        if len(cleaned) >= 10:
            return True
        return False
    
    def parse_rating(self, rating_str):
        """Extract numeric rating from string"""
        if not rating_str or rating_str == "NaN":
            return None
        try:
            # Extract first number from string (e.g., "4.5" from "4.5 stars")
            match = re.search(r'(\d+\.?\d*)', str(rating_str))
            if match:
                return float(match.group(1))
        except:
            pass
        return None
    
    def parse_rating_count(self, count_str):
        """Extract numeric rating count from string"""
        if not count_str or count_str == "NaN":
            return None
        try:
            # Extract number from strings like "(123)" or "123 reviews"
            cleaned = re.sub(r'[^\d]', '', str(count_str))
            if cleaned:
                return int(cleaned)
        except:
            pass
        return None
    
    def apply_filters(self):
        """Apply filters to scraped results"""
        if not self.results:
            messagebox.showwarning("No Data", "Please scrape data first before applying filters.")
            return
        
        self.filtered_results = []
        removed_count = {'no_phone': 0, 'no_website': 0, 'low_rating': 0, 'not_five_star': 0, 'no_whatsapp': 0}
        
        for lead in self.results:
            # Filter: No phone number (mandatory if checked)
            if self.filter_no_phone_var.get():
                phone = lead.get('Phone', 'NaN')
                if not phone or phone == 'NaN' or phone.strip() == '':
                    removed_count['no_phone'] += 1
                    continue
            
            # Filter: No website
            if self.filter_no_website_var.get():
                website = lead.get('Website', 'NaN')
                if not website or website == 'NaN' or website.strip() == '':
                    removed_count['no_website'] += 1
                    continue
            
            # Filter: Low rating
            if self.filter_low_rating_var.get() and 'Rating' in lead:
                rating = self.parse_rating(lead.get('Rating'))
                min_rating = self.min_rating_var.get()
                if rating is None or rating < min_rating:
                    removed_count['low_rating'] += 1
                    continue
            
            # Filter: Only 5-star ratings with minimum review count
            if self.filter_five_star_only_var.get():
                rating = self.parse_rating(lead.get('Rating'))
                rating_count = self.parse_rating_count(lead.get('Rating Count', '0'))
                min_count = self.min_rating_count_var.get()
                
                if rating != 5.0 or rating_count is None or rating_count < min_count:
                    removed_count['not_five_star'] += 1
                    continue
            
            # Filter: WhatsApp only
            if self.filter_whatsapp_only_var.get():
                phone = lead.get('Phone', '')
                if not self.is_whatsapp_number(phone):
                    removed_count['no_whatsapp'] += 1
                    continue
            
            # Lead passed all filters
            self.filtered_results.append(lead)
        
        # Update UI
        self.update_results_table()
        
        # Show filter summary
        total = len(self.results)
        kept = len(self.filtered_results)
        removed = total - kept
        
        summary = f"✅ Filtered: {kept}/{total} leads kept"
        if removed > 0:
            details = []
            if removed_count['no_phone'] > 0:
                details.append(f"❌ {removed_count['no_phone']} no phone")
            if removed_count['no_website'] > 0:
                details.append(f"🌐 {removed_count['no_website']} no website")
            if removed_count['low_rating'] > 0:
                details.append(f"⭐ {removed_count['low_rating']} low rating")
            if removed_count['not_five_star'] > 0:
                details.append(f"🌟 {removed_count['not_five_star']} not 5-star")
            if removed_count['no_whatsapp'] > 0:
                details.append(f"📱 {removed_count['no_whatsapp']} no WhatsApp")
            summary += f" | Removed: {', '.join(details)}"
        
        self.filter_status_label.config(text=summary)
        self.log(f"\n{summary}")
        
        # Switch to results tab to view filtered data
        self.notebook.select(self.tab3)
    
    def clear_filters(self):
        """Clear all filters and show all results"""
        self.filtered_results = self.results.copy()
        self.update_results_table()
        self.filter_status_label.config(text=f"Showing all {len(self.results)} results")
    
    def update_results_table(self):
        """Update the results treeview with filtered data"""
        # Clear existing data
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        if not self.filtered_results:
            return
        
        # Get columns from first result
        columns = list(self.filtered_results[0].keys())
        self.results_tree['columns'] = columns
        
        for col in columns:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=150)
        
        # Add data
        for lead in self.filtered_results:
            values = [lead.get(col, 'N/A') for col in columns]
            self.results_tree.insert('', tk.END, values=values)
    
    def start_scraping(self):
        # Validate inputs
        business_type = self.business_type_var.get()
        if business_type == "custom":
            business_type = self.custom_business_var.get().strip()
            if not business_type:
                messagebox.showerror("Error", "Please enter a custom business type")
                return
        
        location = self.location_var.get().strip()
        if not location:
            messagebox.showerror("Error", "Please enter a location")
            return
        
        # Check if at least one field is selected
        if not any([self.include_name_var.get(), self.include_phone_var.get(), 
                   self.include_website_var.get(), self.include_address_var.get(), 
                   self.include_rating_var.get(), self.include_rating_count_var.get(),
                   self.include_hours_var.get()]):
            messagebox.showerror("Error", "Please select at least one CSV column")
            return
        
        # Disable start button, enable stop button
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.is_running = True
        self.results = []
        
        # Start scraping in a separate thread
        thread = threading.Thread(target=self.scrape_leads, daemon=True)
        thread.start()
    
    def stop_scraping(self):
        self.is_running = False
        self.update_status("Stopping...", "orange")
        self.log("⏹ Stop requested by user")
        
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
        
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
    
    def scrape_leads(self):
        try:
            # Build search query
            business_type = self.business_type_var.get()
            if business_type == "custom":
                business_type = self.custom_business_var.get().strip()
            
            location = self.location_var.get().strip()
            search_query = f"{business_type} in {location}"
            
            self.log(f"🔍 Starting search: {search_query}")
            self.update_status(f"Initializing browser...", "blue")
            
            # Setup WebDriver
            chrome_options = Options()
            if self.headless_var.get():
                chrome_options.add_argument("--headless")
                chrome_options.add_argument("--disable-gpu")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            
            # Google Maps search
            search_url = f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}"
            self.driver.get(search_url)
            
            if not self.is_running:
                return
            
            self.log(f"📍 Loaded Google Maps, waiting for results...")
            self.update_status("Waiting for page to load...", "blue")
            
            # Give page more time to load initially
            time.sleep(5)
            
            # Try multiple strategies to find the scrollable feed
            scrollable_div = None
            wait = WebDriverWait(self.driver, 30)
            
            selectors = [
                (By.XPATH, '//div[@role="feed"]', "XPath role=feed"),
                (By.CSS_SELECTOR, 'div[role="feed"]', "CSS role=feed"),
                (By.CSS_SELECTOR, 'div.m6QErb.DxyBCb.kA9KIf.dS8AEf', "CSS specific class"),
                (By.XPATH, '//div[contains(@class, "m6QErb")]', "XPath class contains"),
                (By.CSS_SELECTOR, '[aria-label*="Results"]', "CSS aria-label Results"),
            ]
            
            for selector_type, selector_value, selector_name in selectors:
                if scrollable_div:
                    break
                try:
                    self.log(f"🔍 Trying {selector_name}...")
                    scrollable_div = wait.until(
                        EC.presence_of_element_located((selector_type, selector_value))
                    )
                    self.log(f"✅ Results panel found using {selector_name}")
                    break
                except TimeoutException:
                    self.log(f"⚠️ {selector_name} failed, trying next...")
                    continue
            
            if not scrollable_div:
                # Last resort: check if there are any results at all
                try:
                    self.log(f"🔍 Checking if any stores visible...")
                    stores_check = self.driver.find_elements(By.CSS_SELECTOR, 'a.hfpxzc')
                    if stores_check:
                        self.log(f"⚠️ Found {len(stores_check)} stores but couldn't find scrollable panel")
                        self.log(f"ℹ️ Will attempt to scrape visible results without scrolling")
                        # Create a dummy scrollable div (won't scroll but won't crash)
                        scrollable_div = self.driver.find_element(By.TAG_NAME, 'body')
                    else:
                        raise Exception(f"No results found for '{search_query}'. Try a different search term or location.")
                except:
                    raise Exception(f"Could not find results panel. Try:\n1. Different search query (use categories like 'cafe' not specific names)\n2. Check if location '{location}' is valid\n3. Try with browser visible (uncheck headless mode)")
            
            time.sleep(3)  # Additional wait for content to stabilize
            
            if not self.is_running:
                return
            
            self.update_status("Scrolling to load results...", "blue")
            
            prev_count = 0
            no_change_count = 0  # Track consecutive scrolls with no new results
            scroll_number = 0
            max_scrolls = self.max_scrolls_var.get()  # Safety limit
            
            while scroll_number < max_scrolls:
                if not self.is_running:
                    return
                
                try:
                    self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
                    time.sleep(2)
                    
                    stores = self.driver.find_elements(By.CSS_SELECTOR, 'a.hfpxzc')
                    current_count = len(stores)
                    
                    scroll_number += 1
                    progress = min((scroll_number / 100) * 30, 30)  # 30% of progress for scrolling
                    self.progress_var.set(progress)
                    self.log(f"Scroll {scroll_number}: {current_count} stores loaded")
                    
                    # Check if no new results loaded
                    if current_count == prev_count:
                        no_change_count += 1
                        if no_change_count >= 3:  # No new results for 3 consecutive scrolls
                            self.log("✅ All results loaded (reached end)")
                            break
                    else:
                        no_change_count = 0  # Reset counter when new results appear
                    
                    prev_count = current_count
                except Exception as e:
                    self.log(f"⚠️ Scroll {scroll_number} warning: {str(e)}")
                    continue
            
            if not self.is_running:
                return
            
            # Collect store links
            store_links = []
            
            # Try multiple selectors for store links
            stores = self.driver.find_elements(By.CSS_SELECTOR, 'a.hfpxzc')
            if not stores:
                self.log(f"⚠️ Primary selector found no stores, trying alternatives...")
                stores = self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="/maps/place/"]')
            
            if not stores:
                raise Exception(f"No stores found for '{search_query}'.\nTry:\n• Use business categories (cafe, restaurant) instead of specific names\n• Check spelling of location\n• Increase Max Scrolls\n• Try without headless mode")
            
            for s in stores:
                try:
                    href = s.get_attribute("href")
                    if href and href not in store_links:
                        store_links.append(href)
                except:
                    continue
            
            total_stores = len(store_links)
            
            if total_stores == 0:
                raise Exception("No valid store links found. The page structure may have changed.")
            
            self.log(f"\n🟢 Total stores found: {total_stores}")
            self.update_status(f"Extracting details from {total_stores} stores...", "blue")
            
            # Extract details from each store
            for index, link in enumerate(store_links):
                if not self.is_running:
                    return
                
                # Check if driver session is still alive
                try:
                    _ = self.driver.title  # Test if session is valid
                except:
                    self.log(f"⚠️ Browser session lost at store {index+1}. Stopping extraction...")
                    self.log(f"✅ Successfully scraped {len(self.results)} stores before session ended")
                    break
                
                try:
                    self.driver.get(link)
                    # Wait for page to load
                    wait = WebDriverWait(self.driver, 15)
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1.DUwDvf')))
                    time.sleep(1.5)  # Additional stabilization time
                except TimeoutException:
                    self.log(f"⚠️ Timeout loading store {index+1}, skipping...")
                    continue
                except Exception as e:
                    error_msg = str(e)
                    if "invalid session" in error_msg.lower() or "session" in error_msg.lower():
                        self.log(f"⚠️ Browser session crashed at store {index+1}. Saving progress...")
                        self.log(f"✅ Successfully scraped {len(self.results)} stores before crash")
                        break
                    self.log(f"⚠️ Error loading store {index+1}: {error_msg}")
                    continue
                
                store_data = {}
                
                # Name
                if self.include_name_var.get():
                    try:
                        name = self.driver.find_element(By.CSS_SELECTOR, 'h1.DUwDvf').text.strip()
                        store_data['Name'] = name
                    except:
                        store_data['Name'] = "NaN"
                
                # Phone
                if self.include_phone_var.get():
                    try:
                        phone_btn = self.driver.find_element(By.XPATH, '//button[contains(@aria-label, "Phone")]')
                        phone = phone_btn.get_attribute('aria-label').replace("Phone: ", "").strip()
                        store_data['Phone'] = phone
                    except:
                        store_data['Phone'] = "NaN"
                
                # Website
                if self.include_website_var.get():
                    try:
                        website = self.driver.find_element(By.XPATH, '//a[contains(@aria-label, "Website")]').get_attribute("href").strip()
                        store_data['Website'] = website
                    except:
                        store_data['Website'] = "NaN"
                
                # Address
                if self.include_address_var.get():
                    try:
                        address = self.driver.find_element(By.CSS_SELECTOR, 'button[data-item-id="address"]').get_attribute('aria-label').replace("Address: ", "").strip()
                        store_data['Address'] = address
                    except:
                        store_data['Address'] = "NaN"
                
                # Rating
                if self.include_rating_var.get():
                    try:
                        rating = self.driver.find_element(By.CSS_SELECTOR, 'div.F7nice span[aria-hidden="true"]').text.strip()
                        store_data['Rating'] = rating
                    except:
                        store_data['Rating'] = "NaN"
                
                # Rating Count
                if self.include_rating_count_var.get():
                    try:
                        # Try to find rating count - usually appears next to rating
                        rating_count = self.driver.find_element(By.CSS_SELECTOR, 'div.F7nice span[aria-label*="reviews"]').get_attribute('aria-label')
                        # Extract just the number from text like "123 reviews"
                        count_match = re.search(r'([\d,]+)', rating_count)
                        if count_match:
                            store_data['Rating Count'] = count_match.group(1).replace(',', '')
                        else:
                            store_data['Rating Count'] = "NaN"
                    except:
                        # Alternative selector for rating count
                        try:
                            rating_text = self.driver.find_element(By.CSS_SELECTOR, 'div.F7nice').text
                            # Extract number in parentheses like "4.5 (123)"
                            count_match = re.search(r'\(([\d,]+)\)', rating_text)
                            if count_match:
                                store_data['Rating Count'] = count_match.group(1).replace(',', '')
                            else:
                                store_data['Rating Count'] = "NaN"
                        except:
                            store_data['Rating Count'] = "NaN"
                
                # Hours (Open/Close Time)
                if self.include_hours_var.get():
                    try:
                        # Try to find hours button or text
                        hours_button = self.driver.find_element(By.CSS_SELECTOR, 'button[data-item-id*="oh"]')
                        hours_aria = hours_button.get_attribute('aria-label')
                        store_data['Hours'] = hours_aria
                    except:
                        try:
                            # Alternative: look for hours in text
                            hours_elem = self.driver.find_element(By.XPATH, '//div[contains(@class, "ZDu9vd")]//span[contains(text(), "Open") or contains(text(), "Closed") or contains(text(), ":")]')
                            store_data['Hours'] = hours_elem.text.strip()
                        except:
                            store_data['Hours'] = "NaN"
                
                self.results.append(store_data)
                
                # Update progress
                progress = 30 + ((index + 1) / total_stores * 70)  # 70% for extraction
                self.progress_var.set(progress)
                
                display_text = " | ".join([f"{k}: {v}" for k, v in store_data.items()])
                self.log(f"{index+1}/{total_stores}. {display_text}")
            
            # Auto-save all results (unfiltered)
            if self.results:
                self.save_to_csv()
            else:
                self.log(f"⚠️ No results to save")
                self.update_status("No results extracted", "orange")
                return
            
            # Auto-apply default filters and show in table
            self.filtered_results = self.results.copy()
            self.apply_filters()
            
            scraped_count = len(self.results)
            self.update_status(f"✅ Completed! {scraped_count} leads extracted", "green")
            self.log(f"\n✅ Scraping completed successfully!")
            self.log(f"📊 Total leads extracted: {scraped_count}/{total_stores}")
            self.log(f"💡 Switch to 'Filter & Clean' tab to refine your leads!")
            
            # Switch to filter tab
            self.notebook.select(self.tab2)
            
            messagebox.showinfo("Success", 
                              f"Successfully scraped {scraped_count} leads!\n"
                              f"(Out of {total_stores} stores found)\n\n"
                              f"➡️ Now go to 'Filter & Clean' tab to find contactable leads.")
            
        except Exception as e:
            self.log(f"❌ Error: {str(e)}")
            self.update_status(f"Error: {str(e)}", "red")
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
        
        finally:
            if self.driver:
                self.driver.quit()
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.is_running = False
    
    def save_to_csv(self):
        if not self.results:
            return
        
        filename = self.filename_var.get()
        
        try:
            # Get headers from selected fields
            headers = []
            if self.include_name_var.get():
                headers.append('Name')
            if self.include_phone_var.get():
                headers.append('Phone')
            if self.include_website_var.get():
                headers.append('Website')
            if self.include_address_var.get():
                headers.append('Address')
            if self.include_rating_var.get():
                headers.append('Rating')
            if self.include_rating_count_var.get():
                headers.append('Rating Count')
            if self.include_hours_var.get():
                headers.append('Hours')
            
            with open(filename, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                for row in self.results:
                    writer.writerow(row)
            
            self.log(f"💾 Data saved to {filename}")
        except Exception as e:
            self.log(f"❌ Error saving CSV: {str(e)}")
            messagebox.showerror("Error", f"Failed to save CSV:\n{str(e)}")
    
    def export_results(self):
        """Export filtered results to CSV"""
        if not self.results:
            messagebox.showwarning("No Data", "No results to export. Please run the scraper first.")
            return
        
        # Ask which data to export
        export_choice = messagebox.askyesno(
            "Export Data", 
            f"Export FILTERED results ({len(self.filtered_results)} leads)?\n\n"
            f"Click 'Yes' to export filtered results\n"
            f"Click 'No' to export all {len(self.results)} unfiltered results"
        )
        
        data_to_export = self.filtered_results if export_choice else self.results
        
        if not data_to_export:
            messagebox.showwarning("No Data", "No data to export. Apply filters first or scrape new data.")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"filtered_leads_{len(data_to_export)}.csv"
        )
        
        if filename:
            try:
                headers = list(data_to_export[0].keys())
                with open(filename, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=headers)
                    writer.writeheader()
                    for row in data_to_export:
                        writer.writerow(row)
                
                self.log(f"💾 Exported {len(data_to_export)} leads to {filename}")
                messagebox.showinfo("Success", f"Exported {len(data_to_export)} leads to:\n{filename}")
            except Exception as e:
                self.log(f"❌ Error exporting: {str(e)}")
                messagebox.showerror("Error", f"Failed to export:\n{str(e)}")
    
    def clear_results(self):
        if messagebox.askyesno("Confirm", "Clear all results and console output?"):
            self.results = []
            self.filtered_results = []
            self.console_text.delete(1.0, tk.END)
            self.progress_var.set(0)
            self.update_status("Ready to start", "green")
            self.filter_status_label.config(text="")
            self.update_results_table()
            self.log("🗑️ Results cleared")
    
    def show_branding_popup(self):
        """Display branding popup when application opens"""
        popup = tk.Toplevel(self.root)
        popup.title("About - NexX Spark")
        popup.geometry("420x260")
        popup.resizable(False, False)
        
        # Center the popup
        popup.transient(self.root)
        popup.grab_set()
        
        # Main frame
        frame = ttk.Frame(popup, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Branding text
        title_label = ttk.Label(frame, text="Powered by", 
                                font=("Arial", 11))
        title_label.pack(pady=(5, 2))
        
        company_label = ttk.Label(frame, text="NexX Spark", 
                                  font=("Arial", 16, "bold"),
                                  foreground="#0066cc")
        company_label.pack(pady=4)
        
        # Website link
        website_label = ttk.Label(frame, text="🌐 www.nexxspark.com", 
                                  font=("Arial", 10, "underline"),
                                  foreground="#0066cc",
                                  cursor="hand2")
        website_label.pack(pady=4)
        
        # Make website clickable
        def open_website(e=None):
            webbrowser.open("https://nexxspark.com")
        
        website_label.bind("<Button-1>", open_website)
        
        # WhatsApp contact link (Message Only)
        whatsapp_label = ttk.Label(frame, text="💬 WhatsApp: +91 9363582044 (Only Msg)", 
                                   font=("Arial", 10, "underline"),
                                   foreground="#128C7E",
                                   cursor="hand2")
        whatsapp_label.pack(pady=6)
        
        # Make WhatsApp clickable
        def open_whatsapp(e=None):
            webbrowser.open("https://wa.me/919363582044?text=Hello%20NexX%20Spark")
        
        whatsapp_label.bind("<Button-1>", open_whatsapp)
        
        # Close button
        close_btn = ttk.Button(frame, text="Continue", 
                               command=popup.destroy)
        close_btn.pack(pady=(15, 5))
        
        # Center popup on screen
        popup.update_idletasks()
        x = (popup.winfo_screenwidth() // 2) - (popup.winfo_width() // 2)
        y = (popup.winfo_screenheight() // 2) - (popup.winfo_height() // 2)
        popup.geometry(f"+{x}+{y}")


def main():
    root = tk.Tk()
    app = LeadGenUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
