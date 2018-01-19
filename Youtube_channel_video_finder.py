#!/usr/bin/env python

import urllib
import json
import sys

# Strings
import requests

youtubeApiUrl = 'https://www.googleapis.com/youtube/v3/'
youtubeChannelsApiUrl = youtubeApiUrl + 'channels?key={0}&'.format("AIzaSyDqMCuBVu1RmnxtwCuft7DrXlPr4hvx28s")
youtubeSearchApiUrl = youtubeApiUrl + 'search?key={0}&'.format("AIzaSyDqMCuBVu1RmnxtwCuft7DrXlPr4hvx28s")

requestParametersChannelId = youtubeChannelsApiUrl + 'forUsername={0}&part=id'
requestChannelVideosInfo = youtubeSearchApiUrl + 'channelId={0}&part=id&order=date&type=video&pageToken={1}&maxResults=50'

youtubeVideoUrl = 'https://www.youtube.com/watch?v={0}'


def getChannelId(channelName):
	print 'Searching channel id for channel: %s',channelName
	retVal = -1
	try:
		url = requestParametersChannelId.format(channelName)
		print "Request: %s", url
		print "Sending request"
		response = urllib.urlopen(url)
		print "Parsing the response"
		responseAsJson = json.load(response)

		response.close()
		print "Response: %s",json.dumps(responseAsJson,indent=4)

		print "Extracting the channel id"

		if(responseAsJson['pageInfo'].get('totalResults') > 0):
			returnedInfo = responseAsJson['items'][0]
			retVal = returnedInfo.get('id')
			print "Channel id found: %s",str(retVal)
		else:
			print "Response received but it contains no item"
			raise Exception('The channel id could not be retrieved. Make sure that the channel name is correct')
			
		if(responseAsJson['pageInfo'].get('totalResults') > 1):
			print "Multiple channels were received in the response. If this happens, something can probably be improved around here"
	except Exception, err:
		print "An exception occurred while trying to retrieve the channel id: %s", err.message

	return retVal

def getChannelVideosPublishedInInterval(channelId):
    retVal = []
    foundAll = False

    nextPageToken = ''

    while not foundAll:
        try:
            url = requestChannelVideosInfo.format(channelId,nextPageToken)
            print 'Request: %s',url
            print "Sending request"
            response = urllib.urlopen(url)
            print "Parsing the response"
            responseAsJson = json.load(response)
            response.close()
            total_pages = responseAsJson['pageInfo'].get('totalResults')
            returnedVideos = responseAsJson['items']
			
            for video in returnedVideos:
                retVal.append(video)
				
            try:
                nextPageToken = responseAsJson['nextPageToken']
                print 'More videos to load, continuing'
            except Exception, err:
                print "No more videos to load"
                foundAll = True
        except Exception, err:
            print "An exception occurred while trying to retrieve a subset of the channel videos. Stopping search: %s",err.message
            foundAll = True
	
    print 'Found %d video(s) in this time interval',len(retVal)
    return retVal
	
def getChannelVideos(channelId):

    retVal = []
    videosPublishedInInterval = getChannelVideosPublishedInInterval(channelId)

    print "Adding videos found in the interval to the results list"
    retVal.extend(videosPublishedInInterval)
    print("Total video(s) found so far: %d",len(retVal))
    return retVal


def getVideoURL(videoId):
    retVal = youtubeVideoUrl.format(videoId)
    print 'Video URL: %s',retVal
    return retVal

def main():
    output_file_path = "/home/hpcnl/Desktop/output.txt"
    try:
        #channelId = getChannelId("UCvT3VHGg5YiFsID4E7WHU3w")
        channelId = "UCqMsB_WQ4HcUfZLXrh2ApsQ"
        if(channelId == -1):
            raise Exception('Impossible to continue without the channel id')
		
        channelVideos = getChannelVideos(channelId)
		
        if(not len(channelVideos) > 0):
            print "No video found for that channel! Either there's none or a problem occurred. Enable verbose or debug logging for more details.."
            sys.exit(0)
		
        print "Generating links for found videos"
        videoURLs = []
        for video in channelVideos:
            print 'Processing video: %s',json.dumps(video,indent=4)
            videoId = video.get('id').get('videoId')
            print 'Video id: %s',videoId
            videoURL = getVideoURL(videoId)
            videoURLs.append(videoURL)

        if(output_file_path is not None and output_file_path is not ''):
            print "File output enabled"
            print 'Links will be written to %s',output_file_path

            f = None
            try:
                f = open(output_file_path,'w')
            except Exception, err:
                print 'Could not create/open the output file!'
                raise Exception('Impossible to write the links to the output file. Verify that the path is correct and that it is accessible/can be created/can be written to')
			
            for videoURL in videoURLs:
                f.write(videoURL+"\n")
				
            f.close()
        else:
            for videoURL in videoURLs:
                print videoURL
        print 'Done!'
    except Exception, err:
        print "We tried our best but still.."
        sys.exit(2)


if __name__ == '__main__':
    main()
