#!/usr/bin/env python3
"""
SnapZone - Automated Screenshot Tool with GUI and System Tray
Captures screenshots of a selected screen region at specified intervals.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time
import os
from datetime import datetime
from PIL import Image, ImageGrab, ImageTk
from plyer import notification
from typing import Tuple, Optional, Dict, Any
import sys
import pystray
from pystray import MenuItem as item


class SnapZoneGUI:
    """GUI Application for SnapZone screenshot tool."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.is_running = False
        self.is_paused = False
        self.screenshot_thread = None
        self.tray_icon = None
        self.capture_box = None
        self.total_screenshots = 0
        self.session_start_time = None
        
        self.setup_gui()
        self.create_tray_icon()
        
    def setup_gui(self):
        """Setup the main GUI window."""
        self.root.title("SnapZone - Screenshot Tool")
        self.root.geometry("500x600")
        self.root.resizable(True, True)
        
        # Handle window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="SnapZone", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Duration settings
        ttk.Label(main_frame, text="Duration (seconds):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.duration_var = tk.StringVar(value="60")
        duration_frame = ttk.Frame(main_frame)
        duration_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        ttk.Entry(duration_frame, textvariable=self.duration_var, width=10).pack(side=tk.LEFT)
        ttk.Label(duration_frame, text="(0 = unlimited)").pack(side=tk.LEFT, padx=(5, 0))
        
        # Interval settings
        ttk.Label(main_frame, text="Interval (seconds):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.interval_var = tk.StringVar(value="5")
        ttk.Entry(main_frame, textvariable=self.interval_var, width=10).grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # Save directory
        ttk.Label(main_frame, text="Save Directory:").grid(row=3, column=0, sticky=tk.W, pady=5)
        dir_frame = ttk.Frame(main_frame)
        dir_frame.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)
        dir_frame.columnconfigure(0, weight=1)
        self.save_dir_var = tk.StringVar(value=os.path.expanduser("~/Desktop"))
        ttk.Entry(dir_frame, textvariable=self.save_dir_var).grid(row=0, column=0, sticky=(tk.W, tk.E))
        ttk.Button(dir_frame, text="Browse", command=self.browse_directory).grid(row=0, column=1, padx=(5, 0))
        
        # Capture region
        ttk.Label(main_frame, text="Capture Region:").grid(row=4, column=0, sticky=tk.W, pady=5)
        region_frame = ttk.Frame(main_frame)
        region_frame.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5)
        self.region_label = ttk.Label(region_frame, text="Not selected", foreground="red")
        self.region_label.pack(side=tk.LEFT)
        ttk.Button(region_frame, text="Select Region", command=self.select_region).pack(side=tk.RIGHT)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        self.start_button = ttk.Button(button_frame, text="Start Capture", command=self.start_capture)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.pause_button = ttk.Button(button_frame, text="Pause", command=self.toggle_pause, state=tk.DISABLED)
        self.pause_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_capture, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # Status section
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(20, 0))
        status_frame.columnconfigure(1, weight=1)
        
        ttk.Label(status_frame, text="Status:").grid(row=0, column=0, sticky=tk.W)
        self.status_label = ttk.Label(status_frame, text="Ready", foreground="green")
        self.status_label.grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(status_frame, text="Screenshots taken:").grid(row=1, column=0, sticky=tk.W)
        self.count_label = ttk.Label(status_frame, text="0")
        self.count_label.grid(row=1, column=1, sticky=tk.W)
        
        ttk.Label(status_frame, text="Time running:").grid(row=2, column=0, sticky=tk.W)
        self.time_label = ttk.Label(status_frame, text="00:00:00")
        self.time_label.grid(row=2, column=1, sticky=tk.W)
        
        # Log section
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding="10")
        log_frame.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(7, weight=1)
        
        # Text widget with scrollbar
        text_frame = ttk.Frame(log_frame)
        text_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        self.log_text = tk.Text(text_frame, height=8, wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.log_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.log_text.configure(yscrollcommand=scrollbar.set)

        
        self.log_message("SnapZone initialized and ready.")
        
    def create_tray_icon(self):
        """Create system tray icon."""
        # Create a simple icon using PIL
        icon_image = Image.new('RGB', (64, 64), color='blue')
        
        # Create menu for tray icon
        menu = pystray.Menu(
            item('Show SnapZone', self.show_window),
            item('Start Capture', self.start_capture, enabled=lambda item: not self.is_running),
            item('Stop Capture', self.stop_capture, enabled=lambda item: self.is_running),
            pystray.Menu.SEPARATOR,
            item('Exit', self.quit_application)
        )
        
        self.tray_icon = pystray.Icon("SnapZone", icon_image, "SnapZone Screenshot Tool", menu)
    
    def show_window(self, icon=None, item=None):
        """Show the main window."""
        self.root.after(0, self._show_window_safe)
    
    def _show_window_safe(self):
        """Thread-safe window show."""
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
    
    def hide_to_tray(self):
        """Hide window to system tray."""
        self.root.withdraw()
        if not hasattr(self, '_tray_started'):
            threading.Thread(target=self.tray_icon.run, daemon=True).start()
            self._tray_started = True
        
    def on_closing(self):
        """Handle window close event (always quit)."""
        self.quit_application()
    
    def quit_application(self, icon=None, item=None):
        """Quit the entire application."""
        self.is_running = False
        if self.tray_icon:
            self.tray_icon.stop()
        self.root.quit()
        self.root.destroy()
        
    def log_message(self, message):
        """Add message to log with timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.root.after(0, lambda: self._append_to_log(log_entry))
    
    def _append_to_log(self, message):
        """Thread-safe log append."""
        self.log_text.insert(tk.END, message)
        self.log_text.see(tk.END)
        
    def browse_directory(self):
        """Browse for save directory."""
        directory = filedialog.askdirectory(initialdir=self.save_dir_var.get())
        if directory:
            self.save_dir_var.set(directory)
    
    def select_region(self):
        """Select screen region for capture."""
        self.log_message("Click and drag to select capture region. Press ESC to cancel.")
        self.root.withdraw()  # Hide main window during selection
        
        try:
            region = self.get_capture_region()
            if region:
                self.capture_box = region
                self.region_label.config(text=f"{region[2]-region[0]}x{region[3]-region[1]} px", foreground="green")
                self.log_message(f"Capture region selected: {region}")
            else:
                self.log_message("Region selection cancelled.")
        finally:
            self.root.deiconify()  # Show main window again
    
    def get_capture_region(self) -> Optional[Tuple[int, int, int, int]]:
        """Allow user to select screen region for capture with a visible colored border."""
        region = {}
        selection_cancelled = False
        rect_id = None
        start_x, start_y = 0, 0

        SELECTION_COLOR = "lime"   # Bright and visible color
        BORDER_WIDTH = 3

        def on_mouse_down(event):
            nonlocal start_x, start_y, rect_id
            start_x, start_y = event.x, event.y
            rect_id = canvas.create_rectangle(
                start_x, start_y, start_x, start_y,
                outline=SELECTION_COLOR, width=BORDER_WIDTH
            )

        def on_mouse_drag(event):
            if rect_id:
                canvas.coords(rect_id, start_x, start_y, event.x, event.y)

        def on_mouse_up(event):
            region['x1'] = overlay.winfo_rootx() + start_x
            region['y1'] = overlay.winfo_rooty() + start_y
            region['x2'] = overlay.winfo_rootx() + event.x
            region['y2'] = overlay.winfo_rooty() + event.y
            overlay.quit()

        def on_key_press(event):
            nonlocal selection_cancelled
            if event.keysym == 'Escape':
                selection_cancelled = True
                overlay.quit()

        try:
            overlay = tk.Tk()
            overlay.attributes("-fullscreen", True)
            overlay.attributes("-topmost", True)
            overlay.overrideredirect(True)  # Removes window border/title bar

            # Use transparent background via Windows trick
            overlay.configure(bg='black')
            overlay.attributes('-alpha', 0.3)  # Slight transparency for canvas, rectangle remains visible

            canvas = tk.Canvas(
                overlay, bg='black', cursor='crosshair',
                highlightthickness=0
            )
            canvas.pack(fill=tk.BOTH, expand=True)

            canvas.bind("<ButtonPress-1>", on_mouse_down)
            canvas.bind("<B1-Motion>", on_mouse_drag)
            canvas.bind("<ButtonRelease-1>", on_mouse_up)
            overlay.bind("<KeyPress>", on_key_press)

            overlay.focus_force()
            overlay.mainloop()

            overlay.destroy()

            if selection_cancelled or len(region) < 4:
                return None

            x1, y1 = region['x1'], region['y1']
            x2, y2 = region['x2'], region['y2']

            if abs(x2 - x1) < 10 or abs(y2 - y1) < 10:
                messagebox.showwarning("Selection Too Small", "Please select a larger area (minimum 10x10 pixels).")
                return None

            return (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))

        except Exception as e:
            self.log_message(f"Error during region selection: {str(e)}")
            return None


    
    def validate_inputs(self) -> bool:
        """Validate user inputs."""
        try:
            duration = int(self.duration_var.get())
            interval = int(self.interval_var.get())
            save_dir = self.save_dir_var.get()
            
            if duration < 0:
                messagebox.showerror("Invalid Input", "Duration cannot be negative.")
                return False
            
            if interval <= 0:
                messagebox.showerror("Invalid Input", "Interval must be positive.")
                return False
                
            if not os.path.exists(save_dir) or not os.access(save_dir, os.W_OK):
                messagebox.showerror("Invalid Directory", f"Cannot write to directory: {save_dir}")
                return False
            
            if not self.capture_box:
                messagebox.showerror("No Region Selected", "Please select a capture region first.")
                return False
                
            return True
            
        except ValueError:
            messagebox.showerror("Invalid Input", "Duration and interval must be numbers.")
            return False
    
    def start_capture(self, icon=None, item=None):
        """Start the screenshot capture process."""
        if not self.validate_inputs():
            return
            
        self.is_running = True
        self.is_paused = False
        self.total_screenshots = 0
        self.session_start_time = time.time()
        
        # Update UI
        self.start_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.NORMAL)
        self.status_label.config(text="Running", foreground="blue")
        
        duration = int(self.duration_var.get())
        interval = int(self.interval_var.get())
        save_dir = self.save_dir_var.get()
        
        self.log_message(f"Starting capture: Duration={duration}s, Interval={interval}s")
        
        # Start screenshot thread
        self.screenshot_thread = threading.Thread(
            target=self.take_screenshots,
            args=(duration, interval, save_dir, self.capture_box),
            daemon=True
        )
        self.screenshot_thread.start()
        
        # Start status update timer
        self.update_status()
    
    def toggle_pause(self):
        """Toggle pause/resume."""
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.pause_button.config(text="Resume")
            self.status_label.config(text="Paused", foreground="orange")
            self.log_message("Capture paused.")
        else:
            self.pause_button.config(text="Pause")
            self.status_label.config(text="Running", foreground="blue")
            self.log_message("Capture resumed.")
    
    def stop_capture(self, icon=None, item=None):
        """Stop the screenshot capture process."""
        self.is_running = False
        self.is_paused = False
        
        # Update UI
        self.start_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED, text="Pause")
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="Stopped", foreground="red")
        
        self.log_message("Capture stopped by user.")
    
    def update_status(self):
        """Update status display."""
        if self.is_running and self.session_start_time:
            elapsed = time.time() - self.session_start_time
            hours = int(elapsed // 3600)
            minutes = int((elapsed % 3600) // 60)
            seconds = int(elapsed % 60)
            self.time_label.config(text=f"{hours:02d}:{minutes:02d}:{seconds:02d}")
            
            self.count_label.config(text=str(self.total_screenshots))
            
            # Schedule next update
            self.root.after(1000, self.update_status)
    
    def take_screenshots(self, duration: int, interval: int, save_dir: str, 
                        capture_box: Tuple[int, int, int, int]) -> None:
        """Take screenshots at specified intervals."""
        start_time = time.time()
        counter = 1
        
        # Create session directory
        session_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_dir = os.path.join(save_dir, f"SnapZone_Session_{session_timestamp}")
        
        try:
            os.makedirs(session_dir, exist_ok=True)
        except OSError as e:
            self.log_message(f"Error creating session directory: {str(e)}")
            self.stop_capture()
            return
        
        self.log_message(f"Screenshots will be saved to: {session_dir}")
        
        try:
            while self.is_running:
                # Check duration limit
                if duration > 0 and time.time() - start_time >= duration:
                    self.log_message("Duration limit reached.")
                    break
                
                # Handle pause
                while self.is_paused and self.is_running:
                    time.sleep(0.1)
                
                if not self.is_running:
                    break
                
                # Take screenshot
                try:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                    filename = os.path.join(session_dir, f"screenshot_{timestamp}_{counter:04d}.png")
                    
                    screenshot = ImageGrab.grab(bbox=capture_box)
                    screenshot.save(filename, optimize=True)
                    
                    self.total_screenshots = counter
                    self.log_message(f"Screenshot #{counter} saved")
                    
                    # Show notification
                    try:
                        notification.notify(
                            title="SnapZone",
                            message=f"Screenshot #{counter} saved",
                            app_name="SnapZone",
                            timeout=1
                        )
                    except Exception:
                        pass  # Ignore notification errors
                    
                    counter += 1
                    
                except Exception as e:
                    self.log_message(f"Error taking screenshot: {type(e).__name__}: {str(e)}")
                
                # Wait for next screenshot
                time.sleep(interval)
                
        except Exception as e:
            self.log_message(f"Screenshot process error: {str(e)}")
        finally:
            # Update UI when finished
            self.root.after(0, lambda: self.stop_capture())
            self.log_message(f"Session completed. {counter-1} screenshots saved to: {session_dir}")

    def run(self):
        """Start the GUI application."""
        self.root.mainloop()


def main():
    """Entry point for the application."""
    try:
        app = SnapZoneGUI()
        app.run()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user.")
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()