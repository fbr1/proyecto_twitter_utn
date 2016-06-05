import json, argparse, Entity, csv
import xml.etree.ElementTree as ET

#
# usage: raw_processing.py [-h] [-f FORMAT] inputfile outputfile

def main():

    # Read arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("inputfile", help="Input tweet data path")
    parser.add_argument("outputfile", help="Output tweet data path")
    parser.add_argument("-f", "--format", action="store",
                        help="set the format of the input data [xml/json]")
    args = parser.parse_args()

    # Read raw data
    if args.format == "xml":
        tweets = readxml(args.inputfile)
    else:
        tweets = readjson(args.inputfile)

    save_to_file(tweets, args.outputfile)

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


def save_to_file(tweets, outputfile):
    print("Saving to:", outputfile)

    with open(outputfile, "w") as saveFile:
        saveFile.write("id,text\n")
        writer = csv.writer(saveFile,delimiter=",", lineterminator='\n')
        for tw in tweets:

            # Replace newline characters
            tw.text = tw.text.replace("\r", " ").replace("\n", " ")

            writer.writerow([tw.id,tw.text])

if __name__ == "__main__":
    main()
