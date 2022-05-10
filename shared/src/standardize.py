"""contains functions for standardizing fields that exist across multiple datasets"""


def standardize_ori(ori):
    """converts agency ORIs to the longer format"""

    if isinstance(ori, str) and len(ori) == 7:
        return ori + "00"

    return ori
