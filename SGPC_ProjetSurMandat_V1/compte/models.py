# Create your models here.
from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)


class MyUserManager(BaseUserManager):
    def create_user(self, email, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, date_of_birth, password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class SGPC_Utilisateur(AbstractBaseUser):
    UTI_EMAIL = models.EmailField(
        verbose_name='email',
        max_length=255,
        unique=True,
    )
    UTI_PRENOM = models.CharField(max_length=30, unique=False)
    UTI_NOM = models.CharField(max_length=30, unique=False)
    UTI_DATENAISSANCE = models.DateField(auto_now_add=False)
    UTI_NUMEROTEL = models.CharField(max_length=20, unique=True)
    UTI_RUE = models.CharField(max_length=60)
    UTI_NUMERORUE = models.PositiveIntegerField(null=False)
    UTI_CODEPOSTALE = models.PositiveIntegerField(null=False)
    UTI_LOCALITE = models.CharField(max_length=30, unique=False)
    UTI_is_deleted = models.BooleanField(default=False)
    UTI_is_active = models.BooleanField(default=True)
    UTI_is_admin = models.BooleanField(default=False)
    objects = MyUserManager()

    USERNAME_FIELD = 'UTI_EMAIL'
    REQUIRED_FIELDS = ['UTI_PRENOM','UTI_NOM','UTI_DATENAISSANCE','UTI_RUE','UTI_NUMERORUE','UTI_CODEPOSTALE','UTI_LOCALITE',]

    def __str__(self):
        return self.UTI_NOM + ' '+ self.UTI_PRENOM

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.UTI_is_admin

