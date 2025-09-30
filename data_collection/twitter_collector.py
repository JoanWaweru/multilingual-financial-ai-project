import tweepy
import pandas as pd
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict
import logging
from pathlib import Path
import sqlite3

from config.settings import (
    FINANCIAL_KEYWORDS, COUNTRIES, DATA_COLLECTION,
    RAW_DATA_DIR, LOGS_DIR
)
from config.api_keys import TWITTER_BEARER_TOKEN

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / 'data_collection.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TwitterFinancialCollector:
    """Collect financial tweets from East African users"""
    
    def __init__(self):
        self.client = tweepy.Client(
            bearer_token=TWITTER_BEARER_TOKEN,
            wait_on_rate_limit=True
        )
        self.db_path = RAW_DATA_DIR / "tweets.db"
        self.init_database()
        
    def init_database(self):
        """Initialize SQLite database for storing tweets"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tweets (
                id TEXT PRIMARY KEY,
                text TEXT NOT NULL,
                created_at TEXT,
                author_id TEXT,
                language TEXT,
                country TEXT,
                likes INTEGER,
                retweets INTEGER,
                replies INTEGER,
                quotes INTEGER,
                query TEXT,
                collected_at TEXT,
                is_code_switched INTEGER
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info(f"Database initialized at {self.db_path}")
    
    def collect_all_tweets(self) -> pd.DataFrame:
        """Main method to collect tweets from all countries"""
        logger.info("Starting tweet collection across East Africa")
        
        all_tweets = []
        
        for country, target_count in DATA_COLLECTION["tweets_per_country"].items():
            logger.info(f"\n{'='*50}")
            logger.info(f"Collecting {target_count} tweets from {country}")
            logger.info(f"{'='*50}")
            
            country_tweets = self.collect_country_tweets(country, target_count)
            all_tweets.extend(country_tweets)
            
            # Save to database after each country
            self.save_to_database(country_tweets)
            
            # Save checkpoint CSV
            df = pd.DataFrame(all_tweets)
            checkpoint_file = RAW_DATA_DIR / f"tweets_checkpoint_{country}.csv"
            df.to_csv(checkpoint_file, index=False, encoding='utf-8')
            
            logger.info(f"Collected {len(country_tweets)} tweets from {country}")
            logger.info(f"Total collected so far: {len(all_tweets)}")
            
            # Sleep between countries to avoid rate limits
            time.sleep(60)
        
        # Final save
        final_df = pd.DataFrame(all_tweets)
        final_file = RAW_DATA_DIR / "all_tweets_raw.csv"
        final_df.to_csv(final_file, index=False, encoding='utf-8')
        
        logger.info(f"\n{'='*50}")
        logger.info(f"Collection complete! Total tweets: {len(all_tweets)}")
        logger.info(f"Saved to: {final_file}")
        logger.info(f"{'='*50}")
        
        return final_df
    
    def collect_country_tweets(self, country: str, target_count: int) -> List[Dict]:
        """Collect tweets for a specific country"""
        collected_tweets = []
        queries = self.build_queries(country)
        tweets_per_query = target_count // len(queries)
        
        for i, query in enumerate(queries):
            logger.info(f"Query {i+1}/{len(queries)}: {query}")
            
            try:
                query_tweets = self.search_tweets(
                    query=query,
                    max_results=tweets_per_query,
                    country=country
                )
                
                # Filter relevant tweets
                relevant_tweets = [
                    t for t in query_tweets 
                    if self.is_relevant_financial(t['text'])
                ]
                
                collected_tweets.extend(relevant_tweets)
                logger.info(f"  ✓ Collected {len(relevant_tweets)} relevant tweets")
                
                if len(collected_tweets) >= target_count:
                    collected_tweets = collected_tweets[:target_count]
                    break
                
                time.sleep(3)  # Rate limiting
                
            except Exception as e:
                logger.error(f"  ✗ Error with query: {e}")
                continue
        
        return collected_tweets
    
    def build_queries(self, country: str) -> List[str]:
        """Build search queries for Twitter API"""
        country_code = COUNTRIES[country]["code"]
        queries = []
        
        # English financial terms
        for term in FINANCIAL_KEYWORDS["english"][:5]:
            query = f'"{term}" place_country:{country_code} -is:retweet lang:en'
            queries.append(query)
        
        # Swahili financial terms
        for term in FINANCIAL_KEYWORDS["swahili"][:5]:
            query = f'"{term}" place_country:{country_code} -is:retweet'
            queries.append(query)
        
        # Hashtags
        for hashtag in FINANCIAL_KEYWORDS["hashtags"][:3]:
            query = f'{hashtag} place_country:{country_code} -is:retweet'
            queries.append(query)
        
        return queries
    
    def search_tweets(self, query: str, max_results: int, country: str) -> List[Dict]:
        """Execute Twitter search"""
        tweets_data = []
        
        try:
            tweets = tweepy.Paginator(
                self.client.search_recent_tweets,
                query=query,
                tweet_fields=['created_at', 'author_id', 'public_metrics', 'lang'],
                max_results=100
            ).flatten(limit=max_results)
            
            for tweet in tweets:
                tweet_data = {
                    'id': str(tweet.id),
                    'text': tweet.text,
                    'created_at': tweet.created_at.isoformat() if tweet.created_at else None,
                    'author_id': str(tweet.author_id),
                    'language': tweet.lang,
                    'country': country,
                    'likes': tweet.public_metrics.get('like_count', 0),
                    'retweets': tweet.public_metrics.get('retweet_count', 0),
                    'replies': tweet.public_metrics.get('reply_count', 0),
                    'quotes': tweet.public_metrics.get('quote_count', 0),
                    'query': query,
                    'collected_at': datetime.now().isoformat(),
                    'is_code_switched': None  # To be determined in preprocessing
                }
                tweets_data.append(tweet_data)
                
        except tweepy.TooManyRequests:
            logger.warning("Rate limit hit, waiting 15 minutes...")
            time.sleep(15 * 60)
        except Exception as e:
            logger.error(f"Search error: {e}")
        
        return tweets_data
    
    def is_relevant_financial(self, text: str) -> bool:
        """Check if tweet is relevant to financial topics"""
        if len(text) < 30:  # Too short
            return False
        
        text_lower = text.lower()
        
        # Check for financial keywords
        all_keywords = (
            FINANCIAL_KEYWORDS["english"] + 
            FINANCIAL_KEYWORDS["swahili"]
        )
        
        keyword_matches = sum(1 for kw in all_keywords if kw in text_lower)
        
        # Exclude spam
        spam_words = [
            'follow back', 'dm for', 'click here', 'buy now',
            'limited offer', '100% profit', 'guaranteed returns'
        ]
        has_spam = any(spam in text_lower for spam in spam_words)
        
        return keyword_matches >= 1 and not has_spam
    
    def save_to_database(self, tweets: List[Dict]):
        """Save tweets to SQLite database"""
        if not tweets:
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for tweet in tweets:
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO tweets VALUES (
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                    )
                ''', (
                    tweet['id'], tweet['text'], tweet['created_at'],
                    tweet['author_id'], tweet['language'], tweet['country'],
                    tweet['likes'], tweet['retweets'], tweet['replies'],
                    tweet['quotes'], tweet['query'], tweet['collected_at'],
                    tweet['is_code_switched']
                ))
            except Exception as e:
                logger.error(f"Database insert error: {e}")
                continue
        
        conn.commit()
        conn.close()
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about collected data"""
        conn = sqlite3.connect(self.db_path)
        
        stats = {}
        
        # Total tweets
        stats['total'] = pd.read_sql_query(
            "SELECT COUNT(*) as count FROM tweets", conn
        )['count'][0]
        
        # By country
        stats['by_country'] = pd.read_sql_query(
            "SELECT country, COUNT(*) as count FROM tweets GROUP BY country", conn
        ).to_dict('records')
        
        # By language
        stats['by_language'] = pd.read_sql_query(
            "SELECT language, COUNT(*) as count FROM tweets GROUP BY language", conn
        ).to_dict('records')
        
        conn.close()
        
        return stats

# Main execution
if __name__ == "__main__":
    collector = TwitterFinancialCollector()
    
    print("\n" + "="*60)
    print("EAST AFRICAN FINANCIAL TWEET COLLECTOR")
    print("="*60)
    print(f"Target: {DATA_COLLECTION['target_tweets']} tweets")
    print(f"Countries: {', '.join(COUNTRIES.keys())}")
    print("="*60 + "\n")
    
    # Collect tweets
    tweets_df = collector.collect_all_tweets()
    
    # Show statistics
    stats = collector.get_collection_stats()
    print("\n" + "="*60)
    print("COLLECTION STATISTICS")
    print("="*60)
    print(f"Total tweets collected: {stats['total']}")
    print("\nBy country:")
    for item in stats['by_country']:
        print(f"  {item['country']}: {item['count']}")
    print("\nBy language:")
    for item in stats['by_language']:
        print(f"  {item['language']}: {item['count']}")
    print("="*60)