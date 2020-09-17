from django.contrib.auth.base_user import BaseUserManager

"""
Used for customizing authentication and setting email as a unique field used for authentication 
instead of username
"""
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, is_active = True, is_staff = False, is_admin = False, is_business = False):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')
        if not password:
            raise ValueError('Users must have a password')

        user = self.model(
            email = self.normalize_email(email),
        )

        user.set_password(password)
        user.active = is_active
        user.staff = is_staff
        user.admin = is_admin 
        user.business = is_business
        user.save(using=self._db)
        return user

    def create_staffuser(self, email, password):
        """
        Creates and saves a staff user with the given email and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            email,
            password = password,
        )
        user.staff = True
        user.admin = True
        user.save(using = self._db)
        return user