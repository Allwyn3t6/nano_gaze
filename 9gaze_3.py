from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDFillRoundFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.progressbar import MDProgressBar
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.slider import MDSlider
from kivymd.uix.textfield import MDTextField
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.chip import MDChip
from kivymd.uix.list import MDList, OneLineListItem
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.behaviors import CommonElevationBehavior
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.icon_definitions import md_icons

from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.properties import StringProperty, NumericProperty, DictProperty, BooleanProperty
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.utils import get_color_from_hex

import cv2
import numpy as np
from datetime import datetime
import os
import json
import warnings

warnings.filterwarnings("ignore")

# Set window size for desktop testing
Window.size = (1200, 800)

# ---------------- CAMERA CONTROLLER ---------------- #

class CameraController:
    def __init__(self):
        self.cap = None
        self.open_camera()
        
    def open_camera(self):
        try:
            self.cap = cv2.VideoCapture(0)
            if self.cap.isOpened():
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                return True
        except:
            pass
        return False
    
    def get_frame(self):
        if not self.cap or not self.cap.isOpened():
            return None
        ret, frame = self.cap.read()
        if not ret:
            return None
        return cv2.flip(frame, 1)
    
    def release(self):
        if self.cap:
            self.cap.release()

# ---------------- CUSTOM WIDGETS ---------------- #

class ThumbnailCard(MDCard):
    position = NumericProperty(1)
    has_image = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (dp(100), dp(100))
        self.radius = dp(15)
        self.elevation = 2
        
        self.layout = MDBoxLayout(
            orientation="vertical",
            padding=dp(10)
        )
        
        self.position_label = MDLabel(
            text=str(self.position),
            halign="center",
            font_style="H5",
            theme_text_color="Secondary"
        )
        
        self.layout.add_widget(self.position_label)
        self.add_widget(self.layout)
        
    def set_image(self, frame):
        if frame is not None:
            # Convert to thumbnail
            thumb = cv2.resize(frame, (80, 80))
            rgb = cv2.cvtColor(thumb, cv2.COLOR_BGR2RGB)
            
            # Create texture
            texture = Texture.create(size=(rgb.shape[1], rgb.shape[0]), colorfmt='rgb')
            texture.blit_buffer(rgb.tobytes(), colorfmt='rgb', bufferfmt='ubyte')
            
            # Create image widget
            img = Image(texture=texture, size=(dp(80), dp(80)))
            
            # Clear layout and add image
            self.layout.clear_widgets()
            self.layout.add_widget(img)
            
            # Add position badge
            badge = MDLabel(
                text=str(self.position),
                size_hint=(None, None),
                size=(dp(25), dp(25)),
                halign="center",
                valign="center",
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1),
                font_style="Caption"
            )
            badge.canvas.before.clear()
            with badge.canvas.before:
                from kivy.graphics import Color, RoundedRectangle
                Color(0.2, 0.7, 0.3, 0.9)  # Green
                RoundedRectangle(pos=badge.pos, size=badge.size, radius=[dp(12)])
            
            self.layout.add_widget(badge)
            self.has_image = True
            self.md_bg_color = get_color_from_hex("#E8F5E9")  # Light green
        else:
            # Reset to default
            self.layout.clear_widgets()
            self.position_label = MDLabel(
                text=str(self.position),
                halign="center",
                font_style="H5",
                theme_text_color="Secondary"
            )
            self.layout.add_widget(self.position_label)
            self.has_image = False
            self.md_bg_color = get_color_from_hex("#F5F5F5")  # Light gray

class DirectionIcon(MDLabel):
    def __init__(self, gaze_position, **kwargs):
        super().__init__(**kwargs)
        self.gaze_position = gaze_position
        self.update_icon()
        
    def update_icon(self):
        icons = {
            1: "◎",  # Center
            2: "↗",  # Up-right
            3: "→",  # Right
            4: "↘",  # Down-right
            5: "↓",  # Down
            6: "↙",  # Down-left
            7: "←",  # Left
            8: "↖",  # Up-left
            9: "↑"   # Up
        }
        self.text = icons.get(self.gaze_position, "◎")
        self.font_size = dp(60)
        self.halign = "center"
        self.valign = "middle"

# ---------------- WELCOME SCREEN ---------------- #

class WelcomeScreen(MDScreen):
    def on_enter(self):
        self.clear_widgets()
        
        # Main layout with gradient background
        main_layout = MDFloatLayout()
        
        # Decorative background elements
        from kivy.graphics import Color, Rectangle
        with main_layout.canvas.before:
            Color(0.9686, 0.9765, 0.9804, 1)  # Light blue-gray
            Rectangle(pos=main_layout.pos, size=Window.size)
        
        # Content container
        content = MDBoxLayout(
            orientation="vertical",
            padding=dp(50),
            spacing=dp(40),
            size_hint=(0.9, 0.9),
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )
        
        # Header section
        header = MDBoxLayout(
            orientation="vertical",
            spacing=dp(20),
            size_hint_y=None,
            height=dp(200)
        )
        
        # Title with icon
        title_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(20),
            size_hint_y=None,
            height=dp(80)
        )
        
        icon_label = MDLabel(
            text="👁️",
            font_size=dp(60),
            halign="center",
            valign="center"
        )
        
        title_label = MDLabel(
            text="Aravind Eye Hospitals",
            halign="center",
            font_style="H3",
            bold=True,
            theme_text_color="Primary"
        )
        
        title_layout.add_widget(icon_label)
        title_layout.add_widget(title_label)
        
        # Subtitle with decorative line
        subtitle_label = MDLabel(
            text="9-Gaze Ophthalmology Examination",
            halign="center",
            font_style="H5",
            theme_text_color="Secondary",
            bold=True
        )
        
        header.add_widget(title_layout)
        header.add_widget(subtitle_label)
        
        # Features card
        features_card = MDCard(
            orientation="vertical",
            padding=dp(25),
            spacing=dp(15),
            size_hint=(1, None),
            height=dp(120),
            elevation=3,
            radius=[dp(20),],
            md_bg_color=get_color_from_hex("#FFFFFF")
        )
        
        features_text = MDLabel(
            text="• Complete 9-Gaze Assessment • Patient-Friendly Interface •\n• Automated Collage Generation • Secure Data Management •",
            halign="center",
            theme_text_color="Secondary",
            font_style="Body1"
        )
        
        features_card.add_widget(features_text)
        
        # Developer credit
        developer_label = MDLabel(
            text="👨‍💻 Developed by Allwyn",
            halign="center",
            theme_text_color="Hint",
            font_style="Subtitle1",
            bold=True
        )
        
        # Buttons section
        buttons_layout = MDBoxLayout(
            orientation="vertical",
            spacing=dp(25),
            padding=[dp(100), 0, dp(100), 0],
            size_hint_y=None,
            height=dp(200)
        )
        
        # Start Examination Button
        start_button = MDFillRoundFlatButton(
            text="▶ START EXAMINATION",
            size_hint=(1, None),
            height=dp(60),
            font_size=dp(18),
            md_bg_color=get_color_from_hex("#27AE60"),  # Green
            text_color=(1, 1, 1, 1),
            on_release=self.start_examination
        )
        
        # Settings Button
        settings_button = MDRaisedButton(
            text="⚙ SETTINGS & CONFIGURATION",
            size_hint=(1, None),
            height=dp(50),
            font_size=dp(16),
            md_bg_color=get_color_from_hex("#3498DB"),  # Blue
            on_release=self.open_settings
        )
        
        buttons_layout.add_widget(start_button)
        buttons_layout.add_widget(settings_button)
        
        # Add all widgets
        content.add_widget(header)
        content.add_widget(features_card)
        content.add_widget(developer_label)
        content.add_widget(buttons_layout)
        
        main_layout.add_widget(content)
        self.add_widget(main_layout)
    
    def start_examination(self, *args):
        self.manager.switch_to(self.manager.get_screen("gaze"))
    
    def open_settings(self, *args):
        self.manager.switch_to(self.manager.get_screen("settings"))

# ---------------- GAZE SCREEN ---------------- #

class GazeScreen(MDScreen):
    def on_enter(self):
        self.clear_widgets()
        
        # Initialize variables
        self.camera = CameraController()
        self.current_gaze = 1
        self.captured_images = {}
        self.camera_update_event = None
        
        # Main layout
        main_layout = MDBoxLayout(
            orientation="vertical",
            padding=dp(10),
            spacing=dp(10)
        )
        
        # Top bar
        top_bar = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(60),
            spacing=dp(10)
        )
        
        # Back button
        back_button = MDFlatButton(
            text="◀ Back",
            theme_text_color="Custom",
            text_color=get_color_from_hex("#7F8C8D"),
            on_release=self.go_home
        )
        
        # Title
        title_label = MDLabel(
            text="Gaze Position Examination",
            halign="center",
            font_style="H5",
            bold=True,
            theme_text_color="Primary",
            size_hint_x=0.6
        )
        
        # Progress indicator
        progress_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(10),
            size_hint_x=0.4
        )
        
        self.progress_label = MDLabel(
            text=f"Progress: {self.current_gaze}/9",
            theme_text_color="Secondary",
            bold=True
        )
        
        self.progress_bar = MDProgressBar(
            value=self.current_gaze * 11.11,
            max=100
        )
        
        progress_layout.add_widget(self.progress_label)
        progress_layout.add_widget(self.progress_bar)
        
        top_bar.add_widget(back_button)
        top_bar.add_widget(title_label)
        top_bar.add_widget(progress_layout)
        
        # Main content area
        content_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(20)
        )
        
        # Left panel - Controls and instructions
        left_panel = MDBoxLayout(
            orientation="vertical",
            spacing=dp(20),
            size_hint_x=0.4
        )
        
        # Position card
        position_card = MDCard(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(20),
            elevation=3,
            radius=[dp(20),],
            md_bg_color=get_color_from_hex("#F8F9FA")
        )
        
        # Direction icon
        self.direction_icon = DirectionIcon(
            gaze_position=self.current_gaze,
            size_hint_y=None,
            height=dp(100)
        )
        
        # Instruction label
        self.instruction_label = MDLabel(
            text=self.get_instruction(),
            halign="center",
            valign="center",
            theme_text_color="Primary",
            font_style="Body1",
            bold=True,
            size_hint_y=None,
            height=dp(100)
        )
        
        # Hint label
        hint_label = MDLabel(
            text="💡 Ensure the illuminated light is clearly visible and centered",
            halign="center",
            theme_text_color="Error",
            font_style="Caption",
            size_hint_y=None,
            height=dp(40)
        )
        
        position_card.add_widget(self.direction_icon)
        position_card.add_widget(self.instruction_label)
        position_card.add_widget(hint_label)
        
        # Control buttons
        self.capture_button = MDRaisedButton(
            text="📸 CAPTURE PHOTO",
            size_hint_y=None,
            height=dp(50),
            font_size=dp(16),
            md_bg_color=get_color_from_hex("#27AE60"),
            on_release=self.capture_photo
        )
        
        action_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(10),
            size_hint_y=None,
            height=dp(50)
        )
        
        self.retake_button = MDRaisedButton(
            text="🔄 RETAKE",
            size_hint=(0.5, 1),
            md_bg_color=get_color_from_hex("#F39C12"),
            disabled=True,
            on_release=self.retake_photo
        )
        
        self.next_button = MDRaisedButton(
            text="NEXT ▶",
            size_hint=(0.5, 1),
            md_bg_color=get_color_from_hex("#3498DB"),
            disabled=True,
            on_release=self.next_gaze
        )
        
        action_layout.add_widget(self.retake_button)
        action_layout.add_widget(self.next_button)
        
        # Navigation buttons
        nav_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(10),
            size_hint_y=None,
            height=dp(50)
        )
        
        self.prev_button = MDFlatButton(
            text="◀ PREVIOUS",
            theme_text_color="Custom",
            text_color=get_color_from_hex("#7F8C8D"),
            disabled=True,
            on_release=self.previous_gaze
        )
        
        self.finish_button = MDRaisedButton(
            text="✅ FINISH EXAMINATION",
            size_hint=(0.7, 1),
            md_bg_color=get_color_from_hex("#9B59B6"),
            disabled=True,
            on_release=self.finish_examination
        )
        
        nav_layout.add_widget(self.prev_button)
        nav_layout.add_widget(self.finish_button)
        
        # Add to left panel
        left_panel.add_widget(position_card)
        left_panel.add_widget(self.capture_button)
        left_panel.add_widget(action_layout)
        left_panel.add_widget(nav_layout)
        
        # Right panel - Camera and thumbnails
        right_panel = MDBoxLayout(
            orientation="vertical",
            spacing=dp(20),
            size_hint_x=0.6
        )
        
        # Camera preview card
        camera_card = MDCard(
            orientation="vertical",
            padding=dp(10),
            elevation=3,
            radius=[dp(15),],
            md_bg_color=get_color_from_hex("#2C3E50")
        )
        
        camera_title = MDLabel(
            text="Live Camera View",
            halign="center",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            font_style="H6",
            bold=True
        )
        
        self.camera_preview = Image(
            size_hint=(1, 0.8),
            allow_stretch=True
        )
        
        status_label = MDLabel(
            text="🔴 Live View - Ready",
            halign="center",
            theme_text_color="Custom",
            text_color=get_color_from_hex("#27AE60"),
            font_style="Caption"
        )
        
        camera_card.add_widget(camera_title)
        camera_card.add_widget(self.camera_preview)
        camera_card.add_widget(status_label)
        
        # Thumbnails section
        thumbnails_label = MDLabel(
            text="📷 Captured Positions:",
            theme_text_color="Primary",
            font_style="Subtitle1",
            bold=True
        )
        
        self.thumbnails_layout = MDGridLayout(
            cols=3,
            spacing=dp(10),
            size_hint_y=None,
            height=dp(350)
        )
        
        # Initialize thumbnails
        self.thumbnails = []
        for i in range(1, 10):
            thumb = ThumbnailCard(position=i)
            self.thumbnails.append(thumb)
            self.thumbnails_layout.add_widget(thumb)
        
        right_panel.add_widget(camera_card)
        right_panel.add_widget(thumbnails_label)
        right_panel.add_widget(self.thumbnails_layout)
        
        # Add panels to content
        content_layout.add_widget(left_panel)
        content_layout.add_widget(right_panel)
        
        # Assemble main layout
        main_layout.add_widget(top_bar)
        main_layout.add_widget(content_layout)
        
        self.add_widget(main_layout)
        
        # Start camera updates
        self.start_camera()
    
    def get_instruction(self):
        instructions = {
            1: "Ask the patient to focus on the illuminated light straight ahead.\nEnsure both eyes are clearly visible and centered.",
            2: "Ask the patient to focus on the illuminated light UP and to the RIGHT.\nMaintain eye contact with the light source.",
            3: "Ask the patient to focus on the illuminated light to the RIGHT.\nKeep the head steady, only eyes should move.",
            4: "Ask the patient to focus on the illuminated light DOWN and to the RIGHT.\nCheck for clear eyelid and sclera visibility.",
            5: "Ask the patient to focus on the illuminated light straight DOWN.\nEnsure lower eyelids and iris are visible.",
            6: "Ask the patient to focus on the illuminated light DOWN and to the LEFT.\nMaintain consistent lighting on both eyes.",
            7: "Ask the patient to focus on the illuminated light to the LEFT.\nKeep the light source in clear view.",
            8: "Ask the patient to focus on the illuminated light UP and to the LEFT.\nEnsure upper eyelids don't obstruct the view.",
            9: "Ask the patient to focus on the illuminated light straight UP.\nCheck for complete iris visibility."
        }
        return instructions.get(self.current_gaze, "")
    
    def start_camera(self):
        if self.camera_update_event:
            self.camera_update_event.cancel()
        
        if self.camera.open_camera():
            self.camera_update_event = Clock.schedule_interval(self.update_camera, 1/30)
        else:
            from kivymd.uix.dialog import MDDialog
            dialog = MDDialog(
                title="Camera Error",
                text="Cannot open camera. Please check your camera connection.",
                buttons=[
                    MDFlatButton(
                        text="OK",
                        on_release=lambda x: dialog.dismiss()
                    )
                ]
            )
            dialog.open()
    
    def update_camera(self, dt):
        frame = self.camera.get_frame()
        if frame is None:
            return
        
        # Apply brightness from settings
        app = MDApp.get_running_app()
        brightness = app.settings.get('brightness', 50)
        frame = self.adjust_brightness(frame, brightness)
        
        # Convert to RGB
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Create texture
        texture = Texture.create(size=(rgb.shape[1], rgb.shape[0]), colorfmt='rgb')
        texture.blit_buffer(rgb.tobytes(), colorfmt='rgb', bufferfmt='ubyte')
        
        # Update preview
        self.camera_preview.texture = texture
    
    def adjust_brightness(self, image, brightness):
        brightness = (brightness - 50) * 2
        if brightness != 0:
            if brightness > 0:
                shadow = brightness
                highlight = 255
            else:
                shadow = 0
                highlight = 255 + brightness
            alpha_b = (highlight - shadow)/255
            gamma_b = shadow
            image = cv2.addWeighted(image, alpha_b, image, 0, gamma_b)
        return image
    
    def capture_photo(self, *args):
        frame = self.camera.get_frame()
        if frame is None:
            return
        
        # Store image
        app = MDApp.get_running_app()
        brightness = app.settings.get('brightness', 50)
        frame = self.adjust_brightness(frame, brightness)
        self.captured_images[self.current_gaze] = frame
        
        # Update thumbnail
        self.thumbnails[self.current_gaze - 1].set_image(frame)
        
        # Update UI
        self.capture_button.disabled = True
        self.retake_button.disabled = False
        self.next_button.disabled = False
        
        # Check if all images captured
        if len(self.captured_images) == 9:
            self.finish_button.disabled = False
    
    def retake_photo(self, *args):
        if self.current_gaze in self.captured_images:
            del self.captured_images[self.current_gaze]
        
        # Reset thumbnail
        self.thumbnails[self.current_gaze - 1].set_image(None)
        
        # Update UI
        self.capture_button.disabled = False
        self.retake_button.disabled = True
        self.next_button.disabled = True
        self.finish_button.disabled = len(self.captured_images) != 9
        
        # Restart camera
        self.start_camera()
    
    def next_gaze(self, *args):
        if self.current_gaze < 9:
            self.current_gaze += 1
            self.update_gaze_display()
    
    def previous_gaze(self, *args):
        if self.current_gaze > 1:
            self.current_gaze -= 1
            self.update_gaze_display()
    
    def update_gaze_display(self):
        # Update progress
        self.progress_bar.value = self.current_gaze * 11.11
        self.progress_label.text = f"Progress: {self.current_gaze}/9"
        
        # Update direction icon
        self.direction_icon.gaze_position = self.current_gaze
        self.direction_icon.update_icon()
        
        # Update instruction
        self.instruction_label.text = self.get_instruction()
        
        # Update buttons
        self.capture_button.disabled = self.current_gaze in self.captured_images
        self.retake_button.disabled = self.current_gaze not in self.captured_images
        self.next_button.disabled = self.current_gaze not in self.captured_images
        self.prev_button.disabled = self.current_gaze == 1
        self.finish_button.disabled = len(self.captured_images) != 9
        
        # Show captured image or live camera
        if self.current_gaze in self.captured_images:
            # Stop camera and show captured image
            if self.camera_update_event:
                self.camera_update_event.cancel()
            
            frame = self.captured_images[self.current_gaze]
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            texture = Texture.create(size=(rgb.shape[1], rgb.shape[0]), colorfmt='rgb')
            texture.blit_buffer(rgb.tobytes(), colorfmt='rgb', bufferfmt='ubyte')
            self.camera_preview.texture = texture
        else:
            # Start live camera
            self.start_camera()
    
    def finish_examination(self, *args):
        if len(self.captured_images) == 9:
            app = MDApp.get_running_app()
            app.captured_images = self.captured_images
            self.manager.switch_to(self.manager.get_screen("result"))
    
    def go_home(self, *args):
        # Confirm dialog
        dialog = MDDialog(
            title="Confirm Exit",
            text="Return to home page? All unsaved progress will be lost.",
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDFlatButton(
                    text="YES",
                    on_release=lambda x: self.confirm_go_home(dialog)
                )
            ]
        )
        dialog.open()
    
    def confirm_go_home(self, dialog):
        dialog.dismiss()
        if self.camera_update_event:
            self.camera_update_event.cancel()
        self.camera.release()
        self.manager.switch_to(self.manager.get_screen("welcome"))
    
    def on_leave(self):
        if self.camera_update_event:
            self.camera_update_event.cancel()
        self.camera.release()

# ---------------- RESULT SCREEN ---------------- #

class ResultScreen(MDScreen):
    def on_enter(self):
        self.clear_widgets()
        
        # Main layout
        main_layout = MDBoxLayout(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(20)
        )
        
        # Top bar
        top_bar = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(60)
        )
        
        back_button = MDFlatButton(
            text="◀ Back to Examination",
            theme_text_color="Custom",
            text_color=get_color_from_hex("#7F8C8D"),
            on_release=self.retake_all
        )
        
        title_label = MDLabel(
            text="📊 Examination Results - 9-Gaze Collage",
            halign="center",
            font_style="H4",
            bold=True,
            theme_text_color="Primary",
            size_hint_x=0.8
        )
        
        top_bar.add_widget(back_button)
        top_bar.add_widget(title_label)
        
        # Success message
        success_card = MDCard(
            orientation="horizontal",
            padding=dp(20),
            size_hint_y=None,
            height=dp(80),
            elevation=2,
            radius=[dp(15),],
            md_bg_color=get_color_from_hex("#D5F4E6")
        )
        
        success_label = MDLabel(
            text="✅ All 9 gaze positions successfully captured!",
            halign="center",
            theme_text_color="Custom",
            text_color=get_color_from_hex("#27AE60"),
            font_style="H6",
            bold=True
        )
        
        success_card.add_widget(success_label)
        
        # Collage display
        collage_card = MDCard(
            orientation="vertical",
            padding=dp(20),
            elevation=3,
            radius=[dp(20),],
            md_bg_color=get_color_from_hex("#FFFFFF")
        )
        
        collage_title = MDLabel(
            text="Final Collage",
            halign="center",
            font_style="H5",
            bold=True,
            theme_text_color="Primary"
        )
        
        self.collage_image = Image(
            size_hint=(1, 0.9),
            allow_stretch=True
        )
        
        collage_card.add_widget(collage_title)
        collage_card.add_widget(self.collage_image)
        
        # Action buttons title
        actions_title = MDLabel(
            text="📁 Export & Share Options:",
            theme_text_color="Primary",
            font_style="H6",
            bold=True
        )
        
        # Action buttons
        buttons_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(20),
            size_hint_y=None,
            height=dp(60)
        )
        
        save_button = MDRaisedButton(
            text="💾 SAVE COLLAGE",
            size_hint=(0.33, 1),
            md_bg_color=get_color_from_hex("#3498DB"),
            on_release=self.save_collage
        )
        
        share_button = MDRaisedButton(
            text="📤 SHARE RESULTS",
            size_hint=(0.33, 1),
            md_bg_color=get_color_from_hex("#9B59B6"),
            on_release=self.share_collage
        )
        
        drive_button = MDRaisedButton(
            text="☁️ UPLOAD TO DRIVE",
            size_hint=(0.33, 1),
            md_bg_color=get_color_from_hex("#27AE60"),
            on_release=self.upload_to_drive
        )
        
        buttons_layout.add_widget(save_button)
        buttons_layout.add_widget(share_button)
        buttons_layout.add_widget(drive_button)
        
        # Bottom navigation
        bottom_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(20),
            size_hint_y=None,
            height=dp(60)
        )
        
        home_button = MDRaisedButton(
            text="🏠 HOME",
            size_hint=(0.3, 1),
            md_bg_color=get_color_from_hex("#7F8C8D"),
            on_release=self.go_home
        )
        
        new_exam_button = MDRaisedButton(
            text="🔄 NEW EXAMINATION",
            size_hint=(0.7, 1),
            md_bg_color=get_color_from_hex("#E74C3C"),
            on_release=self.retake_all
        )
        
        bottom_layout.add_widget(home_button)
        bottom_layout.add_widget(new_exam_button)
        
        # Add all widgets
        main_layout.add_widget(top_bar)
        main_layout.add_widget(success_card)
        main_layout.add_widget(collage_card)
        main_layout.add_widget(actions_title)
        main_layout.add_widget(buttons_layout)
        main_layout.add_widget(bottom_layout)
        
        self.add_widget(main_layout)
        
        # Create and display collage
        self.create_collage()
    
    def create_collage(self):
        app = MDApp.get_running_app()
        images = app.captured_images
        
        if len(images) != 9:
            dialog = MDDialog(
                title="Error",
                text="Not enough images captured!",
                buttons=[
                    MDFlatButton(
                        text="OK",
                        on_release=lambda x: (dialog.dismiss(), 
                                             self.manager.switch_to(self.manager.get_screen("gaze")))
                    )
                ]
            )
            dialog.open()
            return
        
        try:
            # Create 3x3 grid
            collage = np.zeros((900, 1200, 3), dtype=np.uint8)
            positions = {
                1: (300, 0, 600, 300),   # Top middle
                2: (600, 0, 900, 300),   # Top right
                3: (600, 300, 900, 600), # Middle right
                4: (600, 600, 900, 900), # Bottom right
                5: (300, 600, 600, 900), # Bottom middle
                6: (0, 600, 300, 900),   # Bottom left
                7: (0, 300, 300, 600),   # Middle left
                8: (0, 0, 300, 300),     # Top left
                9: (300, 300, 600, 600)  # Center
            }
            
            for gaze_pos, (x1, y1, x2, y2) in positions.items():
                img = images[gaze_pos]
                img = cv2.resize(img, (300, 300))
                collage[y1:y2, x1:x2] = img
            
            # Add timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cv2.putText(collage, timestamp, (10, 890), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            # Add position labels if enabled
            app = MDApp.get_running_app()
            if app.settings.get('show_positions', True):
                labels = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
                label_positions = [(450, 50), (750, 50), (750, 350), (750, 650),
                                  (450, 650), (150, 650), (150, 350), (150, 50),
                                  (450, 350)]
                
                for label, (x, y) in zip(labels, label_positions):
                    cv2.putText(collage, label, (x, y), 
                               cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
            
            self.collage_result = collage
            self.display_collage(collage)
            
        except Exception as e:
            dialog = MDDialog(
                title="Error",
                text=f"Failed to create collage: {str(e)}",
                buttons=[
                    MDFlatButton(
                        text="OK",
                        on_release=lambda x: (dialog.dismiss(), 
                                             self.manager.switch_to(self.manager.get_screen("gaze")))
                    )
                ]
            )
            dialog.open()
    
    def display_collage(self, collage):
        rgb = cv2.cvtColor(collage, cv2.COLOR_BGR2RGB)
        texture = Texture.create(size=(rgb.shape[1], rgb.shape[0]), colorfmt='rgb')
        texture.blit_buffer(rgb.tobytes(), colorfmt='rgb', bufferfmt='ubyte')
        self.collage_image.texture = texture
    
    def save_collage(self, *args):
        if hasattr(self, 'collage_result'):
            filename = f"gaze_collage_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            path = os.path.join(os.getcwd(), filename)
            cv2.imwrite(path, self.collage_result)
            
            dialog = MDDialog(
                title="Success",
                text=f"Collage saved to:\n{path}",
                buttons=[
                    MDFlatButton(
                        text="OK",
                        on_release=lambda x: dialog.dismiss()
                    )
                ]
            )
            dialog.open()
    
    def share_collage(self, *args):
        if hasattr(self, 'collage_result'):
            temp_file = f"temp_share_collage_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            cv2.imwrite(temp_file, self.collage_result)
            
            dialog = MDDialog(
                title="Share",
                text=f"Collage saved to:\n{temp_file}\n\nReady for sharing.",
                buttons=[
                    MDFlatButton(
                        text="OK",
                        on_release=lambda x: dialog.dismiss()
                    )
                ]
            )
            dialog.open()
    
    def upload_to_drive(self, *args):
        app = MDApp.get_running_app()
        drive_link = app.settings.get('drive_link', '')
        
        if drive_link:
            dialog = MDDialog(
                title="Drive Upload",
                text=f"Would upload to:\n{drive_link}",
                buttons=[
                    MDFlatButton(
                        text="OK",
                        on_release=lambda x: dialog.dismiss()
                    )
                ]
            )
            dialog.open()
        else:
            dialog = MDDialog(
                title="Drive Error",
                text="Please set Drive link in Settings first",
                buttons=[
                    MDFlatButton(
                        text="OK",
                        on_release=lambda x: dialog.dismiss()
                    )
                ]
            )
            dialog.open()
    
    def go_home(self, *args):
        self.manager.switch_to(self.manager.get_screen("welcome"))
    
    def retake_all(self, *args):
        app = MDApp.get_running_app()
        app.captured_images = {}
        self.manager.switch_to(self.manager.get_screen("gaze"))

# ---------------- SETTINGS SCREEN ---------------- #

class SettingsScreen(MDScreen):
    def on_enter(self):
        self.clear_widgets()
        
        # Main layout
        main_layout = MDBoxLayout(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(20)
        )
        
        # Top bar
        top_bar = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(60)
        )
        
        back_button = MDFlatButton(
            text="◀ Back",
            theme_text_color="Custom",
            text_color=get_color_from_hex("#7F8C8D"),
            on_release=self.go_home
        )
        
        title_label = MDLabel(
            text="⚙️ Application Settings",
            halign="center",
            font_style="H4",
            bold=True,
            theme_text_color="Primary",
            size_hint_x=0.8
        )
        
        top_bar.add_widget(back_button)
        top_bar.add_widget(title_label)
        
        # Settings container
        scroll = ScrollView()
        settings_container = MDBoxLayout(
            orientation="vertical",
            spacing=dp(25),
            size_hint_y=None,
            padding=[dp(30), dp(30), dp(30), dp(30)]
        )
        settings_container.bind(minimum_height=settings_container.setter('height'))
        
        # Load settings
        app = MDApp.get_running_app()
        settings = app.settings
        
        # Brightness setting
        brightness_card = MDCard(
            orientation="vertical",
            padding=dp(25),
            spacing=dp(15),
            elevation=2,
            radius=[dp(20),],
            md_bg_color=get_color_from_hex("#FEF9E7")
        )
        
        brightness_title = MDLabel(
            text="💡 Display Brightness",
            theme_text_color="Custom",
            text_color=get_color_from_hex("#F39C12"),
            font_style="H6",
            bold=True
        )
        
        # Brightness slider
        slider_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(20)
        )
        
        dim_label = MDLabel(
            text="🌙",
            font_size=dp(24)
        )
        
        self.brightness_slider = MDSlider(
            min=0,
            max=100,
            value=settings.get('brightness', 50),
            hint=False
        )
        self.brightness_slider.bind(value=self.on_brightness_change)
        
        bright_label = MDLabel(
            text="☀️",
            font_size=dp(24)
        )
        
        slider_layout.add_widget(dim_label)
        slider_layout.add_widget(self.brightness_slider)
        slider_layout.add_widget(bright_label)
        
        brightness_value = MDLabel(
            text=f"Current: {int(self.brightness_slider.value)}%",
            halign="center",
            theme_text_color="Secondary"
        )
        
        brightness_card.add_widget(brightness_title)
        brightness_card.add_widget(slider_layout)
        brightness_card.add_widget(brightness_value)
        
        # Position indicators setting
        position_card = MDCard(
            orientation="vertical",
            padding=dp(25),
            spacing=dp(15),
            elevation=2,
            radius=[dp(20),],
            md_bg_color=get_color_from_hex("#E8F4FC")
        )
        
        position_title = MDLabel(
            text="🔢 Position Indicators",
            theme_text_color="Custom",
            text_color=get_color_from_hex("#3498DB"),
            font_style="H6",
            bold=True
        )
        
        position_info = MDLabel(
            text="Show position numbers on the final collage for easy reference.",
            theme_text_color="Secondary",
            font_style="Body2"
        )
        
        self.position_checkbox = MDCheckbox(
            size_hint=(None, None),
            size=(dp(40), dp(40)),
            active=settings.get('show_positions', True)
        )
        
        checkbox_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(10)
        )
        
        checkbox_layout.add_widget(self.position_checkbox)
        checkbox_layout.add_widget(MDLabel(
            text="Display position numbers",
            theme_text_color="Primary"
        ))
        
        position_card.add_widget(position_title)
        position_card.add_widget(position_info)
        position_card.add_widget(checkbox_layout)
        
        # Drive settings
        drive_card = MDCard(
            orientation="vertical",
            padding=dp(25),
            spacing=dp(15),
            elevation=2,
            radius=[dp(20),],
            md_bg_color=get_color_from_hex("#F5EEF8")
        )
        
        drive_title = MDLabel(
            text="☁️ Cloud Storage",
            theme_text_color="Custom",
            text_color=get_color_from_hex("#9B59B6"),
            font_style="H6",
            bold=True
        )
        
        drive_info = MDLabel(
            text="Configure Google Drive integration for automatic backup of examination results.",
            theme_text_color="Secondary",
            font_style="Body2"
        )
        
        self.drive_input = MDTextField(
            hint_text="https://drive.google.com/drive/folders/...",
            mode="rectangle",
            text=settings.get('drive_link', ''),
            size_hint_y=None,
            height=dp(50)
        )
        
        drive_card.add_widget(drive_title)
        drive_card.add_widget(drive_info)
        drive_card.add_widget(self.drive_input)
        
        # Save button
        save_button = MDRaisedButton(
            text="💾 SAVE ALL SETTINGS",
            size_hint=(0.5, None),
            height=dp(55),
            pos_hint={"center_x": 0.5},
            md_bg_color=get_color_from_hex("#27AE60"),
            on_release=self.save_settings
        )
        
        # Add all cards
        settings_container.add_widget(brightness_card)
        settings_container.add_widget(position_card)
        settings_container.add_widget(drive_card)
        settings_container.add_widget(save_button)
        
        scroll.add_widget(settings_container)
        
        # Assemble main layout
        main_layout.add_widget(top_bar)
        main_layout.add_widget(scroll)
        
        self.add_widget(main_layout)
    
    def on_brightness_change(self, instance, value):
        # Update settings in real-time
        app = MDApp.get_running_app()
        app.settings['brightness'] = int(value)
    
    def save_settings(self, *args):
        app = MDApp.get_running_app()
        app.settings['brightness'] = int(self.brightness_slider.value)
        app.settings['show_positions'] = self.position_checkbox.active
        app.settings['drive_link'] = self.drive_input.text
        
        # Save to file
        try:
            with open('kivy_settings.json', 'w') as f:
                json.dump(app.settings, f)
        except:
            pass
        
        dialog = MDDialog(
            title="Settings Saved",
            text="All settings have been saved successfully!",
            buttons=[
                MDFlatButton(
                    text="OK",
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open()
    
    def go_home(self, *args):
        self.manager.switch_to(self.manager.get_screen("welcome"))

# ---------------- MAIN APP ---------------- #

class NineGazeApp(MDApp):
    captured_images = DictProperty({})
    settings = DictProperty({
        'brightness': 50,
        'show_positions': True,
        'drive_link': ''
    })
    
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        
        # Load settings
        try:
            with open('kivy_settings.json', 'r') as f:
                loaded_settings = json.load(f)
                self.settings.update(loaded_settings)
        except:
            pass
        
        # Create screen manager
        self.sm = MDScreenManager()
        
        # Add screens
        self.sm.add_widget(WelcomeScreen(name="welcome"))
        self.sm.add_widget(GazeScreen(name="gaze"))
        self.sm.add_widget(ResultScreen(name="result"))
        self.sm.add_widget(SettingsScreen(name="settings"))
        
        return self.sm

if __name__ == "__main__":
    NineGazeApp().run()
