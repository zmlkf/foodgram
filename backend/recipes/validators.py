import re

from django.core.exceptions import ValidationError

from . import constants


def validate_username(username):
    if username.lower() == 'me':
        raise ValidationError(constants.INVALID_USERNAME)
    invalid_chars = re.sub(r'[\w.@+-]', '', username)
    if invalid_chars:
        raise ValidationError(f'{constants.INVALID_CHARACTERS}: {invalid_chars}')
    return username
