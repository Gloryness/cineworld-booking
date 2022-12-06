from base.common import get_films, gather_input, is_expiry_date, luhn_algorithm
from base.cache import Cache
from base.auth import Authorization
from base.color import *
from base.bookings import Booking
import datetime

if __name__ == '__main__':
    auth_cache = Cache("authentication.json")
    booking_cache = Cache("bookings.json")

    while True:

        auth = Authorization(auth_cache, booking_cache)
        username, password = auth.get_authorization()
        
        films = get_films()
        booking = Booking(username, films, booking_cache)

        while True:
            print("\n" + title("Cineworld"))

            if auth.get_account_type() == "Cineworld Plus":
                renewal = auth.get_account_renewal()
                due = 0
                while datetime.datetime.now() > datetime.datetime.fromisoformat(renewal):
                    due += 9.99
                    renewal = str(datetime.datetime.fromisoformat(renewal) + datetime.timedelta(days=32))[:10]
                
                if due:
                    print("\n" + title(f"{RED}ATTENTION!"))
                    print(f"{YELLOW}You are due a total of {CYAN}£{due:,} {YELLOW}because of your {MAGENTA}Cineworld Plus {YELLOW}membership.\n"
                          f"If you wish to keep your membership, you must pay the amount due now.")
                    
                    while True:
                        option = gather_input(f"\n{RED}[{GREEN}0{RED}] {YELLOW}Pay Now\n"
                                    f"{RED}[{GREEN}1{RED}] {YELLOW}Cancel\n"
                                    f"{MAGENTA}>>> {GREEN}", req=[0, 1])
                        
                        if option == 0:
                            print(f"{GREEN}Thank you for continuing to support us and you with {CYAN}Cineworld Plus{GREEN}.\n")
                            auth_cache.json[username]["other"].update({"renewal": renewal})
                            auth_cache.store({username: auth_cache.json[username]})
                            break

                        elif option == 1:
                            print(f"\n{GREEN}Are you sure you wish to cancel your {CYAN}Cineworld Plus {GREEN}membership?\n"
                                f"{RED}You will lose your 15% discount on purchasing tickets.")
                            
                            confirm = gather_input(f"{WHITE}Confirm Cancellation {BLUE}[{GREEN}Y{BLUE}/{RED}N{BLUE}]{WHITE}: ", datatype=str.upper, req=['Y', 'N'])
                            if confirm == "N":
                                print(f"{RED}Cancelled cancellation{WHITE}.")
                                continue

                            auth_cache.json[username]["other"].clear()
                            auth_cache.json[username]["account_type"] = "Standard"
                            auth_cache.store({username: auth_cache.json[username]})
                            break

                    print("\n" + title("Cineworld"))

            menu = gather_input(f"{RED}[{GREEN}0{RED}] {CYAN}View or choose available bookings\n"
                                f"{RED}[{GREEN}1{RED}] {CYAN}View booking history\n"
                                f"{RED}[{GREEN}2{RED}] {CYAN}View membership\n"
                                f"{RED}[{GREEN}3{RED}] {CYAN}View prices\n"
                                f"{RED}[{GREEN}4{RED}] {CYAN}Sign up for a Cineworld Plus membership\n"
                                f"{RED}[{GREEN}5{RED}] {CYAN}Sign out\n"
                                f"{RED}[{GREEN}6{RED}] {CYAN}Exit\n"
                                f"{MAGENTA}>>> {GREEN}", req=[0, 1, 2, 3, 4, 5, 6])

            if menu == 0:
                booking.create_booking(auth.get_account_type())
            
            elif menu == 1:
                bookings = booking.get_user_bookings()
                print("\n" + title("Your Booking History"))
                price = 0
                for history in bookings:
                    print(f"{GREEN}Film: {YELLOW}{history['film']}\n"
                        f"{GREEN}When: {YELLOW}{history['when']}\n"
                        f"{GREEN}Adults attending: {YELLOW}{history['adults']}\n"
                        f"{GREEN}Students attending: {YELLOW}{history['students']}\n"
                        f"{GREEN}Children attending: {YELLOW}{history['children']}\n"
                        f"{GREEN}Price: {CYAN}£{history['price']:,}\n")
                    price += history['price']
                print(f"{RED}Total Spent: {YELLOW}£{round(price, 2):,}")

            elif menu == 2:
                print("\n" + title("Cineworld Membership"))
                account_type = auth.get_account_type()
                print(f"{GREEN}Account Creation: {YELLOW}{str(datetime.datetime.fromtimestamp(auth_cache.json[username]['joined']))}")
                print(f"{GREEN}Account Type: {MAGENTA}{account_type}")

                discount = 0
                if account_type == 'Cineworld Plus':
                    print(f"{GREEN}Price: {RED}£9.99 / month {CYAN}(Next Renewal Date: {MAGENTA}{auth.get_account_renewal()}{CYAN})")
                    discount = 15
                print(f"{GREEN}Ticket discounts: {MAGENTA}{discount}%")

            elif menu == 3:
                def calculate_discount(price, membership):
                    discount = 0
                    if membership == 'Cineworld Plus':
                        discount = 15
                    return round(price - ((price / 100) * discount), 2)
                
                discount_applied = 0
                if auth.get_account_type() == "Cineworld Plus":
                    discount_applied = 15

                print("\n" + title("Cineworld Prices"))
                print(f"{YELLOW}Adults (18+) - {MAGENTA}£{calculate_discount(12.99, auth.get_account_type())} {GREEN}per ({RED}{discount_applied}% discount{GREEN})\n"
                    f"{YELLOW}Students (15-17) - {MAGENTA}£{calculate_discount(7.99, auth.get_account_type())} {GREEN}per ({RED}{discount_applied}% discount{GREEN})\n"
                    f"{YELLOW}Children (0-14) - {MAGENTA}£{calculate_discount(7.99, auth.get_account_type())} {GREEN}per ({RED}{discount_applied}% discount{GREEN})")

            elif menu == 4:
                if auth.get_account_type() == "Cineworld Plus":
                    print(f"\n{YELLOW}You already have a {CYAN}Cineworld Plus {YELLOW}membership!")
                    continue

                print("\n" + title("Sign up for a Cineworld Plus membership"))

                print(f"{GREEN}With a {CYAN}Cineworld Plus {GREEN}membership{GREEN} for just {MAGENTA}£9.99 / month{GREEN}, "
                      f"you'll be able to enjoy a {RED}15% discount {GREEN}when purchasing tickets.\n")
                
                confirm = gather_input(f"{WHITE}Confirm {BLUE}[{GREEN}Y{BLUE}/{RED}N{BLUE}]{WHITE}: ", datatype=str.upper, req=['Y', 'N'])
                if confirm == "N":
                    print(f"{RED}Order has been cancelled{WHITE}.")
                    continue
                
                print(f"\n{CYAN}How would you like to pay?")
                
                option = gather_input(f"{RED}[{GREEN}0{RED}] {YELLOW}Credit Card / Debit Card\n"
                                f"{RED}[{GREEN}1{RED}] {YELLOW}Exit\n"
                                f"{MAGENTA}>>> {GREEN}", req=[0, 1])

                if option == 0:
                    print(f"{WHITE}\nType 'exit' to exit at any time.")
                    full_name = gather_input(f"{GREEN}Full Name: {MAGENTA}", condition=lambda k: len(k.split(" ")) >= 2, datatype=str, allow_exit=True)
                    if full_name == "exit":
                        print(f"{RED}Order has been cancelled{WHITE}.")
                        continue
                    
                    card_number = gather_input(f"{GREEN}Card Number: {MAGENTA}", condition=luhn_algorithm, datatype=str, allow_exit=True)
                    if card_number == "exit":
                        print(f"{RED}Order has been cancelled{WHITE}.")
                        continue

                    expiry_date = gather_input(f"{GREEN}Expiry Date (MM/YY): {MAGENTA}", condition=is_expiry_date, datatype=str, allow_exit=True)
                    if expiry_date == "exit":
                        print(f"{RED}Order has been cancelled{WHITE}.")
                        continue

                    cvv = gather_input(f"{GREEN}CVV: {MAGENTA}", condition=lambda k: len(k) == 3, datatype=str, allow_exit=True)
                    if cvv == "exit":
                        print(f"{RED}Order has been cancelled{WHITE}.")
                        continue
                    
                    confirm = gather_input(f"{WHITE}Confirm Order {BLUE}[{GREEN}Y{BLUE}/{RED}N{BLUE}]{WHITE}: ", datatype=str.upper, req=['Y', 'N'])
                    if confirm == "N":
                        print(f"{RED}Order has been cancelled{WHITE}.")
                        continue
                    
                    renewal = str(datetime.datetime.now() + datetime.timedelta(days=32))[:10]
                    print(f"{GREEN}Successfully purchased {CYAN}Cineworld Plus {GREEN}for {MAGENTA}£9.99 / month{GREEN}.")
                    print(f"{GREEN}You will be charged next on {YELLOW}{renewal}")

                    auth_cache.json[username]["other"].update({
                        "name": full_name,
                        "card": card_number,
                        "expiry": expiry_date,
                        "cvv": cvv,
                        "renewal": renewal
                    })
                    auth_cache.json[username].update({
                        "account_type": "Cineworld Plus"
                    })
                    auth_cache.store({username: auth_cache.json[username]})

                elif option == 1:
                    print(f"{RED}Order has been cancelled{WHITE}.")
                    continue

            elif menu == 5:
                print(f"\n{GREEN}[{MAGENTA}{username}{GREEN}] {RED}Signing out...{RESET}\n")
                break

            elif menu == 6:
                print(f"\n{GREEN}We hope you visit again!\n{RED}Exiting...{RESET}")
                quit()