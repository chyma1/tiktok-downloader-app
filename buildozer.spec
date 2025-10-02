[app]
title = TikTok Downloader
package.name = tiktokdownloader
package.domain = org.mcfly
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt,ttf
version = 1.0
requirements = python3,kivy==2.2.1,kivymd==1.1.1,requests,urllib3,certifi,android
orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2

[app:android]
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.sdk = 24
android.ndk = 25b
android.allow_backup = true
android.debuggable = true