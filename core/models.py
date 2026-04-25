
# كود يدمج التشفير والمواقع الجغرافية

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from cryptography.fernet import Fernet
from django.conf import settings

# 1. جدول المناطق الأمنية: يجمع بين البيانات الجغرافية والإدارية
class SecurityZone(models.Model):
    name = models.CharField("اسم المنطقة/العملية", max_length=100)
    description = models.TextField("وصف المهمة", blank=True)
    latitude = models.FloatField("خط العرض")
    longitude = models.FloatField("خط الطول")
    radius_meters = models.IntegerField("نطاق الأمان (متر)", default=100)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="المسؤول")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# 2. جدول الرسائل المشفرة والذكية
class SecureMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    zone = models.ForeignKey(SecurityZone, on_delete=models.CASCADE, verbose_name="المنطقة الأمنية")
    
    # التشفير: البيانات تُخزن كرموز غير مقروءة
    encrypted_payload = models.BinaryField("محتوى مشفر")
    
    # الإدارة: تتبع الوقت والحالة
    sent_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField("تاريخ انتهاء الصلاحية", null=True, blank=True)
    is_read = models.BooleanField("تمت القراءة", default=False)

    # دالة التشفير
    def encrypt_text(self, plain_text):
        f = Fernet(settings.ENCRYPTION_KEY)
        self.encrypted_payload = f.encrypt(plain_text.encode())

    # دالة فك التشفير (تُستخدم برمجياً عند التحقق من الموقع والوقت)
    def decrypt_text(self):
        if self.is_expired():
            return "هذه الرسالة منتهية الصلاحية ولا يمكن فك تشفيرها."
        f = Fernet(settings.ENCRYPTION_KEY)
        return f.decrypt(self.encrypted_payload).decode()

    # دالة التحقق من صلاحية الوقت
    def is_expired(self):
        return self.expires_at and timezone.now() >= self.expires_at

    def __str__(self):
        return f"رسالة من {self.sender} إلى {self.receiver}"