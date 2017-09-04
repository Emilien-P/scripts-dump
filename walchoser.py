#! /usr/bin/env python

import os
import subprocess
import json
import ConfigParser
import random
from optparse import OptionParser

def configuring ():
	print("Configuring Wizard: ")
	configer = ConfigParser.RawConfigParser()
	try:
		config_file = open(config_path, 'w')
	except IOError as e:
		print("Creating the config file was unsuccesful")
		raise

	valid = False
	while not valid:
		wall_path = raw_input("Where are your wallpapers located : ")
		if not os.path.isdir(os.path.expandvars(wall_path)):
			ans = raw_input("The directory entered is not valid\nR to rentry, any to exit")
			if ans != 'R':
				config_file.close()
				os.remove(config_path)
				exit(0)
		else:
			valid = True

	configer.add_section("PATHS")
	configer.set("PATHS", "wall_path", wall_path)
	json_path = raw_input("Where do you want your json tag structure to be located ? (enter for default) : ")
	if not json_path:
		json_path = wall_path + "/tags.json"
	configer.set("PATHS", "json_path", json_path)
	#Check whether the file exists
	keep = 'N'
	if os.path.isfile(json_path):
		keep = raw_input("An index file exists already at " + json_path + ".\nDo you want to keep it ? (Y/N)")
	if keep != 'Y': #Create a new Json file.
		with open(json_path, "w") as json_file:
			json_file.write("{}")

	configer.add_section("COMMANDS")
	configer.set("COMMANDS", "cmd_set_wp", "wal")
	configer.write(config_file)
	print("The configuration is now complete")
	config_file.close()
	exit(0)

def listing (a, b, c, d):
	#Open the json file
	with open(os.path.expandvars(json_path), "r") as data_json:
		tags_dict = json.load(data_json)

	print(json.dumps(tags_dict, indent=4, sort_keys=True))

#look for config file
config_path = os.environ['HOME'] + "/.config/walchoser"
if os.path.isfile(config_path) :
	try:
		config_file = open(config_path, "r")
	except:
		exit(1)

	configer = ConfigParser.RawConfigParser()
	configer.readfp(config_file)
	global json_path 
	json_path = configer.get("PATHS", "json_path")
	cmd_set_wp = configer.get("COMMANDS", "cmd_set_wp")
	wall_path = configer.get("PATHS", "wall_path")

	with open(os.path.expandvars(json_path), "r") as data_json:
		tags_dict = json.load(data_json)

	usage = "usage: %prog [Options] args"
	parser = OptionParser(usage)
	parser.add_option("-a", "--add", dest="path_tags", help="-a [PATH] [TAGS] \n Reference a wallpaper at path relative to the set wallpapers directory. The tags must be separated by comas (CSV).", nargs=2)
	parser.add_option("-l", "--list", action="callback", callback=listing, help="List your json index file.", nargs=0)
	parser.add_option("-c", "--config", action="callback", callback=configuring, help="Calls the config wizard.")
	parser.add_option("-p", "--print", action="store_true", dest="printing", default=False, help="-p [TAGS] To use with tags to print what wallpapers match.")
	parser.add_option("--get-wp", action="store_true", dest="wall_path", default=False)
	parser.add_option("-q", "--quiet", action="store_true", dest="quiet", default=False)
	parser.add_option("-t", "--get-tags", dest="wp_path", nargs=1, help="Output the tags of a given wallpaper")

	(option, args) = parser.parse_args()

	if option.path_tags:
		user_tag_list = option.path_tags[1].split(',')
		filename = option.path_tags[0]

		if not os.path.isfile(os.path.expandvars(wall_path + "/" + filename)):
			print("your filename is incorrect, exiting")
			exit(1)

		for tag in user_tag_list:
			toadd = []
			toadd.append(filename)
			if tag in tags_dict:
				 toadd.extend(tags_dict[tag])
			toadd = list(set(toadd)) #remove potential duplicate reference
			tags_dict.update({tag:toadd})

		data_json = open(os.path.expandvars(json_path), "w")
		json.dump(tags_dict, data_json)

		data_json.close()

	#Change the wallpaper according to tags given
	if not args and not option:
		os.system(cmd_set_wp + " -t -i" + wall_path)
	else:
		#In case of the wp printing option, useful for the albert extension
		if option.wall_path:
			print(os.path.expandvars(wall_path))
			exit(0)
		#in case of tags wanted
		elif option.wp_path:
			#NOT efficient by efficiency is not compulsory here
			tags = {k: v for k, v in tags_dict.items() if option.wp_path in v}
			print(json.dumps(tags.keys()))
			exit(0)
		if args and args[0] in tags_dict:
			matching = set(tags_dict[args[0]])
			for tag in args:
				if tag in tags_dict:
					matching = matching.intersection(set(tags_dict[tag]))

			#In case of printing option
			if option.printing:
				if not option.quiet:
					print("Those Wallpapers are matching your tags:")
				print(json.dumps(list(matching), indent=4, sort_keys=True))
				exit(0)
			#Else the a wallpaper is set
			else:
				if not option.quiet:
					print("Chosing a wallpaper at random among matching")
				chosen_wp = random.choice(list(matching))
				os.system(cmd_set_wp + " -t -i" + wall_path + "/" + chosen_wp)
		elif args:
			if not option.quiet:
				print("No wallpaper is matching your tags, exiting.")
			exit(0)

else:
	ans = raw_input("Your config file doesn't exist yet, do you want to create it (Y/N) ? ")
	if ans == 'Y':
		configuring()
	else:
		print("aborting")
		exit(0)
exit(0)