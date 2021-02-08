'''
Dynamic DNS service for Vultr
By Andy Smith
https://ajsmith.us/
https://github.com/andyjsmith/Vultr-Dynamic-DNS
'''

import json
import sys
import requests

# Import the values from the configuration file
with open("config.json") as config_file:
	config = json.load(config_file) # Convert JSON to Python

domain = config["domain"]
api_key = config["api_key"]
dynamic_records = config["dynamic_records"]

# Get the public IP of the server
ip = requests.get("https://api.ipify.org").text

# Get the list of DNS records from Vultr to translate the record name to recordid
raw_response = requests.get("https://api.vultr.com/v1/dns/records?domain=" + domain, headers={"API-Key": api_key}).text
if "is not authorized" in raw_response:
    print("There was an error. You are not authorized to use the API. Details are below.")
    print("NOTE: If using IPv6, or an IPv6 address is displayed below, you need to go to your account API settings and click Allow all IPv6.")
    print("Error returned from Vultr API:")
    print(raw_response)
    sys.exit(1)

try:
    raw_records = json.loads(raw_response)
except json.decoder.JSONDecodeError:
    print("Error returned from Vultr API:")
    print(raw_response)
    sys.exit(1)

# Filter out other records besides A records
records = []
for record in raw_records:
	if record["type"] == "A":
		records.append(record)

# Make a new array of the IDs from the records in the config file
records_to_change = []
for record in records:
	if record["name"] in dynamic_records:
		records_to_change.append(record)

# Cancel if no records from Vultr match the config file
if len(records_to_change) == 0:
	print("Configuration error, no records to change.")
	quit()

# Check if the IP address actually differs from any of the records
needsUpdated = False
for record in records_to_change:
	if record["data"] != ip:
		needsUpdated = True

# Cancel if the IP has not changed
if not needsUpdated:
	print("IP address has not changed. No records have been updated.")
	quit()

print("IP has changed since last checking.")
print("Old IP on Vultr: " + records_to_change[0]["data"] + ", current server IP: " + ip)

# Update the records in Vultr with the new IP address
for record in records_to_change:
	payload = {"domain": domain, "RECORDID": record["RECORDID"], "data": ip}
	response = requests.post("https://api.vultr.com/v1/dns/update_record", data = payload, headers={"API-Key": api_key})
	name = record["name"]
	if name == "":
		name = "@"
	print("Changed " + name + " (" + str(record["RECORDID"]) + ") to " + ip + " in " + domain)
