from base.common import get_films, gather_input, is_expiry_date, luhn_algorithm
from base.cache import Cache
from base.auth import Authorization
from base.color import *
from base.bookings import Booking
from collections import Counter
import datetime
import msvcrt as m

if __name__ == '__main__':
    auth_cache = Cache("authentication.json")
    booking_cache = Cache("bookings.json")

    while True:

        auth = Authorization(auth_cache, booking_cache)
        username, password = auth.get_authorization()
        
        films = get_films()
        booking = Booking(username, films, booking_cache)
        mainloop = 0

        while True:
            if mainloop >= 1:
                print(f"\n{DARK_MAGENTA}Press any key to continue...")
                m.getch()
                
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
            
            if not auth.is_admin():
                extra = f"{RED}[{GREEN}5{RED}] {CYAN}Sign out\n" \
                        f"{RED}[{GREEN}6{RED}] {CYAN}Exit\n"
            else:
                extra = f"{RED}[{GREEN}5{RED}] {CYAN}Admin Panel\n" \
                        f"{RED}[{GREEN}6{RED}] {CYAN}Sign out\n" \
                        f"{RED}[{GREEN}7{RED}] {CYAN}Exit\n"

            mainloop += 1

            menu = gather_input(f"{RED}[{GREEN}0{RED}] {CYAN}View or choose available bookings\n"
                                f"{RED}[{GREEN}1{RED}] {CYAN}View booking history\n"
                                f"{RED}[{GREEN}2{RED}] {CYAN}View membership\n"
                                f"{RED}[{GREEN}3{RED}] {CYAN}View prices\n"
                                f"{RED}[{GREEN}4{RED}] {CYAN}Sign up for a Cineworld Plus membership\n"
                                f"{extra}"
                                f"{MAGENTA}>>> {GREEN}", req=[0, 1, 2, 3, 4, 5, 6] + ([7] if auth.is_admin() else []))

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
                print(f"{GREEN}Account Type: {MAGENTA}{account_type}" + (f" {RED}[ADMIN]" if auth.is_admin() else ""))

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
            
            elif not auth.is_admin():
                if menu == 5:
                    print(f"\n{GREEN}[{MAGENTA}{username}{GREEN}] {RED}Signing out...{RESET}\n")
                    break

                elif menu == 6:
                    print(f"\n{GREEN}We hope you visit again!\n{RED}Exiting...{RESET}")
                    quit()
            
            elif auth.is_admin():
                if menu == 5:
                    adminloop = 0
                    while True:
                        if adminloop >= 1:
                            print(f"\n{DARK_MAGENTA}Press any key to continue...")
                            m.getch()

                        adminloop += 1

                        print("\n" + title("Cineworld Admin Panel"))
                        option = gather_input(f"{YELLOW}[{RED}0{YELLOW}] {GREEN}View all users\n"
                                            f"{YELLOW}[{RED}1{YELLOW}] {GREEN}View all users with a membership\n"
                                            f"{YELLOW}[{RED}2{YELLOW}] {GREEN}View all users without a membership\n"
                                            f"{YELLOW}[{RED}3{YELLOW}] {GREEN}Show total bookings for each film\n"
                                            f"{YELLOW}[{RED}4{YELLOW}] {GREEN}Refund a users membership\n"
                                            f"{YELLOW}[{RED}5{YELLOW}] {GREEN}Modify a users membership\n"
                                            f"{YELLOW}[{RED}6{YELLOW}] {GREEN}Remove a users membership\n"
                                            f"{YELLOW}[{RED}7{YELLOW}] {GREEN}Refund a users booking\n"
                                            f"{YELLOW}[{RED}8{YELLOW}] {GREEN}Remove a users booking\n"
                                            f"{YELLOW}[{RED}9{YELLOW}] {GREEN}Exit\n"
                                            f"{MAGENTA}>>> {RED}", req=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
                        
                        if option in [0, 1, 2]: # View users
                            
                            if option == 0:
                                print("\n" + title("All Users"))
                            elif option == 1:
                                print("\n" + title("All Users (with a membership)"))
                            elif option == 2:
                                print("\n" + title("All Users (without a membership)"))

                            if option == 0:
                                filtered = auth_cache.json
                            elif option == 1:
                                filtered = list(filter(lambda k: auth_cache.json[k]['account_type'] == 'Cineworld Plus', auth_cache.json))
                            elif option == 2:
                                filtered = list(filter(lambda k: auth_cache.json[k]['account_type'] == 'Standard', auth_cache.json))

                            for user in filtered:
                                obj = auth_cache.json[user]
                                user_bookings = booking_cache.json[user]
                                total = adult = student = child = 0
                                for film in user_bookings:
                                    total += film['adults'] + film['students'] + film['children']
                                    adult += film['adults']
                                    student += film['students']
                                    child += film['children']
                                print(f"{RED}USERNAME: {MAGENTA}{user}")
                                print(f"{GREEN}Account Creation: {YELLOW}{str(datetime.datetime.fromtimestamp(obj['joined']))}")
                                print(f"{GREEN}Account Type: {YELLOW}{obj['account_type']}" + (f" {RED}[ADMIN]" if "admin" in obj and obj["admin"] else ""))
                                print(f"{GREEN}First Name: {YELLOW}{obj['first_name']}")
                                print(f"{GREEN}Last Name: {YELLOW}{obj['last_name']}")
                                print(f"{GREEN}Films watched: {YELLOW}{len(user_bookings):,}")
                                print(f"{GREEN}Total tickets bought: {YELLOW}{total:,}")
                                print(f"{GREEN}Adult tickets bought: {YELLOW}{adult:,}")
                                print(f"{GREEN}Student tickets bought: {YELLOW}{student:,}")
                                print(f"{GREEN}Child tickets bought: {YELLOW}{child:,}\n")
                        
                        elif option == 3: # Total bookings
                            print("\n" + title("Total bookings for each film"))

                            all_films = Counter()
                            for films in booking_cache.json.values():
                                for film in films:
                                    all_films[film['film']] += 1
                            
                            for index, film in enumerate(all_films.most_common(), start=1):
                                print(f"{MAGENTA}{index}{WHITE}. {CYAN}{film[0]} {RED}[{film[1]:,}]")
                        
                        elif option == 4: # Refund a users membership
                            print("\n" + title("Refund a users membership"))
                            user_to_refund = gather_input(f"{MAGENTA}User to refund: {YELLOW}",
                                                          datatype=str, condition=lambda k: k in auth_cache.json, error_msg="Username does not exist.", allow_exit=True)
                            if user_to_refund == "exit":
                                print(f"{RED}Refund has been cancelled{WHITE}.")
                                continue
                            user_obj = auth_cache.json[user_to_refund]

                            if user_obj['account_type'] != 'Cineworld Plus':
                                print(f"{RED}This user does not have an active membership.")
                                continue

                            users_first_name = gather_input(f"{MAGENTA}Please confirm users first name that was used with their payment method: {YELLOW}", datatype=str.lower, condition=lambda k: user_obj['other']['name'].split()[0].lower() == k, error_msg="Users first name does not match")
                            users_last_name = gather_input(f"{MAGENTA}Please confirm users last name that was used with their payment method: {YELLOW}", datatype=str.lower, condition=lambda k: user_obj['other']['name'].split()[1].lower() == k, error_msg="Users last name does not match")

                            confirm = gather_input(f"\n{GREEN}You are about to refund {CYAN}{user_to_refund}'s {GREEN}membership.\n"
                                                   f"{WHITE}Confirm {BLUE}[{GREEN}Y{BLUE}/{RED}N{BLUE}]{WHITE}: ", datatype=str.upper, req=['Y', 'N'])
                            if confirm == "N":
                                print(f"{RED}Refund has been cancelled{WHITE}.")
                                continue

                            auth_cache.json[user_to_refund]['other'].clear()
                            auth_cache.json[user_to_refund]['account_type'] = "Standard"
                            auth_cache.store({user_to_refund: auth_cache.json[user_to_refund]})
                            
                            print(f"\n{GREEN}Successfully refunded {CYAN}{user_to_refund}'s {GREEN}membership.")
                        
                        elif option == 5: # Modify a users membership
                            print("\n" + title("Modify a users membership"))
                            user_to_modify = gather_input(f"{MAGENTA}User to modify: {YELLOW}",
                                                          datatype=str, condition=lambda k: k in auth_cache.json, error_msg="Username does not exist.", allow_exit=True)
                            if user_to_modify == "exit":
                                print(f"{RED}Modification has been cancelled{WHITE}.")
                                continue
                            user_obj = auth_cache.json[user_to_modify]

                            if user_obj['account_type'] != 'Cineworld Plus':
                                print(f"{RED}This user does not have an active membership.")
                                continue

                            while True:
                            
                                option = gather_input(f"{MAGENTA}What would you like to modify?\n"
                                                    f"{RED}[{YELLOW}0{RED}] {BLUE}Full Name\n"
                                                    f"{RED}[{YELLOW}1{RED}] {BLUE}Card Number\n"
                                                    f"{RED}[{YELLOW}2{RED}] {BLUE}Expiry Date\n"
                                                    f"{RED}[{YELLOW}3{RED}] {BLUE}CVV\n"
                                                    f"{RED}[{YELLOW}4{RED}] {BLUE}Renewal Date\n"
                                                    f"{RED}[{YELLOW}5{RED}] {BLUE}Exit\n"
                                                    f"{MAGENTA}>>> {YELLOW}", req=[0, 1, 2, 3, 4, 5])
                                
                                full_name = user_obj['other']['name']
                                card_number = user_obj['other']['card']
                                expiry_date = user_obj['other']['expiry']
                                cvv = user_obj['other']['cvv']
                                renewal = user_obj['other']['renewal']
                                
                                if option == 0:
                                    print(f"\n{WHITE}Type 'exit' to exit.")
                                    full_name_ = gather_input(f"{GREEN}New Full Name: {MAGENTA}", condition=lambda k: len(k.split(" ")) >= 2, datatype=str, allow_exit=True)
                                    if full_name_ == "exit":
                                        print(f"{RED}Modification has been cancelled{WHITE}.")
                                        continue
                                    full_name = full_name_

                                elif option == 1:
                                    print(f"\n{WHITE}Type 'exit' to exit.")
                                    card_number_ = gather_input(f"{GREEN}New Card Number: {MAGENTA}", condition=luhn_algorithm, datatype=str, allow_exit=True)
                                    if card_number_ == "exit":
                                        print(f"{RED}Modification has been cancelled{WHITE}.")
                                        continue
                                    card_number = card_number_

                                elif option == 2:
                                    print(f"\n{WHITE}Type 'exit' to exit.")
                                    expiry_date_ = gather_input(f"{GREEN}New Expiry Date (MM/YY): {MAGENTA}", condition=is_expiry_date, datatype=str, allow_exit=True)
                                    if expiry_date_ == "exit":
                                        print(f"{RED}Modification has been cancelled{WHITE}.")
                                        continue
                                    expiry_date = expiry_date_

                                elif option == 3:
                                    print(f"\n{WHITE}Type 'exit' to exit.")
                                    cvv_ = gather_input(f"{GREEN}New CVV: {MAGENTA}", condition=lambda k: len(k) == 3, datatype=str, allow_exit=True)
                                    if cvv_ == "exit":
                                        print(f"{RED}Modification has been cancelled{WHITE}.")
                                        continue
                                    cvv = cvv_
                                
                                elif option == 4:
                                    days_to_add = gather_input(f"\n{MAGENTA}Current Renewal Date: {renewal}\n"
                                                               f"{YELLOW}Amount of days to add (use negative numbers to subtract): ")

                                    renewal_ = str(datetime.datetime.fromisoformat(renewal) + datetime.timedelta(days=days_to_add))[:10]
                                    print(f"{GREEN}New Renewal Date: {renewal_}")

                                    confirm = gather_input(f"{WHITE}Confirm {BLUE}[{GREEN}Y{BLUE}/{RED}N{BLUE}]{WHITE}: ", datatype=str.upper, req=['Y', 'N'])
                                    if confirm == "N":
                                        print(f"{RED}Modification has been cancelled{WHITE}.")
                                        continue

                                    renewal = renewal_

                                elif option == 5:
                                    print(f"\n{RED}Exiting user membership modify...{RESET}")
                                    break

                                auth_cache.json[user_to_modify]["other"].update({
                                    "name": full_name,
                                    "card": card_number,
                                    "expiry": expiry_date,
                                    "cvv": cvv,
                                    "renewal": renewal
                                })
                                print("\n")

                            auth_cache.store({user_to_modify: auth_cache.json[user_to_modify]})

                        elif option == 6: # Remove a users membership
                            print("\n" + title("Remove a users membership"))
                            user_to_remove = gather_input(f"{MAGENTA}User to remove: {YELLOW}",
                                                          datatype=str, condition=lambda k: k in auth_cache.json, error_msg="Username does not exist.", allow_exit=True)
                            if user_to_remove == "exit":
                                print(f"{RED}Force remove has been cancelled{WHITE}.")
                                continue
                            user_obj = auth_cache.json[user_to_remove]

                            if user_obj['account_type'] != 'Cineworld Plus':
                                print(f"{RED}This user does not have an active membership.")
                                continue
                            
                            confirm = gather_input(f"\n{GREEN}You are about to remove {CYAN}{user_to_remove}'s {GREEN}membership.\n"
                                                   f"{WHITE}Confirm {BLUE}[{GREEN}Y{BLUE}/{RED}N{BLUE}]{WHITE}: ", datatype=str.upper, req=['Y', 'N'])
                            if confirm == "N":
                                print(f"{RED}Force remove has been cancelled{WHITE}.")
                                continue

                            auth_cache.json[user_to_remove]['other'].clear()
                            auth_cache.json[user_to_remove]['account_type'] = "Standard"
                            auth_cache.store({user_to_remove: auth_cache.json[user_to_remove]})
                            
                            print(f"\n{GREEN}Successfully removed {CYAN}{user_to_remove}'s {GREEN}membership.")

                        elif option == 7: # Refund a users booking
                            print("\n" + title("Refund a users booking"))
                            print(f"\n{RED}Refund eligibility will be {YELLOW}automatically {RED}checked.")
                            user_to_refund = gather_input(f"{MAGENTA}User to refund: {YELLOW}",
                                                          datatype=str, condition=lambda k: k in auth_cache.json, error_msg="Username does not exist.", allow_exit=True)
                            if user_to_refund == "exit":
                                print(f"{RED}Refund has been cancelled{WHITE}.")
                                continue

                            eligible = []
                            
                            for index, book in enumerate(booking_cache.json[user_to_refund]):
                                name = book['film']
                                when = datetime.datetime.strptime(book['when'], '%H:%M:%S @ %Y/%m/%d')

                                if (datetime.datetime.now() - when).total_seconds() <= (60 * 45):
                                    eligible.append((index, name, when))
                            
                            if eligible:
                                print(f"\n{YELLOW}{user_to_refund} {GREEN}is refund-eligible for the following bookings:")
                                for index, eligibility in enumerate(eligible):
                                    print(f"{YELLOW}[{WHITE}{index}{YELLOW}] {CYAN}{eligibility[1]} {YELLOW}({MAGENTA}{eligibility[2].strftime('%H:%M:%S @ %Y/%m/%d')}{YELLOW})")
                                option = gather_input(f"{MAGENTA}Booking to refund: {YELLOW}", condition=lambda k: 0 <= k < len(eligible), error_msg="Invalid booking.")

                                obj = eligible[option]
                                when_ = f"{YELLOW}({MAGENTA}{obj[2].strftime('%H:%M:%S @ %Y/%m/%d')}{YELLOW}){GREEN}"

                                confirm = gather_input(f"\n{GREEN}You are about to refund {CYAN}{user_to_remove}'s {GREEN}booking for {CYAN}{obj[1]}{GREEN} {when_}.\n"
                                                   f"{WHITE}Confirm {BLUE}[{GREEN}Y{BLUE}/{RED}N{BLUE}]{WHITE}: ", datatype=str.upper, req=['Y', 'N'])
                                if confirm == "N":
                                    print(f"{RED}Refund has been cancelled{WHITE}.")
                                    continue

                                booking_cache.json[user_to_refund].pop(obj[0])
                                booking_cache.store({user_to_refund: booking_cache.json[user_to_refund]})
                                print(f"{GREEN}Successfully refunded {YELLOW}{user_to_refund}'s {GREEN}booking for {CYAN}{obj[1]}{GREEN} {when_}.")
                            else:
                                print(f"\n{YELLOW}{user_to_refund} {RED}is not eligible for any refund.")

                        elif option == 8: # Remove a users booking
                            print("\n" + title("Remove a users booking"))
                            user_to_remove = gather_input(f"{MAGENTA}User to remove: {YELLOW}",
                                                          datatype=str, condition=lambda k: k in auth_cache.json, error_msg="Username does not exist.", allow_exit=True)
                            if user_to_remove == "exit":
                                print(f"{RED}Force remove has been cancelled{WHITE}.")
                                continue

                            films = []
                            
                            for index, book in enumerate(booking_cache.json[user_to_remove]):
                                films.append((index, book['film'], book['when']))
                            
                            if films:
                                print(f"\n{YELLOW}{user_to_remove} {GREEN}can have the following bookings removed:")
                                for index, film in enumerate(films):
                                    print(f"{YELLOW}[{WHITE}{index}{YELLOW}] {CYAN}{film[1]} {YELLOW}({MAGENTA}{film[2]}{YELLOW})")
                                option = gather_input(f"{MAGENTA}Booking to refund: {YELLOW}", condition=lambda k: 0 <= k < len(films), error_msg="Invalid booking.")

                                obj = films[option]
                                when_ = f"{YELLOW}({MAGENTA}{obj[2]}{YELLOW}){GREEN}"

                                confirm = gather_input(f"\n{GREEN}You are about to remove {CYAN}{user_to_remove}'s {GREEN}booking for {CYAN}{obj[1]}{GREEN} {when_}.\n"
                                                   f"{WHITE}Confirm {BLUE}[{GREEN}Y{BLUE}/{RED}N{BLUE}]{WHITE}: ", datatype=str.upper, req=['Y', 'N'])
                                if confirm == "N":
                                    print(f"{RED}Force remove has been cancelled{WHITE}.")
                                    continue

                                booking_cache.json[user_to_remove].pop(obj[0])
                                booking_cache.store({user_to_remove: booking_cache.json[user_to_remove]})
                                print(f"{GREEN}Successfully removed {YELLOW}{user_to_remove}'s {GREEN}booking for {CYAN}{obj[1]}{GREEN} {when_}.")
                            else:
                                print(f"\n{YELLOW}{user_to_remove} {RED}has no bookings to remove.")

                        elif option == 9:
                            print(f"\n{RED}Exiting Admin Panel...{RESET}")
                            mainloop = 0
                            break

                elif menu == 6:
                    print(f"\n{GREEN}[{MAGENTA}{username}{GREEN}] {RED}Signing out...{RESET}\n")
                    break

                elif menu == 7:
                    print(f"\n{GREEN}We hope you visit again!\n{RED}Exiting...{RESET}")
                    quit()