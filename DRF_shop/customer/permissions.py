from rest_framework.permissions import BasePermission


class IsStaffOrSuperuserPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_staff or request.user.is_superuser


class HasCompleteAddressPermission(BasePermission):
    message = "You must have a complete address to perform this action."

    def has_permission(self, request, view):
        user = request.user
        use_new_address = request.data.get("use_new_address")

        if use_new_address is True:
            address = request.data.get('delivery_address')
            if (
                address.get('city')
                and address.get('street_address')
                and address.get('apartment_address')
                and address.get('postal_code')
            ):  # Checks if address is complete
                return True
            return False

        if user.is_authenticated:
            address = user.address  # Get user address by related name

            if (
                address.city
                and address.street_address
                and address.apartment_address
                and address.postal_code
            ):
                return True
            return False
        return False


class IsEmailVerifiedPermission(BasePermission):
    message = "Please confirm your email address!"

    def has_permission(self, request, view):
        return request.user.is_confirmed_email
