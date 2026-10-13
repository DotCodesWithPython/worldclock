[app]
title = World Clock
package.name = worldclock
package.domain = org.worldclock
source.dir = .
source.include_exts = py
version = 1.0
requirements = python3,kivy,plyer,tzdata,pyjnius
orientation = portrait
fullscreen = 0
android.permissions = POST_NOTIFICATIONS
android.api = 34
android.minapi = 24
android.archs = arm64-v8a, armeabi-v7a
p4a.branch = v2024.01.21

[buildozer]
log_level = 2
