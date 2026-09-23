def calculate_discount(price, discount):
    try:
        # Treat both inputs like floats
        numeric_price = float(price)
        numeric_discount = float(discount)
    except (ValueError, TypeError):
        raise ValueError("Invalid input: price and discount must be numeric types.")
        
    if numeric_price < 0 or numeric_discount < 0:
        raise ValueError("Price and discount cannot be negative.")
        
    if numeric_discount > 100:
        raise ValueError("Discount cannot exceed 100%.")
        
    final_price = numeric_price * (1 - (numeric_discount / 100))
    return round(final_price, 2)