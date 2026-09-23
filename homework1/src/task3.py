def check_sign(number):
    if number > 0:
        return "positive"
    elif number < 0:
        return "negative"
    else:
        return "zero"

def get_first_ten_primes():
    primes = []
    candidate = 2
    
    while len(primes) < 10:
        is_prime = True
        # Efficient way of finding prime numbers
        for i in range(2, int(candidate ** 0.5) + 1):
            if candidate % i == 0:
                is_prime = False
                break
        
        if is_prime:
            print(candidate)
            primes.append(candidate)
            
        candidate += 1
        
    return primes

def sum_to_one_hundred():
    total = 0
    current = 1
    
    while current <= 100:
        total += current
        current += 1
        
    return total