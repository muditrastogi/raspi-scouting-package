import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import configparser
import threading
from upload_data_to_s3 import upload_to_s3

class S3UploadUI:
    def __init__(self, root):
        self.root = root
        self.root.title("S3 Upload Manager")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Load configuration
        self.config = configparser.ConfigParser()
        self.load_config()
        
        # Variables
        self.local_dir = tk.StringVar()
        self.s3_bucket = tk.StringVar()
        self.s3_path = tk.StringVar()
        self.selected_subfolder = tk.StringVar()
        self.upload_progress = tk.StringVar(value="Ready to upload")
        
        # Set default values from config
        self.local_dir.set(self.config.get('S3', 'local_dir', fallback=''))
        self.s3_bucket.set(self.config.get('S3', 's3_bucket', fallback=''))
        self.s3_path.set(self.config.get('S3', 's3_path', fallback=''))
        
        self.setup_ui()
        self.refresh_subfolders()
        
    def load_config(self):
        """Load configuration from config.txt"""
        try:
            self.config.read('config.txt', encoding='utf-8')
            if not self.config.has_section('S3'):
                self.config.add_section('S3')
        except Exception as e:
            messagebox.showerror("Config Error", f"Error loading config.txt: {str(e)}")
    
    def save_config(self):
        """Save current settings to config.txt"""
        try:
            self.config.set('S3', 'local_dir', self.local_dir.get())
            self.config.set('S3', 's3_bucket', self.s3_bucket.get())
            self.config.set('S3', 's3_path', self.s3_path.get())
            
            with open('config.txt', 'w', encoding='utf-8') as configfile:
                self.config.write(configfile)
            messagebox.showinfo("Success", "Configuration saved successfully!")
        except Exception as e:
            messagebox.showerror("Save Error", f"Error saving config: {str(e)}")
    
    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="S3 Upload Manager", font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Local Directory Selection
        ttk.Label(main_frame, text="Local Directory:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.local_dir, width=50).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_local_dir).grid(row=1, column=2, pady=5)
        
        # S3 Bucket
        ttk.Label(main_frame, text="S3 Bucket:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.s3_bucket, width=50).grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        
        # S3 Path
        ttk.Label(main_frame, text="S3 Path:").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.s3_path, width=50).grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        
        # Subfolder Selection
        ttk.Label(main_frame, text="Select Subfolder:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.subfolder_combo = ttk.Combobox(main_frame, textvariable=self.selected_subfolder, width=47, state="readonly")
        self.subfolder_combo.grid(row=4, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        ttk.Button(main_frame, text="Refresh", command=self.refresh_subfolders).grid(row=4, column=2, pady=5)
        
        # Progress Label
        ttk.Label(main_frame, text="Status:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.progress_label = ttk.Label(main_frame, textvariable=self.upload_progress, foreground="blue")
        self.progress_label.grid(row=5, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        
        # Progress Bar
        self.progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress_bar.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Buttons Frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=7, column=0, columnspan=3, pady=20)
        
        # Upload Button
        self.upload_button = ttk.Button(buttons_frame, text="Upload to S3", command=self.start_upload, style="Accent.TButton")
        self.upload_button.pack(side=tk.LEFT, padx=5)
        
        # Save Config Button
        ttk.Button(buttons_frame, text="Save Config", command=self.save_config).pack(side=tk.LEFT, padx=5)
        
        # Test Connection Button
        ttk.Button(buttons_frame, text="Test Connection", command=self.test_connection).pack(side=tk.LEFT, padx=5)
        
        # Exit Button
        ttk.Button(buttons_frame, text="Exit", command=self.root.quit).pack(side=tk.LEFT, padx=5)
        
        # Configure style for accent button
        style = ttk.Style()
        style.configure("Accent.TButton", foreground="white", background="#0078d4")
    
    def browse_local_dir(self):
        """Browse for local directory"""
        directory = filedialog.askdirectory(title="Select Local Directory")
        if directory:
            self.local_dir.set(directory)
            self.refresh_subfolders()
    
    def refresh_subfolders(self):
        """Refresh the subfolder dropdown"""
        local_path = self.local_dir.get()
        if not local_path or not os.path.exists(local_path):
            self.subfolder_combo['values'] = []
            return
        
        try:
            subfolders = []
            for item in os.listdir(local_path):
                item_path = os.path.join(local_path, item)
                if os.path.isdir(item_path):
                    subfolders.append(item)
            
            subfolders.sort()
            self.subfolder_combo['values'] = subfolders
            
            if subfolders and not self.selected_subfolder.get():
                self.selected_subfolder.set(subfolders[0])
                
        except Exception as e:
            messagebox.showerror("Error", f"Error reading directory: {str(e)}")
    
    def test_connection(self):
        """Test S3 connection"""
        try:
            from upload_data_to_s3 import test_s3_connection
            if test_s3_connection():
                messagebox.showinfo("Success", "S3 connection test successful!")
            else:
                messagebox.showerror("Error", "S3 connection test failed!")
        except Exception as e:
            messagebox.showerror("Error", f"Connection test error: {str(e)}")
    
    def start_upload(self):
        """Start the upload process in a separate thread"""
        if not self.validate_inputs():
            return
        
        # Disable upload button and start progress bar
        self.upload_button.config(state='disabled')
        self.progress_bar.start()
        self.upload_progress.set("Starting upload...")
        
        # Start upload in separate thread
        upload_thread = threading.Thread(target=self.upload_worker)
        upload_thread.daemon = True
        upload_thread.start()
    
    def validate_inputs(self):
        """Validate user inputs"""
        if not self.local_dir.get():
            messagebox.showerror("Error", "Please select a local directory")
            return False
        
        if not self.s3_bucket.get():
            messagebox.showerror("Error", "Please enter S3 bucket name")
            return False
        
        if not self.selected_subfolder.get():
            messagebox.showerror("Error", "Please select a subfolder")
            return False
        
        local_path = os.path.join(self.local_dir.get(), self.selected_subfolder.get())
        if not os.path.exists(local_path):
            messagebox.showerror("Error", f"Selected subfolder does not exist: {local_path}")
            return False
        
        return True
    
    def upload_worker(self):
        """Worker function for upload process"""
        try:
            local_path = os.path.join(self.local_dir.get(), self.selected_subfolder.get())
            s3_uri = f"s3://{self.s3_bucket.get()}/{self.s3_path.get()}/{self.selected_subfolder.get()}/"
            
            self.root.after(0, lambda: self.upload_progress.set("Uploading files..."))
            
            # Call the upload function
            upload_to_s3(local_path, s3_uri)
            
            # Upload completed successfully
            self.root.after(0, lambda: self.upload_progress.set("Upload completed successfully!"))
            self.root.after(0, lambda: messagebox.showinfo("Success", "Upload completed successfully!"))
            
        except Exception as e:
            error_msg = f"Upload failed: {str(e)}"
            self.root.after(0, lambda: self.upload_progress.set(error_msg))
            self.root.after(0, lambda: messagebox.showerror("Upload Error", error_msg))
        
        finally:
            # Re-enable upload button and stop progress bar
            self.root.after(0, lambda: self.upload_button.config(state='normal'))
            self.root.after(0, lambda: self.progress_bar.stop())

def main():
    root = tk.Tk()
    app = S3UploadUI(root)
    
    # Center the window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()
