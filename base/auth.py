import sys
import time
import hashlib
from base.common import gather_input
from base.cache import Cache
from base.color import *
from string import ascii_lowercase, ascii_uppercase, digits, punctuation

class Authorization:
    """This class deals with the authorization menu (Register or Log in)

    Attributes
    ------------
    cache: Cache
        An already defined cache object that manages the file where authentication is kept.
    bookings: Cache
        An already defined cache object that manages the file where bookings are kept.

    """
    def __init__(self, cache: Cache, bookings: Cache):
        self.cache = cache
        self.bookings = bookings
    
    def validify_password(self, password: str) -> bool:
        try:
            assert len(password) > 6
            assert any([i in password for i in ascii_lowercase])
            assert any([i in password for i in ascii_uppercase])
            assert any([i in password for i in digits])
            assert any([i in password for i in punctuation])
            return True
        except:
            return False
    
    def get_authorization(self) -> tuple:
        """
        Shows an authorization menu used to determine 
        whether the user wants to log in or register and deals with the input.
        """
        while True:
            print(title("Cineworld Login"))
            option = gather_input(f"{RED}[{GREEN}0{RED}] {YELLOW}Register\n"
                                  f"{RED}[{GREEN}1{RED}] {YELLOW}Log In\n"
                                  f"{RED}[{GREEN}2{RED}] {YELLOW}Exit\n"
                                  f"{MAGENTA}>>> {GREEN}", req=[0, 1, 2])
            
            if option == 0:
                username = gather_input(f"{YELLOW}Username: {GREEN}", datatype=str, condition=lambda k: k.lower() != 'exit', notreq=[""])
                if self.cache.cached(username): # checking if username is already taken
                    print("Username is already taken! Sorry about that.\n")
                    continue
                first_name = gather_input(f"{YELLOW}First Name: {GREEN}", datatype=str, notreq=[""])
                last_name = gather_input(f"{YELLOW}Last Name: {GREEN}", datatype=str, notreq=[""])
                password = gather_input(f"{YELLOW}Password: {GREEN}", datatype=str, condition=self.validify_password, error_msg="Must be greater than length of 6 and contain 1 of lowercase, uppercase, digit & punctuation.")
                print(f"You've successfully registered as {username}!")
                self.cache.store(
                    {
                        username: {
                            'pw': hashlib.sha256(password.encode()).hexdigest(),
                            'first_name': first_name,
                            'last_name': last_name,
                            'joined': time.time(),
                            'account_type': 'Standard',
                            'other': {}
                        }
                    }
                )
                self.bookings.store({username: []})
                break

            elif option == 1:
                username = input(f"{MAGENTA}Username: {GREEN}").strip()
                if not self.cache.cached(username): # checking if username doesnt exist
                    print("Username does not exist.\n")
                    continue
                password = input(f"{MAGENTA}Password: {GREEN}").strip()
                if self.cache.json[username]['pw'] == hashlib.sha256(password.encode()).hexdigest():
                    print(f"You've successfully logged in as {username}!")
                    break
                else:
                    print("Incorrect password.\n")
                    continue
                
            elif option == 2:
                sys.exit(1)
        
        self.username = username

        return (username, password)
    
    def get_account_type(self):
        return self.cache.json[self.username]['account_type']
    
    def get_account_renewal(self):
        return self.cache.json[self.username]["other"]["renewal"]
    
    def is_admin(self):
        return "admin" in self.cache.json[self.username] and self.cache.json[self.username]["admin"] is True
