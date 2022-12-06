from base.color import *
from typing import Optional, TypeVar, Callable
from fake_useragent import UserAgent
import requests
import datetime

T = TypeVar('T', int, float, str, dict, object)

def luhn_algorithm(card: str):
    res = 0
    second = False

    for i in range(len(card) - 1, -1, -1):
        d = ord(card[i]) - ord('0')

        if second:
            d *= 2
        
        res += d // 10
        res += d % 10

        second = not second
    
    return res % 10 == 0

def is_expiry_date(date: str):
    if '/' not in date:
        return False

    split = date.split('/')
    if len(split) != 2:
        return False
    
    if not (len(split[0]) == 2 and len(split[1]) == 2):
        return False
    
    if split[0].isdigit() and split[1].isdigit():
        a, b = list(map(int, split))
        b = 2000 + b
        if (a > 0 and a <= 12) and b >= datetime.datetime.now().year:
            return True
        else:
            return False
    else:
        return False

def get_films():
    today = str(datetime.datetime.now())[:10]
    ua = UserAgent()
    user_agent = ua.random
    url = f"https://www.cineworld.co.uk/uk/data-api-service/v1/quickbook/10108/film-events/in-cinema/109/at-date/{today}?attr=&lang=en_GB"
    return requests.get(url, headers={'User-Agent': user_agent}).json()

def gather_input(
    input_string: str,
    datatype: Optional[T] = int,
    req: list = [],
    notreq: list = [],
    condition: Optional[Callable] = None,
    allow_exit: bool = False
) -> Optional[T]:
    """
    Create an input and return the users input - it will catch for invalid inputs.

    Parameters
    -----------
    input_string: str
        This will be passed into the builtin input() function. 
    datatype: Optional[T]
        The data type to convert the input into - if it cannot be converted it will ask the user again.
    req: list
        A list with all possible inputs and if the user input is not a match it will ask again.
        - If [], anything is allowed.
    notreq: list
        A list with all inputs that should NOT be allowed
        - If [], nothing will happen.
    condition: Optional[Callable]
        A callable object allowing one parameter (which is the input received by the user)
        and is called when user has entered the input.
        If the callable returns False, ask user again.
    allow_exit: bool
        Allow the user to type 'exit' to exit.
    
    Returns
    -------
    Optional[T]
        The input that was received from the user. 
    """
    assert callable(condition) or condition is None

    def support_user_exit(input_string, datatype, allow_exit=False):
        if allow_exit:
            res = str(input(input_string).strip())
            if res.lower() == "exit":
                return 'exit'
            return datatype(res)
        else:
            return datatype(input(input_string).strip())

    while True:
        try:
            menu = support_user_exit(input_string, datatype, allow_exit=allow_exit)
            if allow_exit and menu == 'exit':
                return menu
        except:
            print(f"{RED}Invalid input.{RESET}")
            continue
        if req:
            if menu not in req:
                print(f"{RED}Invalid input.{RESET}")
                continue
        elif notreq:
            if menu in notreq:
                print(f"{RED}Invalid input.{RESET}")
                continue
        if condition:
            try:
                if not condition(menu):
                    print(f"{RED}Invalid input.{RESET}")
                    continue
            except:
                print(f"{RED}Invalid input.{RESET}")
                continue
        return menu