import re
import uuid
from typing import Union, Optional

def clean_transaction_id(transaction_id: Union[str, int, None]) -> Optional[str]:
    """
    Clean and standardize transaction IDs.

    This function performs the following cleanup strategies:
    1. Converts input to string
    2. Removes non-alphanumeric characters
    3. Truncates to a maximum length
    4. Generates a UUID if input is invalid or empty
    5. Converts to lowercase
    6. Handles different input types

    Args:
        transaction_id: Input transaction ID of various types

    Returns:
        A cleaned, standardized transaction ID string or None
    """
    # Handle None or empty input
    if transaction_id is None:
        return str(uuid.uuid4())

    # Convert to string
    try:
        id_str = str(transaction_id)
    except Exception:
        return str(uuid.uuid4())

    # Remove non-alphanumeric characters and convert to lowercase
    cleaned_id = re.sub(r'[^a-zA-Z0-9]', '', id_str).lower()

    # Truncate to 36 characters (standard UUID length)
    cleaned_id = cleaned_id[:36]

    # Generate a new UUID if the cleaned ID is empty
    return cleaned_id if cleaned_id else str(uuid.uuid4())