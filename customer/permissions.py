from rest_framework.permissions import BasePermission

from customer.models import UserAddresses


class IsStaffOrSuperuserPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_staff or request.user.is_superuser


class HasCompleteAddressPermission(BasePermission):
    message = "You must have a complete address to perform this action."

    def has_permission(self, request, view):
        user = request.user

        if request.data.get("use_new_address") is False:
            # Checks if the user is using a new address.
            # If not we will check the existing address
            if user.is_authenticated:
                try:
                    address = user.address  # Get user address by related name
                except UserAddresses.DoesNotExist:
                    return False

                if (
                    address.city
                    and address.street_address
                    and address.apartment_address
                    and address.postal_code
                ):
                    return True
                else:
                    return False

            return False


class IsEmailVerifiedPermission(BasePermission):
    message = "Please confirm your email address!"

    def has_permission(self, request, view):
        return request.user.is_confirmed_email
