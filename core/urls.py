from django.urls import path
from . import views

urlpatterns = [
    path("", views.landing, name="landing"),
    path("gesture-login/", views.gesture_login_page, name="gesture_login"),
    path("verify-gesture/", views.verify_gesture, name="verify_gesture"),
    path("leader/dashboard/", views.leader_dashboard, name="leader_dashboard"),
    path("add-zone/", views.add_zone, name="add_zone"),
    path("send-message/", views.send_encrypted_message, name="send_message"),
    path("soldier/messages/", views.soldier_messages, name="soldier_messages"),
    path("soldier/location/", views.soldier_location_page, name="soldier_location"),
    path("check-location/", views.check_location, name="check_location"),
]