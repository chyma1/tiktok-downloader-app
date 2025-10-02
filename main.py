from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.progressbar import MDProgressBar
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import MDList, OneLineListItem
from kivy.clock import Clock
from kivy.core.clipboard import Clipboard
import requests
import os
import uuid
from urllib.parse import urljoin
import threading
import json

class ModernTikTokDownloader(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "DeepOrange"
        self.theme_cls.accent_palette = "Orange"
        self.dialog = None
        self.downloaded_files = []

    def build(self):
        # Main layout
        main_layout = MDBoxLayout(
            orientation="vertical",
            spacing="15dp",
            padding="20dp"
        )
        
        # Header
        header_layout = MDBoxLayout(
            orientation="vertical",
            adaptive_height=True,
            spacing="10dp"
        )
        
        # App title
        title_label = MDLabel(
            text="TikTok Downloader",
            halign="center",
            theme_text_color="Primary",
            font_style="H4",
            bold=True
        )
        
        subtitle_label = MDLabel(
            text="Download videos without watermarks",
            halign="center",
            theme_text_color="Secondary",
            font_style="Subtitle1"
        )
        
        header_layout.add_widget(title_label)
        header_layout.add_widget(subtitle_label)
        main_layout.add_widget(header_layout)
        
        # URL input card
        input_card = MDCard(
            orientation="vertical",
            padding="20dp",
            spacing="15dp",
            size_hint_y=None,
            height="140dp",
            elevation=3,
            radius=[15]
        )
        
        self.url_input = MDTextField(
            hint_text="Paste TikTok URL here...",
            mode="round",
            size_hint_y=None,
            height="60dp",
            icon_left="link-variant",
            helper_text="Supported: tiktok.com, vm.tiktok.com, vt.tiktok.com",
            helper_text_mode="on_focus"
        )
        
        input_card.add_widget(self.url_input)
        main_layout.add_widget(input_card)
        
        # Buttons card
        button_card = MDCard(
            orientation="horizontal",
            padding="15dp",
            spacing="15dp",
            size_hint_y=None,
            height="80dp",
            elevation=2,
            radius=[15]
        )
        
        self.download_btn = MDRaisedButton(
            text="Download Video",
            size_hint_x=0.7,
            md_bg_color=self.theme_cls.primary_color,
            on_release=self.download_video
        )
        
        clear_btn = MDFlatButton(
            text="Clear",
            size_hint_x=0.3,
            theme_text_color="Custom",
            text_color=self.theme_cls.primary_color,
            on_release=self.clear_input
        )
        
        button_card.add_widget(self.download_btn)
        button_card.add_widget(clear_btn)
        main_layout.add_widget(button_card)
        
        # Progress bar
        self.progress = MDProgressBar(
            value=0,
            size_hint_y=None,
            height="10dp"
        )
        main_layout.add_widget(self.progress)
        
        # Result card
        result_card = MDCard(
            orientation="vertical",
            padding="20dp",
            spacing="15dp",
            size_hint_y=0.4,
            elevation=2,
            radius=[15]
        )
        
        result_title = MDLabel(
            text="Download Status",
            theme_text_color="Primary",
            font_style="H6",
            size_hint_y=None,
            height="30dp"
        )
        
        self.result_label = MDLabel(
            text="Ready to download...",
            theme_text_color="Secondary",
            size_hint_y=1
        )
        
        result_card.add_widget(result_title)
        result_card.add_widget(self.result_label)
        main_layout.add_widget(result_card)
        
        # History card (optional)
        history_card = MDCard(
            orientation="vertical",
            padding="15dp",
            spacing="10dp",
            size_hint_y=0.3,
            elevation=2,
            radius=[15]
        )
        
        history_title = MDLabel(
            text="Recent Downloads",
            theme_text_color="Primary",
            font_style="H6",
            size_hint_y=None,
            height="30dp"
        )
        
        self.history_list = MDList()
        history_card.add_widget(history_title)
        history_card.add_widget(self.history_list)
        main_layout.add_widget(history_card)
        
        return main_layout
    
    def on_start(self):
        # Check for clipboard content when app starts
        self.check_clipboard()
    
    def check_clipboard(self):
        """Check if clipboard contains a TikTok URL"""
        try:
            clipboard_text = Clipboard.paste()
            if clipboard_text and self.is_valid_tiktok_url(clipboard_text):
                self.show_clipboard_dialog(clipboard_text)
        except:
            pass
    
    def show_clipboard_dialog(self, url):
        """Show dialog when TikTok URL is detected in clipboard"""
        if not self.dialog:
            self.dialog = MDDialog(
                title="TikTok URL Detected",
                text=f"Found TikTok URL in clipboard:\n{url[:50]}...",
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        theme_text_color="Primary",
                        on_release=lambda x: self.dialog.dismiss()
                    ),
                    MDRaisedButton(
                        text="USE THIS URL",
                        on_release=lambda x: self.use_clipboard_url(url)
                    ),
                ],
            )
        self.dialog.open()
    
    def use_clipboard_url(self, url):
        """Use the URL from clipboard"""
        self.url_input.text = url
        if self.dialog:
            self.dialog.dismiss()
    
    def clear_input(self, instance):
        self.url_input.text = ""
        self.result_label.text = "Ready to download..."
        self.progress.value = 0
    
    def download_video(self, instance):
        url = self.url_input.text.strip()
        
        if not url:
            self.show_error("Please enter a TikTok URL")
            return
        
        if not self.is_valid_tiktok_url(url):
            self.show_error("Please enter a valid TikTok URL")
            return
        
        # Disable button and show progress
        self.download_btn.disabled = True
        self.download_btn.text = "Downloading..."
        self.progress.value = 50
        self.result_label.text = "🔄 Processing video...\nThis may take a few seconds."
        
        # Run download in background thread
        thread = threading.Thread(target=self.download_thread, args=(url,))
        thread.daemon = True
        thread.start()
    
    def download_thread(self, url):
        try:
            filepath, error = self.download_tiktok_video(url)
            Clock.schedule_once(lambda dt: self.download_complete(filepath, error))
        except Exception as e:
            Clock.schedule_once(lambda dt: self.download_complete(None, str(e)))
    
    def download_complete(self, filepath, error):
        self.download_btn.disabled = False
        self.download_btn.text = "Download Video"
        self.progress.value = 100 if filepath else 0
        
        if error:
            self.result_label.text = f"❌ Error: {error}"
            self.show_error(error)
        else:
            self.result_label.text = f"✅ Download Complete!\n📁 Saved to: {filepath}"
            self.add_to_history(filepath)
            self.show_success("Video downloaded successfully!")
    
    def add_to_history(self, filepath):
        """Add downloaded file to history list"""
        filename = os.path.basename(filepath)
        item = OneLineListItem(
            text=f"📹 {filename[:20]}...",
            on_release=lambda x: self.show_file_details(filepath)
        )
        self.history_list.add_widget(item)
        self.downloaded_files.append(filepath)
    
    def show_file_details(self, filepath):
        """Show details of downloaded file"""
        self.show_success(f"Video saved at:\n{filepath}")
    
    def show_error(self, message):
        """Show error dialog"""
        dialog = MDDialog(
            title="Error",
            text=message,
            buttons=[
                MDFlatButton(
                    text="OK",
                    theme_text_color="Primary",
                    on_release=lambda x: dialog.dismiss()
                ),
            ],
        )
        dialog.open()
    
    def show_success(self, message):
        """Show success dialog"""
        dialog = MDDialog(
            title="Success",
            text=message,
            buttons=[
                MDFlatButton(
                    text="OK",
                    theme_text_color="Primary",
                    on_release=lambda x: dialog.dismiss()
                ),
            ],
        )
        dialog.open()
    
    def is_valid_tiktok_url(self, url):
        patterns = [
            'tiktok.com/',
            'vm.tiktok.com/',
            'vt.tiktok.com/'
        ]
        return any(pattern in url for pattern in patterns)
    
    def download_tiktok_video(self, tiktok_url):
        """Download TikTok video without watermark"""
        try:
            # Using multiple API endpoints for reliability
            api_endpoints = [
                "https://tikwm.com/api/",
                "https://www.tikwm.com/api/"
            ]
            
            payload = {
                "url": tiktok_url,
                "count": 12,
                "cursor": 0,
                "web": 1,
                "hd": 1
            }
            
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Linux; Android 10; Mobile) AppleWebKit/537.36"
            }
            
            for api_url in api_endpoints:
                try:
                    response = requests.post(api_url, json=payload, headers=headers, timeout=30)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        if data.get('code') == 0 and 'data' in data:
                            video_data = data['data']
                            
                            # Get video URL
                            video_url = video_data.get('play')
                            if not video_url:
                                continue
                            
                            # Fix relative URLs
                            if video_url.startswith('/'):
                                video_url = urljoin(api_url, video_url)
                            elif not video_url.startswith(('http://', 'https://')):
                                video_url = urljoin('https://tikwm.com', video_url)
                            
                            # Download video
                            video_response = requests.get(video_url, headers=headers, timeout=30)
                            
                            if video_response.status_code == 200:
                                # Create downloads directory
                                download_dir = self.get_download_directory()
                                if not os.path.exists(download_dir):
                                    os.makedirs(download_dir)
                                
                                # Generate filename
                                filename = f"tiktok_{uuid.uuid4().hex}.mp4"
                                filepath = os.path.join(download_dir, filename)
                                
                                # Save video
                                with open(filepath, 'wb') as f:
                                    f.write(video_response.content)
                                
                                return filepath, None
                                
                except Exception as e:
                    continue
            
            return None, "Failed to download video. Please try another URL or check your connection."
            
        except Exception as e:
            return None, f"Error: {str(e)}"
    
    def get_download_directory(self):
        """Get the appropriate download directory"""
        try:
            # For Android
            from android.storage import primary_external_storage_path
            base_path = primary_external_storage_path()
            download_path = os.path.join(base_path, "Download", "TikTok")
            return download_path
        except:
            # For testing
            return os.path.join(os.getcwd(), "downloads")

if __name__ == '__main__':
    ModernTikTokDownloader().run()