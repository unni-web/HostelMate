from django.db import models
from django.contrib.auth.models import User
from django.db.models.fields import CharField
from app.constants import PaymentStatus
from django.utils.translation import gettext_lazy as _



class Hostel(models.Model):

    CATEGORY_CHOICES = [
        ('gents', 'Gents'),
        ('ladies', 'Ladies'),
    ]

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='hostels'
    )

    name = models.CharField(max_length=200)
    category = models.CharField(
        max_length=10,
        choices=CATEGORY_CHOICES
    )
    location = models.CharField(max_length=200)

    beds_available = models.PositiveIntegerField()
    price = models.PositiveIntegerField(help_text="Price per bed")

    # 🔥 NEW
    image = models.ImageField(
        upload_to='hostels/',
        default='hostels/default.jpg'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.category})"


class BookingRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    is_paid = models.BooleanField(default=False)   # 🔥 NEW
    requested_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} → {self.hostel.name}"


class HostelReview(models.Model):
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()  # 1–5
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('hostel', 'user')

    def __str__(self):
        return f"{self.hostel.name} - {self.rating}"


