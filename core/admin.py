
from django.contrib import admin
from .models import SecurityZone, SecureMessage

@admin.register(SecurityZone)
class SecurityZoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'latitude', 'longitude', 'radius_meters')

@admin.register(SecureMessage)
class SecureMessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'zone', 'is_read', 'sent_at')
    readonly_fields = ('encrypted_payload',)  # منع رؤية النص المشفر