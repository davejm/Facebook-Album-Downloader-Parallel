Facebook-Album-Downloader-Parallel
==================================

Downloads pictures from Facebook albums of a specific user. Uses multiprocessing to download pictures in parallel which makes it very fast.
Downloading the pictures in parallel seemed to produce a speed increase of around a factor of 10 from the original non-parallel implementation.

##Usage:

Simply run the fbalbumdownload.py with the other files from the repo in the same directory and enter the required information at the prompt.

Alternatively, you can use some of the commandline arguments which can be viewed by typing fbalbumdownload.py -h

###Obtaining an oAuth key

The easiest way to get an oAuth key for use with the downloader is to log into facbook, click on the arrow next to your name in the top right and select 'manage apps'. Then click on the 'Tools' drop down and select Graph API Explorer.
From the explorer click 'Get Access Token' and select the permission for facebook albums for yourself and your friends.
Then copy this key into the oauthkey.txt file from the repo (or specificy by using -o option) and run the program.
Note: You must remain logged in to Facebook while using an access token from the API Explorer. These tokens expire after a certain amount of time. To get a more persistent acces token, see Facebook Long-Term tokens at https://developers.facebook.com/docs/facebook-login/access-tokens/
