from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _

class CustomerManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('The Phone Number field must be set')
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(phone_number, password, **extra_fields)

class Customer(AbstractUser):
    username = models.CharField(_('username'), max_length=150, unique=True)
    phone_number = models.CharField(_('phone number'), max_length=15, unique=True)
    location = models.CharField(_('location'), max_length=255, blank=True)
    is_verified = models.BooleanField(_('verified'), default=False)
    
    # Add related_name to avoid clashes
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=_('groups'),
        blank=True,
        related_name='customer_set',
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=_('user permissions'),
        blank=True,
        related_name='customer_set',
        help_text=_('Specific permissions for this user.'),
    )
    
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    objects = CustomerManager()

    class Meta:
        verbose_name = _('customer')
        verbose_name_plural = _('customers')
        db_table = 'registration_customer'

    def __str__(self):
        return f"{self.get_full_name()} ({self.phone_number})"
