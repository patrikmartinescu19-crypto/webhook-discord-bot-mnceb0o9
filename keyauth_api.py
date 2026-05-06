"""
KeyAuth API wrapper for the Undetected PC Tweaks application.
Handles initialization, login, register, and license key validation.
"""
import hashlib
import json
import time
import uuid

import requests


class KeyAuth:
    """KeyAuth API client for application authentication."""

    API_URL = "https://keyauth.win/api/1.2/"

    def __init__(self, name: str, owner_id: str, secret: str, version: str):
        self.name = name
        self.owner_id = owner_id
        self.secret = secret
        self.version = version
        self.session_id = ""
        self.initialized = False
        self.user_data = {}
        self.response_message = ""
        self.hwid = self._get_hwid()

    @staticmethod
    def _get_hwid() -> str:
        """Generate a hardware ID from the machine UUID."""
        try:
            with open("/etc/machine-id", "r") as f:
                machine_id = f.read().strip()
        except FileNotFoundError:
            machine_id = str(uuid.getnode())
        return hashlib.sha256(machine_id.encode()).hexdigest()[:32]

    def _make_request(self, params: dict) -> dict:
        """Send a request to the KeyAuth API."""
        try:
            resp = requests.post(self.API_URL, data=params, timeout=15)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            return {"success": False, "message": f"Connection error: {e}"}
        except json.JSONDecodeError:
            return {"success": False, "message": "Invalid server response"}

    def initialize(self) -> bool:
        """Initialize a session with KeyAuth."""
        params = {
            "type": "init",
            "ver": self.version,
            "name": self.name,
            "ownerid": self.owner_id,
        }
        data = self._make_request(params)
        if data.get("success"):
            self.session_id = data.get("sessionid", "")
            self.initialized = True
            self.response_message = "Initialized successfully"
            return True
        self.response_message = data.get("message", "Initialization failed")
        return False

    def login(self, username: str, password: str) -> bool:
        """Log in with username and password."""
        if not self.initialized:
            self.response_message = "Not initialized"
            return False
        params = {
            "type": "login",
            "username": username,
            "pass": password,
            "sessionid": self.session_id,
            "name": self.name,
            "ownerid": self.owner_id,
            "hwid": self.hwid,
        }
        data = self._make_request(params)
        if data.get("success"):
            self.user_data = data.get("info", {})
            self.response_message = "Login successful"
            return True
        self.response_message = data.get("message", "Login failed")
        return False

    def register(self, username: str, password: str, license_key: str) -> bool:
        """Register a new account with a license key."""
        if not self.initialized:
            self.response_message = "Not initialized"
            return False
        params = {
            "type": "register",
            "username": username,
            "pass": password,
            "key": license_key,
            "sessionid": self.session_id,
            "name": self.name,
            "ownerid": self.owner_id,
            "hwid": self.hwid,
        }
        data = self._make_request(params)
        if data.get("success"):
            self.user_data = data.get("info", {})
            self.response_message = "Registration successful"
            return True
        self.response_message = data.get("message", "Registration failed")
        return False

    def license_only(self, license_key: str) -> bool:
        """Authenticate with just a license key."""
        if not self.initialized:
            self.response_message = "Not initialized"
            return False
        params = {
            "type": "license",
            "key": license_key,
            "sessionid": self.session_id,
            "name": self.name,
            "ownerid": self.owner_id,
            "hwid": self.hwid,
        }
        data = self._make_request(params)
        if data.get("success"):
            self.user_data = data.get("info", {})
            self.response_message = "License activated"
            return True
        self.response_message = data.get("message", "License validation failed")
        return False

    def get_subscription_info(self) -> str:
        """Get formatted subscription info."""
        if not self.user_data:
            return "No active session"
        username = self.user_data.get("username", "N/A")
        subs = self.user_data.get("subscriptions", [])
        if subs:
            sub = subs[0]
            expiry = sub.get("expiry", "N/A")
            try:
                exp_time = time.strftime("%Y-%m-%d %H:%M", time.localtime(int(expiry)))
            except (ValueError, TypeError):
                exp_time = expiry
            return f"User: {username} | Expires: {exp_time}"
        return f"User: {username} | No subscription"
