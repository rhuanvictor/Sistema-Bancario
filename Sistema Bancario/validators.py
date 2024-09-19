import re

def format_cpf(cpf):
    cpf = re.sub(r'\D', '', cpf)  # Remove non-numeric characters
    if len(cpf) == 11:
        return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
    return cpf

def is_valid_cpf(cpf):
    cpf = re.sub(r'\D', '', cpf)  # Remove non-numeric characters
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    def calculate_digit(cpf, weights):
        total = sum(int(cpf[i]) * weights[i] for i in range(len(weights)))
        digit = (total * 10) % 11
        return 0 if digit == 10 else digit
    weights1 = list(range(10, 1, -1))
    weights2 = list(range(11, 1, -1))
    return (calculate_digit(cpf, weights1) == int(cpf[9]) and
            calculate_digit(cpf, weights2) == int(cpf[10]))
