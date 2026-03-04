#!/usr/bin/env python3
"""
Dice Job Agent - Main Entry Point
Automated job application agent for Dice.com
"""

import argparse
import sys
import os
from src.logger import get_logger
from src.scheduler import scheduler
from src.dashboard import run_dashboard

logger = get_logger()

def main():
    parser = argparse.ArgumentParser(
        description='Dice Job Application Agent',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python main.py start              # Start the agent scheduler
  python main.py stop               # Stop the agent
  python main.py run-once           # Run job cycle once (testing)
  python main.py dashboard          # Start web dashboard
  python main.py status             # Check agent status
        '''
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Start command
    subparsers.add_parser('start', help='Start the job agent scheduler')

    # Stop command
    subparsers.add_parser('stop', help='Stop the job agent scheduler')

    # Run once command
    subparsers.add_parser('run-once', help='Run one job cycle (for testing)')

    # Dashboard command
    from dotenv import load_dotenv
    load_dotenv()
    dashboard_parser = subparsers.add_parser('dashboard', help='Start web dashboard')
    dashboard_parser.add_argument('--host', default=os.getenv('FLASK_HOST', '0.0.0.0'), help='Dashboard host')
    dashboard_parser.add_argument('--port', type=int, default=int(os.getenv('FLASK_PORT', 5000)), help='Dashboard port')

    # Status command
    subparsers.add_parser('status', help='Check agent status')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command == 'start':
            logger.info("Starting Dice Job Agent...")
            scheduler.start()
            logger.info("Agent is now running. Press Ctrl+C to stop.")
            # Keep the script running
            while True:
                pass

        elif args.command == 'stop':
            logger.info("Stopping Dice Job Agent...")
            scheduler.stop()
            logger.info("Agent stopped.")

        elif args.command == 'run-once':
            logger.info("Running job cycle once...")
            scheduler.run_once()
            logger.info("Job cycle completed.")

        elif args.command == 'dashboard':
            logger.info(f"Starting dashboard on {args.host}:{args.port}...")
            logger.info(f"Open browser to http://{args.host}:{args.port}")
            run_dashboard(host=args.host, port=args.port, debug=False)

        elif args.command == 'status':
            status = scheduler.get_status()
            logger.info("Agent Status:")
            logger.info(f"  Running: {status['is_running']}")
            if status['next_run_time']:
                logger.info(f"  Next Run: {status['next_run_time']}")
            if status['jobs']:
                logger.info(f"  Scheduled Jobs: {', '.join(status['jobs'])}")

    except KeyboardInterrupt:
        logger.info("\nInterrupted by user. Shutting down...")
        scheduler.stop()
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
