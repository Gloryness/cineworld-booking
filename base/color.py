from colorama import Style, Fore

BRIGHT = Style.BRIGHT
NORMAL = Style.NORMAL
DIM = Style.DIM
BLACK = Fore.LIGHTBLACK_EX
RED = Fore.LIGHTRED_EX
DARK_RED = Fore.RED
GREEN = Fore.LIGHTGREEN_EX
DARK_GREEN = Fore.GREEN
YELLOW = Fore.LIGHTYELLOW_EX
BLUE = Fore.LIGHTBLUE_EX
DARK_BLUE = Fore.BLUE
MAGENTA = Fore.LIGHTMAGENTA_EX
DARK_MAGENTA = Fore.MAGENTA
CYAN = Fore.LIGHTCYAN_EX
DARK_CYAN = Fore.CYAN
WHITE = Fore.LIGHTWHITE_EX
RESET = Style.RESET_ALL

def title(text):
    return f"{RED}--------------- {GREEN}{text} {RED}---------------{RESET}"