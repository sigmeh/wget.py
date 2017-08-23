#!/usr/bin/env python
'''

        -- wget.py --
    
Basic python implementation of wget 

Create new directory based on <title> tag from url
Add requested page as index.html
Retrieve the contents of all hrefs having relative urls
Save each html doc in new directory under its filename 

Usage:
	python wget.py example.com
	
	
'''

import subprocess as sp
import requests
import sys
import re
import os 
from time import sleep


def bash(cmd, shell=False):		
	''' execute subprocess call '''
	out,err = sp.Popen(cmd if shell else cmd.split(), stdout=sp.PIPE, shell=shell).communicate()
	return out if out else err


def pe(*msg):					
	''' pe: print and exit '''
	if msg: print msg[0]
	sys.exit()


def format_url(url, href):
	''' alter url to handle files in parent directories '''
	print 'url: %s ...... href: %s' % (url,href)
	url = url.rstrip('/')
	href = href.lstrip('/')
	for c in range( href.count('..') ):
		url = url[ :url.rfind('/') ]
	href = href.replace('../','')
	return url, href
	
	

def main():
	
	headers = {
		'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:43.0) Gecko/20100101 Firefox/44.0',
		'accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
		'accept-language' : 'en-US,en;q=0.5',
		'dnt' : '1'
	}
	

	#	----------------------------------
	#	Retrieve document from user-supplied url with requests module
	#	Create directory from <title> tag (or url)
	#	Add index.html (this page) to the directory
	
	url = sys.argv[1] if len(sys.argv) > 1 else pe('Must specify URL')	

	try:
		r = requests.get(url, headers=headers)
		doc = r.text
	except Exception as e:
		pe(e)

	title = re.search('<title>(?P<title>.*)</title>', doc)
	title = title.group('title').replace(' ','_') if title else url
	print 'Saving to: %s' % title
	
	
	if os.path.exists(title):
		print('Directory "%s" already exists. Any missing files will be added.' % title)
	else:
		bash('mkdir %s' % title)
		while 1:
			if os.path.exists(title):					
				with open( '%s/index.html' % title ,'w') as f:
					f.write(doc.encode('utf8'))
				break
			sleep(.1)
			print 'Waiting on directory creation...'
	#
	#
	#	-----------------------------------
	
	
	
	#	------------------------------------
	#	Extract hrefs from document
	#	Retrieve their contents via requests module
	#	Save href files in appropriate directory
	
	href_list = [x[1] for x in re.findall('''href=(?P<quote>["'])(.*?)(?P=quote)''',doc)]
	
	if any([url.endswith(x) for x in ['.html','.htm']]):
		url = url[:url.rfind('/')]
	if not url.endswith('/') : url += '/'
	print 'url: %s' % url
	dir_contents = bash('ls "%s"' % title, shell=True) 
	
	
	for href in href_list:
		if any([
				'//' 	in href, 
				'#' 	in href,
				href 	in dir_contents,
				href 	== 'index.html'
			]): 	 continue
		

		f_url, f_href = format_url(url, href)	#formatted
		
		try:
			new_url = '%s/%s' % (f_url, f_href)
			print 'Trying %s' % new_url
			r = requests.get(new_url, headers=headers)
		except Exception as e:
			pe(e)
		print 'href: %s ..... Page status: %s' % (f_href, r.status_code)
		
		try:
			with open('%s/%s' % ( title, f_href ),'w') as f:
				f.write( r.text.encode('utf8') )
			sleep(.1)
		except Exception as e:
			print 'exception raised trying to write to file: \n\t %s/%s \n\t Exception:' % ( title, f_href )
			print e
	
	
if __name__ == '__main__':
	main()