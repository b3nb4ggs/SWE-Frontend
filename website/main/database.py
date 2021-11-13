from warnings import resetwarnings
from pymongo import MongoClient
from datetime import datetime
from datetime import timedelta
import pprint
import re

cluster = MongoClient(
    "mongodb://localhost:27017"
)

db = cluster["Group5"]
Hotel = db["Hotel"]
Room = db["Room"]
Customer = db["Customer"]
Amenities = db["Amenities"]
Reservation = db["Reservation"]


def strip_off_id(processthis):
    for element in processthis:
        element.pop("_id")
    return processthis


def make_hotel(
    name: str, no_rooms: int, differential: int, amenities: list, Rooms: dict
):
    index = Hotel.count_documents({})
    id = int(index)
    post = {
        "index": id,
        "name": name,
        "weekend_differential": differential,
        "rooms": no_rooms,
    }
    for type in Rooms:
        post[type["type"]] = type["number"]

    # The amenities
    amenity_dict = {k: v for k, v in enumerate(amenities)}
    amenity_dict = {str(v): True for k, v in amenity_dict.items()}
    amenity_dict["index"] = id

    # The rooms already keys value pairs
    for room in Rooms:
        room["weekend_price"] = room["price"] * (differential + 100) / 100
        room["index"] = id

    # Put them in the database
    try:
        Hotel.insert_one(post)
        Room.insert_many(Rooms)
        Amenities.insert_one(amenity_dict)
    except:
        print("Unable to make hotel")


def delete_hotel(index: int):
    Hotel.delete_many({"index": index})
    Room.delete_many({"index": index})
    Amenities.delete_many({"index": index})


def update_hotel(
    index: int,
    name: str,
    no_rooms: int,
    differential: int,
    amenities: list,
    Rooms: dict,
):
    delete_hotel(index)
    id = int(index)
    post = {
        "index": id,
        "name": name,
        "weekend_differential": differential,
        "rooms": no_rooms,
    }
    for type in Rooms:
        post[type["type"]] = type["number"]

    # The amenities
    amenity_dict = {k: v for k, v in enumerate(amenities)}
    amenity_dict = {str(v): True for k, v in amenity_dict.items()}
    amenity_dict["index"] = id

    # The rooms already keys value pairs
    for room in Rooms:
        room["weekend_price"] = room["price"] * (differential + 100) / 100
        room["index"] = id

    # Put them in the database
    try:
        Hotel.insert_one(post)
        Room.insert_many(Rooms)
        Amenities.insert_one(amenity_dict)
    except:
        print("Unable to make hotel")


def search_hotel(name: str):
    pattern = re.compile(name, re.I)
    query = {"name": {"$regex": pattern}}
    result = Hotel.find(query)
    return list(result)


def number_of_days(in_date: datetime, out_date: datetime):
    result = out_date - in_date
    return result.days


def weekdays_between(in_date: datetime, out_date: datetime):
    day_generator = (
        in_date + timedelta(x + 1) for x in range((out_date - in_date).days)
    )
    delta_days = sum(1 for day in day_generator if day.weekday() < 5)
    return delta_days


def make_reservation(
    in_date: datetime,
    out_date: datetime,
    hotel_index: int,
    user_index: int,
    room_type: str,
):

    weekday_price = 0
    weekend_price = 0
    total_cost = 0

    result = rooms_by_index(hotel_index)
    for i in range(len(result)):
        if result[i]["type"] == room_type:
            weekday_price, weekend_price = (
                result[i]["price"],
                result[i]["weekend_price"],
            )
    total_days = number_of_days(in_date, out_date)
    total_weekdays = weekdays_between(in_date, out_date)
    total_weekend_days = total_days - total_weekdays

    total_cost = (total_weekdays * weekday_price) + (total_weekend_days * weekend_price)

    index = Reservation.count_documents({})

    post = {
        "index": index,
        "made_on": datetime.utcnow(),
        "in": in_date,
        "out": out_date,
        "hotel": hotel_index,
        "user": user_index,
        "type": room_type,
        "total_days": total_days,
        "weekdays": total_weekdays,
        "weekends": total_days - total_weekdays,
        "price": total_cost,
    }

    result = Reservation.insert_one(post)
    return result


def get_all_hotels():
    result = list(Hotel.find({}))
    return result


def hotel_by_index(index):
    result = list(Hotel.find({"index": index}))
    return result


def list_all_rooms():
    result = list(Room.find())
    return result


def rooms_by_index(index):
    query = {"index": index}
    result = list(Room.find(query))
    return result


def room_max_price(amount):
    query = {"price": {"$lt": amount}}
    result = list(Room.find(query))
    return result


def room_price_range(low, high):
    query = {"price": {"$gt": low, "$lt": high}}
    result = list(Room.find(query))
    return result


def room_amenity(amenity: list):
    query = {str(v): True for v in amenity}
    result = Amenities.find(query)
    return list(result)


def room_amenity_range_type(low: int, high: int, amenity: list, type: str):
    query = {str(v): True for v in amenity}
    result = Amenities.find(query)
    hotels = [l["index"] for l in result]
    rooms = room_price_range(low, high)
    output = [x for x in rooms if x["index"] in hotels]
    final_output = [x for x in output if x["type"] == type]
    return final_output


# helper function for date time where you just enter year month day
def date_maker(day, month, year):
    return datetime(year, month, day)


def is_weekend(date: datetime):
    if int(date.weekday()) >= 4:
        return True
    else:
        return False


def find_reservation_in_range(hotel_index: int, in_date: datetime, out_date: datetime):
    query = {"in": {"$lt": out_date, "$gte": in_date}, "hotel": hotel_index}
    result = list(Reservation.find(query))
    return result


def hotel_has_vacancy(day: datetime, hotel_index: int, type: str):
    day_before = datetime(day.year, day.month, day.day, 23, 59, 59)
    day_after = date_maker(day.day + 1, day.month, day.year)

    query = {
        "hotel": hotel_index,
        "in": {"$lt": day_after},
        "out": {"$gte": day_before},
        "type": type,
    }
    number_of_reservations = Reservation.count_documents(query)

    result = Hotel.find_one({"index": hotel_index})
    number_of_rooms = result[type]
    return number_of_rooms - number_of_reservations


def hotel_vacancy_range(
    in_date: datetime, out_date: datetime, hotel_index: int, type: str
):
    room_vacancy_by_day = []
    iterable_days = number_of_days(in_date, out_date)
    for day in range(iterable_days):
        room_vacancy_by_day.append(hotel_has_vacancy(in_date, hotel_index, type))
        in_date += timedelta(days=1)
    return room_vacancy_by_day


def make_customer(uname: str, pw: str, fname: str, lname: str, phone: str):
    index = Customer.count_documents({})
    id = int(index)
    post = {
        "index": id,
        "username": uname,
        "password": pw,
        "first_name": fname,
        "last_name": lname,
        "phone": phone,
    }
    Customer.insert_one(post)


def get_customers():
    result = list(Customer.find({}))
    return result


def get_amenities():
    result = list(Amenities.find({}))
    return result


def amenities_by_index(index):
    query = {"index": index}
    result = Amenities.find(query)
    return list(result)


this = get_all_hotels()
this = strip_off_id(this)
for item in this:
    amenity = amenities_by_index(item["index"])
    process = [k for k, v in amenity[0].items() if v == True]
    thestring = " ".join(process)
    print(thestring)
    item["amenity"] = thestring

pprint.pprint(this)


# Line change
# ----------------------------------------------CUSTOMER FUNCTIONS------------------------------------------------------------------------------------------
# -----------------------------------------------------ENTER HOTELS INTO DATABASE---------------------------------------------------------------------------
# result = make_hotel(
#     "Rio Inn",
#     50,
#     20,
#     ["Pool"],
#     [
#         {"type": "Standard", "price": 25, "number": 25},
#         {"type": "Queen", "price": 55, "number": 15},
#         {"type": "King", "price": 89, "number": 10},
#     ],
# )
# ----------------------------------------------------QUERY ROOMS----------------------------------------------------------------------------------------

# result = list_all_rooms()
# pprint.pprint(result)

# result = rooms_by_index(0)
# pprint.pprint(result[0]["type"])
# for i in range(len(result)):
#     if result[i]["type"] == "King":
#         # print(result[i]["price"])
#         v1, v2 = result[i]["price"], result[i]["weekend_price"]
# print(v1, v2)

# result = room_max_price(200)
# pprint.pprint(result[0]["type"])

# result = room_price_range(100, 200)
# pprint.pprint(result)

# ---------------------------------------------------MAKE RESERVATION------------------------------------------------------------------------------------
# print(number_of_days(date_maker(22, 10, 2021), date_maker(28, 10, 2021)))
# print(weekdays_between(date_maker(22, 10, 2021), date_maker(28, 10, 2021)))

# ------------------------------------------(year,month,day) for datetime-------------------------------------------------

# in_date = datetime(2021, 11, 5)
# out_date = datetime(2021, 11, 15)
# make_reservation(in_date, out_date, 2, 2, "Standard")

# --------------------------------------------------CHECK RESERVATIONS AND OCCUPANCY---------------------------------------------------------------------------------------
# hotel_by_index(0)
# find_reservation_in_range(0, date_maker(3, 10, 2021), date_maker(6, 10, 2021))
# print(hotel_has_vacancy(date_maker(3, 10, 2021), 0))  # day followed by

# rooms = room_max_price(300)
# rooms = strip_off_id(rooms)
# hotels = get_all_hotels()
# hotels = strip_off_id(hotels)
# pprint.pprint(rooms)
# result = search_hotel("All")
# pprint.pprint(result)
# pprint.pprint(room_amenity(["Gym", "Pool", "Spa"]))


# pprint.pprint(room_amenity_range_type(0, 200, ["Gym", "Pool", "Spa"], "Standard"))


# delete_hotel(10)


# print(
#     hotel_vacancy_range(
#         date_maker(5, 11, 2021), date_maker(20, 11, 2021), 2, "Standard"
#     )
# )
