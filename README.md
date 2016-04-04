# Python_Learnings
This repository contains a grab bag of Python scripts I have written.  The thought is to be aids in future scripts.

## getContextualElectronicsVideos.py

I wrote this script so that I could download the Contextual Electronics videos that were available to me as a Premier member.
Since I plan to be the only user, the script is "good enough" to do what I needed - download CE videos.  The script is not "user friendly".  I embed all the interactions as hard-coded strings.  Robust.  Once the script worked, I am done with it.  Performant.
 I am new to python programming and do not claim to be a programmer.  Even if I did, there was no focus on faster/smaller.
 The things I learned from this script include:
 - Logging into a member web site.  A feature of Premier membership is downloading videos. I needed to log into the CE web site and keep authenticated when I went to the web page. In order to login, I used the advice from this stackexchange post: http://stackoverflow.com/questions/13925983/login-to-website-using-urllib2-python-2-7
   The stuff to make the login happen is contained within logInToCE().  Cookielib is instrumental in maintaining the "goo" needed between URL gets.  I learned a little more about FakeBrowser - the script looks like a browser session to
   the CE Server.  See logInToCE().
 - more practice at using split() and rsplit().  getRelativePath() is a good example of practice.
 - more practice with try/except.  readAndWriteVideo() provide a good example of practice.
 - reading and writing big chunks-o-data.  See readAndWriteVideo()
