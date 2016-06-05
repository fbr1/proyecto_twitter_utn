import json, argparse, Entity, util
import xml.etree.ElementTree as ET


#
# usage: raw_processing.py [-h] [-f FORMAT] inputfile outputfile

def main(inputfilepath,outputfilepath,format):

    return get_processed_tweets(inputfilepath,format)


def get_processed_tweets(inputfilepath,outputfilepath = None,format = "JSON"):

    # Read raw data
    if format == "xml":
        tweets = readxml(inputfilepath)
    else:
        tweets = readjson(inputfilepath)

    if outputfilepath:
        util.save_to_file(tweets, outputfilepath)

    return tweets


# Returns a list of tweets from json
def readjson(inputfilepath):
    print("Reading JSON")
    tweets = []
    try:

        with open(inputfilepath, "r") as input_file:
            for line in input_file:
                tweet = json.loads(line)

                # If it's a tweet
                # Since sometimes there are objects other than tweets (limits,etc)
                if "id" in tweet.keys():
                    tw = Entity.Tweet(tweet["id"],tweet["text"])
                    tweets.append(tw)

    except Exception as e:
        print("error: {0}".format(e))

    return tweets


# Returns a list of tweets from xml
def readxml(inputfilepath):

    print("Reading XML")

    # XML fields
    ID = "tweetid"
    TEXT = "content"
    TWEET = "tweet"

    tweets = []
    tree = ET.parse(inputfilepath)
    root = tree.getroot()

    for tweet in root.findall(TWEET):
        tw = Entity.Tweet()
        tw.id = tweet.find(ID).text
        tw.text = tweet.find(TEXT).text

        tweets.append(tw)

    return tweets


if __name__ == "__main__":

    # Read arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("inputfile", help="Input tweet data path")
    parser.add_argument("outputfile", help="Output tweet data path")
    parser.add_argument("-f", "--format", action="store",
                        help="set the format of the input data [xml/json]")
    args = parser.parse_args()

    main(args.inputfile,args.outputfile,args.format)
