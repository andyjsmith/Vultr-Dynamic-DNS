#!/usr/bin/env python3
'''
Dynamic DNS service for Vultr
By Andy Smith
https://ajsmith.us/
https://github.com/andyjsmith/Vultr-Dynamic-DNS
'''

import json
import sys
import requests
import warnings

# Import the values from the configuration file
with open("config.json") as config_file:
	config = json.load(config_file) # Convert JSON to Python

domain = config["domain"]
api_key = config["api_key"]
dynamic_records = config["dynamic_records"]

# Get the public IP of the server
ip = requests.get("https://api.ipify.org").text
try:
	ipv6 = requests.get("https://api6.ipify.org").text
except requests.ConnectionError as e:
	warnings.warn(f'Couldn\'t get IPv6 address: {str(e)}')
	ipv6 = None

response = requests.get("https://api.vultr.com/v2/domains/{}/records?per_page=500".format(domain), headers={"Authorization": "Bearer " + api_key})

# Get the list of DNS records from Vultr to translate the record name to recordid
raw_response = response.text
if "is not authorized" in raw_response:
	print("There was an error. You are not authorized to use the API. Details are below.")
	print("NOTE: If using IPv6, or an IPv6 address is displayed below, you need to go to your account API settings and click Allow all IPv6.")
	print("Error returned from Vultr API:")

try:
	response.raise_for_status()
except requests.HTTPError:
	print("Error returned from Vultr API:")
	print(raw_response)
	sys.exit(1)

try:
	raw_records = json.loads(raw_response)
except json.decoder.JSONDecodeError:
	print("Error returned from Vultr API:")
	print(raw_response)
	sys.exit(1)

def get_records_to_change(record_type, ip):
	# Filter out other records besides A/AAAA records
	records_to_check = [
		record
		for record in raw_records["records"]
		if record["type"] == record_type and record["name"] in dynamic_records
	]

	records_to_change = [
		record
		for record in records_to_check
		if record["data"] != ip
	]

	for record in records_to_change:
		record["new_ip"] = ip

	return records_to_check, records_to_change

check_ipv4, change_ipv4 = get_records_to_change("A", ip)
check_ipv6, change_ipv6 = get_records_to_change("AAAA", ipv6) if ipv6 is not None else ([], [])

# Cancel if no records from Vultr match the config file
if len(check_ipv4+check_ipv6) == 0:
	print("Configuration error, no records to change.")
	sys.exit(1)

records_to_change = change_ipv4 + change_ipv6
if len(records_to_change) == 0:
	print("IP address has not changed. No records have been updated.")
	sys.exit(0)

changes = sorted(set(
	(record["data"], record["new_ip"])
	for record in records_to_change
))

print("IP has changed since last checking.")
for old_ip, new_ip in changes:
	print(f"Old IP on Vultr: {old_ip}, current server IP: {new_ip}")

# Update the records in Vultr with the new IP address
for record in records_to_change:
	payload = {"data": record["new_ip"]}
	response = requests.patch("https://api.vultr.com/v2/domains/{}/records/{}".format(domain, record["id"]), json=payload, headers={"Authorization": "Bearer " + api_key})
	name = record["name"]
	if name == "":
		name = "@"
	if "error" in response.text:
		print("Error returned from Vultr API:")
		print(response.text)
	else:
		print(f"Changed {name}/{record['type']} ({record['id']}) to {record['new_ip']} in {domain}")
