"""
Main execution script for Multilingual Financial AI System
Provides command-line interface for running all project components

Usage:
    python main.py --step all           # Run complete pipeline
    python main.py --step collect       # Collect data only
    python main.py --step validate      # Validate data only
    python main.py --step preprocess    # Preprocess data only
    python main.py --step train         # Train models only
    python main.py --step chatbot       # Run chatbot CLI
    python main.py --step webapp        # Launch web application

Author: Joan Waweru
Date: September 2025
Version: 1.0.0
"""

import logging
import sys
import os
from pathlib import Path
import argparse
from datetime import datetime
import traceback

# Setup logging
LOG_DIR = Path(__file__).parent / 'logs'
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / f'main_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Banner
BANNER = """
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║     MULTILINGUAL FINANCIAL AI SYSTEM                                 ║
║     East African Code-Switching Assistant                            ║
║                                                                      ║
║     University of Debrecen - MSc Thesis Project                      ║
║     Version 1.0.0 | September 2025                                   ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
"""


def print_banner():
    """Print application banner"""
    print("\n" + BANNER)


def print_section(title: str):
    """Print formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def print_step(step: str, status: str = "START"):
    """Print step status"""
    symbols = {
        "START": "▶",
        "SUCCESS": "✓",
        "ERROR": "✗",
        "INFO": "ℹ"
    }
    symbol = symbols.get(status, "•")
    print(f"{symbol} {step}")


def check_dependencies():
    """Check if all required packages are installed"""
    print_step("Checking dependencies...", "INFO")

    required_packages = {
        'torch': 'PyTorch',
        'transformers': 'Hugging Face Transformers',
        'pandas': 'Pandas',
        'numpy': 'NumPy',
        'tweepy': 'Tweepy',
        'streamlit': 'Streamlit',
        'nltk': 'NLTK',
        'sklearn': 'Scikit-learn'
    }

    missing_packages = []

    for package, name in required_packages.items():
        try:
            __import__(package)
            print(f"  ✓ {name}")
        except ImportError:
            print(f"  ✗ {name} - NOT INSTALLED")
            missing_packages.append(package)

    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False

    print("\n✓ All dependencies satisfied")
    return True


def check_configuration():
    """Check if configuration is set up correctly"""
    print_step("Checking configuration...", "INFO")
    try:
        import snscrape.modules.twitter as _  # noqa: F401
        print("  ✓ Using snscrape (no API key needed)")
        return True
    except Exception as e:
        print(f"  ✗ snscrape not available: {e}")
        print("\n⚠️  Install it: pip install snscrape")
        return False


def step_collect_data():
    """Step 1: Collect data from Twitter"""
    print_section("STEP 1: DATA COLLECTION")

    try:
        from data_collection.twitter_collector import TwitterFinancialCollector
        from config.settings import DATA_COLLECTION

        print_step("Initializing Twitter collector...", "START")
        collector = TwitterFinancialCollector()

        # NEW: probe what operators your plan supports (so we avoid 400s)
        supports = collector.probe_capabilities()
        print_step(f"Operator support: {supports}", "INFO")

        target = DATA_COLLECTION.get('target_tweets', 'N/A')
        print_step(f"Target: {target} tweets", "INFO")
        print_step("Starting collection...", "START")

        # Collect tweets
        df = collector.collect_all_tweets()

        # Get statistics
        stats = collector.get_collection_stats()

        print_step("Collection complete!", "SUCCESS")
        print(f"\n📊 Collection Statistics:")
        print(f"  Total tweets: {stats['total']}")
        print(f"\n  By country:")
        for item in stats['by_country']:
            print(f"    {item['country']}: {item['count']}")
        print(f"\n  By language:")
        for item in stats['by_language']:
            print(f"    {item['language']}: {item['count']}")

        return True

    except Exception as e:
        print_step(f"Data collection failed: {str(e)}", "ERROR")
        logger.error(f"Data collection error: {traceback.format_exc()}")
        return False


def step_validate_data():
    """Step 2: Validate collected data"""
    print_section("STEP 2: DATA VALIDATION")

    try:
        from data_collection.data_validator import DataValidator

        print_step("Initializing validator...", "START")
        validator = DataValidator()

        print_step("Validating dataset...", "START")
        valid_df = validator.validate_dataset()

        # Get validation report
        report = validator.get_validation_report(valid_df)

        print_step("Validation complete!", "SUCCESS")
        print(f"\n📊 Validation Report:")
        print(f"  Total tweets: {report['total_tweets']}")
        print(f"  Valid tweets: {report['valid_tweets']}")
        print(f"  Invalid tweets: {report['invalid_tweets']}")
        print(f"  Average length: {report['avg_length']:.1f} characters")

        return True

    except Exception as e:
        print_step(f"Data validation failed: {str(e)}", "ERROR")
        logger.error(f"Data validation error: {traceback.format_exc()}")
        return False


def step_preprocess_data():
    """Step 3: Preprocess and analyze data"""
    print_section("STEP 3: DATA PREPROCESSING")

    try:
        from preprocessing.text_cleaner import MultilingualTextCleaner
        from preprocessing.language_detector import CodeSwitchingDetector
        from config.settings import PROCESSED_DATA_DIR
        import pandas as pd

        print_step("Loading validated data...", "START")
        df = pd.read_csv(PROCESSED_DATA_DIR / "tweets_validated.csv")
        print(f"  Loaded {len(df)} tweets")

        # Clean text
        print_step("Cleaning text...", "START")
        cleaner = MultilingualTextCleaner()
        df = cleaner.clean_dataset(df)
        print_step("Text cleaning complete", "SUCCESS")

        # Analyze code-switching
        print_step("Analyzing code-switching patterns...", "START")
        detector = CodeSwitchingDetector()
        df = detector.analyze_dataset(df)
        print_step("Language analysis complete", "SUCCESS")

        # Save processed data
        output_file = PROCESSED_DATA_DIR / "tweets_analyzed.csv"
        df.to_csv(output_file, index=False, encoding='utf-8')

        print_step("Preprocessing complete!", "SUCCESS")
        print(f"\n📊 Preprocessing Statistics:")
        print(f"  Total processed: {len(df)}")
        print(f"  Code-switched: {df['has_code_switching'].sum()}")
        print(f"  Average words: {df['word_count'].mean():.1f}")
        print(f"  Output file: {output_file}")

        return True

    except Exception as e:
        print_step(f"Preprocessing failed: {str(e)}", "ERROR")
        logger.error(f"Preprocessing error: {traceback.format_exc()}")
        return False


def step_train_models():
    """Step 4: Train machine learning models"""
    print_section("STEP 4: MODEL TRAINING")

    try:
        from models.code_switching_detector import BERTCodeSwitchingDetector, CodeSwitchingTrainer
        from models.engagement_analyzer import EngagementAnalyzer
        from config.settings import PROCESSED_DATA_DIR, MODEL_CONFIG
        import pandas as pd
        import torch.nn as nn

        print_step("Loading processed data...", "START")
        df = pd.read_csv(PROCESSED_DATA_DIR / "tweets_analyzed.csv")
        print(f"  Loaded {len(df)} tweets")

        # Train code-switching detector
        print_step("Training code-switching detector...", "START")
        print("\n" + "-" * 70)
        print("BERT Model Training")
        print("-" * 70 + "\n")

        # Balance dataset
        code_switched = df[df['has_code_switching'] == True].sample(
            n=min(5000, len(df[df['has_code_switching'] == True])),
            random_state=42
        )
        non_code_switched = df[df['has_code_switching'] == False].sample(
            n=len(code_switched),
            random_state=42
        )
        balanced_df = pd.concat([code_switched, non_code_switched]).sample(frac=1, random_state=42)

        print(f"Balanced dataset: {len(balanced_df)} tweets")
        print(f"  Code-switched: {balanced_df['has_code_switching'].sum()}")
        print(f"  Non code-switched: {(~balanced_df['has_code_switching']).sum()}")

        # Initialize and train model
        model = BERTCodeSwitchingDetector(n_classes=2)
        trainer = CodeSwitchingTrainer(model)

        train_loader, val_loader, test_loader = trainer.prepare_data(balanced_df)
        trainer.train(train_loader, val_loader, epochs=MODEL_CONFIG['num_epochs'])

        # Test
        test_acc, test_loss = trainer.evaluate(test_loader, nn.CrossEntropyLoss())

        print_step(f"BERT training complete! (Accuracy: {test_acc:.2f}%)", "SUCCESS")

        # Train engagement analyzer
        print_step("Training engagement analyzer...", "START")
        print("\n" + "-" * 70)
        print("Engagement Analyzer Training")
        print("-" * 70 + "\n")

        analyzer = EngagementAnalyzer()
        analyzer.train(df)
        analyzer.save_model()

        print_step("Engagement analyzer training complete!", "SUCCESS")

        print_step("All models trained successfully!", "SUCCESS")
        print(f"\n📊 Training Results:")
        print(f"  BERT Accuracy: {test_acc:.2f}%")
        print(f"  BERT Loss: {test_loss:.4f}")
        print(f"  Models saved in: saved_models/")

        return True

    except Exception as e:
        print_step(f"Model training failed: {str(e)}", "ERROR")
        logger.error(f"Training error: {traceback.format_exc()}")
        return False


def step_evaluate_models():
    """Step 5: Evaluate trained models"""
    print_section("STEP 5: MODEL EVALUATION")

    try:
        from training.evaluation import evaluate_model
        from config.settings import MODELS_DIR

        print_step("Evaluating code-switching detector...", "START")

        metrics = evaluate_model(
            model_path="best_model.pt",
            test_data_file="tweets_analyzed.csv"
        )

        print_step("Evaluation complete!", "SUCCESS")
        print(f"\n📊 Model Performance:")
        print(f"  Accuracy:  {metrics['accuracy'] * 100:.2f}%")
        print(f"  Precision: {metrics['precision'] * 100:.2f}%")
        print(f"  Recall:    {metrics['recall'] * 100:.2f}%")
        print(f"  F1-Score:  {metrics['f1_score'] * 100:.2f}%")
        print(f"  ROC-AUC:   {metrics['roc_auc']:.4f}")
        print(f"\n  Results saved in: {MODELS_DIR / 'evaluation'}/")

        return True

    except Exception as e:
        print_step(f"Evaluation failed: {str(e)}", "ERROR")
        logger.error(f"Evaluation error: {traceback.format_exc()}")
        return False


def step_run_chatbot():
    """Step 6: Run interactive chatbot"""
    print_section("STEP 6: CHATBOT INTERFACE")

    try:
        from chatbot.chatbot_engine import MultilingualFinancialChatbot

        print_step("Initializing chatbot...", "START")
        chatbot = MultilingualFinancialChatbot()
        print_step("Chatbot initialized!", "SUCCESS")

        print("\n" + "=" * 70)
        print("MULTILINGUAL FINANCIAL CHATBOT")
        print("East African Code-Switching Assistant")
        print("=" * 70)
        print("\nCommands:")
        print("  'quit' or 'exit' - Exit chatbot")
        print("  'reset' - Start new conversation")
        print("  'stats' - Show conversation statistics")
        print("  'tip' - Get personalized financial tip")
        print("  'suggest' - Get topic suggestion")
        print("=" * 70 + "\n")

        # Welcome message
        print(f"Bot: {chatbot.cultural_kb.get_contextual_greeting()}\n")

        while True:
            try:
                user_input = input("You: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ['quit', 'exit']:
                    print(f"\nBot: {chatbot.cultural_kb.get_encouragement()}")
                    print("Asante sana! Kwaheri! 👋\n")
                    break

                if user_input.lower() == 'reset':
                    chatbot.reset_conversation()
                    print("\n✓ Conversation reset. Let's start fresh!")
                    print(f"Bot: {chatbot.cultural_kb.get_contextual_greeting()}\n")
                    continue

                if user_input.lower() == 'stats':
                    stats = chatbot.get_conversation_stats()
                    print("\n📊 Conversation Statistics:")
                    print(f"  Total messages: {stats['total_messages']}")
                    print(
                        f"  Topics discussed: {', '.join(stats['topics_discussed']) if stats['topics_discussed'] else 'None yet'}")
                    print(f"  Language preference: {stats['language_preference']}")
                    print(f"  Experience level: {stats['experience_level']}")
                    if stats['country']:
                        print(f"  Country: {stats['country']}")
                    print()
                    continue

                if user_input.lower() == 'tip':
                    tip = chatbot.get_personalized_tip()
                    print(f"\n💡 {tip}\n")
                    continue

                if user_input.lower() == 'suggest':
                    suggestion = chatbot.get_next_topic_suggestion()
                    print(f"\nBot: {suggestion}\n")
                    continue

                # Get response
                response = chatbot.chat(user_input)
                print(f"\nBot: {response}\n")

            except KeyboardInterrupt:
                print("\n\nAsante! Kwaheri! 👋\n")
                break
            except Exception as e:
                logger.error(f"Chat error: {e}")
                print(f"\nPole! An error occurred: {str(e)}")
                print("Please try again or type 'reset' to start over.\n")

        return True

    except Exception as e:
        print_step(f"Chatbot initialization failed: {str(e)}", "ERROR")
        logger.error(f"Chatbot error: {traceback.format_exc()}")
        return False


def step_launch_webapp():
    """Step 7: Launch web application"""
    print_section("STEP 7: WEB APPLICATION")

    try:
        import subprocess

        print_step("Launching Streamlit web application...", "START")
        print("\n" + "-" * 70)
        print("The web application will open in your default browser")
        print("Press Ctrl+C to stop the server")
        print("-" * 70 + "\n")

        # Launch streamlit
        webapp_path = Path(__file__).parent / "web_app" / "app.py"

        if not webapp_path.exists():
            print_step("Web app file not found!", "ERROR")
            return False

        subprocess.run([sys.executable, "-m", "streamlit", "run", str(webapp_path)])

        return True

    except KeyboardInterrupt:
        print("\n\nWeb application stopped by user.")
        return True
    except Exception as e:
        print_step(f"Web application failed: {str(e)}", "ERROR")
        logger.error(f"Webapp error: {traceback.format_exc()}")
        return False


def run_all_steps():
    """Run complete pipeline"""
    print_section("RUNNING COMPLETE PIPELINE")

    steps = [
        ("Data Collection", step_collect_data),
        ("Data Validation", step_validate_data),
        ("Data Preprocessing", step_preprocess_data),
        ("Model Training", step_train_models),
        ("Model Evaluation", step_evaluate_models)
    ]

    start_time = datetime.now()
    results = []

    for step_name, step_func in steps:
        print(f"\n🔄 Starting: {step_name}")
        success = step_func()
        results.append((step_name, success))

        if not success:
            print(f"\n⚠️  Pipeline stopped at: {step_name}")
            print("Please fix the errors and try again.")
            break

    end_time = datetime.now()
    duration = end_time - start_time

    # Print summary
    print("\n" + "=" * 70)
    print("PIPELINE EXECUTION SUMMARY")
    print("=" * 70)
    print(f"\nExecution time: {duration}")
    print("\nSteps completed:")

    for step_name, success in results:
        status = "✓ SUCCESS" if success else "✗ FAILED"
        print(f"  {status} - {step_name}")

    all_success = all(success for _, success in results)

    if all_success:
        print("\n" + "=" * 70)
        print("🎉 ALL STEPS COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print("\n📚 Next Steps:")
        print("  1. Run chatbot:    python main.py --step chatbot")
        print("  2. Launch web app: python main.py --step webapp")
        print("  3. View results:   Check saved_models/evaluation/")
        print("\n✨ Your MSc thesis project is ready!")
    else:
        print("\n" + "=" * 70)
        print("⚠️  PIPELINE INCOMPLETE")
        print("=" * 70)
        print("\nPlease check the error messages above and:")
        print("  1. Review logs in: logs/")
        print("  2. Fix any configuration issues")
        print("  3. Re-run failed steps individually")

    return all_success


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Multilingual Financial AI System - Main Execution Script',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --step all           Run complete pipeline
  python main.py --step collect       Collect Twitter data
  python main.py --step train         Train ML models
  python main.py --step chatbot       Run chatbot interface
  python main.py --step webapp        Launch web application

For more information, visit: https://github.com/yourname/multilingual-finance-ai
        """
    )

    parser.add_argument(
        '--step',
        type=str,
        choices=['all', 'collect', 'validate', 'preprocess', 'train', 'evaluate', 'chatbot', 'webapp'],
        default='all',
        help='Which step to run'
    )

    parser.add_argument(
        '--skip-checks',
        action='store_true',
        help='Skip dependency and configuration checks'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Print banner
    print_banner()

    # Pre-flight checks
    if not args.skip_checks:
        print_section("PRE-FLIGHT CHECKS")

        if not check_dependencies():
            print("\n❌ Dependency check failed!")
            print("Please install required packages: pip install -r requirements.txt")
            sys.exit(1)

        if args.step in ['all', 'collect'] and not check_configuration():
            print("\n❌ Configuration check failed!")
            print("Please set up your .env file with API credentials")
            sys.exit(1)

        print("\n✅ All pre-flight checks passed!")

    # Execute requested step
    try:
        if args.step == 'all':
            success = run_all_steps()
        elif args.step == 'collect':
            success = step_collect_data()
        elif args.step == 'validate':
            success = step_validate_data()
        elif args.step == 'preprocess':
            success = step_preprocess_data()
        elif args.step == 'train':
            success = step_train_models()
            if success:
                step_evaluate_models()
        elif args.step == 'evaluate':
            success = step_evaluate_models()
        elif args.step == 'chatbot':
            success = step_run_chatbot()
        elif args.step == 'webapp':
            success = step_launch_webapp()
        else:
            print(f"Unknown step: {args.step}")
            success = False

        # Exit with appropriate code
        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n\n⚠️  Execution interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
        logger.error(f"Unexpected error: {traceback.format_exc()}")
        sys.exit(1)


if __name__ == "__main__":
    main()