from datetime import datetime
import time
class TransactionFormatter:
    @staticmethod
    def format_status(status):
        """Format status with color codes for terminal output"""
        status_colors = {
            'confirmed': '\033[92m',  # Green
            'success': '\033[94m',    # Blue
            'failed': '\033[91m',     # Red
            'error': '\033[93m',      # Yellow
            'pending': '\033[90m'     # Gray
        }
        color = status_colors.get(status, '\033[0m')
        return f"{color}{status}\033[0m"

    @staticmethod
    def format_timestamp(timestamp):
        """Format timestamp to human readable format"""
        if timestamp:
            return datetime.fromtimestamp(time.mktime(timestamp)).strftime('%Y-%m-%d %H:%M:%S')
        return 'N/A'

    @staticmethod
    def format_txid(txid):
        """Format TXID for display"""
        return f"{txid[:8]}...{txid[-8:]}" 