#!/usr/bin/env python

# Copyright (c) 2016 Clay Wells 
#
# A Python-based link checker.
#  
# Usage: pylinkcheck.py -r https://www.example.com
#
# By default, we can spider and check all of the links found at the URL's
# domain. For example, a check of https://foo.example.com will only check
# links with the base URL path of foo.example.com. Link found to
# bar.example.com will not be checked.
# 
# Fancy run-time options
#   url root (domain): this is simply required
#   generate report file: -o output.txt, --output=output.txt
#   limit depth: -l 2, --limit=2
#   TODO: report format: --format=txt,html,xml
##############################################################################

import argparse
import urllib2
import csv
from datetime import datetime
import re
from urlparse import urlparse
from bs4 import BeautifulSoup


#######################################
# Functions

# Spider the base URL
def spiderURL(baseurl, pathlimit):
	# build a list based on each sub directory found
	print '[spider] path limit set to %d' % pathlimit


# Print an informative summary of the dead links
def printReport(deadlinks):
	# print each item in the deadlinks list or CLEAN if empty
	print '\n\n'
	print '#' * 79 
	print ' Link Checker Results\n'
	if not deadlinks:
		print '[+] CLEAN: No dead links found'
	else:
		for item in deadlinks:
			print '[-] NOT FOUND: %s' % item


#######################################
# Main program
#
# Get command line options
parser = argparse.ArgumentParser(description='A Python-based link checker.')
parser.add_argument('-f','--format', required=False, default='txt',
	help='Output file format ')
parser.add_argument('-l','--limit', required=False, default=2,
	help='Limit directory depth, example.com/limit/dir/depth/')
parser.add_argument('-u','--url', help='Base URL to check', required=True)
parser.add_argument('-o','--output', help='Output file name', required=False)
args = parser.parse_args()

# Assign program arguments to variables
# - we may want to add a '/' to baseurl if it's not present.
# - if the href links are relative we need to add the baseurl when checking
#   the link.
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

deadlinks = []

# This for loop will completely change once the spiderURL function is working.
# We'll iterate over the various directory paths instead.

outofscope = 0
# Check the URLs
for link in soup("a"):
	# Fetch the link but only return the status code
	# hrefs are unpredicatable we can add a function to 'clean' them up, i.e.,
	# get the proto, domain, path, file (TODO: for a complete solution we
	# need to get all of this)
	#if baseurl[:-1] == '/':
	#	print '[debug] strip last char from baseurl'
	# mailto: is causing an error
	href = link.get('href')
	print '[debug] href: %s' % href
	if re.match('^mailto', href):
		# skip this one
		continue
	
	
	# Separate the file from the path
	thisurl = urlparse(href)

	if thisurl.netloc != baseurl and thisurl.netloc != '':
		print '[-] HREF %s is out of scope' % thisurl.netloc
		outofscope = 1
	else:
		print '[debug] path %s' % thisurl.path
		outofscope = 0

	# Build the full URL if the href is relative.
	# - assuming, for now, other protocols are not desired
	# - place this in the Spider function
	try:
		if re.match('^http', href):
			checkurl = href
		else:
			checkurl = baseurl + href
	except:
		print '[-] Unknown error in re.match()'

	try:
		#print '[+] checking %s' % checkurl
		hrefpage = urllib2.urlopen(checkurl)
	except urllib2.HTTPError as e:
		if e.code == 404:	
			print '[-] 404 ERROR: %s' % checkurl
			# add this URL to deadlink list
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