#!/usr/bin/env python

# Clay Wells 
#
#
# A Python-based link checker.
#  
# Usage: pylinkcheck.py -r https://www.example.com
#
# By default, we can spider and check all of the links found at the URL's domain.
# For example, a check of https://foo.example.com will only check links with the base
# URL path of foo.example.com. Link found to bar.example.com will not be checked.
# 
# Fancy run-time options
#   url root (domain): this is simply required
#   generate report file: -o output.txt, --output=output.txt
#   limit depth: -l 2, --limit=2
#   TODO: report format: --format=txt,md,html,xml
##############################################################################

import argparse
import urllib2
import csv
from datetime import datetime
import re
from bs4 import BeautifulSoup

#######################################
# Functions

# Spider the base URL
def spiderURL(baseurl, pathlimit):
	# build a list based on each sub directory found.. this could get a litte hairy
	print '[spider] path limit set to %d' % pathlimit


# Print an informative summary of the dead links
def printReport(deadlinks):
	# print each item in the deadlinks list
	print '\n\n'
	print '###############################################################################'
	print ' Link Checker Results'
	print ' '
	if not deadlinks:
		print '[+] SUCCESS: No dead links found'
	else:
		for item in deadlinks:
			print '[-] NOT FOUND: %s' % item


#######################################
# Main program
#
# Get command line options
parser = argparse.ArgumentParser(description='This is a Python-based link checker.')
parser.add_argument('-f','--format', help='Output file format ', required=False, default='txt')
parser.add_argument('-l','--limit', help='Limit directory depth, example.com/limit/dir/depth/', required=False, default=2)
parser.add_argument('-u','--url', help='Base URL to check', required=True)
parser.add_argument('-o','--output', help='Output file name', required=False)
args = parser.parse_args()
 
# Validate input
#validate = Validate()

# Assign args to vars
baseurl = str(args.url)
pathlimit = int(args.limit)

# Show values
print 'Base URL: %s' % args.url
print 'Output file format: %s' % args.format
print 'Output file: %s' % args.output
print 'Limit spider: %d' % args.limit

# Grab today's date for timestamping output file.
now = datetime.now()
tstamp = now.strftime("%Y%m%d-%H%M")

# Grab all a href links
checkurl = urllib2.urlopen(baseurl).read()
soup = BeautifulSoup(checkurl, 'html.parser')

# Spider the site and build our list of URLs to check
spiderURL(baseurl, pathlimit)

# Check the URLs

deadlinks = []

for link in soup("a"):
	# only grab the href string
	#print '[+] found link: %s' % link.get('href')

	# fetch the link but only return the status code
	href = link.get('href')

	# build the full URL if the href is relative
	if re.match('^http', href):
		checkurl = href
	else:
		checkurl = baseurl + href

	try:
		#print '[+] checking %s' % checkurl
		hrefpage = urllib2.urlopen(checkurl)
	except urllib2.HTTPError as e:
		if e.code == 404:	
			print '[-] 404 ERROR: %s' % checkurl
			# add this URL
			deadlinks.append(checkurl)
		else:
			print '[-] HTTP ERROR: %d - %s' % (e.code, checkurl)
	except urllib2.URLError as e:
		# Not an HTTP-specific error (e.g. connection refused)
		print '[-] NON-HTTP ERROR: %d - %s' % (e.code, checkurl)
	else:
		print '[+] Status %d for %s' % (hrefpage.getcode(), checkurl)


printReport(deadlinks)

# EOF