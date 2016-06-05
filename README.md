# Proyecto Twitter UTN

### Example
```python
import raw_processing,filter
tweets = raw_processing.get_processed_tweets("raw_tweets.json",format="json")
filter.filter_tweets(tweets,"filtered_tweets_output.csv")
```