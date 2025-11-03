from datetime import date

def nights_between(check_in: date, check_out: date) -> int:
    return (check_out - check_in).days
