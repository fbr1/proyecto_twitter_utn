import re, json, argparse, util
from unicodedata import normalize
from collections import defaultdict

#
# usage: filter.py [-h] inputfile outputfile

# Minimum allowed word frecuency
MINIMUM_FREQUENCY = 0.0005


def main(inputfilepath, outputfilepath):
    return filter_tweets_from_file(inputfilepath, outputfilepath)


def filter_tweets_from_file(inputfilepath, outputfilepath = None):

    tweets = filter_tweets(util.read_from_file(inputfilepath))
    return tweets


def filter_tweets(tweets, outputfilepath = None):

    # Clean tweets
    for i in range(len(tweets)):
        tweets[i].text = clean(tweets[i].text)

    # Remove duplicated tweets
    seen = set()
    deduped = []
    for i in range(len(tweets)):
        if tweets[i].text not in seen:
            seen.add(tweets[i].text)
            deduped.append(tweets[i])
    tweets = deduped
            
    # Remove articulos,pronombres y preposiciones
    for i in range(len(tweets)):
        tweets[i].text = removerArtProPre(tweets[i].text)

    # Remove less used words
    # TODO review effectiveness
    total = 0
    d = defaultdict(int)
    for tw in tweets:
        for word in tw.text:
            d[word] += 1
            total += 1

    freq_ord = [(word,count) for word, count in sorted(d.items(), key=lambda k_v: (k_v[1], k_v[0]),reverse=True)]

    wordsFiltered = []
    freqFiltered = []

    for i in range(len(freq_ord)):
        if freq_ord[i][1]/total < MINIMUM_FREQUENCY:
            wordsFiltered = [x[0] for x in freq_ord[:i]]
            freqFiltered = [x[1] for x in freq_ord[:i]]
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
    
    _punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.:…]+')

    # Remove url, RT, Mentions(@), "..."
    text = re.sub(r"(RT)|(@[_A-Za-z0-9]+)|(\w+:\/\S+)|(http)|(https)", "", text)
    
    # Remove strange characters
    result = []
    for word in _punct_re.split(text.lower()):        
        word = normalize('NFKD', word)
        # word = normalize('NFKD', word).encode('ascii',False)
        # word = word.decode('utf-8')
        if word:            
            result.append(word)

    return ' '.join(result)
    

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


if __name__ == "__main__":

    # Read arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("inputfile", help="Input tweet data path")
    parser.add_argument("outputfile", help="Output tweet data path")
    args = parser.parse_args()

    main(args.inputfile,args.outputfile)