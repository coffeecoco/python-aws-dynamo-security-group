
# This is a script to call a row from a db and update a security group based on that ip.
# It runs as a companinion to a lambda script, which is used to track your ip changes.

import json
from pprint import pprint
import subprocess
import sys
import re
import time
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('ip_tracker')
response = table.get_item( Key={ 'username': 'neil' })
json_item_result = response['Item']

# specify the file to write json ip stuff to
json_file="neils_ip.json"

# write it
with open(json_file, 'w') as json_file_handle:
    json_file_handle.write(json.dumps(json_item_result))

#define our ssh-to-bc2 security group
my_sg=sys.argv[1]

# use a regexsearch, sleep to do nothing
# this basic check makes sure we pass a security group id or quits

if re.search(r'^sg\-', my_sg):
    time.sleep (0.1)
else:
    print "No, its not an sg- Bye."
    sys.exit()

# load the data from the dynamodb query, resulting in neils_ip.json
data = json.load(open('neils_ip.json'))

# Extract the ip information
ip_address=json.dumps(data["ip_address"]).strip('"')

# Has this ip been updated ? Check the state file

ip_file="neilsip.txt"

with open(ip_file, 'r') as thefile:
    old_ip=thefile.read().replace('\n', '')

# No need to update if the old and new ips are the same
# sleep instead of doing anything where there is no need to update
if (old_ip==ip_address):
    time.sleep (0.1)
else:
    # Updated the ip_file, as the ip has changed
    with open(ip_file, 'w') as update_file:
        update_file.write(ip_address)

    # Launch the ec2 api command to update the security group ( ec2 api is preconfigured )
    ec2_command='aws ec2 authorize-security-group-ingress --group-id %s --protocol tcp --port 22 --cidr %s/32' % (my_sg,ip_address)
    process_ec2 = subprocess.Popen(ec2_command.split(), stdout=subprocess.PIPE)
    output, error = process_ec2.communicate()

# End of ...
