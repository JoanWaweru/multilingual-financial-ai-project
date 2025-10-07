"""
Extended Reddit collection for Kenyan code-switching
"""

import praw
import pandas as pd
from pathlib import Path
import logging
import time
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExtendedKenyaCollector:
    """Collect more data from Reddit and public sources"""
    
    def __init__(self):
        self.output_path = Path("data/raw/reddit_extended")
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize Reddit from environment variables
        reddit_client_id = os.getenv('REDDIT_CLIENT_ID')
        reddit_client_secret = os.getenv('REDDIT_CLIENT_SECRET')
        reddit_user_agent = os.getenv('REDDIT_USER_AGENT', 'multilingual-financial-ai/0.1 by your_username')

        if not reddit_client_id or not reddit_client_secret:
            raise RuntimeError(
                "Missing Reddit credentials. Set 'REDDIT_CLIENT_ID', 'REDDIT_CLIENT_SECRET', and optionally 'REDDIT_USER_AGENT' in your environment or .env file."
            )

        self.reddit = praw.Reddit(
            client_id=reddit_client_id,
            client_secret=reddit_client_secret,
            user_agent=reddit_user_agent,
        )
    
    def collect_kenya_subreddit(self, limit=2000):
        """Collect from r/Kenya"""
        
        logger.info("Collecting from r/Kenya...")
        
        subreddit = self.reddit.subreddit('Kenya')
        
        # Financial keywords
        keywords = [
            'mpesa', 'm-pesa', 'money', 'pesa', 'bank', 'benki',
            'savings', 'akiba', 'loan', 'mkopo', 'chama', 'sacco',
            'investment', 'budget', 'bajeti', 'equity', 'kcb',
            'cooperative', 'fuliza', 'mshwari', 'salary', 'mshahara'
        ]
        
        posts = []
        
        # Top posts
        for post in subreddit.top(time_filter='all', limit=limit):
            posts.append({
                'id': post.id,
                'title': post.title,
                'text': post.selftext,
                'score': post.score,
                'num_comments': post.num_comments,
                'created_utc': datetime.fromtimestamp(post.created_utc),
                'subreddit': 'Kenya',
                'type': 'post'
            })
        
        # Search each keyword
        for keyword in keywords:
            try:
                for post in subreddit.search(keyword, limit=100):
                    posts.append({
                        'id': post.id,
                        'title': post.title,
                        'text': post.selftext,
                        'score': post.score,
                        'num_comments': post.num_comments,
                        'created_utc': datetime.fromtimestamp(post.created_utc),
                        'subreddit': 'Kenya',
                        'type': 'post',
                        'keyword': keyword
                    })
                
                time.sleep(2)
            except Exception as e:
                logger.warning(f"Error searching {keyword}: {e}")
        
        df = pd.DataFrame(posts)
        df = df.drop_duplicates(subset=['id'])
        
        logger.info(f"✓ Collected {len(df)} posts from r/Kenya")
        return df
    
    def collect_comments(self, post_ids, limit=50):
        """Collect comments from posts"""
        
        logger.info("Collecting comments...")
        
        comments = []
        
        for post_id in post_ids[:100]:  # Top 100 posts
            try:
                submission = self.reddit.submission(id=post_id)
                submission.comments.replace_more(limit=0)
                
                for comment in submission.comments.list()[:limit]:
                    comments.append({
                        'post_id': post_id,
                        'comment_id': comment.id,
                        'text': comment.body,
                        'score': comment.score,
                        'created_utc': datetime.fromtimestamp(comment.created_utc),
                        'type': 'comment'
                    })
                
                time.sleep(1)
            except Exception as e:
                logger.debug(f"Error getting comments for {post_id}: {e}")
        
        df = pd.DataFrame(comments)
        logger.info(f"✓ Collected {len(df)} comments")
        return df
    
    def collect_related_subreddits(self):
        """Collect from related subreddits"""
        
        subreddits = ['nairobi', 'FinancialAdvice', 'personalfinance']
        
        all_data = []
        
        for sub_name in subreddits:
            logger.info(f"Collecting from r/{sub_name}...")
            
            try:
                subreddit = self.reddit.subreddit(sub_name)
                
                for post in subreddit.search('Kenya', limit=200):
                    all_data.append({
                        'id': post.id,
                        'title': post.title,
                        'text': post.selftext,
                        'score': post.score,
                        'subreddit': sub_name,
                        'type': 'post'
                    })
                
                time.sleep(3)
            except Exception as e:
                logger.warning(f"Error with r/{sub_name}: {e}")
        
        df = pd.DataFrame(all_data)
        logger.info(f"✓ Collected {len(df)} posts from related subreddits")
        return df
    
    def filter_financial_and_cs(self, df):
        """Filter for financial content with code-switching"""
        
        financial_keywords = [
            'mpesa', 'm-pesa', 'pesa', 'money', 'benki', 'bank',
            'akiba', 'savings', 'mkopo', 'loan', 'chama', 'sacco'
        ]
        
        swahili_markers = ['na', 'ni', 'ya', 'kwa', 'sana', 'tu', 'lakini']
        english_markers = ['the', 'is', 'and', 'to', 'for', 'you', 'can']
        
        def has_financial(text):
            if pd.isna(text):
                return False
            text_lower = str(text).lower()
            return any(kw in text_lower for kw in financial_keywords)
        
        def has_code_switching(text):
            if pd.isna(text):
                return False
            text_lower = str(text).lower()
            has_sw = any(marker in text_lower for marker in swahili_markers)
            has_en = any(marker in text_lower for marker in english_markers)
            return has_sw and has_en
        
        # Some dataframes (e.g., comments) may not have a 'title' column
        has_title_column = 'title' in df.columns
        text_financial = df['text'].apply(has_financial) if 'text' in df.columns else False
        text_cs = df['text'].apply(has_code_switching) if 'text' in df.columns else False
        if has_title_column:
            title_financial = df['title'].apply(has_financial)
            title_cs = df['title'].apply(has_code_switching)
            df['is_financial'] = text_financial | title_financial
            df['has_code_switching'] = text_cs | title_cs
        else:
            df['is_financial'] = text_financial
            df['has_code_switching'] = text_cs
        
        # Filter
        filtered = df[df['is_financial'] & df['has_code_switching']].copy()
        
        logger.info(f"✓ Filtered to {len(filtered)} financial + CS samples")
        return filtered
    
    def collect_all(self):
        """Complete collection pipeline"""
        
        logger.info("=" * 60)
        logger.info("EXTENDED REDDIT COLLECTION")
        logger.info("=" * 60)
        
        # Collect posts
        kenya_posts = self.collect_kenya_subreddit()
        related_posts = self.collect_related_subreddits()
        
        # Collect comments
        top_post_ids = kenya_posts.nlargest(100, 'score')['id'].tolist()
        comments = self.collect_comments(top_post_ids)
        
        # Combine
        all_posts = pd.concat([kenya_posts, related_posts], ignore_index=True)
        
        # Filter
        filtered_posts = self.filter_financial_and_cs(all_posts)
        filtered_comments = self.filter_financial_and_cs(comments)
        
        # Save
        posts_file = self.output_path / "reddit_posts_extended.csv"
        filtered_posts.to_csv(posts_file, index=False)
        logger.info(f"✓ Saved posts: {posts_file}")
        
        comments_file = self.output_path / "reddit_comments_extended.csv"
        filtered_comments.to_csv(comments_file, index=False)
        logger.info(f"✓ Saved comments: {comments_file}")
        
        logger.info(f"\n✓ COLLECTION COMPLETE!")
        logger.info(f"  Posts: {len(filtered_posts)}")
        logger.info(f"  Comments: {len(filtered_comments)}")
        logger.info(f"  Total: {len(filtered_posts) + len(filtered_comments)}")
        
        return filtered_posts, filtered_comments

if __name__ == "__main__":
    collector = ExtendedKenyaCollector()
    collector.collect_all()