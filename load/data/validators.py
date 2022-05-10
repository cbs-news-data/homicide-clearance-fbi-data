"""contains validator functions for django models"""

from django.core.validators import RegexValidator
from .constants import ORI_REGEX


validate_ori = RegexValidator(ORI_REGEX)
