"""Persistent two-time-zone notification, updated once per minute."""
import json
import os
import time
from datetime import datetime
from zoneinfo import ZoneInfo
from jnius import autoclass

PythonService = autoclass("org.kivy.android.PythonService")
service = PythonService.mService
Context = autoclass("android.content.Context")
Notification = autoclass("android.app.Notification")
NotificationChannel = autoclass("android.app.NotificationChannel")
NotificationManager = autoclass("android.app.NotificationManager")
Build = autoclass("android.os.Build")

channel_id = "world_clock_live"
manager = service.getSystemService(Context.NOTIFICATION_SERVICE)
if Build.VERSION.SDK_INT >= 26:
    channel = NotificationChannel(channel_id, "Live world clocks", NotificationManager.IMPORTANCE_LOW)
    channel.setDescription("Shows your local time and another selected time zone")
    manager.createNotificationChannel(channel)

def current(tz):
    return datetime.now(ZoneInfo(tz)) if tz else datetime.now().astimezone()

def update():
    try:
        settings = json.loads(os.environ.get("PYTHON_SERVICE_ARGUMENT", "{}"))
    except Exception:
        settings = {}
    clocks = settings.get("clocks") or [{"name": "My time", "tz": None}]
    main_index = min(max(int(settings.get("main", 0)), 0), len(clocks) - 1)
    selected = clocks[main_index]
    other = next((c for i, c in enumerate(clocks) if i != main_index), None)
    local = next((c for c in clocks if c.get("tz") is None), {"name": "My time", "tz": None})
    first = local
    second = selected if selected is not local else other
    if second is None:
        second = {"name": "Georgia, USA", "tz": "America/New_York"}
    title = "World Clock"
    body = "{}: {}   |   {}: {}".format(
        first["name"], current(first.get("tz")).strftime("%H:%M"),
        second["name"], current(second.get("tz")).strftime("%H:%M"))
    builder = Notification.Builder(service, channel_id) if Build.VERSION.SDK_INT >= 26 else Notification.Builder(service)
    builder.setContentTitle(title)
    builder.setContentText(body)
    builder.setSmallIcon(service.getApplicationInfo().icon)
    builder.setOngoing(True)
    builder.setOnlyAlertOnce(True)
    notification = builder.build()
    manager.notify(1, notification)

while True:
    try:
        update()
    except Exception as exc:
        print("World Clock service update failed:", exc)
    time.sleep(max(1, 60 - datetime.now().second))
