#! /usr/bin/env python3
import API as pk
import pygeocoder
import requests
import json
import datetime
import time
import datetime


messageIDs = set();

def getTime():
	return time.strftime("%Y-%m-%d--%H-%M-%S")

def main():
	# Title text
	print("\nYik Yak Command Line Edition : Created by djtech42\n\n")

	# Initialize Google Geocoder API
	geocoder = pygeocoder.Geocoder("AIzaSyAGeW6l17ATMZiNTRExwvfa2iuPA1DvJqM")

	try:
		# If location already set in past, read file
		f = open("locationsetting", "r")
		fileinput = f.read()
		f.close()

		# Extract location coordinates and name from file
		coords = fileinput.split('\n')

		currentlatitude = coords[0]
		currentlongitude = coords[1]
		print("Location is set to: ", coords[2])

		# Set up coordinate object
		coordlocation = pk.Location("temp", currentlatitude, currentlongitude)

	except FileNotFoundError:
		# If first time using app, ask for preferred location
		coordlocation = newLocation(geocoder)

		# If location retrieval fails, ask user for coordinates
		if coordlocation == 0:
			print("Please enter coordinates manually: ")

			currentlatitude = input("Latitude: ")
			currentlongitude = input("Longitude: ")
			coordlocation = pk.Location("temp", currentlatitude, currentlongitude)

	print()

	try:
		# If user already has ID, read file
		f = open("userID", "r")
		userID = f.read()
		f.close()

		# start API with saved user ID
		remoteyakker = pk.Yakker(userID, coordlocation, False)

	except FileNotFoundError:
		# start API and create new user ID
		remoteyakker = pk.Yakker(None, coordlocation, True)

		try:
			# Create file if it does not exist and write user ID
			f = open("userID", 'w+')
			f.write(remoteyakker.id)
			f.close()

		except:
			pass

	# Print User Info Text
	print("User ID: ", remoteyakker.id, "\n")
	print("Connecting to Yik Yak server...\n")
	connection = True
	try:
		print("Yakarma Level:",remoteyakker.get_yakarma(), "\n")
	except:
		print("Error: Not connected to the Internet\n")
		connection = False
	if connection:


		locations = [
			pk.Location("Cornell University", "42.4485", "-76.4786"),
			pk.Location("Harvard University", "42.3744", "-71.1169"),
			pk.Location("Brown University", "41.8262", "-71.4032"),
			pk.Location("Columbia University", "40.8075", "-73.9619"),
			pk.Location("Dartmouth College", "43.7033", "-72.2883"),
			pk.Location("Princeton University", "40.3487", "-74.6593"),
			pk.Location("Yale University", "41.3111", "-72.9267"),
			pk.Location("Times Square, NYC", "40.7588", "-79.951"),
			pk.Location("austin texas", "30.267153", "-97.743061"),
			pk.Location("Palo Alto, CA", "37.441883", "-122.143019"),
			pk.Location("Los Angeles, CA", "34.052234", "-118.243685"),
			pk.Location("Chicago, CA", "41.878114", "-87.629798")
		]


		while True:
			for coordlocation in locations:
				print("Retreiving Yaks for: "+coordlocation.address)
				time.sleep(2)
				remoteyakker.update_location(coordlocation)
				yaklist = remoteyakker.get_yaks()
				currentlist =[]

				currentlist = remoteyakker.get_area_tops()
				# print(currentlist)
				jsonData = yaksToJson(currentlist, coordlocation)

				with open(coordlocation.address+'_'+getTime()+'.json', 'w') as outfile:
				    outfile.write(str(jsonData))

			print("Going to sleep for an hour")
			time.sleep(3600) #sleep for an hour then update
			print()



def newLocation(geocoder, address=""):
	# figure out location latitude and longitude based on address
	if len(address) == 0:
		address = input("Enter college name or address: ")
	try:
		currentlocation = geocoder.geocode(address)
	except:
		print("\nGoogle Geocoding API is offline or has reached the limit of queries.\n")
		return 0

	coordlocation = 0
	try:
		coordlocation = pk.Location(address, currentlocation.latitude, currentlocation.longitude)

		# Create file if it does not exist and write
		f = open("locationsetting", 'w+')
		coordoutput = str(currentlocation.latitude) + '\n' + str(currentlocation.longitude)
		f.write(coordoutput)
		f.write("\n")
		f.write(address)
		f.close()
	except:
		print("Unable to get location.")

	return coordlocation

def setUserID(location, userID=""):
	if userID == "":
		userID = input("Enter userID or leave blank to generate random ID: ")

	if userID == "":
		# Create new userID
		remoteyakker = pk.Yakker(None, location, True)
	else:
		# Use existing userID
		remoteyakker = pk.Yakker(userID, location, False)
	try:
		# Create file if it does not exist and write user ID
		f = open("userID", 'w+')
		f.write(remoteyakker.id)
		f.close()

	except:
		pass

	return remoteyakker

def changeLocation(geocoder, address=""):
	coordlocation = newLocation(geocoder, address)

	# If location retrieval fails, ask user for coordinates
	if coordlocation == 0:
		print("\nPlease enter coordinates manually: ")
		currentlatitude = input("Latitude: ")
		currentlongitude = input("Longitude: ")
		coordlocation = pk.Location(address, currentlatitude, currentlongitude)

	return coordlocation

def read(yaklist):
	yakNum = 1
	for yak in yaklist:
		# line between yaks
		print ("_" * 93)
		# show yak
		print (yakNum)
		yak.print_yak()

		commentNum = 1
		# comments header
		comments = yak.get_comments()
		print ("\n\t\tComments:", end='')
		# number of comments
		print (len(comments))

		# print all comments separated by dashes
		for comment in comments:
			print ("\t   {0:>4}".format(commentNum), end=' ')
			print ("-" * 77)
			comment.print_comment()
			commentNum += 1

		yakNum += 1

def yaksToJson(yaks, coordlocation):

	jsonData = {
		"location" : coordlocation.address,
		"coordinateLong" : str(coordlocation.longitude),
		"coordinateLat" : str(coordlocation.latitude),
		"time" : str(datetime.datetime.now().time()),
		"yacks" : []
		}


	yackarray = []
	for yak in yaks:
		if not (yak.message_id in messageIDs):
			messageIDs.add(yak.message_id)
			dic = yak.encode_json()

			dat = json.dumps(dic,ensure_ascii=False)

			yackarray.append(dic)



	jsonData["yacks"] = yackarray

	return json.dumps(jsonData, ensure_ascii=False)





main()
