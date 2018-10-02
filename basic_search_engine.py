from urllib.parse import urlparse
import urllib.request

# Returns the url of first hyperlink in the page
def get_next_target(page):
	start_link = page.find('<a href=')
	if start_link == -1:
		return None, 0
	start_quote = page.find('"', start_link)
	end_quote = page.find('"', start_quote + 1)
	url = page[start_quote + 1 : end_quote]
	return url, end_quote

# Prints the urls of all hyperlinks in the page
def print_all_links(page):
	while True:
		url, end_pos = get_next_target(page)
		if url:
			page = page[end_pos:]
		else:
			break

# Retrieves the page from url
def get_page(url):
	try:
	    return str(urllib.request.urlopen(url).read())
	except:
	    return "error"

# Merges two lists removing duplicates
def union(a, b):
	for e in b:
		if e not in a:
			a.append(e)

# Returns the list of urls of all hyperlinks in the page
def get_all_links(curr_page_url, page):
	links = []
	while True:
		url, end_pos = get_next_target(page)
		if url:
			if 'http' not in url:
				if url[0] == '/':
					parsed_page_url = urlparse(curr_page_url)
					host_name = '{uri.scheme}://{uri.netloc}/'.format(uri = parsed_page_url)
					url = host_name + url
				else:
					url = curr_page_url + url
			links.append(url)
			page = page[end_pos:]
		else:
			break
	return links

# Crawls web pages starting from the seed
def crawl_web(seed, max_depth):
	tocrawl = [seed]
	crawled = []
	next_to_crawl = []
	depth = 0
	index = {}
	graph = {}
	while tocrawl and depth <= max_depth:
		page = tocrawl.pop()
		if page not in crawled:
			content = get_page(page)
			add_page_to_index(index, page, content)
			crawled.append(page)
			outlinks = get_all_links(page, content)
			graph[page] = outlinks
			union(next_to_crawl,outlinks)
		if not tocrawl:
			tocrawl, next_to_crawl = next_to_crawl, []
			depth = depth + 1
	return index, graph

# Splits the string on provided delimiters
def splitstring(source, splitlist):
	l = []
	s = ''
	for i in range(len(source)):
		if source[i] in splitlist:
			if s != '':
				l.append(s)
				s = ''
		else:
			s = s + source[i]
	if s!= '':
		l.append(s)
	return l

# Computes rank of all crawled pages
def compute_ranks(graph):
	d = 0.8 # damping factor
	numloops = 10
	ranks = {}
	npages = len(graph)
	for page in graph:
		ranks[page] = 1.0 / npages
	for i in range(0, numloops):
		newranks = {}
		for page in graph:
			newrank = (1 - d) / npages
			for other_page in graph:
				if page in graph[other_page]:
					newrank += d * ranks[other_page] / len(graph[other_page])
			newranks[page] = newrank
		ranks = newranks
	return ranks

# Returns the page with the highest rank for a given keyword
def lucky_search(index, ranks, keyword):
	if keyword in index:
		list_of_urls = index[keyword]
		max_rank_url = list_of_urls[0]
		for url in list_of_urls:
			if ranks[url] > ranks[max_rank_url]:
				max_rank_url = url
		return max_rank_url
	else:
		return None

# Adds all the words in a page to index
def add_page_to_index(index, url, content):
	words_in_content = splitstring(content, " ,!$\@<>=/._;""'")
	for word in words_in_content:
		word = word.lower()
		add_to_index(index,word,url)

# Adds a word to index
def add_to_index(index, keyword, url):
	if keyword in index:
		if url not in index[keyword]:
			index[keyword].append(url)
		else:
			return
	else:
		index[keyword] = [url]

# Returns all pages that contain a given keyword
def lookup(index, keyword):
	if keyword in index:
		return index[keyword]
	else:
		return []

# Set seed_page here
seed_page = 'https://udacity.github.io/cs101x/urank/'
# Set crawl_depth here
crawl_depth = 2
index, graph = crawl_web(seed_page, crawl_depth)
ranks = compute_ranks(graph)
ch = 'y'

while ch == 'y':
	choice = int(input('Types of search:\n1. Search\n2. Feeling lucky\nEnter your choice (1 or 2): '))
	search_query = input('Enter a search query: ')
	if choice == 1:
		print(lookup(index, search_query.lower()))
	elif choice == 2:
		print(lucky_search(index, ranks, search_query.lower()))
	else:
		continue
	ch = input('Enter Y or y if you want to continue searching and N or n if you want to quit searching: ')
	ch = ch.lower()