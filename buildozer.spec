[app]

# App name (shown on phone)
title = NanoGaze

# Package name (no spaces, all lowercase)
package.name = nanogaze
package.domain = org.aravind

# Source code folder
source.dir = .
source.include_exts = py,png,jpg,kv

# App version
version = 0.1

# Python requirements
requirements = python3,kivy,kivymd,numpy,opencv-python

# App orientation
orientation = landscape

# Fullscreen
fullscreen = 1

# Android permissions (VERY IMPORTANT)
android.permissions = CAMERA,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# Android versions
android.api = 33
android.minapi = 24
android.arch = arm64-v8a

# Disable backup (medical app safety)
android.allow_backup = False

# Log level
log_level = 2
