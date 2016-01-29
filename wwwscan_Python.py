#coding=utf-8
import Queue
import threading
import os
import urllib2
import urllib
import argparse

threads = 10
resume = None
#extensions=None
def build_worldlist(worldlist_file):
	fd = open(worldlist_file,'rb')
	raw_worlds = fd.readlines()
	fd.close()
	found_resume = False
	worlds = Queue.Queue()
	for world in raw_worlds:
		world = world.rstrip()
		if resume is not None:
			if found_resume:
				worlds.put(world)
			else:
				if world == resume:
					found_resume = True
					print "resume worldlist from : %s" %resume
		else:
			worlds.put(world)
	return worlds


#def dir_bruter(world_queue,extensions=None):
def dir_bruter(world_queue,target_url):
	while not world_queue.empty():
		attempt = world_queue.get()
		attempt_list = []
		if "." not in attempt:
			attempt_list.append("/%s/" %attempt)
		else:
			attempt_list.append("/%s" %attempt)
#		if extensions:
#			for extension in extensions:
#				attempt_list.append("/%s%s" %(attempt,extension))

		for brute in attempt_list:
			url = "%s%s" %(target_url,urllib.quote(brute))
			try:
				request = urllib2.Request(url)
				response = urllib2.urlopen(request)
				if len(response.read()):
					print "[%d] == > %s" %(response.code,url)
			except urllib2.URLError, e:
				if hasattr(e,"code"):
					if e.code == 302 or e.code == 403:
						print "[%d] == > %s" %(e.code,url)
				elif hasattr(e,"reason"):
					print e.reason
					continue


if __name__ == '__main__':

	parser = argparse.ArgumentParser(description='A simple scanner like wwwscan build by python.')
	parser.add_argument("-u", "--url", help="the target url")
	parser.add_argument("-f", "--file", help="the worldlist file")
	parser.add_argument("-t", "--threads", type = int ,help="the threads")
	args = parser.parse_args()
	if args.url and args.file and args.threads:
		url = args.url
		filelist = args.file
		threads = args.threads
		world_queue = build_worldlist(filelist)
		for i in xrange(threads):
			t = threading.Thread(target = dir_bruter,args = (world_queue,url))
			t.start()
		#dir_bruter(world_queue,url)

	elif (args.url and args.file):
		url = args.url
		filelist = args.file
		world_queue = build_worldlist(filelist)
		dir_bruter(world_queue,url)

	else:
		print "Useage: python target.py -u http://192.168.1.1 -f filelist.txt -t 10\n"
		print "Parameter error or incomplete parameters or unknown parameter\nplease refer --help | -h for more detail."
