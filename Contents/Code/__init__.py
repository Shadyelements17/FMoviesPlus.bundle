######################################################################################
#
#	FMovies.se by Coder Alpha
# 	https://github.com/coder-alpha/FMoviesPlus.bundle
#
######################################################################################

import re, urllib, urllib2, json, sys, time, random
import common, updater, fmovies
from DumbTools import DumbKeyboard

# import Shared ServiceCode
Openload = SharedCodeService.openload
Constants = SharedCodeService.constants

SITE = "FMovies"
TITLE = common.TITLE
PREFIX = common.PREFIX
ART = "art-default.jpg"
ICON = "icon-fmovies.png"
ICON_LIST = "icon-list.png"
ICON_COVER = "icon-cover.png"
ICON_SEARCH = "icon-search.png"
ICON_SEARCH_QUE = "icon-search-queue.png"
ICON_NEXT = "icon-next.png"
ICON_MOVIES = "icon-movies.png"
ICON_FILTER = "icon-filter.png"
ICON_GENRE = "icon-genre.png"
ICON_LATEST = "icon-latest.png"
ICON_SIMILAR = "icon-similar.png"
ICON_OTHERSEASONS = "icon-otherseasons.png"
ICON_HOT = "icon-hot.png"
ICON_ENTER = "icon-enter.png"
ICON_QUEUE = "icon-bookmark.png"
ICON_UNAV = "MoviePosterUnavailable.jpg"
ICON_PREFS = "icon-prefs.png"
ICON_UPDATE = "icon-update.png"
ICON_UPDATE_NEW = "icon-update-new.png"
ICON_OPTIONS = "icon-options.png"
ICON_CLEAR = "icon-clear.png"
ICON_DK_ENABLE = "icon-dumbKeyboardE.png"
ICON_DK_DISABLE = "icon-dumbKeyboardD.png"
ICON_GL_ENABLE = "icon-gl-enable.png"
ICON_GL_DISABLE = "icon-gl-disable.png"
ICON_INFO = "icon-info.png"
ICON_STAR = "icon-star.png"
ICON_PEOPLE = "icon-people.png"
ICON_TAG = "icon-tag.png"

MC = common.NewMessageContainer(common.PREFIX, common.TITLE)

######################################################################################
# Set global variables

CAT_WHATS_HOT = ['Sizzlers','Most Favourited','Recommended','Most Watched This Week','Most Watched This Month','Latest Movies','Latest TV-Series','Requested Movies']
CAT_REGULAR = ['Movies','TV-Series','Top-IMDb','Most Watched']
CAT_FILTERS = ['Release','Genre','Country','Filter Setup >>>']
CAT_GROUPS = ['What\'s Hot ?', 'Movies & TV-Series', 'Sort using...','Site News']

Filter = {}
Filter_Search = {}

SITE_NEWS_LOCS = []

VALID_PREFS_MSGS = []

CONVERT_BMS = []

CUSTOM_TIMEOUT_DICT = {}

CUSTOM_TIMEOUT_CLIENTS = {'Plex Web': 15}

NoMovieInfo = True

######################################################################################

def Start():

	ObjectContainer.title1 = TITLE
	ObjectContainer.art = R(ART)
	DirectoryObject.thumb = R(ICON_LIST)
	DirectoryObject.art = R(ART)
	VideoClipObject.thumb = R(ICON_UNAV)
	VideoClipObject.art = R(ART)
	
	fmovies.CACHE.clear()
	HTTP.ClearCache()
	
	try:
		CACHE_EXPIRY = 60 * int(Prefs["cache_expiry_time"])
	except:
		CACHE_EXPIRY = fmovies.CACHE_EXPIRY_TIME
		
	HTTP.CacheTime = CACHE_EXPIRY
	HTTP.Headers['User-Agent'] = Constants.USER_AGENT
	HTTP.Headers['Referer'] = fmovies.BASE_URL
	
	DumpPrefs()
	ValidateMyPrefs()
	
	# convert old style bookmarks to new
	if len(CONVERT_BMS) == 0:
		convertbookmarks()

######################################################################################
# Menu hierarchy
@handler(PREFIX, TITLE, art=ART, thumb=ICON)
@route(PREFIX + "/MainMenu")
def MainMenu():

	ClientInfo()
	if len(VALID_PREFS_MSGS) > 0:
		return DisplayMsgs()
	
	oc = ObjectContainer(title2=TITLE, no_cache=isForceNoCache())
	oc.add(DirectoryObject(key = Callback(ShowMenu, title = CAT_GROUPS[0]), title = CAT_GROUPS[0], thumb = R(ICON_HOT)))
	oc.add(DirectoryObject(key = Callback(ShowMenu, title = CAT_GROUPS[1]), title = CAT_GROUPS[1], thumb = R(ICON_MOVIES)))
	oc.add(DirectoryObject(key = Callback(ShowMenu, title = CAT_GROUPS[2]), title = CAT_GROUPS[2], thumb = R(ICON_FILTER)))
	oc.add(DirectoryObject(key = Callback(ShowMenu, title = CAT_GROUPS[3]), title = CAT_GROUPS[3], thumb = R(ICON_INFO)))
	
	# ToDo: Not quite sure how to read back what was actually played from ServiceCode and not just show a viewed item
	oc.add(DirectoryObject(key = Callback(RecentWatchList, title="Recent WatchList"), title = "Recent WatchList", thumb = R(ICON_LATEST)))
	oc.add(DirectoryObject(key = Callback(Bookmarks, title="Bookmarks"), title = "Bookmarks", thumb = R(ICON_QUEUE)))
	oc.add(DirectoryObject(key = Callback(SearchQueueMenu, title = 'Search Queue'), title = 'Search Queue', summary='Search using saved search terms', thumb = R(ICON_SEARCH_QUE)))
	
	if common.UsingOption(key='ToggleDumbKeyboard'):
		DumbKeyboard(PREFIX, oc, Search,
				dktitle = 'Search',
				dkthumb = R(ICON_SEARCH)
		)
	else:
		oc.add(InputDirectoryObject(key = Callback(Search), thumb = R(ICON_SEARCH), title='Search', summary='Search Channel', prompt='Search for...'))
	
	oc.add(DirectoryObject(key = Callback(Options), title = 'Options', thumb = R(ICON_OPTIONS), summary='Options that can be accessed from a Client, includes Enabling DumbKeyboard & Clearing Cache'))
	oc.add(PrefsObject(title = 'Preferences', thumb = R(ICON_PREFS)))
	try:
		if updater.update_available()[0]:
			oc.add(DirectoryObject(key = Callback(updater.menu, title='Update Plugin'), title = 'Update (New Available)', thumb = R(ICON_UPDATE_NEW)))
		else:
			oc.add(DirectoryObject(key = Callback(updater.menu, title='Update Plugin'), title = 'Update (Running Latest)', thumb = R(ICON_UPDATE)))
	except:
		pass
	
	return oc

######################################################################################
@route(PREFIX + "/options")
def Options():
	oc = ObjectContainer(title2='Options', no_cache=isForceNoCache())
	
	session = common.getSession()
	if Dict['ToggleDumbKeyboard'+session] == None or Dict['ToggleDumbKeyboard'+session] == 'disabled':
		oc.add(DirectoryObject(key=Callback(common.setDictVal,key='ToggleDumbKeyboard',session=session, val='enabled'), title = 'Enable DumbKeyboard', summary='Click here to Enable DumbKeyboard for this Device', thumb = R(ICON_DK_ENABLE)))
	else:
		oc.add(DirectoryObject(key=Callback(common.setDictVal,key='ToggleDumbKeyboard',session=session, val='disabled'), title = 'Disable DumbKeyboard', summary='Click here to Disable DumbKeyboard for this Device', thumb = R(ICON_DK_DISABLE)))
		
	if Dict['ToggleRedirector'+session] == None or Dict['ToggleRedirector'+session] == 'disabled':
		oc.add(DirectoryObject(key=Callback(common.setDictVal,key='ToggleRedirector',session=session, val='enabled'), title = 'Enable Redirector', summary='Click here to Enable Redirector method for this Device', thumb = R(ICON_GL_ENABLE)))
	else:
		oc.add(DirectoryObject(key=Callback(common.setDictVal,key='ToggleRedirector',session=session, val='disabled'), title = 'Disable Redirector', summary='Click here to Disable Redirector method for this Device', thumb = R(ICON_GL_DISABLE)))
		
	oc.add(DirectoryObject(key = Callback(ClearCache), title = "Clear Cache", summary='Forces clearing of the Cache cookies and links. Cache items: %s' % (len(fmovies.CACHE)), thumb = R(ICON_CLEAR)))
	
	return oc

######################################################################################
@route(PREFIX + "/clearcache")
def ClearCache():
	
	fmovies.CACHE.clear()
	HTTP.ClearCache()
	return MC.message_container('Clear Cache', 'Cache has been cleared !')
	
	
######################################################################################
@route(PREFIX + "/testSite")
def testSite(url):
	try:
		resp = '0'
		cookies = None
		req = common.GetHttpRequest(url=url, cookies=cookies)
		if req != None:
			response = urllib2.urlopen(req, timeout=fmovies.GLOBAL_TIMEOUT_FOR_HTTP_REQUEST)
			resp = str(response.getcode())
		
		if resp in fmovies.HTTP_GOOD_RESP_CODES:
			page_data = HTML.ElementFromString(response.read())
			return (True, None, page_data)
		else:
			msg = ("HTTP Code %s for %s. Enable SSL option in Channel Prefs." % (resp, url))
			Log("HTTP Error: %s", msg)
			return (False, MC.message_container("HTTP Error", msg), None)
	except urllib2.HTTPError, err:
		msg = ("%s for %s" % (err.code, url))
		Log(msg)
		return (False, MC.message_container("HTTP Error %s" % (err.code), "Error: Try Enabling SSL option in Channel Prefs."), None)
	except urllib2.URLError, err:
		msg = ("%s for %s" % (err.args, url))
		Log(msg)
		return (False, MC.message_container("HTTP Error %s" % (err.args), "Error: Try Enabling SSL option in Channel Prefs."), None)

######################################################################################
@route(PREFIX + "/showMenu")
def ShowMenu(title):

	oc = ObjectContainer(title2 = title, no_cache=isForceNoCache())
	
	if title == CAT_GROUPS[0]:
		elems = CAT_WHATS_HOT
	elif title == CAT_GROUPS[1]:
		elems = CAT_REGULAR
	elif title == CAT_GROUPS[2]:
		elems = CAT_FILTERS
		
	if title == CAT_GROUPS[1]:
		for title in elems:
			oc.add(DirectoryObject(
				key = Callback(ShowCategory, title = title),
				title = title
				)
			)
	elif title == CAT_GROUPS[3]:
		
		page_data = common.GetPageElements(url=fmovies.BASE_URL)
		if page_data == None:
			bool, noc, page_data = testSite(url=fmovies.BASE_URL)
			if bool == False:
				return noc

		try:
			if len(SITE_NEWS_LOCS) == 0:
				elems = page_data.xpath(".//*[@id='body-wrapper']//div[@class='row movie-list']//div[@class='item']")
				for elem in elems:
					loc = fmovies.BASE_URL + elem.xpath(".//a[@class='name']//@href")[0]
					SITE_NEWS_LOCS.append(loc)
			
			if len(SITE_NEWS_LOCS) > 0:
				LOC = random.choice(SITE_NEWS_LOCS)
				page_data = common.GetPageElements(url=LOC)
				SITE_NEWS_LOCS.remove(LOC)
				notices = page_data.xpath(".//*[@id='movie']//div[@class='alert alert-warning']//b//text()")
				if notices[0] == '':
					notices = ['No site news Available.']
			else:
				notices = ['Could not connect to site.']
		except:
			notices = ['Could not connect to site.']
			
		for notice in notices:
			notice = unicode(notice)
			oc.add(DirectoryObject(
				title = notice,
				key = Callback(MC.message_container, 'Site News', 'No site news Available.'),
				summary = notice,
				thumb = R(ICON_INFO)
				)
			)
	else:
		for title in elems:
			if title == CAT_FILTERS[3]:
				oc.add(DirectoryObject(
					key = Callback(FilterSetup, title = title),
					title = title
					)
				)
			else:
				oc.add(DirectoryObject(
					key = Callback(SortMenu, title = title),
					title = title
					)
				)
			
	if common.UsingOption(key='ToggleDumbKeyboard'):
		DumbKeyboard(PREFIX, oc, Search,
				dktitle = 'Search',
				dkthumb = R(ICON_SEARCH)
		)
	else:
		oc.add(InputDirectoryObject(key = Callback(Search), thumb = R(ICON_SEARCH), title='Search', summary='Search Channel', prompt='Search for...'))
	return oc

######################################################################################
@route(PREFIX + "/sortMenu")
def SortMenu(title):

	url = fmovies.BASE_URL
	oc = ObjectContainer(title2 = title, no_cache=isForceNoCache())
	
	# Test for the site url initially to report a logical error
	page_data = common.GetPageElements(url = url)
	if page_data == None:
		bool, noc, page_data = testSite(url=url)
		if bool == False:
			return noc

	if title in CAT_FILTERS:
		if title == CAT_FILTERS[0]:
			elems = page_data.xpath(".//*[@id='menu']//li[@class='has-children'][3]//li//a")
		elif title == CAT_FILTERS[1]:
			elems = page_data.xpath(".//*[@id='menu']//li[@class='has-children'][1]//li//a")
		elif title == CAT_FILTERS[2]:
			elems = page_data.xpath(".//*[@id='menu']//li[@class='has-children'][2]//li//a")

		for elem in elems:
			key = elem.xpath(".//text()")[0]
			urlpath = elem.xpath(".//@href")[0]
			if 'http' not in urlpath:
				urlpath = fmovies.BASE_URL + urlpath
			skey=key
			key=key.replace(' ','-')
				
			oc.add(DirectoryObject(
				key = Callback(ShowCategory, title = title, urlpath = urlpath, key = key),
				title = skey
				)
			)
	elif title in CAT_WHATS_HOT:
		if title == CAT_WHATS_HOT[0]:
			elems = page_data.xpath(".//*[@id='header-wrapper']//div[@class='swiper-wrapper']//div[contains(@class, 'item swiper-slide')]")
			for elem in elems:
				name = elem.xpath(".//a[@class='name']//text()")[0]
				loc = fmovies.BASE_URL + elem.xpath(".//a[@class='name']//@href")[0]
				
				thumbstr = elem.xpath(".//@style")[0]
				matches = re.findall(ur"url=([^\"]*)\)", thumbstr)
				thumb = matches[0]
				quality = elem.xpath(".//div[@class='meta']//span[@class='quality']//text()")[0]
				summary = elem.xpath(".//p[@class='desc']//text()")[0]
				try:
					more_info_link = elem.xpath(".//@data-tip")[0]
				except:
					more_info_link = None

				oc.add(DirectoryObject(
					key = Callback(EpisodeDetail, title = name, url = loc, thumb = thumb),
					title = name + " (" + quality + ")",
					summary = GetMovieInfo(summary=summary, urlPath=more_info_link),
					thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback=ICON_UNAV)
					)
				)
		else:
			if title == CAT_WHATS_HOT[1]:
				elems = page_data.xpath(".//*[@id='body-wrapper']//div[@data-name='most-favorited']//div[@class='item']")
			elif title == CAT_WHATS_HOT[2]:
				elems = page_data.xpath(".//*[@id='body-wrapper']//div[@data-name='recommend']//div[@class='item']")
			elif title == CAT_WHATS_HOT[3]:
				elems = page_data.xpath(".//*[@id='body-wrapper']//div[@data-name='views-week']//div[@class='item']")
			elif title == CAT_WHATS_HOT[4]:
				elems = page_data.xpath(".//*[@id='body-wrapper']//div[@data-name='views-month']//div[@class='item']")
			elif title == CAT_WHATS_HOT[5]:
				elems = page_data.xpath(".//*[@id='body-wrapper']//div[@class='widget latest-movies']//div[@data-name='all']//div[@class='item']")
			elif title == CAT_WHATS_HOT[6]:
				elems = page_data.xpath(".//*[@id='body-wrapper']//div[@class='widget latest-series']//div[@class='item']")
			elif title == CAT_WHATS_HOT[7]:
				elems = page_data.xpath(".//*[@id='body-wrapper']//div[@class='widget requested']//div[@class='item']")
			
			for elem in elems:
				name = elem.xpath(".//a[@class='name']//text()")[0]
				loc = fmovies.BASE_URL + elem.xpath(".//a[@class='name']//@href")[0]
				thumb = elem.xpath(".//a[@class='poster']//@src")[0].split('url=')[1]
				summary = 'Plot Summary on Item Page.'
				
				eps_nos = ''
				title_eps_no = ''
				try:
					eps_nos = elem.xpath(".//div[@class='status']//span//text()")[0]
					eps_no_i = str(int(eps_nos.strip()))
					title_eps_no = ' (Eps:'+eps_no_i+')'
					eps_nos = ' Episodes: ' + eps_no_i
				except:
					pass
				
				try:
					more_info_link = elem.xpath(".//@data-tip")[0]
				except:
					more_info_link = None

				oc.add(DirectoryObject(
					key = Callback(EpisodeDetail, title = name, url = loc, thumb = thumb),
					title = name + title_eps_no,
					summary = GetMovieInfo(summary=summary, urlPath=more_info_link) + eps_nos,
					thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback=ICON_UNAV)
					)
				)
	
	if common.UsingOption(key='ToggleDumbKeyboard'):
		DumbKeyboard(PREFIX, oc, Search,
				dktitle = 'Search',
				dkthumb = R(ICON_SEARCH)
		)
	else:
		oc.add(InputDirectoryObject(key = Callback(Search), thumb = R(ICON_SEARCH), title='Search', summary='Search Channel', prompt='Search for...'))
	if len(oc) == 1:
		return MC.message_container(title, 'No Videos Available')
	return oc
	
######################################################################################
@route(PREFIX + "/showcategory")
def ShowCategory(title, key=' ', urlpath=None, page_count='1'):
	
	if urlpath != None:
		newurl = urlpath + '?page=%s' % page_count
	else:
		if title == CAT_FILTERS[0]:
			newurl = (fmovies.BASE_URL + '/release-' + key.lower() + '?page=%s' % page_count)
		elif title == CAT_FILTERS[1]:
			newurl = (fmovies.BASE_URL + '/genre/' + key.lower() + '?page=%s' % page_count)
		elif title == CAT_FILTERS[2]:
			newurl = (fmovies.BASE_URL + '/country/' + key.lower() + '?page=%s' % page_count)
		elif title == CAT_REGULAR[0]:
			newurl = (fmovies.BASE_URL + '/movies' + '?page=%s' % page_count)
		elif title == CAT_REGULAR[1]:
			newurl = (fmovies.BASE_URL + '/tv-series' + '?page=%s' % page_count)
		elif title == CAT_REGULAR[2]:
			newurl = (fmovies.BASE_URL + '/top-imdb' + '?page=%s' % page_count)
		elif title == CAT_REGULAR[3]:
			newurl = (fmovies.BASE_URL + '/most-watched' + '?page=%s' % page_count)
		
	page_data = common.GetPageElements(url=newurl)
	
	elems = page_data.xpath(".//*[@id='body-wrapper']//div[@class='row movie-list']//div[@class='item']")
	last_page_no = int(page_count)
	try:
		last_page_no = int(page_data.xpath(".//*[@id='body-wrapper']//ul[@class='pagination'][1]//li[last()-1]//text()")[0])
	except:
		pass
		
	if key != ' ':
		oc = ObjectContainer(title2 = title + '|' + key.title() + '|Page ' + str(page_count) + ' of ' + str(last_page_no), no_cache=isForceNoCache())
	else:
		oc = ObjectContainer(title2 = title + '|Page ' + str(page_count) + ' of ' + str(last_page_no), no_cache=isForceNoCache())
		
	for elem in elems:
		name = elem.xpath(".//a[@class='name']//text()")[0]
		loc = fmovies.BASE_URL + elem.xpath(".//a[@class='name']//@href")[0]
		thumb = elem.xpath(".//a[@class='poster']//@src")[0].split('url=')[1]
		summary = 'Plot Summary on Item Page.'
		
		eps_nos = ''
		title_eps_no = ''
		try:
			eps_nos = elem.xpath(".//div[@class='status']//span//text()")[0]
			eps_no_i = str(int(eps_nos.strip()))
			title_eps_no = ' (Eps:'+eps_no_i+')'
			eps_nos = ' Episodes: ' + eps_no_i
		except:
			pass
		try:
			more_info_link = elem.xpath(".//@data-tip")[0]
		except:
			more_info_link = None

		oc.add(DirectoryObject(
			key = Callback(EpisodeDetail, title = name, url = loc, thumb = thumb),
			title = name + title_eps_no,
			summary = GetMovieInfo(summary=summary, urlPath=more_info_link) + eps_nos,
			thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback=ICON_UNAV)
			)
		)
		
	if int(page_count) < last_page_no:
		oc.add(NextPageObject(
			key = Callback(ShowCategory, title = title, key = key, urlpath = urlpath, page_count = str(int(page_count) + 1)),
			title = "Next Page (" + str(int(page_count) + 1) +'/'+ str(last_page_no) + ") >>",
			thumb = R(ICON_NEXT)
			)
		)
		
	if common.UsingOption(key='ToggleDumbKeyboard'):
		DumbKeyboard(PREFIX, oc, Search,
				dktitle = 'Search',
				dkthumb = R(ICON_SEARCH)
		)
	else:
		oc.add(InputDirectoryObject(key = Callback(Search), thumb = R(ICON_SEARCH), title='Search', summary='Search Channel', prompt='Search for...'))

	if len(oc) == 1:
		return MC.message_container(title, 'No More Videos Available')
		
	oc.add(DirectoryObject(
		key = Callback(MainMenu),
		title = '<< Main Menu',
		thumb = R(ICON)
		)
	)
	
	return oc

######################################################################################
@route(PREFIX + "/episodedetail")
def EpisodeDetail(title, url, thumb):

	page_data = common.GetPageElements(url=url)
	if page_data == None:
		return MC.message_container("Unknown Error", "Error: The page was not received.")
		
	session = common.getSession()
	client_id = '%s-%s' % (Client.Product, session)
	if client_id not in CUSTOM_TIMEOUT_DICT:
		CUSTOM_TIMEOUT_DICT[client_id] = {}
		
	try:
		title = unicode(page_data.xpath(".//*[@id='info']//h1[@class='name']//text()")[0])
	except:
		title = unicode(title)
		
	try:
		item_unav = ''
		errs = page_data.xpath(".//*[@id='movie']//div[@class='alert alert-primary notice'][2]//text()")
		for err in errs:
			if 'There is no server for this movie right now, please try again later.' in err:
				item_unav = ' ' + common.GetEmoji(type='neg')
				break
	except:
		pass
		
	try:
		if thumb == None:
			thumb = page_data.xpath(".//*[@id='info']//div//img")[0].split('url=')[1]
	except:
		thumb = R(ICON_UNAV)
		
	try:
		serverts = page_data.xpath(".//body[@class='watching']//@data-ts")[0]
	except:
		serverts = 0
	
	try:
		art = page_data.xpath(".//meta[@property='og:image'][1]//@content")[0]
	except:
		art = 'https://cdn.rawgit.com/coder-alpha/FMoviesPlus.bundle/master/Contents/Resources/art-default.jpg'
	oc = ObjectContainer(title2 = title + item_unav, art = art, no_cache=isForceNoCache())
	
	try:
		summary = page_data.xpath(".//*[@id='info']//div[@class='info col-md-19']//div[@class='desc']//text()")[0]
		#summary = re.sub(r'[^0-9a-zA-Z \-/.,\':+&!()]', '', summary)
	except:
		summary = 'Summary Not Available.'
	
	try:
		trailer = page_data.xpath(".//*[@id='control']//div['item mbtb watch-trailer hidden-xs']//@data-url")[0]
	except:
		trailer = None
	
	try:
		year = str(page_data.xpath(".//*[@id='info']//dl[@class='meta col-sm-12'][2]//dd[2]//text()")[0][0:4])
	except:
		year = 'Not Available'
		
	try:
		rating = str(page_data.xpath(".//*[@id='info']//div[@class='info col-md-19']//span[1]//b//text()")[0])
	except:
		rating = 'Not Available'
		
	try:
		duration = int(page_data.xpath(".//*[@id='info']//div[@class='info col-md-19']//span[2]//b//text()")[0].strip('/episode').strip(' min'))
	except:
		duration = 'Not Available'

	try:
		genre0 = page_data.xpath(".//*[@id='info']//dl[@class='meta col-sm-12'][1]//dd[1]//a//text()")
		genre = (','.join(str(x) for x in genre0))
		if genre == '':
			genre = 'Not Available'
	except:
		genre = 'Not Available'
	
	try:
		directors0 = page_data.xpath(".//*[@id='info']//dl[@class='meta col-sm-12'][1]//dd[3]//text()")
		directors = (','.join(str(x) for x in directors0))
		if directors.strip() == '...':
			directors = 'Not Available'
	except:
		directors = 'Not Available'
	
	try:
		roles0 = page_data.xpath(".//*[@id='info']//dl[@class='meta col-sm-12'][1]//dd[2]//a//text()")
		roles = (','.join(str(x) for x in roles0))
		if roles == '':
			roles = 'Not Available'
	except:
		roles = 'Not Available'
	
	try:
		servers = page_data.xpath(".//*[@id='servers']//div[@class='server row']")
	except:
		servers = []
	
	summary += '\n '
	summary += 'Actors: ' + roles + '\n '
	summary += 'Directors: ' + directors + '\n '
	
	if str(duration) == 'Not Available':
		summary += 'Runtime: ' + str(duration) + '\n '
	else:
		summary += 'Runtime: ' + str(duration) + ' min.' + '\n '
	
	summary += 'Year: ' + year + '\n '
	summary += 'Genre: ' + genre + '\n '
	summary += 'IMDB rating: ' + rating + '\n '
	
	summary = unicode(summary)
	
	try:
		similar_reccos = []
		similar_reccos_elems = page_data.xpath(".//*[@id='movie']//div[@class='row movie-list']//div[@class='item']")

		for elem in similar_reccos_elems:
			similar_reccos_name = elem.xpath(".//a[@class='name']//text()")[0]
			similar_reccos_loc = elem.xpath(".//a[@class='name']//@href")[0]
			similar_reccos_thumb = elem.xpath(".//a[@class='poster']//@src")[0].split('url=')[1]
			try:
				eps_nos = elem.xpath(".//div[@class='status']//span//text()")[0]
				eps_nos = ' Episodes: ' + str(int(eps_nos.strip()))
			except:
				eps_nos = ''
			try:
				similar_reccos_more_info_link = elem.xpath(".//@data-tip")[0]
			except:
				similar_reccos_more_info_link = None
			similar_reccos.append({'name':similar_reccos_name, 'loc':similar_reccos_loc, 'thumb':similar_reccos_thumb, 'more_info_link':similar_reccos_more_info_link, 'eps_nos':eps_nos})
	except:
		similar_reccos = []
		
	try:
		tags0 = page_data.xpath(".//*[@id='tags']//a//text()")
		tags = (','.join(str(x) for x in tags0))
		if tags == '':
			tags = 'Not Available'
	except:
		tags = 'Not Available'
	
	episodes = []
	try:
		episodes = page_data.xpath(".//*[@id='movie']//div[@class='widget boxed episode-summary']//div[@class='item']")
	except:
		pass
		
	servers_list = {}
	episodes_list = []
	server_lab = []
	isTvSeries = False
	
	try:
		item_type = page_data.xpath(".//div[@id='movie']/@data-type")[0]
		if item_type == 'series':
			isTvSeries = True
	except:
		pass
		
	for server in servers:
		label = server.xpath(".//label[@class='name col-md-4 col-sm-5']//text()[2]")[0].strip()
		if 'Server F' in label:
			label = label.replace('Server F','Google ')
		
		server_lab.append(label)
		items = server.xpath(".//ul//li")
		if len(items) > 1:
			isTvSeries = True
			
		servers_list[label] = []
		c=0
		for item in items:
			servers_list[label].append([])
			servers_list[label][c]={}
			label_qual = item.xpath(".//a//text()")[0].strip()
			label_val = item.xpath(".//a//@data-id")[0]
			servers_list[label][c]['quality'] = label_qual
			servers_list[label][c]['loc'] = label_val
			c += 1

	# label array of servers available - sort them so that presentation order is consistent
	server_lab = sorted(server_lab)
	
	# remap server list - this way its easier to iterate for tv-show episodes
	servers_list_new = []
	c=0
	
	if len(servers_list) > 0:
		for k in servers_list:
			break
		for no in servers_list[k]:
			servers_list_new.append([])
			servers_list_new[c] = {}
			for label in servers_list:
				servers_list_new[c][label] = {}
				try:
					servers_list_new[c][label] = {'quality':servers_list[label][c]['quality'], 'loc':servers_list[label][c]['loc']}
				except:
					if c > 99:
						servers_list_new[c][label] = {'quality':"%03d" % (c+1), 'loc':''}
					else:
						servers_list_new[c][label] = {'quality':"%02d" % (c+1), 'loc':''}
			c += 1
		
	# trailer
	if trailer != None:
		oc.add(VideoClipObject(
			url = trailer,
			title = title + ' (Trailer)',
			thumb = thumb,
			art = art,
			summary = summary)
		)
		
	if len(episodes) > 0:
		# case for presenting tv-series with synopsis
		if Prefs["use_debug"]:
			Log("case for presenting tv-series with synopsis")
		det_Season = title.replace(' (Special)','').split(' ')
		SeasonN = 0
		try:
			SeasonN = int(det_Season[len(det_Season)-1])
			oc.title2 = title.replace(str(SeasonN), '(Season ' + str(SeasonN) + ')')
		except:
			oc.title2 = title
			
		c_not_missing = 1
		for episode in episodes:
			ep_no = None
			try:
				noS = episode.xpath(".//div[@class='ep']//i//text()")[0].strip()
				no = noS
				ep_no = int(no)
			except:
				no = '0'
				
			if no != '0' and ep_no == c_not_missing:
				try:
					name = episode.xpath(".//span[@class='name']//text()")[0]
				except:
					name = 'Episode Name Not Available.'
				try:
					air_date = episode.xpath(".//div[@class='date']//text()")[0]
				except:
					air_date = ''
				try:
					desc = episode.xpath(".//div[@class='desc']//text()")[0]
				except:
					desc = 'Episode Summary Not Available.'

				episodes_list.append({"name":name,"air_date":air_date,"desc":desc})
			else:
				# episode does not have a number - could be a Special - its listed alphabetically but might fall in a different airing sequence
				c=0
				successIns = False
				for eps in servers_list_new:
					
					if noS in eps[server_lab[0]]['quality']:
						try:
							name = episode.xpath(".//span[@class='name']//text()")[0]
						except:
							name = 'Episode Name Not Available.'
						try:
							air_date = episode.xpath(".//div[@class='date']//text()")[0]
						except:
							air_date = ''
						try:
							desc = episode.xpath(".//div[@class='desc']//text()")[0]
						except:
							desc = 'Episode Summary Not Available.'
						episodes_list.insert(c, {"name":name,"air_date":air_date,"desc":desc})
						successIns = True
						break
					c += 1
				if not successIns:
					episodes_list.append({"name":'',"air_date":'',"desc":''})
			c_not_missing += 1
		
		eps_i = 1
		c_not_missing=-1
		c=0
		for eps in servers_list_new:
		
			if '-' in eps[server_lab[0]]['quality'] and verify2partcond(eps[server_lab[0]]['quality']): # 2 part episode condition
				qual_i = (int(eps[server_lab[0]]['quality'].split('-')[0])-eps_i)
				eps_i += 1
			else:
				try:
					qual_i = (int(eps[server_lab[0]]['quality'])-eps_i)
				except:
					qual_i = c_not_missing+1
					eps_i = eps_i-1
			
			try:
				if '-' in eps[server_lab[0]]['quality'] and episodes_list[qual_i]['name'] in eps[server_lab[0]]['quality'] and not verify2partcond(eps[server_lab[0]]['quality']):
					title_s = 'Ep:' + eps[server_lab[0]]['quality']
				else:
					title_s = 'Ep:' + eps[server_lab[0]]['quality'] + ' - ' + episodes_list[qual_i]['name']
			except:
				title_s = 'Ep:' + eps[server_lab[0]]['quality']
			try:
				desc = episodes_list[qual_i]['air_date'] + " : " + episodes_list[qual_i]['desc']
			except:
				desc = 'Episode Summary Not Available.'
				
			try:
				oc.add(DirectoryObject(
					key = Callback(TvShowDetail, tvshow=title, title=title_s, url=url, servers_list_new=servers_list_new[c], server_lab=(','.join(str(x) for x in server_lab)), summary=desc+'\n '+summary, thumb=thumb, art=art, year=year, rating=rating, duration=duration, genre=genre, directors=directors, roles=roles, serverts=serverts),
					title = title_s,
					summary = desc+ '\n ' +summary,
					art = art,
					thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback=ICON_UNAV)
					)
				)
				c_not_missing = qual_i
				c += 1
			except Exception as e:
				Log('ERROR init.py>EpisodeDetail>Tv1 %s, %s' % (e.args, title_s))
				pass
			
		if SeasonN > 0 or True: # enable for all - even if this might be a single season
			oc.add(DirectoryObject(
			key = Callback(Search, query = title.replace(str(SeasonN),'').replace('(Special)','').strip(), mode='other seasons', thumb=thumb, summary=summary),
			title = "Other Seasons",
			summary = 'Other Seasons of ' + title.replace(str(SeasonN),'').replace('(Special)','').strip(),
			art = art,
			thumb = R(ICON_OTHERSEASONS)
			))

		isTvSeries = True
	elif isTvSeries:
		# case for presenting tv-series without synopsis
		if Prefs["use_debug"]:
			Log("case for presenting tv-series without synopsis")
		det_Season = title.replace(' (Special)','').split(' ')
		SeasonN = 0
		try:
			SeasonN = int(det_Season[len(det_Season)-1])
			oc.title2 = title.replace(str(SeasonN), '(Season ' + str(SeasonN) + ')')
		except:
			oc.title2 = title
			
		c=0
		for eps in servers_list_new:
			try:
				title_s = 'Ep:' + eps[server_lab[0]]['quality']
				oc.add(DirectoryObject(
					key = Callback(TvShowDetail, tvshow=title, title=title_s, url=url, servers_list_new=servers_list_new[c], server_lab=(','.join(str(x) for x in server_lab)), summary='Episode Summary Not Available.\n ' + summary, thumb=thumb, art=art, year=year, rating=rating, duration=duration, genre=genre, directors=directors, roles=roles, serverts=serverts),
					title = title_s,
					summary = 'Episode Summary Not Available.\n ' + summary,
					thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback=ICON_UNAV)
					)
				)
				c += 1
			except Exception as e:
				Log('ERROR init.py>EpisodeDetail>Tv2 %s, %s' % (e.args, title_s))
				pass
		if SeasonN > 0 or True: # enable for all - even if this might be a single season
			oc.add(DirectoryObject(
			key = Callback(Search, query = title.replace(str(SeasonN),'').replace('(Special)','').strip(), mode='other seasons', thumb=thumb, summary=summary),
			title = "Other Seasons",
			summary = 'Other Seasons of ' + title.replace(str(SeasonN),'').replace('(Special)','').strip(),
			art = art,
			thumb = R(ICON_OTHERSEASONS)
			))
	else:
		# case for presenting movies
		if Prefs["use_debug"]:
			Log("case for presenting movies")
		
		# create timeout thread
		Thread.Create(ThreadTimeoutTimer, {}, Client.Product, E(url), client_id)
	
		for label in server_lab:
			for label_i in servers_list[label]:
				try:
					title_s = label + ' - ' + label_i['quality']
					url_s = label_i['loc']
					server_info, isOpenLoad = fmovies.GetApiUrl(url=url, key=url_s, serverts=serverts)
					if server_info != None:
						status = ''
						isVideoOnline = 'unknown'
						if Prefs["use_linkchecker"]:
							data = server_info
							if not isOpenLoad:
								data = E(JSON.StringFromObject({"server":server_info}))
							isVideoOnline = isItemVidAvailable(isOpenLoad=isOpenLoad, data=data)
							status = common.GetEmoji(type=isVideoOnline) + ' '
						
						try:
							redirector_stat = ''
							redirector_enabled = 'false'
							if common.UsingOption(key='ToggleRedirector') and isOpenLoad == False:
								redirector_stat = ' (via Redirector)'
								redirector_enabled = 'true'
								
							durl = "fmovies://" + E(JSON.StringFromObject({"url":url, "server":server_info, "title":title, "summary":summary, "thumb":thumb, "art":art, "year":year, "rating":rating, "duration":str(duration), "genre":genre, "roles":roles, "directors":directors, "roles":roles, "isOpenLoad":str(isOpenLoad), "useSSL":str(Prefs["use_https_alt"]), "isVideoOnline":str(isVideoOnline), "useRedirector": redirector_enabled}))
							
							oc.add(VideoClipObject(
								url = durl,
								title = status + title + ' - ' + title_s + redirector_stat,
								thumb = thumb,
								art = art,
								summary = summary,
								key = AddRecentWatchList(title=title, url=url, summary=summary, thumb=thumb)
								)
							)
						except Exception as e:
							Log('ERROR init.py>EpisodeDetail>Movie %s, %s' % (e.args, (title + ' - ' + title_s)))
							Log("ERROR: %s with key:%s returned %s" % (url,url_s,server_info))
					else:
						pass
						if Prefs["use_debug"]:
							Log("Video will not be displayed as playback option !")
							Log("ERROR: %s with key:%s returned %s" % (url,url_s,server_info))
				except Exception as e:
					Log('ERROR init.py>EpisodeDetail>Movie %s, %s' % (e.args, (title + ' - ' + title_s)))
					pass
			if isTimeoutApproaching(clientProd = Client.Product, item = E(url), client_id=client_id):
				Log("isTimeoutApproaching action")
				break
				#return MC.message_container('Timeout', 'Timeout: Please try again !')
						
	itemtype = ('show' if isTvSeries else 'movie')
						
	if len(similar_reccos) > 0:
		oc.add(DirectoryObject(
			key = Callback(SimilarRecommendations, title = title, similar_reccos = E(JSON.StringFromObject(similar_reccos))),
			title = "Similar Recommendations",
			summary = 'Discover other %s similar to %s' % (itemtype, title),
			art = art,
			thumb = R(ICON_SIMILAR)
		)
	)
	
	if roles != 'Not Available':
		oc.add(DirectoryObject(
			key = Callback(MoviesWithPeople, stars = roles),
			title = "People Search",
			summary = 'Search for movies/shows based on a person from the current %s' % (itemtype),
			art = art,
			thumb = R(ICON_PEOPLE)
		)
	)
	
	if tags != 'Not Available':
		oc.add(DirectoryObject(
			key = Callback(MoviesWithTag, tags = tags),
			title = "Tag Search",
			summary = 'Search for movies/shows based on a Tag from the current %s' % (itemtype),
			art = art,
			thumb = R(ICON_TAG)
		)
	)
		
	if Check(title=title,url=url):
		oc.add(DirectoryObject(
			key = Callback(RemoveBookmark, title = title, url = url),
			title = "Remove Bookmark",
			summary = 'Removes the current %s from the Boomark que' % (itemtype),
			art = art,
			thumb = R(ICON_QUEUE)
		)
	)
	else:
		oc.add(DirectoryObject(
			key = Callback(AddBookmark, title = title, url = url, summary=summary, thumb=thumb),
			title = "Add Bookmark",
			summary = 'Adds the current %s to the Boomark que' % (itemtype),
			art = art,
			thumb = R(ICON_QUEUE)
		)
	)
	
	return oc

@route(PREFIX + "/TvShowDetail")
def TvShowDetail(tvshow, title, url, servers_list_new, server_lab, summary, thumb, art, year, rating, duration, genre, directors, roles, serverts):

	oc = ObjectContainer(title2 = title, art = art, no_cache=isForceNoCache())

	servers_list_new = servers_list_new.replace("'", "\"")
	servers_list_new = json.loads(servers_list_new)
	
	server_lab = server_lab.split(',')
	
	session = common.getSession()
	client_id = '%s-%s' % (Client.Product, session)
		
	# create timeout thread
	Thread.Create(ThreadTimeoutTimer, {}, Client.Product, E(url), client_id)
	
	for label in server_lab:
		url_s = servers_list_new[label]['loc']
		server_info,isOpenLoad = fmovies.GetApiUrl(url=url, key=url_s, serverts=serverts)
		if server_info != None:
			status = ''
			isVideoOnline = 'unknown'
			if Prefs["use_linkchecker"]:
				data = server_info
				if not isOpenLoad:
					data = E(JSON.StringFromObject({"server":server_info}))
				isVideoOnline = isItemVidAvailable(isOpenLoad=isOpenLoad, data=data)
				status = common.GetEmoji(type=isVideoOnline) + ' '
				
				
			redirector_stat = ''
			redirector_enabled = 'false'
			if common.UsingOption(key='ToggleRedirector') and isOpenLoad == False:
				redirector_stat = ' (via Redirector)'
				redirector_enabled = 'true'
			
			durl = "fmovies://" + E(JSON.StringFromObject({"url":url, "server":server_info, "title":title, "summary":summary, "thumb":thumb, "art":art, "year":year, "rating":rating, "duration":str(duration), "genre":genre, "directors":directors, "roles":roles, "isOpenLoad":str(isOpenLoad), "useSSL":str(Prefs["use_https_alt"]), "isVideoOnline":str(isVideoOnline), "useRedirector": redirector_enabled}))
			try:
				oc.add(VideoClipObject(
					url = durl,
					title = status + title + ' (' + label + ')' + redirector_stat,
					thumb = thumb,
					art = art,
					summary = summary,
					key = AddRecentWatchList(title = "%s - %s" % (tvshow,title), url=url, summary=summary, thumb=thumb)
					)
				)
			except:
				Log('ERROR init.py>TvShowDetail %s, %s' % (e.args, (title + ' - ' + title_s)))
				Log("ERROR: %s with key:%s returned %s" % (url,url_s,server_info))
		else:
			pass
			if Prefs["use_debug"]:
				Log("Video will not be displayed as playback option !")
				Log("ERROR: %s with key:%s returned %s" % (url,url_s,server_info))
			
		if isTimeoutApproaching(clientProd = Client.Product, item = E(url), client_id=client_id):
			Log("isTimeoutApproaching action")
			break
			#return MC.message_container('Timeout', 'Timeout: Please try again !')

	return oc

####################################################################################################
@route(PREFIX + "/ThreadTimeoutTimer")	
def ThreadTimeoutTimer(clientProd, item, client_id):

	if clientProd in CUSTOM_TIMEOUT_CLIENTS:
		c=0
		while c < 60:
			CUSTOM_TIMEOUT_DICT[client_id][item] = c
			time.sleep(1.0)
			c += 1
			
		del CUSTOM_TIMEOUT_DICT[client_id][item]
	
####################################################################################################
@route(PREFIX + "/isTimeoutApproaching")	
def isTimeoutApproaching(clientProd, item, client_id):
	
	# define custom timeouts for each client along with session & item to make it unique for multiple instances
	
	if Client.Product in CUSTOM_TIMEOUT_CLIENTS:
		t_sec = int(CUSTOM_TIMEOUT_DICT[client_id][item])
		if t_sec < int(CUSTOM_TIMEOUT_CLIENTS[clientProd]):
			if Prefs["use_debug"]:
				Log("Custom Timout Timer: %s on %s: %s sec." % (D(item), client_id, t_sec))
			return False
	else:
		# return False for clients not defined in custom timeout checker
		return False
	
	# remove entry before returning True
	if Prefs["use_debug"]:
		Log("Custom Timout was reached for %s on %s" % (D(item), client_id))
		
	del CUSTOM_TIMEOUT_DICT[client_id][item]
	return True

####################################################################################################
@route(PREFIX + "/SimilarRecommendations")	
def SimilarRecommendations(title, similar_reccos):

	oc = ObjectContainer(title2 = 'Similar to ' + title, no_cache=isForceNoCache())
	
	similar_reccos = JSON.ObjectFromString(D(similar_reccos))
	
	for elem in similar_reccos:
		name = elem['name']
		loc = fmovies.BASE_URL + elem['loc']
		thumb = elem['thumb']
		eps_nos = elem['eps_nos']
		summary = 'Plot Summary on Item Page.'
		more_info_link = elem['more_info_link']

		oc.add(DirectoryObject(
			key = Callback(EpisodeDetail, title = name, url = loc, thumb = thumb),
			title = name,
			summary = GetMovieInfo(summary=summary, urlPath=more_info_link) + eps_nos,
			thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback=ICON_UNAV)
			)
		)
	
	oc.add(DirectoryObject(
		key = Callback(MainMenu),
		title = '<< Main Menu',
		thumb = R(ICON)
		)
	)
	
	return oc
	
####################################################################################################
@route(PREFIX + "/MoviesWithPeople")
def MoviesWithPeople(stars):

	oc = ObjectContainer(title2 = 'People Search', no_cache=isForceNoCache())
	
	roles_s = stars.split(',')
	if len(roles_s) > 0:
		roles_s = sorted(roles_s)
	for role in roles_s:
		role = common.removeAccents(role)
		oc.add(DirectoryObject(
			key = Callback(Search, query = role, surl= fmovies.BASE_URL + fmovies.STAR_PATH + role.lower().replace(' ', '-'), mode = 'people'),
			title = role + ' >>>',
			summary = 'Other movie/show starring ' + role,
			thumb = R(ICON_STAR)
			)
		)
	
	oc.add(DirectoryObject(
		key = Callback(MainMenu),
		title = '<< Main Menu',
		thumb = R(ICON)
		)
	)
	
	return oc
	
####################################################################################################
@route(PREFIX + "/MoviesWithTag")	
def MoviesWithTag(tags):

	oc = ObjectContainer(title2 = 'Tag Search', no_cache=isForceNoCache())
	
	tags_s = tags.split(',')
	if len(tags_s) > 0:
		tags_s = sorted(tags_s)
	for tag in tags_s:
		tag = re.sub(r'[^0-9a-zA-Z ]', '', tag)
		oc.add(DirectoryObject(
			key = Callback(Search, query = tag, surl= fmovies.BASE_URL + fmovies.KEYWORD_PATH + tag.lower().replace(' ', '-'), mode = 'tag'),
			title = tag + ' >>>',
			summary = 'Other movie/show with keyword ' + tag,
			thumb = R(ICON_TAG)
			)
		)
	
	oc.add(DirectoryObject(
		key = Callback(MainMenu),
		title = '<< Main Menu',
		thumb = R(ICON)
		)
	)
	
	return oc
	
####################################################################################################
@route(PREFIX + "/getmovieinfo")
def GetMovieInfo(summary, urlPath):

	if NoMovieInfo or urlPath == None and (summary == None or summary == ''):
		return 'Plot Summary on Item Page'
	elif urlPath == None:
		return summary
		
	if Prefs["dont_fetch_more_info"]:
		return summary

	try:
		url = fmovies.BASE_URL + '/' + urlPath
		page_data = common.GetPageElements(url=url)
		
		summary = ''
		
		try:
			summary_n = page_data.xpath(".//div[@class='inner']//p[@class='desc']//text()")[0]
			summary = summary_n + ' |\n '
		except:
			pass
		
		try:
			quality = page_data.xpath(".//div[@class='inner']//span[@class='quality']//text()")[0]
			year = page_data.xpath(".//div[@class='inner']//div[@class='title']//span//text()")[0]
			rating = (page_data.xpath(".//div[@class='inner']//span[@class='imdb']//text()"))[1].strip()
			summary += 'IMDb: ' + rating + ' | ' + 'Year: ' + year + ' | ' + 'Quality: ' + quality + ' |\n '
		except:
			pass
		
		try:
			country = page_data.xpath(".//div[@class='inner']//div[@class='meta'][1]//a//text()")[0]
			genre = page_data.xpath(".//div[@class='inner']//div[@class='meta'][2]//a//text()")[0]
			summary += 'Country: ' + country + ' | ' + 'Genre: ' + genre + ' |\n '
		except:
			pass
		
		try:
			actors = (page_data.xpath(".//div[@class='inner']//div[@class='meta'][3]//text()"))[2].strip()
			summary += 'Actors: ' + actors + '\n '
		except:
			pass
			
		if summary == '':
			summary = 'Plot Summary on Item Page'

	except:
		summary = 'Plot Summary on Item Page'
		
	return summary
	
######################################################################################
# Adds a movie to the RecentWatchList list using the (title + 'R4S') as a key for the url
@route(PREFIX + "/addRecentWatchList")
def AddRecentWatchList(title, url, summary, thumb):

	#append the time string to title so we can sort old to new items
	try:
		timestr = str(int(time.time()))
		Dict[timestr+'RR44SS'+title+'RR44SS'] = title + 'RR44SS' + url +'RR44SS'+ summary + 'RR44SS' + thumb + 'RR44SS' + timestr 
		Dict.Save()
	except:
		pass
		
	return None

######################################################################################
# Loads RecentWatchList shows from Dict.  Titles are used as keys to store the show urls.
@route(PREFIX + "/RecentWatchList")
def RecentWatchList(title):

	oc = ObjectContainer(title1=title, no_cache=isForceNoCache())
	NO_OF_ITEMS_IN_RECENT_LIST = 50
	
	urls_list = []
	items_to_del = []
	items_in_recent = []
	
	for each in Dict:
		longstring = str(Dict[each])
		
		if 'https:' in longstring and 'RR44SS' in longstring:
			longstringsplit = longstring.split('RR44SS')
			urls_list.append({'key': each, 'time': longstringsplit[4], 'val': longstring})
				
	if len(urls_list) == 0:
		return MC.message_container(title, 'No Items Available')
		
	newlist = sorted(urls_list, key=lambda k: k['time'], reverse=True)

	c=0
	for each in newlist:
	
		longstring = each['val']
		longstringsplit = longstring.split('RR44SS')
		stitle = unicode(longstringsplit[0])
		url = longstringsplit[1]
		summary = unicode(longstringsplit[2])
		thumb = longstringsplit[3]
		timestr = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(longstringsplit[4])))
		
		if url in items_in_recent or c > NO_OF_ITEMS_IN_RECENT_LIST:
			items_to_del.append(each['key'])
		else:
			items_in_recent.append(url)
				
			oc.add(DirectoryObject(
				key=Callback(EpisodeDetail, title=stitle, url=url, thumb=thumb),
				title=stitle,
				thumb=thumb,
				tagline = timestr,
				summary=summary
				)
			)
			c += 1

	if c >= NO_OF_ITEMS_IN_RECENT_LIST or len(items_to_del) > 0:
		for each in items_to_del:
			del Dict[each]
		Dict.Save()

	#oc.objects.sort(key=lambda obj: obj.tagline, reverse=True)
	
	#add a way to clear RecentWatchList list
	oc.add(DirectoryObject(
		key = Callback(ClearRecentWatchList),
		title = "Clear Recent WatchList",
		thumb = R(ICON_QUEUE),
		summary = "CAUTION! This will clear your entire Recent WatchList !"
		)
	)
	
	return oc
	
######################################################################################
# Clears the Dict that stores the bookmarks list
@route(PREFIX + "/clearRecentWatchList")
def ClearRecentWatchList():

	remove_list = []
	for each in Dict:
		try:
			longstring = Dict[each]
			if longstring.find(SITE.lower()) != -1 and 'http' in longstring and 'RR44SS' in longstring:
				remove_list.append(each)
		except:
			continue

	for watchlist in remove_list:
		try:
			del Dict[watchlist]
		except Exception as e:
			Log.Error('Error Clearing Recent WatchList: %s' %str(e))
			continue

	Dict.Save()
	return MC.message_container("My Recent WatchList", 'Your Recent WatchList list will be cleared soon.')
	
######################################################################################
# Loads bookmarked shows from Dict.  Titles are used as keys to store the show urls.
@route(PREFIX + "/bookmarks")
def Bookmarks(title):

	oc = ObjectContainer(title1=title, no_cache=isForceNoCache())
	
	for each in Dict:
		longstring = str(Dict[each])
		
		if 'https:' in longstring and 'Key5Split' in longstring:	
			stitle = unicode(longstring.split('Key5Split')[0])
			url = longstring.split('Key5Split')[1]
			summary = unicode(longstring.split('Key5Split')[2])
			thumb = longstring.split('Key5Split')[3]
			
			if fmovies.FILTER_PATH in url:
				oc.add(DirectoryObject(
					key=Callback(Search, query=stitle.replace(' (All Seasons)',''), mode='other seasons', thumb=thumb, summary=summary),
					title=stitle,
					thumb=thumb,
					summary=summary
					)
				)
			else:
				oc.add(DirectoryObject(
					key=Callback(EpisodeDetail, title=stitle, url=url, thumb=thumb),
					title=stitle,
					thumb=thumb,
					summary=summary
					)
				)
				
	if len(oc) == 0:
		return MC.message_container(title, 'No Bookmarked Videos Available')
		
	oc.objects.sort(key=lambda obj: obj.title, reverse=False)
	
	#add a way to clear bookmarks list
	oc.add(DirectoryObject(
		key = Callback(ClearBookmarks),
		title = "Clear Bookmarks",
		thumb = R(ICON_QUEUE),
		summary = "CAUTION! This will clear your entire bookmark list!"
		)
	)
		
	return oc
	
######################################################################################
# Converts old style bookmarks
@route(PREFIX + "/convertbookmarks")
def convertbookmarks():

	try:
		Covert_List = {}
		Delete_List = []
		for each in Dict:
			longstring = str(Dict[each])
			
			if 'https:' in longstring and 'Key4Split' in longstring:	
				title = unicode(longstring.split('Key4Split')[0])
				url = longstring.split('Key4Split')[1]
				summary = unicode(longstring.split('Key4Split')[2])
				thumb = longstring.split('Key4Split')[3]
				
				Covert_List[title+'-'+E(url)] = (title + 'Key5Split' + url +'Key5Split'+ summary + 'Key5Split' + thumb)
				Delete_List.append(title)
		
		if len(Covert_List) > 0:
			for item in Covert_List:
				Dict[item] = Covert_List[item]
			
		if len(Delete_List) > 0:
			for item in Delete_List:
				del Dict[item]
				
		CONVERT_BMS.append('Done')
		Dict.Save()
	except:
		pass

######################################################################################
# Checks a show to the bookmarks list using the title as a key for the url
@route(PREFIX + "/checkbookmark")
def Check(title, url):
	
	longstring = Dict[title+'-'+E(url)]
	if longstring != None and (longstring.lower()).find(SITE.lower()) != -1 and url in longstring:
		return True
	return False

######################################################################################
# Adds a movie to the bookmarks list using the title as a key for the url
@route(PREFIX + "/addbookmark")
def AddBookmark(title, url, summary, thumb):

	if Check(title=title, url=url):
		return MC.message_container(title, 'This item has already been added to your bookmarks.')
		
	Dict[title+'-'+E(url)] = (title + 'Key5Split' + url +'Key5Split'+ summary + 'Key5Split' + thumb)
	Dict.Save()
	return MC.message_container(title, 'This item has been added to your bookmarks.')

######################################################################################
# Removes a movie to the bookmarks list using the title as a key for the url
@route(PREFIX + "/removebookmark")
def RemoveBookmark(title, url):
	del Dict[title+'-'+E(url)]
	Dict.Save()
	return MC.message_container(title, 'This item has been removed from your bookmarks.')

######################################################################################
# Clears the Dict that stores the bookmarks list
@route(PREFIX + "/clearbookmarks")
def ClearBookmarks():

	remove_list = []
	for each in Dict:
		try:
			url = Dict[each]
			if url.find(SITE.lower()) != -1 and 'http' in url and 'RR44SS' not in url:
				remove_list.append(each)
		except:
			continue

	for bookmark in remove_list:
		try:
			del Dict[bookmark]
		except Exception as e:
			Log.Error('Error Clearing Bookmarks: %s' %str(e))
			continue

	Dict.Save()
	return MC.message_container("Bookmarks", 'Your bookmark list will be cleared soon.')

######################################################################################
# Clears the Dict that stores the search list
@route(PREFIX + "/clearsearches")
def ClearSearches():

	remove_list = []
	for each in Dict:
		try:
			if each.find(SITE.lower()) != -1 and 'MyCustomSearch' in each:
				remove_list.append(each)
		except:
			continue

	for search_term in remove_list:
		try:
			del Dict[search_term]
		except Exception as e:
			Log.Error('Error Clearing Searches: %s' %str(e))
			continue

	Dict.Save()
	return MC.message_container("Search Queue", "Your Search Queue list will be cleared soon.")

####################################################################################################
@route(PREFIX + "/search")
def Search(query=None, surl=None, page_count='1', mode='default', thumb=None, summary=None):

	last_page_no = page_count
	
	if surl != None:
		if mode == 'people' or mode == 'tag':
			url = surl + '?page=%s' % (str(page_count))
		else:
			url = surl + '&page=%s' % (str(page_count))
		page_data = common.GetPageElements(url=url)
	else:
		if mode == 'default':
			timestr = str(int(time.time()))
			Dict[SITE.lower() +'MyCustomSearch'+query] = query + 'MyCustomSearch' + timestr
			Dict.Save()
			url = fmovies.BASE_URL + fmovies.SEARCH_PATH + '?page=%s&keyword=%s' % (str(page_count), String.Quote(query, usePlus=True))
		elif mode == 'other seasons':
			url = fmovies.BASE_URL + fmovies.FILTER_PATH + '?type=series&page=%s&keyword=%s' % (str(page_count), String.Quote(query, usePlus=True))
		else:
			url = fmovies.BASE_URL + fmovies.SEARCH_PATH + '?page=%s&keyword=%s' % (str(page_count), String.Quote(query, usePlus=True))
		page_data = common.GetPageElements(url=url)
		
	elems = page_data.xpath(".//*[@id='body-wrapper']//div[@class='row movie-list']//div[@class='item']")
	
	last_page_no = int(page_count)
	try:
		last_page_no = int(page_data.xpath(".//*[@id='body-wrapper']//ul[@class='pagination'][1]//li[last()-1]//text()")[0])
	except:
		pass
		
	if mode == 'default':
		oc = ObjectContainer(title2 = 'Search Results|Page ' + str(page_count) + ' of ' + str(last_page_no), no_cache=isForceNoCache())
	elif mode == 'tag':
		oc = ObjectContainer(title2 = 'Tag: ' + query, no_cache=isForceNoCache())
	elif mode == 'people':
		oc = ObjectContainer(title2 = 'People: ' + query, no_cache=isForceNoCache())
	else:
		oc = ObjectContainer(title2 = 'Other Seasons for ' + query, no_cache=isForceNoCache())
		
	no_elems = len(elems)
	for elem in elems:
		name = elem.xpath(".//a[@class='name']//text()")[0]
		loc = fmovies.BASE_URL + elem.xpath(".//a[@class='name']//@href")[0]
		thumb = elem.xpath(".//a[@class='poster']//@src")[0].split('url=')[1]
		summary = 'Plot Summary on Item Page.'
		
		eps_nos = ''
		title_eps_no = ''
		try:
			eps_nos = elem.xpath(".//div[@class='status']//span//text()")[0]
			eps_no_i = str(int(eps_nos.strip()))
			title_eps_no = ' (Eps:'+eps_no_i+')'
			eps_nos = ' Episodes: ' + eps_no_i
		except:
			pass
		try:
			more_info_link = elem.xpath(".//@data-tip")[0]
		except:
			more_info_link = None
		
		do = DirectoryObject(
			key = Callback(EpisodeDetail, title = name, url = loc, thumb = thumb),
			title = name + title_eps_no,
			summary = GetMovieInfo(summary=summary, urlPath=more_info_link) + eps_nos,
			thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback=ICON_UNAV)
			)
		if mode == 'default' or mode == 'people' or mode == 'tag':
			oc.add(do)
		elif mode == 'other seasons' and query.lower() in name.lower() and len(name.lower().replace(' (special)','').replace(query.lower(), '').strip()) < 3:
			fixname_SN = name.lower().replace(query.lower(),'').replace(' ','').strip()
			# when we clean name we expect the season no. only to be present - if not then maybe its not a related season i.e. skip item
			try:
				if len(fixname_SN) > 0:
					fixname_SN_i = int(fixname_SN)
					newname = query + " " + ("%02d" % fixname_SN_i)
				else:
					newname = query
				do.title = newname + title_eps_no
			except:
				pass
			oc.add(do)
			
	if mode == 'other seasons' or mode == 'tag':
		oc.objects.sort(key=lambda obj: obj.title, reverse=False)
	
	if mode == 'default' or mode == 'people' or mode == 'tag' or (mode == 'other seasons' and no_elems == len(oc)):
		if int(page_count) < last_page_no:
			oc.add(NextPageObject(
				key = Callback(Search, query = query, surl = surl, page_count = str(int(page_count) + 1), mode=mode),
				title = "Next Page (" + str(int(page_count) + 1) +'/'+ str(last_page_no) + ") >>",
				thumb = R(ICON_NEXT)
				)
			)
		
	if len(oc) == 0:
		if mode == 'other seasons':
			return MC.message_container('Other Seasons', 'No Other Seasons Available currently')
		else:
			return MC.message_container('Search Results', 'No More Videos Available')
			
	if mode == 'other seasons' and page_count=='1':
		if Check(title=query + ' (All Seasons)',url=url):
			oc.add(DirectoryObject(
				key = Callback(RemoveBookmark, title = query + ' (All Seasons)', url = url),
				title = "Remove Bookmark",
				summary = 'Removes the current show season from the Boomark que',
				thumb = R(ICON_QUEUE)
				)
			)
		else:
			oc.add(DirectoryObject(
				key = Callback(AddBookmark, title = query + ' (All Seasons)', url = url, summary=summary, thumb=thumb),
				title = "Add Bookmark",
				summary = 'Adds the current show season to the Boomark que',
				thumb = R(ICON_QUEUE)
				)
			)
		
	oc.add(DirectoryObject(
		key = Callback(MainMenu),
		title = '<< Main Menu',
		thumb = R(ICON)
		)
	)

	return oc

####################################################################################################
@route(PREFIX + "/searchQueueMenu")
def SearchQueueMenu(title):

	oc = ObjectContainer(title2='Search Using Term', no_cache=isForceNoCache())
	
	urls_list = []
	
	for each in Dict:
		query = Dict[each]
		try:
			if each.find(SITE.lower()) != -1 and 'MyCustomSearch' in each and query != 'removed':
				timestr = '1483228800'
				if 'MyCustomSearch' in query:
					split_query = query.split('MyCustomSearch')
					query = split_query[0]
					timestr = split_query[1]
					
				urls_list.append({'key': query, 'time': timestr})
				
		except:
			pass
			
	if len(urls_list) == 0:
		return MC.message_container(title, 'No Items Available')
		
	newlist = sorted(urls_list, key=lambda k: k['time'], reverse=True)
		
	oc.add(DirectoryObject(
		key = Callback(ClearSearches),
		title = "Clear Search Queue",
		thumb = R(ICON_SEARCH),
		summary = "CAUTION! This will clear your entire search queue list!"
		)
	)
	
	for item in newlist:
		timestr = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(item['time'])))
		query = item['key']
		oc.add(DirectoryObject(key = Callback(Search, query = query, page_count='1'), title = query, tagline = timestr, thumb = R(ICON_SEARCH)))

	return oc
	
######################################################################################
@route(PREFIX + "/filtersetup")
def FilterSetup(title, key1 = None, key2val = None, mode='add', update=True):

	oc = ObjectContainer(title2 = title, no_cache=isForceNoCache())
	
	if len(Filter) == 0:
		# Initialize Filter Data
		FilterSetupData()
		
	if len(Filter) == 0:
		return MC.message_container("Filter Setup Error", "Sorry but the Filter could not be created !")
	
	#Log(Filter)
		
	if len(Filter_Search) == 0:
		# Set defaults for 'Sort' & 'Order'
		Filter_Search['sort'] = 'post_date'
		Filter_Search['order'] = 'desc'
	
	if key1 == None:
		for f_key in sorted(Filter):
			oc.add(DirectoryObject(
				key = Callback(FilterSetup, title = title, key1 = f_key),
				title = f_key.title()
				)
			)
	else:
		oc = ObjectContainer(title2 = title + ' (' + key1.title() + ')', no_cache=isForceNoCache())
		
		for f2_key in sorted(Filter[key1]):

			selected = ''
			# This indicates selected item
	
			if (key2val != None and key2val == Filter[key1][f2_key]):
				if (mode == 'add' or key1 == 'sort' or key1 == 'order'):
					selected = ' ' + common.GetEmoji(type='pos', mode='simple')
			
			elif (key1 != 'sort' and key1 != 'order' and key1 in Filter_Search and Filter[key1][f2_key] in Filter_Search[key1]):
				selected = ' ' + common.GetEmoji(type='pos', mode='simple')
			
			elif (key2val == None and key1 in Filter_Search and Filter[key1][f2_key] in Filter_Search[key1]):
				selected = ' ' + common.GetEmoji(type='pos', mode='simple')
				
				
			key_title = f2_key.title() + selected
			if key1 == 'quality' or 'mode: and' in f2_key.lower(): # dont Camelcase quality values and Mode in Genre
				key_title = f2_key + selected
			
			if mode == 'rem' and selected != '':
				oc.add(DirectoryObject(
					key = Callback(FilterSetup, title = title, key1 = key1, key2val = Filter[key1][f2_key], update = MakeSelections(key1=key1, key2val=key2val, mode='rem', k2v= Filter[key1][f2_key]), mode='rem'),
					title = key_title
					)
				)
			elif selected != '':
				oc.add(DirectoryObject(
					key = Callback(FilterSetup, title = title, key1 = key1, key2val = Filter[key1][f2_key], update = MakeSelections(key1=key1, key2val=key2val, mode='rem', k2v= Filter[key1][f2_key]), mode='rem'),
					title = key_title
					)
				)
			else:
				oc.add(DirectoryObject(
					key = Callback(FilterSetup, title = title, key1 = key1, key2val = Filter[key1][f2_key], update = MakeSelections(key1=key1, key2val=key2val, mode=mode, k2v=Filter[key1][f2_key])),
					title = key_title
					)
				)
		
		oc.add(DirectoryObject(
			key = Callback(FilterSetup, title = title, key1 = None, key2val = None, update = MakeSelections(key1=key1, key2val=key2val, mode=mode, k2v=key2val)),
			title = 'Continue Filter Setup >>'
			)
		)
		
	# Build search string
	searchString = ''
	searchStringDesc = 'Sorting using ' + common.GetKeyFromVal(Filter['sort'],Filter_Search['sort']) + ' in ' + common.GetKeyFromVal(Filter['order'],Filter_Search['order']) + ' order.'
	
	for k1 in Filter_Search:
		if k1 != 'sort' and k1 != 'order':
			searchStringDesc += ' Filter ' + k1.title() + ' has '
			c=0
			for k2v in Filter_Search[k1]:
				searchString += k1 + '[]=' + k2v + '&'
				if c == len(Filter_Search[k1])-1:
					searchStringDesc += common.GetKeyFromVal(Filter[k1],k2v) + '.'
				else:
					searchStringDesc += common.GetKeyFromVal(Filter[k1],k2v) + ', '
				c += 1

	searchString += Filter_Search['sort'] + ':' + Filter_Search['order']
	searchString = searchString.replace(' ','+')

	
	# Build Filter-Search Url
	#https://fmovies.se/filter?sort=post_date%3Adesc&genre%5B%5D=25&genre_mode=and&country%5B%5D=2&type%5B%5D=movie&quality%5B%5D=HD+1080p&release%5B%5D=2017
	searchUrl = fmovies.BASE_URL + fmovies.FILTER_PATH + '?' + urllib2.quote(searchString, safe='_+=&')
	
	oc.add(DirectoryObject(
		key = Callback(Search, surl=searchUrl),
		title = '<<< Submit Search >>>',
		summary = searchStringDesc
		)
	)
	
	oc.add(DirectoryObject(
		key = Callback(ClearFilter),
		title = 'Reset Search Filter'
		)
	)
	oc.add(DirectoryObject(
		key = Callback(MainMenu),
		title = '<< Main Menu'
		)
	)
	
	return oc
	
######################################################################################
@route(PREFIX + "/makeselections")
def MakeSelections(key1, key2val, mode, k2v):
	
	if k2v != key2val or key1 == None or key2val == None:
		return False
	
	# Update Filter_Search based on previous selection
	# ToDo: This will deselect
	if (key1 != 'sort' and key1 != 'order' and key1 != None and key2val != None and key1 in Filter_Search and key2val in Filter_Search[key1] and mode == 'rem'):
		Filter_Search[key1].remove(key2val)
		if len(Filter_Search[key1]) == 0:
			del Filter_Search[key1]
	
	# This indicates selected item
	elif (key1 != None and key2val != None and (key1 not in Filter_Search or key2val not in Filter_Search[key1]) and mode == 'add'):
		if key1 != None and key2val != None:
			if key1 == 'sort' or key1 == 'order':
				Filter_Search[key1] = key2val
			else:
				if key1 not in Filter_Search:
					Filter_Search[key1] = []
				if key2val not in Filter_Search[key1]:
					Filter_Search[key1].append(key2val)
		
	return True

######################################################################################
@route(PREFIX + "/clearfilter")
def ClearFilter():
	Filter_Search.clear()
	
	oc = ObjectContainer(title2 = "Filter Reset", no_cache=isForceNoCache())
	oc.add(DirectoryObject(
		key = Callback(FilterSetup, title=CAT_FILTERS[3]),
		title = CAT_FILTERS[3]
		)
	)
	return oc

######################################################################################
@route(PREFIX + "/filtersetupdata")
def FilterSetupData():

	try:
		url = (fmovies.BASE_URL + fmovies.SEARCH_PATH + '?keyword=fmovies')
		page_data = common.GetPageElements(url=url)
		
		Filter['sort']={}
		Filter['order']={'Ascending':'asc', 'Descending':'desc'}
		Filter['genre']={}
		Filter['country']={}
		Filter['type']={}
		Filter['quality']={}
		Filter['release']={}
		
		# Get Sort by info
		elems = page_data.xpath(".//*[@id='body-wrapper']//div[@class='filter']//li")
		for elem in elems:
			key = elem.xpath(".//text()")[0].strip()
			val = elem.xpath(".//@data-value")[0].split(':')[0].strip()
			Filter['sort'][key] = val
			
		# Get Genre info
		elems = page_data.xpath(".//*[@id='body-wrapper']//div[@class='filter genre']//li")
		for elem in elems:
			key = elem.xpath(".//label//text()")[0].strip()
			val = elem.xpath(".//@value")[0].strip()
			if key == 'Mode: AND':
				key = 'Mode: AND (unchecked is OR)'
			Filter['genre'][key] = val
			
		# Get Country info
		elems = page_data.xpath(".//*[@id='body-wrapper']//div[@class='filter country']//li")
		for elem in elems:
			key = elem.xpath(".//label//text()")[0].strip()
			val = elem.xpath(".//@value")[0].strip()
			Filter['country'][key] = val
			
		# Get Type info
		elems = page_data.xpath(".//*[@id='body-wrapper']//div[@class='filter type']//li")
		for elem in elems:
			key = elem.xpath(".//label//text()")[0].strip()
			val = elem.xpath(".//@value")[0].strip()
			Filter['type'][key] = val
		
		# Get Quality info - page has wrong div classification using div[6] instead
		elems = page_data.xpath(".//*[@id='body-wrapper']//div[@class='row']//div[6]//li")
		for elem in elems:
			key = elem.xpath(".//label//text()")[0].strip()
			val = elem.xpath(".//@value")[0].strip()
			Filter['quality'][key] = val
			
		# Get Release info
		elems = page_data.xpath(".//*[@id='body-wrapper']//div[@class='filter quality']//li")
		for elem in elems:
			key = elem.xpath(".//label//text()")[0].strip()
			val = elem.xpath(".//@value")[0].strip()
			Filter['release'][key] = val
	
	except:
		# Empty partial Filter if failed - error will be reported when using Filter
		Filter.clear()
	
######################################################################################
@route(PREFIX + "/isItemVidAvailable")
def isItemVidAvailable(isOpenLoad, data):
	# responses - true, false, unknown
	ourl = None
	httpsskip = Prefs["use_https_alt"]
	use_web_proxy = Prefs["use_web_proxy"]
	
	if isOpenLoad:
		ourl = data
	else:
		data = D(data)
		data = JSON.ObjectFromString(data)
		files = JSON.ObjectFromString(data['server'])
		sortable_list = []
		for file in files:
			furl = file['file']
			res = file['label'].replace('p','')
			if res != '1080':
				res = '0'+res
			type = file['type']
			sortable_list.append({'label': res, 'file':furl, 'type':type})
		newlist = sorted(sortable_list, key=lambda k: k['label'], reverse=True)
		for file in newlist:
			ourl = file['file']
			break
			
	isVideoOnline = 'false'
	http_res = 0
	
	if ourl != None:
		try:
			if isOpenLoad:
				vidurl = Openload.openload(url=ourl)
				if vidurl != None:
					http_res = fmovies.request(url=vidurl, output='responsecode', httpsskip=httpsskip)
					if http_res in fmovies.HTTP_GOOD_RESP_CODES:
						isVideoOnline = 'true'
			else:
				http_res, red_url = fmovies.request(url=ourl, output='responsecodeext', followredirect = True, httpsskip=httpsskip)
				if http_res in fmovies.HTTP_GOOD_RESP_CODES:
					chunk = fmovies.request(url=red_url, output='chunk', httpsskip=httpsskip) # dont use web-proxy when retrieving chunk
					if 'mp4' in str(chunk[0:20]):
						isVideoOnline = 'true'
		except Exception as e:
			Log('ERROR init.py>isItemVidAvailable %s, %s:' % (e.args,ourl))
			Log(data)
			isVideoOnline = 'unknown'

	if Prefs["use_debug"]:
		Log("--- LinkChecker ---")
		Log("Url: %s" % (ourl))
		Log("Response: %s, Code: %s" % (isVideoOnline, http_res))
			
	return isVideoOnline

######################################################################################
@route(PREFIX + "/isForceNoCache")
def isForceNoCache():
	# no_cache=isForceNoCache()
	
	try:
		CACHE_EXPIRY = 60 * int(Prefs["cache_expiry_time"])
	except:
		CACHE_EXPIRY = fmovies.CACHE_EXPIRY_TIME
	if CACHE_EXPIRY == 0:
		return True
		
	return False

######################################################################################
@route(PREFIX + "/verify2partcond")
def verify2partcond(ep_title):
# verify 2 part episode condition (eg. "01-02" type of titles)
# single parts can also have "-" in episode titles and this condition will verify (eg "00 - Special - The Journey So Far")

	try:
		splitem = ep_title.split("-")
		for item in splitem:
			i = int(item.strip()) # if success for both splits then it must be a 2 part vid
		return True
	except:
		pass
	return False

######################################################################################
#
# Supposed to run when Prefs are changed but doesnt seem to work on Plex as expected
# https://forums.plex.tv/discussion/182523/validateprefs-not-working
# Update - does not support producing a dialog - show dialog somewhere else/later
#
@route(PREFIX + "/ValidatePrefs")
def ValidatePrefs():

	Log("Your Channel Preferences have changed !")
	DumpPrefs()
	fmovies.CACHE.clear()
	HTTP.ClearCache()
	
	ValidateMyPrefs()
	
	return
	
######################################################################################
@route(PREFIX + "/DumpPrefs")
def DumpPrefs():
	Log("=================FMoviesPlus Prefs=================")
	Log("Channel Preferences:")
	Log("Cache Expiry Time (in mins.): %s" % (Prefs["cache_expiry_time"]))
	Log("No Extra Info. for Nav. Pages (Speeds Up Navigation): %s" % (Prefs["dont_fetch_more_info"]))
	Log("Use SSL Web-Proxy: %s" % (Prefs["use_web_proxy"]))
	Log("Use Alternate SSL/TLS: %s" % (Prefs["use_https_alt"]))
	Log("Use LinkChecker for Videos: %s" % (Prefs["use_linkchecker"]))
	Log("Enable Vibrant Emoji Icons (Limited Clients Support): %s" % (Prefs["use_vibrant_emoji"]))
	Log("Enable Debug Mode: %s" % (Prefs["use_debug"]))
	Log("=============================================")
	
######################################################################################
@route(PREFIX + "/ClientInfo")
def ClientInfo():
	Log("=================FMoviesPlus Client Info=================")
	Log(common.TITLE + ' v.' + common.VERSION)
	Log("OS: " + sys.platform)
	Log("Client.Product: %s" % Client.Product)
	Log("Client.Platform: %s" % Client.Platform)
	Log("Client.Version: %s" % Client.Version)
	Log("=============================================")

######################################################################################
@route(PREFIX + "/ValidateMyPrefs")
def ValidateMyPrefs():

	try:
		test_cache_time = int(Prefs["cache_expiry_time"])
	except:
		ret = ['Error Cache Time', 'Cache Time field needs only numbers.']
		Log("%s : %s" % (ret[0], ret[1]))
		VALID_PREFS_MSGS.append(ret)
	
######################################################################################
@route(PREFIX + "/DisplayMsgs")
def DisplayMsgs():

	if len(VALID_PREFS_MSGS) > 0:
		ret = VALID_PREFS_MSGS[0]
		VALID_PREFS_MSGS.remove(ret)
		Log("Removed - %s : %s" % (ret[0], ret[1]))
		return MC.message_container(ret[0], ret[1])

