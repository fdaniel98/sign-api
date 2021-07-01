def main_route():
    """Welcome message for the API."""
    # Message to the user
    message = {
        'apiVersion': 'v1.0',
        'status': 200,
        'message': 'Welcome to the Sign Flask API'
    }
    # Returning the object
    return message
