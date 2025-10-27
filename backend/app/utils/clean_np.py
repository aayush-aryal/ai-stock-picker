import numpy as np
def clean_for_sqlalchemy(obj):
    """Convert numpy types and other non-serializable types to plain Python."""
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, (np.generic,)):
        return obj.item()
    if isinstance(obj, list):
        return [clean_for_sqlalchemy(i) for i in obj]
    if isinstance(obj, dict):
        return {k: clean_for_sqlalchemy(v) for k, v in obj.items()}
    return obj