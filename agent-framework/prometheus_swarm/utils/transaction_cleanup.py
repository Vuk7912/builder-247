import re
import uuid
import unicodedata
from typing import Union, Optional

def transliterate_unicode(text: str) -> str:
    """
    Transliterate unicode characters to their closest ASCII representation.
    
    Args:
        text (str): Input text with potential unicode characters
    
    Returns:
        str: ASCII transliterated text
    """
    if not text:
        return ""
    
    # Normalize unicode characters
    normalized = unicodedata.normalize('NFKD', text)
    
    # Remove characters that don't translate well
    normalized = ''.join(c for c in normalized if not unicodedata.combining(c))
    
    # Transliterate to ASCII and remove non-ascii characters
    transliterated = normalized.encode('ascii', 'ignore').decode('utf-8')
    
    return transliterated.lower() or text

def clean_transaction_id(transaction_id: Union[str, int, None]) -> str:
    """
    Clean and standardize transaction IDs.

    This function performs the following cleanup strategies:
    1. Converts input to string
    2. Removes non-alphanumeric characters
    3. Transliterates unicode characters
    4. Truncates to a maximum length
    5. Generates a UUID if input is invalid or empty
    6. Converts to lowercase
    7. Handles different input types

    Args:
        transaction_id: Input transaction ID of various types

    Returns:
        A cleaned, standardized transaction ID string
    """
    # Explicit type checks for problematic inputs
    if (transaction_id is None or 
        transaction_id == "" or 
        (isinstance(transaction_id, str) and transaction_id.strip() == "") or
        not hasattr(transaction_id, '__str__') or 
        isinstance(transaction_id, (object, Exception))):
        return str(uuid.uuid4())

    # Ensure safe string conversion
    try:
        id_str = str(transaction_id).strip()
    except Exception:
        return str(uuid.uuid4())

    # Transliterate and remove non-alphanumeric characters
    transliterated_id = transliterate_unicode(id_str)
    cleaned_id = re.sub(r'[^a-z0-9]', '', transliterated_id)

    # Truncate to 36 characters (standard UUID length)
    cleaned_id = cleaned_id[:36]

    # Generate a new UUID if the cleaned ID is empty
    return cleaned_id if cleaned_id else str(uuid.uuid4())