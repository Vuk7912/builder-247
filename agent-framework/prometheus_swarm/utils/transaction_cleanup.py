import re
import uuid
import unicodedata
from typing import Union, Optional

def clean_transaction_id(transaction_id: Union[str, int, None]) -> Optional[str]:
    """
    Clean and standardize transaction IDs.

    This function performs the following cleanup strategies:
    1. Converts input to string
    2. Removes non-alphanumeric characters
    3. Normalizes unicode characters
    4. Truncates to a maximum length
    5. Generates a UUID if input is invalid or empty
    6. Converts to lowercase
    7. Handles different input types

    Args:
        transaction_id: Input transaction ID of various types

    Returns:
        A cleaned, standardized transaction ID string or None
    """
    # Handle None or empty input
    if transaction_id is None:
        return str(uuid.uuid4())

    # Convert to string, handling different types
    try:
        id_str = str(transaction_id)
    except Exception:
        return str(uuid.uuid4())

    # Normalize unicode characters and remove non-alphanumeric characters
    normalized_id = unicodedata.normalize('NFKD', id_str).encode('ascii', 'ignore').decode('utf-8')
    cleaned_id = re.sub(r'[^a-zA-Z0-9]', '', normalized_id).lower()

    # Truncate to 36 characters (standard UUID length)
    cleaned_id = cleaned_id[:36]

    # Generate a new UUID if the cleaned ID is empty
    return cleaned_id if cleaned_id else str(uuid.uuid4())