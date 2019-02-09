# importing important libraries
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import datetime
import json

#--code--

def simple_get(url):
	""" A simple function to get content of url by HTTP GET request.
	If content-type of response is  application/json or HTML return the 
	text else return None"""
	try:
	 	with closing(get(url,stream=True)) as resp:
	 		if is_good_response(resp):
	 			return resp.content
	 		else :
	 			return None


	except RequestException as e:
	 	log_error("Error during request to {0}:{1}".format(url,str(e)))
	 	return None

def is_good_response(resp):
	""" Returns true if response is json or html else return false"""
	content_type=resp.headers['Content-Type'].lower()
	"""print(resp.status_code==200)
	print(content_type is not None)
	print(content_type.find('json')>-1)"""
	return (resp.status_code==200
			and content_type is not None
			and (content_type.find('json')>-1 or content_type.find('html')>-1))

def log_error(e):
	"""Error log"""
	print(e)

def get_names():
	""" Def to get names of mathematicians from a site"""
	url = 'http://www.fabpedigree.com/james/mathmen.htm'
	response=simple_get(url)
	if response is not None:
		html=BeautifulSoup(response,'html.parser')
		names=set()
		for li in html.select('li'):
	 		for name in li.text.split('\n'):
	 			names.add(name.strip())

		return list(names)
	raise Exception('Error retrieving content at {}'.format(url))

def get_hits_on_name(name,n):
	"""
    Accepts a `name` of a mathematician and returns the number
    of hits that mathematician's Wikipedia page received in the 
    last n*30 days, as an `int`
    """
    # url_root is a template string that is used to build a URL.
    #sample https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia.org/all-access/all-agents/Isaac_Newton/monthly/20181209/20190209
	url_root='https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia.org/all-access/all-agents/'
	for part in name.split():
		url_root+=part+"_"
	d_end=datetime.datetime.now()
	d_start=d_end-datetime.timedelta(days=int(n)*30)
	x_start=d_start.strftime("%Y%m01")
	x_end=d_end.strftime("%Y%m%d")

	url_root=url_root[:-1]+"""/monthly/{}/{}""".format(x_start,x_end)
	response=simple_get(url_root)

	if response is not None:
		"""html=BeautifulSoup(response,'html.parser')

		hit_link=[a for a in html.select('a') if a['href'].find('latest-60')>-1]

		if len(hit_link)>0:
			#Strip commas
			link_text=hit_link[0].text.replace(',','')
			try:
				return int(link_text)
			except:
				log_error("Couldn't parse {} as int".format(link_text))"""
		x=json.loads(response)
		hits=0
		for i in x['items']:
			hits+=int(i['views'])
		return hits

	log_error("No page views for {}".format(name))
	return None


if __name__=="__main__":
	print("Getting names of famous mathematicians....")
	names=get_names()
	print("....done\n")
	n=input("Enter number of months to get data for:")
	results=[]

	print("Getting results for each name")

	for name in names:
		if len(name)>0:
			hits=get_hits_on_name(name,n)
			try:
				if hits is None or hits==0:
					hits=-1
				results.append((hits,name))
			except:
				results.append((-1,name))
				log_eror("error encountered while processing {} skipping...".format(name))
	print("Done")

	results.sort()

	results.reverse()

	if len(results)>5:
		top_mark=results[:5]
	else:
		top_mark=results

	print("Most popular Mathematicians are...(based on last "+n+" months search on Wikipedia)")
	for (mark,mathematician) in top_mark:
		print("{} with {} page views".format(mathematician,mark))
	others=0
	for (mark,mathematician) in results[5:]:
		others+=mark
	print("Others with",others," page views in total")
	no_results=len([res for res in results if res[0]==-1])

	print("But we couldn't find results for {} mathematicians".format(no_results))