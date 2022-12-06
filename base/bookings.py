from base.common import gather_input
from base.cache import Cache
from base.color import *
import datetime

class Booking:
    """This class deals with the booking menu

    Attributes
    ------------
    username: str
        The user that is booking
    films: dict
        The films available for viewing today requested from cineworld API
    bookings: Cache
        An already defined cache object that manages the file where bookings are kept.

    """
    def __init__(self, username: str, films: dict, bookings: Cache):
        self.username = username
        self.films = films
        self.bookings = bookings
    
    def _find_film_object(self, filmId):
        for film in self.films['body']['films']:
            if film['id'] == filmId:
                return film
    
    def _get_cert(self, attributes):
        for attribute in attributes:
            if attribute in ['pg', '12a', '15', '18', 'u']:
                return attribute
    
    def get_user_bookings(self):
        return self.bookings.json[self.username]
    
    def get_available_viewings(self):
        viewings = {}
        for viewing in self.films['body']['events']:
            filmId = viewing['filmId']
            film = self._find_film_object(filmId)
            filmName = film['name']
            
            if filmName not in viewings:
                viewings[filmName] = {'cert': self._get_cert(film['attributeIds']), 'times': []}

            viewings[filmName]['times'].append(datetime.datetime.strptime(viewing['eventDateTime'], "%Y-%m-%dT%H:%M:%S"))
        
        for viewing in viewings:
            viewings[viewing]['times'] = list(sorted(viewings[viewing]['times']))

        return viewings
    
    def create_booking(self, membership):
        viewings = list(self.get_available_viewings().items())
        print("\n" + title(f"Available Bookings for {str(datetime.datetime.today())[:10]}"))
        for index, viewing in enumerate(viewings):
            print(f"{RED}[{GREEN}{index}{RED}] {BLUE}{viewing[0]}{RESET}")
    
        option = gather_input(f"{WHITE}Specify a film you'd like to view with their assigned. Type 'exit' to exit.\n{MAGENTA}>>> {GREEN}", condition=lambda k: 0 <= k < len(viewings), allow_exit=True)
        if option == "exit":
            print(f"{RED}Booking has been cancelled{WHITE}.")
            return

        option = int(option)

        viewing = viewings[option]
        print("\n" + title(viewing[0]))
        print(f"{WHITE}Rating: {RED}{viewing[1]['cert']}")

        options = []
        for index, time in enumerate(viewing[1]['times'], start=65):
            print(f"{RED}[{GREEN}{chr(index)}{RED}] {YELLOW}{time.strftime('%H:%M:%S @ %Y/%m/%d')}")
            options.append(chr(index))
        
        when = gather_input(f"{WHITE}Specify a time you'd be happy with by specifying an option A-Z. Type 'exit' to exit.\n{MAGENTA}>>> {GREEN}", datatype=str.upper, condition=lambda k: k in options, allow_exit=True)
        if when == "exit":
            print(f"{RED}Booking has been cancelled{WHITE}.")
            return

        time = viewing[1]['times'][options.index(when)]

        print(f"\n{MAGENTA}This is what you have chosen:\n"
              f"{GREEN}Film: {YELLOW}{viewing[0]}\n"
              f"{GREEN}When: {YELLOW}{time.strftime('%H:%M:%S @ %Y/%m/%d')}{RESET}")
        
        confirm = gather_input(f"{WHITE}Confirm {BLUE}[{GREEN}Y{BLUE}/{RED}N{BLUE}]{WHITE}: ", datatype=str.upper, req=['Y', 'N'])

        if confirm == "N":
            print(f"{RED}Booking has been cancelled{WHITE}.")
            return
        
        display = f"{viewing[0]} {WHITE}[{YELLOW}{time.strftime('%H:%M:%S @ %Y/%m/%d')}{WHITE}]"

        print("\n" + title(display))
        people = gather_input(f"{GREEN}How many people will be attending? (min: 1, max: 10) - {WHITE}Type 'exit' to exit at any time.\n"
                              f"{MAGENTA}>>> ", condition=lambda k: k > 0 and k <= 10, allow_exit=True)
        if people == "exit":
            print(f"{RED}Booking has been cancelled{WHITE}.")
            return

        adults = gather_input(f"{YELLOW}Adults (18+): {GREEN}", condition=lambda k: k > -1 and k <= people, allow_exit=True)
        if adults == "exit":
            print(f"{RED}Booking has been cancelled{WHITE}.")
            return
        
        students = 0

        if adults != people:
            students = gather_input(f"{YELLOW}Students (15-17): {GREEN}", condition=lambda k: k > -1 and k <= people, allow_exit=True)
            if students == "exit":
                print(f"{RED}Booking has been cancelled{WHITE}.")
                return

        children = 0

        if adults+students != people:
            children = gather_input(f"{YELLOW}Children (0-14): {GREEN}", condition=lambda k: k > 0 and k+adults+students == people, allow_exit=True)
            if children == "exit":
                print(f"{RED}Booking has been cancelled{WHITE}.")
                return
        
        def calc(price, membership):
            discount = 0
            if membership == 'Cineworld Plus':
                discount = 15
            return round(price - ((price / 100) * discount), 2)
        
        price = (adults * calc(12.99, membership)) + (students * calc(7.99, membership)) + (children * calc(7.99, membership))
        
        print(f"\n{MAGENTA}This is your booking:\n"
              f"{GREEN}Film: {YELLOW}{viewing[0]}\n"
              f"{GREEN}When: {YELLOW}{time.strftime('%H:%M:%S @ %Y/%m/%d')}\n"
              f"{GREEN}Adults attending: {YELLOW}{adults}\n"
              f"{GREEN}Students attending: {YELLOW}{students}\n"
              f"{GREEN}Children attending: {YELLOW}{children}\n"
              f"{GREEN}Price: {CYAN}£{price:,}")
        
        confirm = gather_input(f"{WHITE}Confirm {BLUE}[{GREEN}Y{BLUE}/{RED}N{BLUE}]{WHITE}: ", datatype=str.upper, req=['Y', 'N'])
        if confirm == "N":
            print(f"{RED}Booking has been cancelled{WHITE}.")
            return
        
        print(f"\n{MAGENTA}Thanks for booking with {RED}Cineworld{MAGENTA}!")
        self.bookings.json[self.username].append({
            "film": viewing[0],
            "when": time.strftime('%H:%M:%S @ %Y/%m/%d'),
            "adults": adults,
            "children": children,
            "price": price
        })
        self.bookings.store(self.bookings.json)