from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from .models import Customer
import logging

logger = logging.getLogger(__name__)

class CustomerAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        logger.info("CustomerAuthBackend.authenticate called")
        
        # Get the phone number from either username or phone_number kwargs
        phone_number = username or kwargs.get('phone_number')
        if phone_number is None or password is None:
            logger.error("Missing phone_number or password")
            return None
        
        logger.info(f"Attempting to authenticate user with phone number: {phone_number}")
        
        try:
            # Try to get the customer by phone number
            customer = Customer.objects.get(phone_number=phone_number)
            logger.info(f"Found customer: {customer}")
            
            # Check the password
            if customer.check_password(password):
                logger.info("Password check successful")
                return customer
            else:
                logger.error("Password check failed")
                return None
                
        except Customer.DoesNotExist:
            logger.error(f"No customer found with phone number: {phone_number}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during authentication: {str(e)}")
            return None

    def get_user(self, user_id):
        try:
            return Customer.objects.get(pk=user_id)
        except Customer.DoesNotExist:
            return None 