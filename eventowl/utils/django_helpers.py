def set_if_different(obj, attr, value):
    current = getattr(obj, attr)
    different = current != value
    
    if different:
        setattr(obj, attr, value)
        
    return different