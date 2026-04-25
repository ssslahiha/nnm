import cv2
import mediapipe as mp
import base64
import numpy as np
import json
from math import radians, sin, cos, sqrt, atan2
from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.utils import timezone

from .models import SecurityZone, SecureMessage


# ================================
# إعدادات الذكاء الاصطناعي لليد (Gesture Login)
# ================================
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7)


# ================================
# صفحة البداية
# ================================
def landing(request):
    return render(request, "landing.html")


# ================================
# تسجيل دخول القائد عبر حركة اليد ✌️
# ================================
def verify_gesture(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        image_data = data.get('image')

        # تحويل الصورة من المتصفح إلى بايثون
        format, imgstr = image_data.split(';base64,')
        nparr = np.frombuffer(base64.b64decode(imgstr), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # فحص حركة اليد
        results = hands.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

        if results.multi_hand_landmarks:
            landmarks = results.multi_hand_landmarks[0].landmark

            # علامة النصر ✌️ (السبابة والوسطى مرفوعين)
            if landmarks[8].y < landmarks[6].y and landmarks[12].y < landmarks[10].y:
                user = User.objects.get(username='Commander')
                login(request, user)
                return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'failed'})


# ================================
# دالة حساب المسافة بين نقطتين GPS
# ================================
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371000  # نصف قطر الأرض بالمتر
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c


# ================================
# لوحة القائد
# ================================
@login_required
def leader_dashboard(request):
    if not request.user.is_staff:
        return redirect("landing")

    zones = SecurityZone.objects.filter(created_by=request.user)
    soldiers = User.objects.filter(is_staff=False)
    messages = SecureMessage.objects.filter(sender=request.user).order_by("-sent_at")

    return render(request, "leader_dashboard.html", {
        "zones": zones,
        "soldiers": soldiers,
        "messages": messages,
    })


# ================================
# إضافة منطقة أمنية
# ================================
@login_required
def add_zone(request):
    if not request.user.is_staff:
        return redirect("landing")

    if request.method == "POST":
        SecurityZone.objects.create(
            name=request.POST["name"],
            description=request.POST["description"],
            latitude=float(request.POST["latitude"]),
            longitude=float(request.POST["longitude"]),
            radius_meters=int(request.POST["radius"]),
            created_by=request.user
        )
        return redirect("leader_dashboard")

    return render(request, "add_zone.html")


# ================================
# القائد يرسل رسالة مشفّرة
# ================================
@login_required
def send_encrypted_message(request):
    if not request.user.is_staff:
        return redirect("landing")

    soldiers = User.objects.filter(is_staff=False)
    zones = SecurityZone.objects.filter(created_by=request.user)

    if request.method == "POST":
        receiver = User.objects.get(id=request.POST["receiver"])
        zone = SecurityZone.objects.get(id=request.POST["zone"])
        duration = int(request.POST["duration"])
        message_text = request.POST["message"]

        expires_at = timezone.now() + timedelta(minutes=duration)

        msg = SecureMessage(
            sender=request.user,
            receiver=receiver,
            zone=zone,
            expires_at=expires_at
        )
        msg.encrypt_text(message_text)
        msg.save()

        return redirect("leader_dashboard")

    return render(request, "leader_send.html", {
        "soldiers": soldiers,
        "zones": zones
    })


# ================================
# الجندي يشاهد رسائله (مشفّرة)
# ================================
@login_required
def soldier_messages(request):
    if request.user.is_staff:
        return redirect("landing")

    messages = SecureMessage.objects.filter(receiver=request.user).order_by("-sent_at")

    return render(request, "soldier_view.html", {
        "messages": messages
    })


# ================================
# صفحة GPS للجندي
# ================================
@login_required
def soldier_location_page(request):
    if request.user.is_staff:
        return redirect("landing")

    return render(request, "soldier_location.html")


# ================================
# API: التحقق من موقع الجندي
# ================================
@login_required
def check_location(request):
    if request.user.is_staff:
        return JsonResponse({"error": "Not allowed"}, status=403)

    data = json.loads(request.body)
    soldier_lat = float(data["lat"])
    soldier_lng = float(data["lng"])

    messages = SecureMessage.objects.filter(receiver=request.user)

    for msg in messages:
        if msg.is_expired():
            continue

        zone = msg.zone
        distance = calculate_distance(
            soldier_lat, soldier_lng,
            zone.latitude, zone.longitude
        )

        if distance <= zone.radius_meters:
            return JsonResponse({
                "status": "inside",
                "message": msg.decrypt_text(),
                "zone": zone.name
            })

    return JsonResponse({"status": "outside"})
