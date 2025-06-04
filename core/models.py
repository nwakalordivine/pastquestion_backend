from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils.timezone import now

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, name=None, wallet_balance=1000.00, is_admin=False, is_staff=False):
        if not email:
            raise ValueError("Users must have an email address")
        user = self.model(
            email=self.normalize_email(email),
            name=name,
            wallet_balance=wallet_balance,
            is_admin=is_admin,
            is_staff=is_staff, 
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, name=None):
        user = self.create_user(
            email=email,
            password=password,
            name=name,
            is_admin=True,
            is_staff=True,
        )
        return user

class User(AbstractBaseUser):
    email = models.EmailField(unique=True, max_length=255)
    name = models.CharField(max_length=255)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False) 
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=1000.00)
    created_at = models.DateTimeField(default=now)
    is_banned = models.BooleanField(default=False)
    ban_until = models.DateTimeField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return self.is_admin

    def save(self, *args, **kwargs):
        if self.wallet_balance < 0:
            raise ValueError("Account balance cannot be negative")
        super(User, self).save(*args, **kwargs)


