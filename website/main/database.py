import ssl
from warnings import resetwarnings

import pymongo as pymongo
import uri as uri
from pymongo import MongoClient
from datetime import datetime
from datetime import timedelta
import pprint
import re

cluster = MongoClient(
    "mongodb+srv://group5:group@cluster0.lbemc.mongodb.net/myFirstDatabase?retryWrites=true&w=majority",
    ssl_cert_reqs=ssl.CERT_NONE
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


# helper function for date time where you just enter year month day
def date_maker(day, month, year):
    return datetime(year, month, day)


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


def rooms_by_index(index):
    query = {"index": index}
    result = list(Room.find(query))
    return result


def get_price(
    in_date: datetime,
    out_date: datetime,
    hotel_index: int,
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
    return total_cost


def get_all_hotels():
    result = list(Hotel.find({}))
    return result


def hotel_by_index(index):
    result = list(Hotel.find({"index": index}))
    return result


def list_all_rooms():
    result = list(Room.find())
    return result


def room_by_type_index(type: str, index: int):
    query = {"type": type, "index": index}
    result = Room.find(query)
    return list(result)


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
