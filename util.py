import csv
import Entity
import random


def save_to_file(tweets, outputfilepath):
    print("Saving to:", outputfilepath)

    with open(outputfilepath, "w", encoding='utf-8') as saveFile:
        saveFile.write("id,text,type,label\n")
        writer = csv.writer(saveFile, delimiter=",", lineterminator='\n')
        for tw in tweets:

            # Replace newline characters
            tw.text = tw.text.replace("\r", " ").replace("\n", " ")

            writer.writerow([tw.id, tw.text, tw.tw_type, tw.label])


# TODO check for desired format : id,text only
def read_from_file(inputfilepath):
    print("Reading :", inputfilepath)

    # CSV Fields
    ID = 0
    TEXT = 1
    TYPE = 2
    LABEL = 3

    tweets = []
    with open(inputfilepath, encoding="utf8") as inputFile:
        # Skips header
        next(inputFile)

        reader = csv.reader(inputFile, delimiter=",")
        for line in reader:
            tw = Entity.Tweet()
            tw.id = line[ID]
            tw.text = line[TEXT]
            tw.tw_type = line[TYPE]
            tw.label = line[LABEL]
            tweets.append(tw)

    return tweets


def precision(tweets):
    """
    Prints precision of preclassified tweets

    Parameters
    ----------
    tweets : Tweet Entity list

    """

    accuracy = []

    # Get list of types and clusters
    seentypes = set()
    seenclusters = set()
    types = []
    clusters = []
    for tw in tweets:
        if tw.tw_type not in seentypes:
            seentypes.add(tw.tw_type)
            types.append(tw.tw_type)
        if tw.label not in seenclusters:
            seenclusters.add(tw.label)
            clusters.append(tw.label)

    # Find the cluster number better suited for each type
    types_count = [0] * len(types)
    assigned_clusters = [0] * len(types)
    used_clusters = set()

    for i in range(len(types)):
        cluster = [0] * len(clusters)
        for tw in tweets:
            if tw.tw_type == types[i]:
                types_count[i] += 1
                if tw.label not in used_clusters:
                    cluster[tw.label] += 1

        # Get the most frequent cluster for the type i
        max_acum = max(cluster)

        # Get cluster list index(es) of the most frequent cluster for the type i
        cluster_number_list = [i for i, j in enumerate(cluster) if j == max_acum]

        # If there is more than one cluster with the same frequency, choose one ramdomly
        if len(cluster_number_list) > 1:
            cluster_number = random.choice(cluster_number_list)
        else:
            cluster_number = cluster_number_list[0]

        # Prevent the same cluster from being chosen again
        used_clusters.add(cluster_number)

        assigned_clusters[i] = cluster_number

    # Calculate precision
    separator = '\t\t\t'
    print(separator, end='')
    for tw_type in types:
        print(tw_type, separator, end='')
    print('\n')
    for typeRow in range(len(types)):
        print(types[typeRow], '\t\t', end='')
        row = []
        for typeCol in range(len(types)):
            total = 0
            for tw in tweets:
                if tw.tw_type == types[typeRow] and tw.label == assigned_clusters[typeCol]:
                    total += 1
            value = total / types_count[typeRow]
            row.append(value)
            print('{:0.3f}'.format(value), separator, end='')

        accuracy.append(row)
        print('\n')

    return accuracy
