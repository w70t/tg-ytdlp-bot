from HELPERS.app_instance import get_app
from CONFIG.config import Config
from CONFIG.messages import Messages, get_messages_instance
from CONFIG.logger_msg import LoggerMsg
from HELPERS.logger import logger, get_log_channel
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ChatMemberStatus
import os
from HELPERS.safe_messeger import safe_send_message
from CONFIG.limits import LimitsConfig
from pyrogram import enums

def humanbytes(size):
    # https://stackoverflow.com/a/49361727/4723940
    # 2 ** 10 = 1024
    if not size:
        return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: ' ', 1: 'Ki', 2: 'Mi', 3: 'Gi', 4: 'Ti'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + 'B'

def TimeFormatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + "d, ") if days else "") +\
        ((str(hours) + "h, ") if hours else "") +\
        ((str(minutes) + "m, ") if minutes else "") +\
        ((str(seconds) + "s, ") if seconds else "") +\
        ((str(milliseconds) + "ms, ") if milliseconds else "")
    return tmp[:-2]

# Check the USAGE of the BOT

def is_user_in_channel(app, message):
    return True  # Bypass channel subscription check
    # Bypass subscription checks for explicitly allowed groups
    try:
        if int(getattr(message.chat, 'id', 0)) in getattr(Config, 'ALLOWED_GROUP', []):
            return True
    except Exception:
        pass
    try:
        logger.info(LoggerMsg.LIMITTER_CHANNEL_CHECK_MEMBERSHIP_LOG_MSG.format(user_id=message.chat.id, channel=Config.SUBSCRIBE_CHANNEL))
        cht_member = app.get_chat_member(
            Config.SUBSCRIBE_CHANNEL, message.chat.id)
        logger.info(LoggerMsg.LIMITTER_CHANNEL_CHECK_STATUS_LOG_MSG.format(user_id=message.chat.id, status=cht_member.status))
        if cht_member.status == ChatMemberStatus.MEMBER or cht_member.status == ChatMemberStatus.OWNER or cht_member.status == ChatMemberStatus.ADMINISTRATOR:
            logger.info(LoggerMsg.LIMITTER_CHANNEL_CHECK_IS_MEMBER_LOG_MSG.format(user_id=message.chat.id))
            return True
        else:
            logger.info(LoggerMsg.LIMITTER_CHANNEL_CHECK_NOT_MEMBER_LOG_MSG.format(user_id=message.chat.id))
            return False

    except Exception as e:
        logger.error(LoggerMsg.LIMITTER_CHANNEL_CHECK_ERROR_LOG_MSG.format(user_id=message.chat.id, error=e))
        text = f"{get_messages_instance().TO_USE_MSG}\n \n{get_messages_instance().CREDITS_MSG}"
        button = InlineKeyboardButton(
            get_messages_instance().CHANNEL_JOIN_BUTTON_MSG, url=Config.SUBSCRIBE_CHANNEL_URL)
        keyboard = InlineKeyboardMarkup([[button]])
        # Use safe send to avoid FloodWait on texts
        safe_send_message(
            chat_id=message.chat.id,
            text=text,
            reply_markup=keyboard
        )
        return False
    
    # If user is not a member, send subscription message
    text = f"{get_messages_instance().TO_USE_MSG}\n \n{get_messages_instance().CREDITS_MSG}"
    button = InlineKeyboardButton(
        get_messages_instance().CHANNEL_JOIN_BUTTON_MSG, url=Config.SUBSCRIBE_CHANNEL_URL)
    keyboard = InlineKeyboardMarkup([[button]])
    # Use safe send to avoid FloodWait on texts
    safe_send_message(
        chat_id=message.chat.id,
        text=text,
        reply_markup=keyboard
    )
    return False


def check_user(message):
    """Check if user is in channel and create user directory"""
    user_id_str = str(message.chat.id)
    
    # Create The User Folder Inside The "Users" Directory
    user_dir = os.path.join("users", user_id_str)
    if not os.path.exists(user_dir):
        os.makedirs(user_dir, exist_ok=True)
    
    # Check if user is in channel (for non-admins), but always allow in allowed groups
    if int(message.chat.id) not in Config.ADMIN and int(message.chat.id) not in getattr(Config, 'ALLOWED_GROUP', []):
        app = get_app()
        if app is None:
            logger.error(get_messages_instance().HELPER_APP_INSTANCE_NONE_MSG)
            return False
        return is_user_in_channel(app, message)
    return True


def ensure_group_admin(app, message):
    """
    For allowed groups, ensure the bot has admin rights. If not, ask to grant admin.
    Returns True if ok to proceed, False if should stop.
    """
    try:
        chat = getattr(message, 'chat', None)
        chat_id = int(getattr(chat, 'id', 0)) if chat else 0
        if chat_id in getattr(Config, 'ALLOWED_GROUP', []):
            try:
                me = app.get_me()
                member = app.get_chat_member(chat_id, me.id)
                status = getattr(member, 'status', None)
                if status not in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
                    # Ask to grant admin. Reply in the same topic/thread when possible
                    safe_send_message(
                        chat_id,
                        get_messages_instance().HELPER_ADMIN_RIGHTS_REQUIRED_MSG,
                        message=message
                    )
                    return False
            except Exception:
                # If check failed for any reason, be safe and request admin
                safe_send_message(
                    chat_id,
                    get_messages_instance().HELPER_ADMIN_RIGHTS_REQUIRED_MSG,
                    message=message
                )
                return False
        return True
    except Exception:
        return True

def check_file_size_limit(info_dict, max_size_bytes=None, message=None):
    """
    Checks if the size of the file is the global limit.
    Returns True if the size is within the limit, otherwise false.
    """
    if max_size_bytes is None:
        max_size_gb = getattr(Config, 'MAX_FILE_SIZE_GB', 8)  # GiB
        # Apply group multiplier for groups/channels
        try:
            if message and getattr(message.chat, 'type', None) != enums.ChatType.PRIVATE:
                mult = getattr(LimitsConfig, 'GROUP_MULTIPLIER', 1)
                max_size_gb = int(max_size_gb * mult)
        except Exception:
            pass
        max_size_bytes = int(max_size_gb * 1024 ** 3)

    # Check if info_dict is None
    if info_dict is None:
        logger.warning(get_messages_instance().HELPER_CHECK_FILE_SIZE_LIMIT_INFO_DICT_NONE_MSG)
        return True

    filesize = info_dict.get('filesize') or info_dict.get('filesize_approx')
    if filesize and filesize > 0:
        size_bytes = int(filesize)
    else:
        # Try to estimate by bitrate (kbit/s) and duration (s)
        tbr = info_dict.get('tbr')
        duration = info_dict.get('duration')
        if tbr and duration:
            size_bytes = float(tbr) * float(duration) * 125  # kbit/s -> bytes
        else:
            # Very rough estimate by resolution and duration
            width = info_dict.get('width')
            height = info_dict.get('height')
            duration = info_dict.get('duration')
            if width and height and duration:
                size_bytes = int(width) * int(height) * float(duration) * 0.07
            else:
                # Could not estimate, allow download
                return True

    return size_bytes <= max_size_bytes

    
def check_subs_limits(info_dict, quality_key=None):
    """
    Checks restrictions for embedding subtitles
    Returns True if subtitles can be built, false if limits are exceeded
    """
    try:
        # Check if info_dict is None
        if info_dict is None:
            logger.warning(get_messages_instance().HELPER_CHECK_SUBS_LIMITS_INFO_DICT_NONE_MSG)
            return True
            
        # We get the parameters from the config
        max_quality = Config.MAX_SUB_QUALITY
        max_duration = Config.MAX_SUB_DURATION
        max_size = Config.MAX_SUB_SIZE
        # Apply group multiplier in groups/channels
        try:
            if getattr(info_dict, 'message', None) and getattr(info_dict.message.chat, 'type', None) != enums.ChatType.PRIVATE:
                mult = getattr(LimitsConfig, 'GROUP_MULTIPLIER', 1)
                max_duration = int(max_duration * mult)
                max_size = int(max_size * mult)
                # For groups, allow up to 1080p for subtitles
                max_quality = 1080
        except Exception:
            pass
        
        logger.info(get_messages_instance().HELPER_CHECK_SUBS_LIMITS_CHECKING_LIMITS_MSG.format(max_quality=max_quality, max_duration=max_duration, max_size=max_size))
        logger.info(get_messages_instance().HELPER_CHECK_SUBS_LIMITS_INFO_DICT_KEYS_MSG.format(keys=list(info_dict.keys()) if info_dict else 'None'))
        
        # Check the duration
        duration = info_dict.get('duration')
        if duration and duration > max_duration:
            logger.info(get_messages_instance().HELPER_SUBTITLE_EMBEDDING_SKIPPED_DURATION_MSG.format(duration=duration, max_duration=max_duration))
            return False
        
        # Check the file size (only if it is accurately known)
        filesize = info_dict.get('filesize') or info_dict.get('filesize_approx')
        if filesize and filesize > 0:  # Check that the size is larger than 0
            size_mb = filesize / (1024 * 1024)  # Fixed: use division instead of integer division
            if size_mb > max_size:
                logger.info(get_messages_instance().HELPER_SUBTITLE_EMBEDDING_SKIPPED_SIZE_MSG.format(size_mb=size_mb, max_size=max_size))
                return False
        
        # Check quality (only if width and height are available)
        width = info_dict.get('width')
        height = info_dict.get('height')
        if width and height:
            min_side = min(width, height)
            if min_side > max_quality:
                logger.info(get_messages_instance().HELPER_SUBTITLE_EMBEDDING_SKIPPED_QUALITY_MSG.format(width=width, height=height, min_side=min_side, max_quality=max_quality))
                return False
        
        logger.info(LoggerMsg.LIMITTER_SUBTITLE_LIMITS_CHECK_PASSED_LOG_MSG.format(duration=duration, size=filesize, width=width, height=height))
        return True
    except Exception as e:
        logger.error(LoggerMsg.LIMITTER_SUBTITLE_LIMITS_CHECK_ERROR_LOG_MSG.format(error=e))
        return False

def check_playlist_range_limits(url, video_start_with, video_end_with, app, message):
    """
    Checks the limits of the download range for playlists, Tiktok and Instagram.
    For single videos, True always returns.
    If the range exceeds the limit, it sends a warning and returns false.
    """
    # If a single video (no range) - always true
    if video_start_with == 1 and video_end_with == 1:
        return True

    url_l = str(url).lower() if url else ''
    if 'tiktok.com' in url_l:
        max_count = Config.MAX_TIKTOK_COUNT
        service = 'TikTok'
    elif 'instagram.com' in url_l:
        max_count = Config.MAX_TIKTOK_COUNT
        service = 'Instagram'
    else:
        max_count = Config.MAX_PLAYLIST_COUNT
        service = 'playlist'
    
    # Apply group multiplier for groups/channels
    try:
        if message and getattr(message.chat, 'type', None) != enums.ChatType.PRIVATE:
            mult = getattr(LimitsConfig, 'GROUP_MULTIPLIER', 1)
            max_count = int(max_count * mult)
    except Exception:
        pass

    count = video_end_with - video_start_with + 1
    if count > max_count:
        # Determine command type based on URL
        if 'tiktok.com' in url_l:
            command_type = get_messages_instance().HELPER_COMMAND_TYPE_TIKTOK_MSG
        elif 'instagram.com' in url_l:
            command_type = get_messages_instance().HELPER_COMMAND_TYPE_INSTAGRAM_MSG
        else:
            command_type = get_messages_instance().HELPER_COMMAND_TYPE_PLAYLIST_MSG
        
        # Create suggested commands with maximum available range
        suggested_command_url_format = f"{url}*{video_start_with}*{video_start_with + max_count - 1}"
        suggested_command_vid_format = f"/vid {video_start_with}-{video_start_with + max_count - 1} {url}"
        suggested_command_audio_format = f"/audio {video_start_with}-{video_start_with + max_count - 1} {url}"
        
        safe_send_message(
            message.chat.id,
            get_messages_instance().HELPER_RANGE_LIMIT_EXCEEDED_MSG.format(service=service, count=count, max_count=max_count, suggested_command_url_format=suggested_command_url_format) +
            f"<code>{suggested_command_vid_format}</code>\n\n"
            f"<code>{suggested_command_audio_format}</code>",
            parse_mode=enums.ParseMode.HTML,
            reply_to_message_id=message.id
        )
        # We send a notification to the log channel
        safe_send_message(
            get_log_channel("general"),
            get_messages_instance().HELPER_RANGE_LIMIT_EXCEEDED_LOG_MSG.format(service=service, count=count, max_count=max_count, user_id=message.chat.id),
        )
        return False
    return True
