import csv, Entity


def save_to_file(tweets, outputfilepath):
    print("Saving to:", outputfilepath)

    with open(outputfilepath, "w") as saveFile:
        saveFile.write("id,text\n")
        writer = csv.writer(saveFile,delimiter=",", lineterminator='\n')
        for tw in tweets:

            # Replace newline characters
            tw.text = tw.text.replace("\r", " ").replace("\n", " ")

            writer.writerow([tw.id,tw.text])


# TODO check for desired format : id,text only
def read_from_file(inputfilepath):
    print("Reading :", inputfilepath)

    # CSV Fields
    ID = 0
    TEXT = 1

    tweets = []
    with open(inputfilepath,encoding='utf-8') as inputFile:
        # Skips header
        next(inputFile)

        reader = csv.reader(inputFile)
        for line in reader:
            tw = Entity.Tweet()
            tw.id = line[ID]
            tw.text = line[TEXT]
            tweets.append(tw)

    return tweets
