import re, json, argparse, util
from unicodedata import normalize
from collections import defaultdict

#
# usage: filter.py [-h] inputfile outputfile

# Minimum allowed word frecuency
MINIMUM_FREQUENCY = 0.0005


def filter_tweets(tweets, outputfilepath=None, art=False, frequency=False, terms_to_remove=None):
    """
    :param tweets: list of Entity.Tweet, required

    :param outputfilepath: string, optional, default: None
        Location path for saving the filtered tweets

    :param art: boolean, optional, default: False
        Remove articles, pronouns and prepositions

    :param frequency: boolean, optional, default: False,
        Remove less used words

    :param terms_to_remove: list of string, optional, default: None
        List of terms to remove from each tweet

    :return tweets: list of tweets cleaned and filtered
    """

    if terms_to_remove:  # Remove search terms
        for i in range(len(tweets)):
            tweets[i].text = remove_search_terms(tweets[i].text.lower(), terms_to_remove)

    # Clean tweets
    for i in range(len(tweets)):
        tweets[i].text = clean(tweets[i].text.lower())

    # Remove duplicated tweets
    seen = set()
    deduped = []
    for i in range(len(tweets)):
        if tweets[i].text not in seen:
            seen.add(tweets[i].text)
            deduped.append(tweets[i])
    tweets = deduped

    if art:  # Remove articulos, pronombres y preposiciones
        for i in range(len(tweets)):
            tweets[i].text = " ".join(removerArtProPre(tweets[i].text))

    if frequency:  # Remove less used words
        # TODO review effectiveness
        total = 0
        d = defaultdict(int)
        for tw in tweets:
            for word in tw.text:
                d[word] += 1
                total += 1

        freq_ord = [(word,count) for word, count in sorted(d.items(), key=lambda k_v: (k_v[1], k_v[0]),reverse=True)]

        wordsFiltered = []
        # freqFiltered = []

        for i in range(len(freq_ord)):
            if freq_ord[i][1]/total < MINIMUM_FREQUENCY:
                wordsFiltered = [x[0] for x in freq_ord[:i]]
                #  Only necessary if it's required to know the frequency of each word
                # freqFiltered = [x[1] for x in freq_ord[:i]]
                break

        for i in range(len(tweets)):
            tweets[i].text = ' '.join([x for x in tweets[i].text if x in wordsFiltered])

    # Remove empty tweets
    super_cleaned = []
    for tweet in tweets:
        if len(tweet.text) != 0:
            super_cleaned.append(tweet)

    tweets = super_cleaned

    if not tweets:
        raise Exception('There is no remaining tweet after filtering')

    if outputfilepath:
        util.save_to_file(tweets, outputfilepath)

    return tweets


def clean(text):

    # Remove extra white spaces
    text = " ".join(text.split())
    
    _punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>¿?@\[\\\]^“_`{|},.;:…]+')

    # Remove url, RT, Mentions(@), "..."
    text = re.sub(r"(rt)|(@[_A-Za-z0-9]+)|(\w+:\/\S+)|(http)|(https)", "", text)

    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               u"\U00002600-\U000027b0"  # various
                               "]+", flags=re.UNICODE)
    text = emoji_pattern.sub(r'', text)  # no emoji
    
    # Remove strange characters
    result = []
    for word in _punct_re.split(text.lower()):        
        word = normalize('NFKD', word)
        # word = normalize('NFKD', word).encode('ascii',False)
        # word = word.decode('utf-8')
        if word:            
            result.append(word)

    return " ".join(result)
    

def removerArtProPre(text):
    preposiciones = ['a','ante','bajo','con','contra','de','desde','durante',
                     'en','entre','hacia','hasta','mediante','para','por','segun',
                     'sin','sobre','tras']    
    
    articulos = ['el','la','los','las','un','una','unos','unas','lo','al','del']
    
    pronombres = ['yo','mi','conmigo','tu','vos','usted','ti','contigo','el','ella',
                  'ello','si','consigo','nosotros','nosotras','ustedes','ellos',
                  'ellas','si','consigo','vosotros','vosotras','me','nos','te','se',
                  'os','lo','la','le','los','las','les','mio','mia','mios','mias',
                  'tuyo','tuya','tuyos','tuyas','suyo','suya','su','suyas','suyos',
                  'nuestro','nuestra','nuestras','nuestros','vuestro','vuestros',
                  'vuestra','vuestras','suyo','suya','suyos','suyas','este','esta',
                  'esto','estos','estas','ese','esa','eso','esos','esas','aquel',
                  'aquella','aquello','aquellas','aquellos','que','cual','cuales',
                  'donde','quien','como','quienes','cuyo','cuyos','cuanto','cuanta',
                  'cuantos','cuantas','bastante','alguno','cualquiera','nadie',
                  'ninguno','otro','quienquiera']
    varios = ['y','o','es','no','va','q','x','era']
              
    filtro = set(preposiciones+articulos+pronombres+varios)
    
    result = []
    for word in text.split(' '):
        if word not in filtro:
            result.append(word)
    return result


def remove_search_terms(text, terms):

    filtro = set(terms)
    result = []
    for word in text.split(' '):
        if word not in filtro:
            result.append(word)
    return " ".join(result)


def filter_tweets_from_file(inputfilepath, outputfilepath=None, art=False, frequency=False, terms_to_remove=None):
    """
    :param inputfilepath: string, required
        Location path for loading the raw tweets

    :param outputfilepath: string, optional, default: None
        Location path for saving the filtered tweets

    :param art: boolean, optional, default: False
        Remove articles, pronouns and prepositions

    :param frequency: boolean, optional, default: False,
        Remove less used words

    :param terms_to_remove: list of string, optional, default: None
        List of terms to remove from each tweet

    :return tweets: list of tweets cleaned and filtered
    """

    tweets = filter_tweets(util.read_from_file(inputfilepath), outputfilepath, art, frequency, terms_to_remove)

    return tweets


def main(inputfilepath, outputfilepath, art, frequency, terms_to_remove):
    return filter_tweets_from_file(inputfilepath, outputfilepath, art, frequency, terms_to_remove)


if __name__ == "__main__":

    # Read arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("inputfile", help="Input tweet data path")
    parser.add_argument("outputfile", help="Output tweet data path")
    parser.add_argument("-r", "--rt", help="List of terms to remove")
    parser.add_argument("-a", "--art", action="store_true",
                        help="Remove articles, pronouns and prepositions")
    parser.add_argument("-f", "--frequency", action="store_true",
                        help="Remove less used words")
    args = parser.parse_args()

    main(args.inputfile, args.outputfile, args.art, args.frequency, args.rst)
