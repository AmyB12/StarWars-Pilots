import json
import requests
import pymongo

client = pymongo.MongoClient()
db = client['starwars']


# Decided to use functions, so that I can see each step of the information and see where there were any hiccups
# The get_ships function goes through each page response and append to a list from the 'results' key, getting a list of
# ships from the API
# This was more for visualisation of the dictionaries and understand the output.
def get_starships():
    list_ships = []
    for page_num in range(1, 5):
        url = "https://swapi.dev/api/starships/?search=a&page=" + str(page_num)
        star_get = requests.get(url)
        for star in star_get.json()['results']:
            list_ships.append(star)
    return list_ships


# The get_pilots function goes through each page response and at the 'results' key look for the 'pilots' key, if there
# are links to pilots then grab the links and if there isn't any links save as 'none'.
def get_pilots():
    pilot_url_list = []
    for page_num in range(1, 5):
        url = "https://swapi.dev/api/starships/?search=a&page=" + str(page_num)
        pilots = requests.get(url)
        for each in pilots.json()['results']:
            if not each['pilots']:
                pilot_url_list.append("None")
            elif each['pilots']:
                pilot_url_list.append(each['pilots'])
    return pilot_url_list


# The get_pilots_name function goes through the list of 'pilot_url_list', where 'none' just append and where there is
# a link, use the link to get the pilot names and append to the list
def get_pilots_name():
    pilot_url_list = get_pilots()
    pilot_name_list = []
    for urls in pilot_url_list:
        if urls == "None":
            pilot_name_list.append("None")
        elif urls != "None":
            name_list = []
            for each in urls:
                info = requests.get(each).json()['name']
                name_list.append(info)
            pilot_name_list.append(name_list)
    return pilot_name_list


# The get_pilot_as_object function takes the 'pilot_name_list' and where 'none' just append and where there is a name
# look for it in the characters' collection, if found grab the '_id' and append to the list.
def get_pilot_as_object():
    pilot_name_list = get_pilots_name()
    pilot_name_objects_list = []
    for names in pilot_name_list:
        if names == "None":
            pilot_name_objects_list.append("None")
        elif names != "None":
            objects_list = []
            for name in names:
                object_id = db.characters.find_one({"name": name}, {"_id": 1})
                objects_list.append(object_id)
            pilot_name_objects_list.append(objects_list)
    return pilot_name_objects_list


# Since we now have the relevant id for the pilots, the update_info function goes through the new ship response,
# iterate through each dictionary and at the 'pilots' key add the id in the 'pilot_name_objects_list' at the
# [object_ind] position and append the id into the new ships' info then increase [object_ind] for the next position.
def update_info():
    object_ind = 0
    all_info = []
    pilot_name_objects_list = get_pilot_as_object()
    for page_num in range(1, 5):
        url = "https://swapi.dev/api/starships/?search=a&page=" + str(page_num)
        get_info = requests.get(url)
        for intel in get_info.json()['results']:
            intel['pilots'] = pilot_name_objects_list[object_ind]
            object_ind += 1
            all_info.append(intel)
    return all_info


# Create the collection and the documents if already made tell me.
def create_collection():
    try:
        all_info = update_info()
        db.create_collection("starShips")
        for things in all_info:
            db.starShips.insert_one(things)
    except:
        print('Already Exist')


create_collection()
starships = db.starShips.find()
for ship in starships:
    print(ship)
