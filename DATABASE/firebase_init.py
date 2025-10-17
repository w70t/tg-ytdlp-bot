import math
import time
import threading
import os
import json
from typing import Any, Dict, List, Optional

import requests
from requests import Session
from requests.adapters import HTTPAdapter
import firebase_admin
from firebase_admin import credentials, db as admin_db

from CONFIG.config import Config
from CONFIG.messages import Messages, get_messages_instance
from HELPERS.logger import logger
from HELPERS.filesystem_hlp import create_directory
from HELPERS.logger import send_to_all

# Global variable for timing
starting_point = []


def _get_database_url() -> str:
    try:
        database_url_local = Config.FIREBASE_CONF.get("databaseURL")
    except Exception:
        database_url_local = None
    if not database_url_local:
        messages = get_messages_instance()
        raise RuntimeError(messages.DB_DATABASE_URL_MISSING_MSG)
    return database_url_local


def _init_firebase_admin_if_needed() -> bool:
    """Initialize firebase_admin with databaseURL from Config."""
    if firebase_admin._apps:
        return True

    database_url = _get_database_url()
    cred_obj = None

    # Try to load Firebase credentials from FIREBASE_CREDENTIALS environment variable
    firebase_credentials_json = os.environ.get("FIREBASE_CREDENTIALS")
    if firebase_credentials_json:
        try:
            cred_dict = json.loads(firebase_credentials_json)
            cred_obj = credentials.Certificate(cred_dict)
            logger.info("✅ Firebase credentials loaded from FIREBASE_CREDENTIALS environment variable.")
        except Exception as e:
            logger.error(f"❌ Error parsing FIREBASE_CREDENTIALS environment variable: {e}")
            cred_obj = None

    if cred_obj is None and not firebase_credentials_json:
        logger.info("ℹ️ FIREBASE_CREDENTIALS environment variable not set.")

    if cred_obj is None:
        # 1) Explicit path in config
        service_account_path = getattr(Config, "FIREBASE_SERVICE_ACCOUNT", None)
        if service_account_path and os.path.exists(service_account_path):
            cred_obj = credentials.Certificate(service_account_path)
        else:
            # 2) GOOGLE_APPLICATION_CREDENTIALS path present?
            adc_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
            if adc_path and os.path.exists(adc_path):
                try:
                    cred_obj = credentials.Certificate(adc_path)
                except Exception:
                    cred_obj = None

    if cred_obj is None:
        logger.warning("ℹ️ firebase_admin credentials not found, will use REST fallback")
        return False

    firebase_admin.initialize_app(cred_obj, {"databaseURL": database_url})
    messages = get_messages_instance()
    logger.info(messages.DB_FIREBASE_ADMIN_INITIALIZED_MSG)
    return True


class _SnapshotChild:
    def __init__(self, key: str, value: Any):
        self._key = key
        self._value = value

    def key(self) -> str:
        return self._key

    def val(self) -> Any:
        return self._value


class _SnapshotCompat:
    """Pyrebase-like snapshot wrapper providing .val() and .each()."""

    def __init__(self, value: Any):
        self._value = value

    def val(self) -> Any:
        return self._value

    def each(self) -> List[_SnapshotChild] | None:
        if isinstance(self._value, dict):
            return [_SnapshotChild(k, v) for k, v in self._value.items()]
        return None


class FirebaseDBAdapter:
    """Adapter to mimic Pyrebase's chained .child().get().set() API on top of firebase_admin."""

    def __init__(self, path: str = "/"):
        self._path = path if path.startswith("/") else f"/{path}"

    def child(self, *path_parts: str) -> "FirebaseDBAdapter":
        path = self._path.rstrip("/")
        for part in path_parts:
            part = str(part).strip("/")
            if not part:
                continue
            path = f"{path}/{part}"
        return FirebaseDBAdapter(path)

    def _ref(self):
        return admin_db.reference(self._path)

    def set(self, data: Any) -> None:
        return self._ref().set(data)

    def get(self) -> _SnapshotCompat:
        value = self._ref().get()
        return _SnapshotCompat(value)

    def push(self, data: Any):
        ref = self._ref().push(data)
        return ref

    def update(self, data: Dict[str, Any]) -> None:
        return self._ref().update(data)

    def remove(self) -> None:
        return self._ref().delete()


class RestDBAdapter:
    """Pyrebase-like adapter using Firebase Realtime Database REST API with idToken."""

    def __init__(
        self,
        database_url: str,
        id_token: str,
        refresh_token: Optional[str],
        api_key: str,
        path: str = "/",
        *,
        _shared: Optional[dict] = None,
        _session: Optional[Session] = None,
        _start_refresher: bool = True,
        _is_child: bool = False,
    ):
        self._database_url = database_url.rstrip("/")
        self._api_key = api_key
        self._path = path if path.startswith("/") else f"/{path}"
        self._is_child = _is_child

        if _shared is None:
            self._shared = {
                "lock": threading.RLock(),
                "id_token": id_token,
                "refresh_token": refresh_token,
                "refresher_started": False,
            }
        else:
            self._shared = _shared

        if _session is None:
            sess = Session()
            sess.headers.update({
                'User-Agent': 'tg-ytdlp-bot/1.0',
                'Connection': 'close'
            })
            adapter = HTTPAdapter(
                pool_connections=3,
                pool_maxsize=5,
                max_retries=2,
                pool_block=False,
            )
            sess.mount('http://', adapter)
            sess.mount('https://', adapter)
            self._session = sess
        else:
            self._session = _session

        if _start_refresher and self._shared.get("refresh_token"):
            with self._shared["lock"]:
                if not self._shared["refresher_started"]:
                    thread = threading.Thread(target=self._token_refresher, daemon=True)
                    thread.start()
                    self._shared["refresher_started"] = True

    def _token_refresher(self):
        while True:
            time.sleep(3000)
            try:
                url = f"https://securetoken.googleapis.com/v1/token?key={self._api_key}"
                with self._shared["lock"]:
                    refresh_token = self._shared.get("refresh_token")
                resp = self._session.post(url, data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                }, timeout=30)
                resp.raise_for_status()
                data = resp.json()
                with self._shared["lock"]:
                    self._shared["id_token"] = data.get("id_token", self._shared.get("id_token"))
                    self._shared["refresh_token"] = data.get("refresh_token", self._shared.get("refresh_token"))
                messages = get_messages_instance()
                logger.info(messages.DB_REST_ID_TOKEN_REFRESHED_MSG)
            except Exception as e:
                messages = get_messages_instance()
                logger.error(messages.DB_REST_TOKEN_REFRESH_ERROR_MSG.format(error=e))

    def _auth_params(self) -> Dict[str, str]:
        with self._shared["lock"]:
            token = self._shared.get("id_token")
        return {"auth": token}

    def child(self, *path_parts: str) -> "RestDBAdapter":
        path = self._path.rstrip("/")
        for part in path_parts:
            part = str(part).strip("/")
            if not part:
                continue
            path = f"{path}/{part}"
        return RestDBAdapter(
            self._database_url,
            self._shared.get("id_token"),
            self._shared.get("refresh_token"),
            self._api_key,
            path,
            _shared=self._shared,
            _session=self._session,
            _start_refresher=False,
            _is_child=True,
        )

    def _url(self) -> str:
        return f"{self._database_url}{self._path}.json"

    def set(self, data: Any) -> None:
        r = self._session.put(self._url(), params=self._auth_params(), json=data, timeout=60)
        r.raise_for_status()

    def update(self, data: Dict[str, Any]) -> None:
        r = self._session.patch(self._url(), params=self._auth_params(), json=data, timeout=60)
        r.raise_for_status()

    def remove(self) -> None:
        r = self._session.delete(self._url(), params=self._auth_params(), timeout=60)
        r.raise_for_status()

    def push(self, data: Any):
        parent_url = f"{self._database_url}{self._path}.json"
        r = self._session.post(parent_url, params=self._auth_params(), json=data, timeout=60)
        r.raise_for_status()
        return r.json()

    def get(self) -> _SnapshotCompat:
        r = self._session.get(self._url(), params=self._auth_params(), timeout=60)
        r.raise_for_status()
        return _SnapshotCompat(r.json())

    def close(self):
        if self._is_child:
            return
        try:
            if hasattr(self, '_session') and self._session:
                for adapter in self._session.adapters.values():
                    if hasattr(adapter, 'poolmanager'):
                        pool = adapter.poolmanager
                        if hasattr(pool, 'clear'):
                            pool.clear()
                self._session.close()
        except Exception as e:
            logger.error(f"RestDBAdapter failed to close session: {e}")


class DB:
    def __init__(self, user_or_chat_id: int):
        self.user_or_chat_id = user_or_chat_id
        self.db = None
        self.use_rest_api = False

        if not _init_firebase_admin_if_needed():
            self.use_rest_api = True
            logger.warning("Firebase Admin SDK not initialized, falling back to REST API")
            if not all([Config.FIREBASE_ID_TOKEN, Config.FIREBASE_API_KEY]):
                messages = get_messages_instance()
                raise RuntimeError(messages.DB_REST_API_CREDENTIALS_MISSING_MSG)
            self.db = RestDBAdapter(
                _get_database_url(),
                Config.FIREBASE_ID_TOKEN,
                Config.FIREBASE_REFRESH_TOKEN,
                Config.FIREBASE_API_KEY,
            )
        else:
            self.db = FirebaseDBAdapter()

    def child(self, *path: str):
        return self.db.child(*path)

    def get_user_or_chat_data(self):
        return self.db.child(self.user_or_chat_id).get()

    def set_user_or_chat_data(self, data):
        return self.db.child(self.user_or_chat_id).set(data)

    def close(self):
        if hasattr(self.db, 'close'):
            self.db.close()


# Initialize global db instance for backward compatibility
try:
    if _init_firebase_admin_if_needed():
        db = FirebaseDBAdapter()
        logger.info("✅ Global 'db' instance initialized with Firebase Admin SDK")
    else:
        if not all([
            hasattr(Config, 'FIREBASE_ID_TOKEN') and Config.FIREBASE_ID_TOKEN,
            hasattr(Config, 'FIREBASE_API_KEY') and Config.FIREBASE_API_KEY
        ]):
            logger.warning("⚠️ Firebase REST credentials missing, 'db' will be None")
            db = None
        else:
            db = RestDBAdapter(
                _get_database_url(),
                Config.FIREBASE_ID_TOKEN,
                getattr(Config, 'FIREBASE_REFRESH_TOKEN', None),
                Config.FIREBASE_API_KEY,
            )
            logger.info("✅ Global 'db' instance initialized with REST API fallback")
except Exception as e:
    logger.error(f"❌ Failed to initialize global 'db' instance: {e}")
    db = None
