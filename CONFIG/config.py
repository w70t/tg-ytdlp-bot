import os

# Main Configuration
# This file combines all configuration classes into one unified Config class

from CONFIG.commands import CommandsConfig
from CONFIG.messages import Messages, get_messages_instance
from CONFIG.domains import DomainsConfig
from CONFIG.limits import LimitsConfig

###########################################################
#        START FILL IN YOUR CUSTOM VALUES HERE
###########################################################
class Config(object):
    # Bot Configuration
    BOT_NAME = os.environ.get("BOT_NAME", "your_bot_name")
    BOT_NAME_FOR_USERS = os.environ.get("BOT_NAME_FOR_USERS", "tg-ytdlp-bot")
    
    # ==================== أضف السطر التالي هنا ====================
    BOT_USERNAME = os.environ.get("BOT_USERNAME", "@YourBotUsername") # استبدل هذا باسم مستخدم بوتك
    # =============================================================

    ADMIN = list(map(int, os.environ.get("ADMIN", "").split(","))) if os.environ.get("ADMIN") else []
    API_ID = int(os.environ.get("API_ID", 0))
    API_HASH = os.environ.get("API_HASH", "your_api_hash_here")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz")
    STAR_RECEIVER = int(os.environ.get("STAR_RECEIVER", 7360853))
    ALLOWED_GROUP = list(map(int, os.environ.get("ALLOWED_GROUP", "").split(","))) if os.environ.get("ALLOWED_GROUP") else []
    MINIAPP_URL = os.environ.get("MINIAPP_URL", "https://t.me/your_bot/?startapp"  )

    # Channel Configuration (Multiple Log Channels)
    LOGS_ID = int(os.environ.get("LOGS_ID", 0))
    LOGS_VIDEO_ID = int(os.environ.get("LOGS_VIDEO_ID", 0))
    LOGS_NSFW_ID = int(os.environ.get("LOGS_NSFW_ID", 0))
    LOGS_IMG_ID = int(os.environ.get("LOGS_IMG_ID", 0))
    LOGS_PAID_ID = int(os.environ.get("LOGS_PAID_ID", 0))
    LOG_EXCEPTION = int(os.environ.get("LOG_EXCEPTION", 0))
    SUBSCRIBE_CHANNEL = int(os.environ.get("SUBSCRIBE_CHANNEL", 0))
    SUBSCRIBE_CHANNEL_URL = os.environ.get("SUBSCRIBE_CHANNEL_URL", "https://t.me/your_channel"  )

    # Cookie Configuration
    COOKIE_URL = os.environ.get("COOKIE_URL", "https://your-domain.com/cookies/cookie.txt"  )

    # YouTube Cookie URLs (Multiple Sources)
    YOUTUBE_COOKIE_URL = os.environ.get("YOUTUBE_COOKIE_URL", "https://your-domain.com/cookies/youtube/cookie1.txt"  )
    YOUTUBE_COOKIE_URL_1 = os.environ.get("YOUTUBE_COOKIE_URL_1", "https://your-domain.com/cookies/youtube/cookie2.txt"  )
    YOUTUBE_COOKIE_URL_2 = os.environ.get("YOUTUBE_COOKIE_URL_2", "https://your-domain.com/cookies/youtube/cookie3.txt"  )
    YOUTUBE_COOKIE_URL_3 = os.environ.get("YOUTUBE_COOKIE_URL_3")
    YOUTUBE_COOKIE_URL_4 = os.environ.get("YOUTUBE_COOKIE_URL_4")
    YOUTUBE_COOKIE_URL_5 = os.environ.get("YOUTUBE_COOKIE_URL_5")
    YOUTUBE_COOKIE_URL_6 = os.environ.get("YOUTUBE_COOKIE_URL_6")
    YOUTUBE_COOKIE_URL_7 = os.environ.get("YOUTUBE_COOKIE_URL_7")
    YOUTUBE_COOKIE_URL_8 = os.environ.get("YOUTUBE_COOKIE_URL_8")
    YOUTUBE_COOKIE_URL_9 = os.environ.get("YOUTUBE_COOKIE_URL_9")
    YOUTUBE_COOKIE_URL_10 = os.environ.get("YOUTUBE_COOKIE_URL_10")
    
    YOUTUBE_COOKIE_ORDER = os.environ.get("YOUTUBE_COOKIE_ORDER", "round_robin") # random, round_robin
    YOUTUBE_COOKIE_TEST_URL = os.environ.get("YOUTUBE_COOKIE_TEST_URL", "https://youtu.be/XqZsoesa55w"  )
    
    INSTAGRAM_COOKIE_URL = os.environ.get("INSTAGRAM_COOKIE_URL")
    TIKTOK_COOKIE_URL = os.environ.get("TIKTOK_COOKIE_URL")
    FACEBOOK_COOKIE_URL = os.environ.get("FACEBOOK_COOKIE_URL")
    TWITTER_COOKIE_URL = os.environ.get("TWITTER_COOKIE_URL")
    VK_COOKIE_URL = os.environ.get("VK_COOKIE_URL")

    COOKIE_FILE_PATH = "TXT/cookie.txt"
    PIC_FILE_PATH = "pic.jpg"
    FIREBASE_CACHE_FILE = "dump.json"
    RELOAD_CACHE_EVERY = int(os.environ.get("RELOAD_CACHE_EVERY", 4)) # in hours
    DOWNLOAD_FIREBASE_SCRIPT_PATH = "DATABASE/download_firebase.py"
    AUTO_CACHE_RELOAD_ENABLED = os.environ.get("AUTO_CACHE_RELOAD_ENABLED", "True").lower() == "true"

    # Firebase Configuration
    FIREBASE_USER = os.environ.get("FIREBASE_USER", "your-email@gmail.com")
    FIREBASE_PASSWORD = os.environ.get("FIREBASE_PASSWORD", "your-firebase-password")
    FIREBASE_CONF = {
        "apiKey": os.environ.get("FIREBASE_API_KEY", "your-api-key"),
        "authDomain": os.environ.get("FIREBASE_AUTH_DOMAIN", "your-project.firebaseapp.com"),
        "projectId": os.environ.get("FIREBASE_PROJECT_ID", "your-project-id"),
        "storageBucket": os.environ.get("FIREBASE_STORAGE_BUCKET", "your-project.appspot.com"),
        "messagingSenderId": os.environ.get("FIREBASE_MESSAGING_SENDER_ID", "123456789"),
        "appId": os.environ.get("FIREBASE_APP_ID", "1:123456789:web:abcdef123456"),
        "databaseURL": os.environ.get("FIREBASE_DATABASE_URL", "https://your-project-default-rtdb.firebaseio.com"  )
    }
    
    BOT_DB_PATH = f"bot/{BOT_NAME_FOR_USERS}/"
    VIDEO_CACHE_DB_PATH = "bot/video_cache"
    PLAYLIST_CACHE_DB_PATH = "bot/video_cache/playlists"
    IMAGE_CACHE_DB_PATH = "bot/video_cache/images"

    # Proxy configuration
    PROXY_TYPE = os.environ.get("PROXY_TYPE", "http"  )
    PROXY_IP = os.environ.get("PROXY_IP", "X.X.X.X")
    PROXY_PORT = int(os.environ.get("PROXY_PORT", 3128))
    PROXY_USER = os.environ.get("PROXY_USER", "XXXXXXXX")
    PROXY_PASSWORD = os.environ.get("PROXY_PASSWORD", "XXXXXXXXX")
    # Additional Proxy configuration  
    PROXY_2_TYPE = os.environ.get("PROXY_2_TYPE", "socks5")
    PROXY_2_IP = os.environ.get("PROXY_2_IP", "X.X.X.X")
    PROXY_2_PORT = int(os.environ.get("PROXY_2_PORT", 3128))
    PROXY_2_USER = os.environ.get("PROXY_2_USER", "XXXXXXXX")
    PROXY_2_PASSWORD = os.environ.get("PROXY_2_PASSWORD", "XXXXXXXXX")
    # Proxy selection method for /proxy on command
    PROXY_SELECT = os.environ.get("PROXY_SELECT", "round_robin")

    # PO Token Provider configuration
    YOUTUBE_POT_ENABLED = os.environ.get("YOUTUBE_POT_ENABLED", "True").lower() == "true"
    YOUTUBE_POT_BASE_URL = os.environ.get("YOUTUBE_POT_BASE_URL", "http://127.0.0.1:4416"  )
    YOUTUBE_POT_DISABLE_INNERTUBE = os.environ.get("YOUTUBE_POT_DISABLE_INNERTUBE", "False").lower() == "true"
    ###########################################################
    #        STOP FILL IN YOUR CUSTOM VALUES HERE
    ###########################################################
    
    # Commands configuration
    DOWNLOAD_COOKIE_COMMAND = CommandsConfig.DOWNLOAD_COOKIE_COMMAND
    PROXY_COMMAND = CommandsConfig.PROXY_COMMAND
    SUBS_COMMAND = CommandsConfig.SUBS_COMMAND
    CHECK_COOKIE_COMMAND = CommandsConfig.CHECK_COOKIE_COMMAND
    SAVE_AS_COOKIE_COMMAND = CommandsConfig.SAVE_AS_COOKIE_COMMAND
    AUDIO_COMMAND = CommandsConfig.AUDIO_COMMAND
    UNCACHE_COMMAND = CommandsConfig.UNCACHE_COMMAND
    PLAYLIST_COMMAND = CommandsConfig.PLAYLIST_COMMAND
    FORMAT_COMMAND = CommandsConfig.FORMAT_COMMAND
    MEDIINFO_COMMAND = CommandsConfig.MEDIINFO_COMMAND
    SETTINGS_COMMAND = CommandsConfig.SETTINGS_COMMAND
    COOKIES_FROM_BROWSER_COMMAND = CommandsConfig.COOKIES_FROM_BROWSER_COMMAND
    BLOCK_USER_COMMAND = CommandsConfig.BLOCK_USER_COMMAND
    UNBLOCK_USER_COMMAND = CommandsConfig.UNBLOCK_USER_COMMAND
    RUN_TIME = CommandsConfig.RUN_TIME
    GET_USER_LOGS_COMMAND = CommandsConfig.GET_USER_LOGS_COMMAND
    CLEAN_COMMAND = CommandsConfig.CLEAN_COMMAND
    USAGE_COMMAND = CommandsConfig.USAGE_COMMAND
    TAGS_COMMAND = CommandsConfig.TAGS_COMMAND
    BROADCAST_MESSAGE = CommandsConfig.BROADCAST_MESSAGE
    GET_USER_DETAILS_COMMAND = CommandsConfig.GET_USER_DETAILS_COMMAND
    SPLIT_COMMAND = CommandsConfig.SPLIT_COMMAND
    RELOAD_CACHE_COMMAND = CommandsConfig.RELOAD_CACHE_COMMAND
    AUTO_CACHE_COMMAND = CommandsConfig.AUTO_CACHE_COMMAND
    SEARCH_COMMAND = CommandsConfig.SEARCH_COMMAND
    KEYBOARD_COMMAND = CommandsConfig.KEYBOARD_COMMAND
    LINK_COMMAND = CommandsConfig.LINK_COMMAND
    IMG_COMMAND = CommandsConfig.IMG_COMMAND
    ADD_BOT_TO_GROUP_COMMAND = CommandsConfig.ADD_BOT_TO_GROUP_COMMAND
    NSFW_COMMAND = CommandsConfig.NSFW_COMMAND
    ARGS_COMMAND = CommandsConfig.ARGS_COMMAND
    LIST_COMMAND = CommandsConfig.LIST_COMMAND
    
    # Messages configuration - using dynamic loading
    @classmethod
    def get_messages(cls, user_id=None, language_code=None):
        """Get messages instance for user or language"""
        return get_messages_instance(user_id, language_code)
    
    @classmethod
    def get_message(cls, message_key, user_id=None, language_code=None):
        """Get specific message for user or language"""
        messages = cls.get_messages(user_id, language_code)
        return getattr(messages, message_key, f"[{message_key}]")
    
    # Domains configuration
    GREYLIST = DomainsConfig.GREYLIST
    BLACK_LIST = DomainsConfig.BLACK_LIST
    PORN_DOMAINS_FILE = DomainsConfig.PORN_DOMAINS_FILE
    PORN_KEYWORDS_FILE = DomainsConfig.PORN_KEYWORDS_FILE
    SUPPORTED_SITES_FILE = DomainsConfig.SUPPORTED_SITES_FILE
    UPDATE_PORN_SCRIPT_PATH = DomainsConfig.UPDATE_PORN_SCRIPT_PATH
    WHITELIST = DomainsConfig.WHITELIST
    NO_COOKIE_DOMAINS = DomainsConfig.NO_COOKIE_DOMAINS
    PROXY_DOMAINS = DomainsConfig.PROXY_DOMAINS    
    PROXY_2_DOMAINS = DomainsConfig.PROXY_2_DOMAINS    
    TIKTOK_DOMAINS = DomainsConfig.TIKTOK_DOMAINS
    CLEAN_QUERY = DomainsConfig.CLEAN_QUERY
    PIPED_DOMAIN = DomainsConfig.PIPED_DOMAIN
    
    # Limits configuration
    MAX_FILE_SIZE_GB = LimitsConfig.MAX_FILE_SIZE_GB
    DOWNLOAD_TIMEOUT = LimitsConfig.DOWNLOAD_TIMEOUT
    MAX_SUB_QUALITY = LimitsConfig.MAX_SUB_QUALITY
    MAX_SUB_DURATION = LimitsConfig.MAX_SUB_DURATION
    MAX_SUB_SIZE = LimitsConfig.MAX_SUB_SIZE
    MAX_PLAYLIST_COUNT = LimitsConfig.MAX_PLAYLIST_COUNT
    MAX_TIKTOK_COUNT = LimitsConfig.MAX_TIKTOK_COUNT
    MAX_VIDEO_DURATION = LimitsConfig.MAX_VIDEO_DURATION
    MAX_IMG_FILES = LimitsConfig.MAX_IMG_FILES
    GROUP_MULTIPLIER = LimitsConfig.GROUP_MULTIPLIER
    NSFW_STAR_COST = LimitsConfig.NSFW_STAR_COST

