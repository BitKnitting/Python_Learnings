###########################################################################################
#
# Copyright Margaret Johnson, 2016
# Use at your own risk.
#
# NOTE: DON'T FORGET TO SUPPLY:
# - username and password to CE server (see logInToCE())
# - Initial directory path where the videos should be stored (see the variable directoryStartPath)
# I wrote this script so that I could download the Contextual Electronics videos that were available to me as a Premier member.
# Since I plan to be the only user, the script is "good enough" to do what I needed - download CE videos.  The script is not "user friendly".  I embed all the interactions as hard-coded strings.  Robust.  Once the script worked, I am done with it.  Performant.
# I am new to python programming and do not claim to be a programmer.  Even if I did, there was no focus on faster/smaller.
# The things I learned from this script include:
# - Logging into a member web site.  A feature of Premier membership is downloading videos. I needed to log into the CE web site and keep authenticated when I went to the web page. In order to login, I used the advice from this stackexchange post: http://stackoverflow.com/questions/13925983/login-to-website-using-urllib2-python-2-7
#   The stuff to make the login happen is contained within logInToCE().  Cookielib is instrumental in maintaining the "goo" needed between URL gets.  I learned a little more about FakeBrowser - the script looks like a browser session to
#   the CE Server.  See logInToCE().
# - more practice at using split() and rsplit().  getRelativePath() is a good example of practice.
# - more practice with try/except.  readAndWriteVideo() provide a good example of practice.
# - reading and writing big chunks-o-data.  See readAndWriteVideo()
#
###########################################################################################
import shutil
import os.path
from bs4 import BeautifulSoup
import cookielib
from urllib2 import urlopen, Request,build_opener, HTTPCookieProcessor,install_opener
from urllib import urlencode
import logging

###########################################################################################
directoryStartPath = '/Users/.... THIS IS WHERE I START WITH THE DIRECTORY PATH'
logger = logging.getLogger('CE_video_application')
consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.INFO)
logger.addHandler(consoleHandler)
###########################################################################################
def FakeBrowser(url):
    req = Request(url)
    req.add_header('Accept-Language', 'en-US')
    req.add_header('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36')
    return req
###########################################################################################
def getSoupPage(url):
    req = FakeBrowser(url)
    try: 
        response = urlopen(req)
    except:
        logger.warning('The page referenced by %s could not be found',url )
        return None
    html = response.read()
    return BeautifulSoup(html)
###########################################################################################
def logInToCE():
    cj = cookielib.CookieJar()
    opener = build_opener(HTTPCookieProcessor(cj))
    install_opener(opener)
    opener.addheaders = [('User-agent', 'Testing')]
    
    authentication_url = "https://contextualelectronics.com/wp-login"
    payload = {
        'log' : 'YOUR USERNAME',
        'pwd' : 'YOUR PASSWORD',
        'rememberme'  : 'forever'    
    }
    data = urlencode(payload)
    req = Request(authentication_url,data)
    req.add_header('Accept-Language', 'en-US')
    req.add_header('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36')
    urlopen(req)    
###########################################################################################
def getRelativePath(url):    

    urlSeparator = '/'
    # A url will look something like this: https://contextualelectronics.com/software-tutorials/c-fundamental-tutorial/em09-c-data-types-from-an-embedded-point-of-view/
    #
    # The directory path comes after https://contextualelectronics.com/ ... so split the url into 4 elements by parsing between the '/' only the first 3.   the 0th element = http: 1st = '' 2nd = contextualelectronics.com, 
    # 3rd = /software-tutorials/c-fundamental-tutorial/em09-c-data-types-from-an-embedded-point-of-view/  .  Then remove the filename.
    path = url.split(urlSeparator,3)[3].rsplit(urlSeparator,2)[0]
    #
    # The filename is between the last two slashes.
    filename = url.rsplit(urlSeparator,2)[1]
    relativePath = path + '/' + filename + '.mp4'
    return relativePath
###########################################################################################
def buildFullFilename(url):
    #
    # The relative path is the path part that can be glommed from the url on contextual electronics. come.  If the url is:
    # https://contextualelectronics.com/software-tutorials/c-fundamental-tutorial/em09-c-data-types-from-an-embedded-point-of-view/
    # The relativePath = software-tutorials/c-fundamental-tutorial/em09-c-data-types-from-an-embedded-point-of-view.mp4
    relativePath = getRelativePath(url)
    fullPathFilename = directoryStartPath + '/' + relativePath
    return fullPathFilename
###########################################################################################
def videoFileExists(fullpathFilename):
    if (os.path.isfile(fullpathFilename)):
        statInfo = os.stat(fullpathFilename)
        if (statInfo.st_size == 0):
            print 'File %s exists but is 0 bytes.  Deleting empty file.  Will download' % fullpathFilename
            os.remove(fullpathFilename)
            return False
        return True
    return False
###########################################################################################
def makeSurePathExists(fullpathFilename):
    dirSeparator = '/'
    directoryPath = fullpathFilename.rsplit(dirSeparator,1)[0]
    if not os.path.exists(directoryPath):
        os.makedirs(directoryPath)
###########################################################################################
def saveYoutubeUrlToFile(fullpathFilename,videoUrl):
    # The local directory is the directory in the fullpathFilename where the mp4 would be located 
    # if it existed
    dirSeparator = '/'
    directoryPath = fullpathFilename.rsplit(dirSeparator,1)[0]
    videoName = fullpathFilename.rsplit(dirSeparator,1)[1]
    videoName = videoName.replace('.mp4','')
    # The CSV filename is the name of the last subdirectory
    filename = fullpathFilename.rsplit(dirSeparator,2)[1]
    fullCsvFilename = directoryPath + dirSeparator + filename + '.csv'
    rowToAdd = videoName + ',' +  videoUrl + '\n'
    with open(fullCsvFilename,'a') as f:
        f.write(rowToAdd)
    return
###########################################################################################
def getVideoURL(soupTutorialPage):
    for link in soupTutorialPage.find_all("a"):
        url = link.get("href")
        try:
            if "hd.mp4" in url:
                return url 
        except:
            # Perhaps this is a 2MT type video.  If it is, there is a Youtube link in the iFrame.
            try:
                url = soupTutorialPage.iframe.get('src')
                if url != None:
                    # Just copy the URL into a file.
                    return url
            except:
                continue     
    return None
###########################################################################################
def readAndWriteVideo(fullpathFilename,videoUrl):
    try:
        req = urlopen(videoUrl)
    except :
        logger.error( 'Not downloading file.  Received error code  when trying to open the URL for reading' )
        return    
    with open(fullpathFilename,'wb') as fp:
        # See http://pythoncentral.io/how-to-copy-a-file-in-python-with-shutil/
        # for buffer size and further info on shutil.
        bufferSize = 10000000
        try:
            shutil.copyfileobj(req,fp,bufferSize)
        except (IOError, os.error) as e:
            print 'error: %s ' % e   
###########################################################################################
def saveVideo(fullpathFilename,soupTutorialPage):
    makeSurePathExists(fullpathFilename)
    try:
        videoUrl = getVideoURL(soupTutorialPage)
        if "youtube.com" in videoUrl:
            saveYoutubeUrlToFile(fullpathFilename,videoUrl)
        else:
            print 'Starting download of %s' % fullpathFilename
            readAndWriteVideo(fullpathFilename,videoUrl)
            print 'Done with download step of %s' % fullpathFilename
    except:
        print 'Received an error.  Will not be downloading video.  '
###########################################################################################
#TODO: Start from __main()__
logInToCE()
url = "https://contextualelectronics.com/table-of-contents/"
soup = getSoupPage(url)
#
# Get the URL to each of the tutorial sections and iterate through
for link in soup.find_all("a", class_="tocc_blog_post_title"):
    urlToTutorial = link.get("href")
    # don't get tutorials from benchbudee and start-here.
    if "start-here" in urlToTutorial or "benchbudee" in urlToTutorial or "kicad-tutorial" in urlToTutorial or "course-logistics" in urlToTutorial:
        print "Skipping video ",urlToTutorial
    else:
        fullpathFilename = buildFullFilename(urlToTutorial)
        if (videoFileExists(fullpathFilename)):
            print "Video already exists ",fullpathFilename
            continue
        print "Getting video ",urlToTutorial
        soupTutorialPage = getSoupPage(urlToTutorial)
        # The URL to the tutorial page could be a 404 page not found.
        if soupTutorialPage is not None:
            saveVideo(fullpathFilename,soupTutorialPage)
print '****Done****'










