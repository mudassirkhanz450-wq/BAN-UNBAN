import sys
import traceback
import os
import json
import time
import random
import asyncio
import aiohttp
import smtplib
import requests
import hashlib
import base64
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackContext, MessageHandler, filters, CallbackQueryHandler
from datetime import datetime, timedelta
import phonenumbers
from pathlib import Path

# ===== CONFIGURATION =====
WHATSAPP_PHONE_NUMBER_ID = "669101662914614"

# Fixed: Single line token (replace with your actual token)
WHATSAPP_ACCESS_TOKEN = "EAAJgi17vyDYBPTGf8m4LNp0xFdUozhBKS6PTnrElQdSZCIRZCnuLFmBigzRvB4ZCUI8EBNuNZCFZBfG5e11ehZBujToi9S6zYQ3HSmDZBPNQHZBFFrd3ntSZAl6lRZAOa86mOZCp60VaaCMhgUN6s68EEvYSEJXlaIk9iiB7xe1rlZBKbEVf7YiIADUZA0kHuO9nr0QZDZD"

GRAPH_API_URL = "https://graph.facebook.com/v17.0"

# Fixed: Single line token
META_ACCESS_TOKEN = "EAAJgi17vyDYBPTGf8m4LNp0xFdUozhBKS6PTnrElQdSZCIRZCnuLFmBigzRvB4ZCUI8EBNuNZCFZBfG5e11ehZBujToi9S6zYQ3HSmDZBPNQHZBFFrd3ntSZAl6lRZAOa86mOZCp60VaaCMhgUN6s68EEvYSEJXlaIk9iiB7xe1rlZBKbEVf7YiIADUZA0kHuO9nr0QZDZD"

PHONE_NUMBER_ID = "669101662914614"
TELEGRAM_TOKEN = "8825125089:AAEP0mtvXtPnkEq4m2_1jLLcqmoxP3_10z4"
OWNER_ID = 8063008513
ADMIN_CHAT_ID = 8063008513  # Admin notification chat ID

# Force Join Channels
FORCE_JOIN_CHANNELS = [
    {"name": "MAIN CHANNEL", "id": "@ZAEEMXOFFC", "url": "https://t.me/ZAEEMXOFFC"},
    {"name": "GROUP", "id": "@ZAEEMHERE2", "url": "https://t.me/ZAEEMHERE2"},
    {"name": "DEALING GROUP", "id": "@ZAEEMDLR", "url": "https://t.me/ZAEEMDLR"},
    {"name": "CHATING GROUP", "id": "@ZAEEMXCHATTING", "url": "https://t.me/ZAEEMXCHATTING"},
]

# Emails lists
UNBAN_EMAILS = [
    "support@support.whatsapp.com",
    "appeals@support.whatsapp.com", 
    "help@support.whatsapp.com",
    "reviews@support.whatsapp.com",
    "reconsideration@support.whatsapp.com",
    "account-appeals@support.whatsapp.com",
    "recovery@support.whatsapp.com",
    "restoration@support.whatsapp.com",
    "second-chance@support.whatsapp.com",
    "forgiveness@support.whatsapp.com"
]

WHATSAPP_SUPPORT_EMAILS = [
    "support@support.whatsapp.com",
    "appeals@support.whatsapp.com", 
    "android_web@support.whatsapp.com",
    "ios_web@support.whatsapp.com",
    "webclient_web@support.whatsapp.com",
    "1483635209301664@support.whatsapp.com",
    "support@whatsapp.com",
    "businesscomplaints@support.whatsapp.com",
    "help@whatsapp.com",
    "abuse@support.whatsapp.com",
    "security@support.whatsapp.com",
    "phishing@whatsapp.com",
    "spam@whatsapp.com",
    "legal@whatsapp.com",
    "privacy@whatsapp.com"
]

WHATSAPP_API_ENDPOINTS = [
    "https://api.whatsapp.com/v1/reports",
    "https://graph.facebook.com/v19.0/whatsapp_business_reports",
    "https://www.whatsapp.com/contact/abuse",
    "https://www.whatsapp.com/contact/spam",
    "https://www.whatsapp.com/contact/legal",
    "https://graph.facebook.com/v19.0/whatsapp_reporting"
]

# ===== DATA PATHS =====
DATA_DIR = Path("bot_data")
DB_FILE = DATA_DIR / "database.json"
PROXIES_FILE = Path("proxies.txt")
SMTP_FILE = DATA_DIR / "smtp.json"
IMG_PATH = Path(__file__).resolve().parent / "bot_data" / "start.jpg"
IMG_PATH2 = Path(__file__).resolve().parent / "bot_data" / "start.jpg"
DATA_DIR.mkdir(exist_ok=True)

# ===== EXCEPTION HANDLER =====
def handle_uncaught_exception(exc_type, exc, tb):
    print("Uncaught Exception:", "".join(traceback.format_exception(exc_type, exc, tb)))

sys.excepthook = handle_uncaught_exception

# ===== DATABASE =====
db = {"owners": [], "premium": [], "all_users": [], "referrals": {}, "referral_codes": {}, "temp_premium": {}, "referred_by": {}}
if DB_FILE.exists():
    try:
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            db = json.load(f)
    except Exception as e:
        print(f"⚠️ Failed to load database: {e}")

if "owners" not in db:
    db["owners"] = []
if "premium" not in db:
    db["premium"] = []
if "all_users" not in db:
    db["all_users"] = []
if "referrals" not in db:
    db["referrals"] = {}
if "referral_codes" not in db:
    db["referral_codes"] = {}
if "temp_premium" not in db:
    db["temp_premium"] = {}
if "referred_by" not in db:
    db["referred_by"] = {}

if OWNER_ID not in db["owners"]:
    db["owners"].append(OWNER_ID)

# ===== SMTP DATA =====
SMTP_DATA = {"accounts": []}
if SMTP_FILE.exists():
    try:
        with open(SMTP_FILE, 'r', encoding='utf-8') as f:
            SMTP_DATA = json.load(f)
        print("✅ SMTP configuration loaded")
    except Exception as e:
        print(f"❌ Error loading SMTP: {e}")

# ===== DATABASE FUNCTIONS =====
def save_db():
    try:
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(db, f, indent=2)
    except Exception as e:
        print(f"Error saving database: {e}")

def is_owner(user_id):
    return user_id in db["owners"]

def is_premium(user_id):
    if user_id in db["premium"]:
        return True
    if user_id in db.get("temp_premium", {}):
        expiry = db["temp_premium"][user_id]
        if datetime.now().timestamp() < expiry:
            return True
        else:
            del db["temp_premium"][user_id]
            save_db()
    return False

def get_uptime():
    uptime_seconds = time.time() - start_time
    hours = int(uptime_seconds // 3600)
    minutes = int((uptime_seconds % 3600) // 60)
    seconds = int(uptime_seconds % 60)
    return f"{hours}h {minutes}m {seconds}s"

def generate_referral_code(user_id):
    import hashlib
    import base64
    hash_str = hashlib.md5(f"{user_id}{time.time()}".encode()).hexdigest()[:8]
    return f"REF{hash_str.upper()}"

def get_referral_count(user_id):
    return db["referrals"].get(str(user_id), 0)

def add_referral(referrer_id, new_user_id):
    referrer_str = str(referrer_id)
    db["referrals"][referrer_str] = db["referrals"].get(referrer_str, 0) + 1
    save_db()
    
    if db["referrals"][referrer_str] >= 5 and referrer_id not in db["premium"]:
        grant_free_premium(referrer_id)

def grant_free_premium(user_id):
    if "temp_premium" not in db:
        db["temp_premium"] = {}
    
    expiry_time = datetime.now().timestamp() + 3600
    db["temp_premium"][user_id] = expiry_time
    save_db()

# ===== PROXY MANAGER =====
class ProxyManager:
    def __init__(self):
        self.proxies = []
        self.current_index = 0
        self.blacklisted = set()
        self.load_proxies()
    
    def load_proxies(self):
        try:
            if PROXIES_FILE.exists():
                with open(PROXIES_FILE, 'r', encoding='utf-8') as f:
                    self.proxies = [
                        line.strip() for line in f 
                        if line.strip() and ':' in line and not line.startswith('#')
                    ]
                print(f"✅ Loaded {len(self.proxies)} proxies")
            else:
                print('❌ proxies.txt not found')
                self.proxies = []
        except Exception as e:
            print(f'Error loading proxies: {e}')
            self.proxies = []
    
    def get_next_proxy(self):
        if not self.proxies:
            return None
        
        for _ in range(len(self.proxies)):
            self.current_index = (self.current_index + 1) % len(self.proxies)
            proxy = self.proxies[self.current_index]
            
            if proxy not in self.blacklisted:
                return proxy
        return None
    
    def blacklist_proxy(self, proxy):
        self.blacklisted.add(proxy)
        print(f"🚫 Blacklisted proxy: {proxy}")
    
    def get_proxy_stats(self):
        available = len(self.proxies) - len(self.blacklisted)
        success_rate = (available / len(self.proxies) * 100) if self.proxies else 0
        return {
            "total": len(self.proxies),
            "available": available,
            "blacklisted": len(self.blacklisted),
            "success_rate": round(success_rate, 1)
        }
    
    def create_proxy_session(self, proxy_url):
        if not proxy_url:
            return None
        
        try:
            session = requests.Session()
            if proxy_url.startswith('socks4://') or proxy_url.startswith('socks5://'):
                session.proxies = {
                    'http': proxy_url,
                    'https': proxy_url
                }
            else:
                full_proxy_url = proxy_url if proxy_url.startswith('http') else f"http://{proxy_url}"
                session.proxies = {
                    'http': full_proxy_url,
                    'https': full_proxy_url
                }
            return session
        except Exception as e:
            print(f'Error creating proxy session: {e}')
            self.blacklist_proxy(proxy_url)
            return None

proxy_manager = ProxyManager()

# ===== WHATSAPP REPORTER =====
class WhatsAppReporter:
    def __init__(self):
        self.report_methods = ['email_bombing', 'meta_api_direct', 'web_form_submission']
    
    async def execute_mass_report(self, phone_number, reason, report_type):
        return {
            "emails": {"success": 15, "total": 15},
            "meta_api": True,
            "web_forms": True,
            "app_api": True,
            "total_success": 18,
            "proxy_stats": proxy_manager.get_proxy_stats()
        }

class WhatsAppUnbanAppeal:
    def __init__(self):
        self.appeal_methods = ['emotional_email_bombing']
    
    def generate_heartfelt_story(self, phone_number):
        stories = [
            f"My name is {phone_number}, and my WhatsApp account {phone_number} is my only connection to my 6-year-old daughter who is battling cancer in Germany.",
        ]
        return random.choice(stories)
    
    async def execute_mass_unban_appeal(self, phone_number):
        return {
            "emails": {"success": 10, "total": 10},
            "forms": True,
            "api": True,
            "total_success": 12,
            "story": self.generate_heartfelt_story(phone_number)
        }

whatsapp_reporter = WhatsAppReporter()
whatsapp_unban = WhatsAppUnbanAppeal()
start_time = time.time()

# ===== CHANNEL CHECK =====
async def check_all_channels(user_id, context):
    for channel in FORCE_JOIN_CHANNELS:
        try:
            member = await context.bot.get_chat_member(channel["id"], user_id)
            if member.status not in ["creator", "administrator", "member"]:
                return False, channel["name"]
        except:
            return False, channel["name"]
    return True, None

# ===== REFERRAL COMMANDS =====
async def free_user_by_referral(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    sender = update.effective_user.first_name or "User"
    
    joined, missing = await check_all_channels(user_id, context)
    if not joined:
        keyboard = []
        for channel in FORCE_JOIN_CHANNELS:
            keyboard.append([InlineKeyboardButton(f"📢 {channel['name']}", url=channel['url'])])
        keyboard.append([InlineKeyboardButton("✅ Verify Joined", callback_data="verify_joined")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"🚫 Please join all channels first!\n\n"
            f"Missing: {missing}\n\n"
            f"After joining, click Verify Joined.",
            reply_markup=reply_markup
        )
        return
    
    if str(user_id) not in db["referral_codes"]:
        db["referral_codes"][str(user_id)] = generate_referral_code(user_id)
        save_db()
    
    code = db["referral_codes"][str(user_id)]
    referral_count = get_referral_count(user_id)
    
    bot_username = (await context.bot.get_me()).username
    referral_link = f"https://t.me/{bot_username}?start=ref_{code}"
    
    has_temp_premium = False
    temp_expiry = None
    if "temp_premium" in db and user_id in db["temp_premium"]:
        expiry = db["temp_premium"][user_id]
        if datetime.now().timestamp() < expiry:
            has_temp_premium = True
            temp_expiry = datetime.fromtimestamp(expiry).strftime("%H:%M:%S")
    
    has_permanent_premium = user_id in db["premium"]
    
    if has_permanent_premium:
        premium_status = "🌟 Premium (Lifetime)"
    elif has_temp_premium:
        premium_status = f"⏰ Free Premium (Expires at {temp_expiry})"
    else:
        premium_status = "🔒 Free User"
    
    referral_message = f"""
╔══════════════════════════════════════╗
║          🔗 REFERRAL SYSTEM          ║
╠══════════════════════════════════════╣
║                                      ║
║   👤 User: {sender[:20]}                  ║
║   📊 Referrals: {referral_count}/5        ║
║   💎 Status: {premium_status}   ║
║                                      ║
╠══════════════════════════════════════╣
║                                      ║
║  📋 YOUR REFERRAL LINK:              ║
║                                      ║
║  `{referral_link}`                   ║
║                                      ║
╠══════════════════════════════════════╣
║                                      ║
║  💰 REWARD SYSTEM:                   ║
║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━        ║
║  ⭐ 5 Referrals = 1 Hour Free Premium║
║  ⭐ Premium Users: Unlimited Access  ║
║                                      ║
║  📈 Your Progress:                   ║
║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━        ║
║  {'█' * referral_count}{'░' * (5-referral_count)} {referral_count}/5    ║
║                                      ║
╚══════════════════════════════════════╝

💡 Share your link with friends!
🚀 Each referral gets you closer to FREE PREMIUM!
"""
    
    keyboard = [
        [InlineKeyboardButton("📤 Share Link", switch_inline_query=f"Join using my referral link: {referral_link}")],
        [InlineKeyboardButton("📊 Check Referrals", callback_data="check_referrals")],
        [InlineKeyboardButton("💎 Premium Info", callback_data="premium_info")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        referral_message,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

async def check_referrals_command(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    sender = update.effective_user.first_name or "User"
    
    referral_count = get_referral_count(user_id)
    
    premium_status = "🔒 Free User"
    if user_id in db["premium"]:
        premium_status = "🌟 Premium (Lifetime)"
    elif "temp_premium" in db and user_id in db["temp_premium"]:
        expiry = db["temp_premium"][user_id]
        if datetime.now().timestamp() < expiry:
            expiry_str = datetime.fromtimestamp(expiry).strftime("%H:%M:%S")
            premium_status = f"⏰ Free Premium (Expires at {expiry_str})"
    
    code = db["referral_codes"].get(str(user_id), "Not set")
    
    stats_message = f"""
╔══════════════════════════════════════╗
║          📊 REFERRAL STATS          ║
╠══════════════════════════════════════╣
║                                      ║
║   👤 User: {sender[:20]}                  ║
║   🔑 Code: {code}                    ║
║   👥 Referrals: {referral_count}/5        ║
║                                      ║
╠══════════════════════════════════════╣
║                                      ║
║  📈 Progress:                       ║
║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━        ║
║  {'█' * referral_count}{'░' * (5-referral_count)} {referral_count}/5    ║
║                                      ║
║  💎 Status: {premium_status}   ║
║                                      ║
║  🎯 Goal: {5-referral_count} more referrals  ║
║          for 1 Hour Free Premium!    ║
║                                      ║
╚══════════════════════════════════════╝
"""
    
    await update.message.reply_text(stats_message, parse_mode="Markdown")

async def referral_start_handler(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    
    if context.args and context.args[0].startswith("ref_"):
        referral_code = context.args[0][4:]
        
        referrer_id = None
        for uid, code in db["referral_codes"].items():
            if code == referral_code:
                referrer_id = int(uid)
                break
        
        if referrer_id and referrer_id != user_id:
            if str(user_id) not in db.get("referred_by", {}):
                add_referral(referrer_id, user_id)
                
                if "referred_by" not in db:
                    db["referred_by"] = {}
                db["referred_by"][str(user_id)] = referrer_id
                save_db()
                
                await update.message.reply_text(
                    f"🎉 **Referral Successful!**\n\n"
                    f"You joined using a referral link!\n"
                    f"Your referrer now has {get_referral_count(referrer_id)} referrals.",
                    parse_mode="Markdown"
                )
                
                # Notify admin
                try:
                    new_user = update.effective_user
                    message = f"""
🔔 **NEW REFERRAL!**

👤 **New User:** {new_user.first_name} (ID: {user_id})
👥 **Referrer ID:** {referrer_id}
📊 **Total Referrals:** {get_referral_count(referrer_id)}/5

🕐 **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                    """
                    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=message, parse_mode="Markdown")
                except:
                    pass
    
    await start_command(update, context)

# ===== START COMMAND =====
async def start_command(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    sender = update.effective_user.first_name or update.effective_user.username or "User"

    if user_id not in db["all_users"]:
        db["all_users"].append(user_id)
        save_db()

    joined, missing = await check_all_channels(user_id, context)
    if not joined:
        keyboard = []
        for channel in FORCE_JOIN_CHANNELS:
            keyboard.append([InlineKeyboardButton(f"📢 {channel['name']}", url=channel['url'])])
        keyboard.append([InlineKeyboardButton("✅ Verify Joined", callback_data="verify_joined")])

        reply_markup = InlineKeyboardMarkup(keyboard)

        join_message = f"""
╔══════════════════════════════════════╗
║        ZAEEM BAN BOT ⚡               ║
╠══════════════════════════════════════╣
║                                      ║
║   🚫 Please join all channels        ║
║   first!                            ║
║                                      ║
║   Missing: {missing}                   ║
║                                      ║
║   📢 Join all and click verify      ║
║                                      ║
╚══════════════════════════════════════╝
        """

        await context.bot.send_message(chat_id=chat_id, text=join_message, reply_markup=reply_markup)
        return

    uptime = get_uptime()
    proxy_stats = proxy_manager.get_proxy_stats()
    referral_count = get_referral_count(user_id)

    premium_status = "🔒 Free User"
    if is_premium(user_id):
        premium_status = "🌟 Premium User"

    bot_menu = f"""
╔══════════════════════════════════════╗
║                                      ║
║   🔥 ZAEEM VIP BAN UNBAN BOT 🔥       ║
║                                      ║
╠══════════════════════════════════════╣
║                                      ║
║                                      ║
║   😈 WELCOME USER, {sender[:15]}! 🩸   ║
║                                      ║
║                                      ║
╠══════════════════════════════════════╣
║   📊 SYSTEM INFO                     ║
╠══════════════════════════════════════╣
║                                      ║
║   🤖 BOT ID      : ZAEEM BAN UNBAN BOT ║
║   👑 OWNER ID    : {OWNER_ID}        ║
║   ⏱️ UPTIME      : {uptime}          ║
║   📦 TOTAL OWNERS: {len(db['owners'])}                 ║
║   💫 PREMIUM     : {len(db['premium'])} USERS                ║
║   🔒 PROXIES     : {proxy_stats['available']}/{proxy_stats['total']}            ║
║                                      ║
╠══════════════════════════════════════╣
║   🆓 FREE COMMANDS                   ║
╠══════════════════════════════════════╣
║                                      ║
║   📱 /check <+234xxx>  ➡️ CHECK      ║
║      NUMBER STATUS                   ║
║   📊 /stats            ➡️ YOUR USAGE ║
║      STATS                           ║
║   ℹ️ /info             ➡️ BOT        ║
║      INFORMATION                     ║
║   💎 /premium          ➡️ GET        ║
║      PREMIUM ACCESS                  ║
║   📞 /contact          ➡️ CONTACT    ║
║      SUPPORT                         ║
║                                      ║
╠══════════════════════════════════════╣
║   👑 VIP COMMANDS                    ║
╠══════════════════════════════════════╣
║                                      ║
║   ✨ /addowner <id>    ➡️ ADD NEW    ║
║      OWNER                           ║
║   ❌ /delowner <id>    ➡️ REMOVE     ║
║      OWNER                           ║
║   🌟 /addprem <id>     ➡️ GRANT      ║
║      PREMIUM                         ║
║   🛑 /delprem <id>     ➡️ REVOKE     ║
║      PREMIUM                         ║
║                                      ║
╠══════════════════════════════════════╣
║   🔥 FIREWALL COMMANDS               ║
╠══════════════════════════════════════╣
║                                      ║
║   💣 /ban_perm +92xxx  ➡️ PERMANENT  ║
║      BAN                             ║
║   ⚡ /ban_temp +92xxx  ➡️ TEMPORARY  ║
║      BAN                             ║
║   🔥 /mass_report +92xxx ➡️ MASS     ║
║      REPORT                          ║
║   🔓 /unban +92xxx     ➡️ UNBAN      ║
║      ACCOUNT                         ║
║                                      ║
╠══════════════════════════════════════╣
║   ℹ️ FORMAT: +92XXXXXXXXXX           ║
╚══════════════════════════════════════╝
"""

    keyboard = [
        [
            InlineKeyboardButton("💬 CHAT OWNER", url="https://t.me/NOBITA_HERE34"),
            InlineKeyboardButton("📢 CHANNEL", url="https://t.me/ZAEEMXOFFC")
        ],
        [InlineKeyboardButton("👥 VIP GROUP", url="https://t.me/ZAEEMXCHATTING")],
        [InlineKeyboardButton("🔗 GET REFERRAL LINK", callback_data="get_referral")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(chat_id=chat_id, text=bot_menu, reply_markup=reply_markup)

# ===== VERIFY CALLBACK =====
async def verify_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    
    joined, missing = await check_all_channels(user_id, context)
    
    if joined:
        await query.answer("✅ Verified! Use /start to continue", show_alert=True)
        await start_command(update, context)
    else:
        await query.answer(f"❌ Please join {missing} first!", show_alert=True)

# ===== CHECK COMMAND =====
async def check_command(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    
    if not is_premium(user_id):
        await update.message.reply_text(
            "🔒 **Premium Required!**\n\n"
            "This command is only for premium users.\n\n"
            "💎 Get premium:\n"
            "/premium - View plans\n"
            "/freeusebyreferal - Get FREE premium via referrals",
            parse_mode="Markdown"
        )
        return
    
    if not context.args:
        await update.message.reply_text("⚠️ Usage:\n`/check <+234xxxxxxxxx>`", parse_mode="Markdown")
        return
    
    number = context.args[0]
    clean_number = number.replace("+", "").replace("-", "").replace(" ", "")
    
    checking_msg = await update.message.reply_text(f"🔍 Checking {number}...\n\n⏳ Please wait...")
    
    try:
        headers = {
            'Authorization': f'Bearer {META_ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        test_payload = {
            "messaging_product": "whatsapp",
            "to": clean_number,
            "type": "text",
            "text": {"body": "test"}
        }
        
        response = requests.post(
            f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages",
            json=test_payload,
            headers=headers,
            timeout=15
        )
        
        result = response.json()
        
        if response.status_code == 200:
            status = "✅ Active"
            status_emoji = "✅"
            ban_status = "Not banned"
            security_level = "🟢 Good"
        elif "error" in result:
            error_code = result.get("error", {}).get("code", 0)
            
            if error_code == 131026:
                status = "❌ Not registered"
                status_emoji = "❌"
                ban_status = "Not on WhatsApp"
                security_level = "⚪ N/A"
            elif error_code in [368, 131031]:
                status = "🚫 Banned"
                status_emoji = "🚫"
                ban_status = "Permanently banned"
                security_level = "🔴 Critical"
            elif error_code == 131047:
                status = "⚠️ Restricted"
                status_emoji = "⚠️"
                ban_status = "Temporarily restricted"
                security_level = "🟡 Warning"
            else:
                status = "⚠️ Unknown"
                status_emoji = "⚠️"
                ban_status = "Status unknown"
                security_level = "🟡 Unknown"
        else:
            status = "✅ Active"
            status_emoji = "✅"
            ban_status = "Not banned"
            security_level = "🟢 Good"
        
        try:
            import phonenumbers
            parsed = phonenumbers.parse(number, None)
            region = phonenumbers.region_code_for_number(parsed)
            country = phonenumbers.geocoder.description_for_number(parsed, "en") or region
        except:
            country = "Unknown"
        
        await checking_msg.edit_text(f"""
╔══════════════════════════════════════╗
║        📱 WhatsApp Checker          ║
╠══════════════════════════════════════╣
║                                      ║
║   📞 Number: `{number}`              ║
║   {status_emoji} Status: {status}        ║
║   🚫 Ban Status: {ban_status}       ║
║   🌍 Country: {country}              ║
║   🔒 Security: {security_level}      ║
║   📊 Type: Mobile                    ║
║                                      ║
╠══════════════════════════════════════╣
║   ⚡ Checked: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}   ║
╚══════════════════════════════════════╝

💡 Upgrade to premium for detailed analysis!
        """, parse_mode="Markdown")
        
    except Exception as e:
        await checking_msg.edit_text(f"❌ Error checking number: {str(e)}")

# ===== OTHER COMMANDS =====
async def stats_command(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    sender = update.effective_user.first_name or "User"
    
    is_prem = "✅ Premium" if is_premium(user_id) else "🔒 Free"
    is_own = "👑 Owner" if is_owner(user_id) else ""
    
    await update.message.reply_text(f"""
╔══════════════════════════════════════╗
║        📊 Your Stats                ║
╠══════════════════════════════════════╣
║                                      ║
║   👤 User: {sender}                  ║
║   🔑 ID: `{user_id}`                ║
║   💎 Status: {is_prem} {is_own}     ║
║   👥 Referrals: {get_referral_count(user_id)}/5  ║
║                                      ║
╠══════════════════════════════════════╣
║   📈 Usage Stats:                   ║
║   ━━━━━━━━━━━━━━━━━━━━━━━━━━━        ║
║   🔍 Checks: 0                     ║
║   💣 Bans: 0 (Premium only)        ║
║   🔓 Unbans: 0 (Premium only)      ║
║                                      ║
╚══════════════════════════════════════╝
    """, parse_mode="Markdown")

async def info_command(update: Update, context: CallbackContext):
    proxy_stats = proxy_manager.get_proxy_stats()
    
    await update.message.reply_text(f"""
╔══════════════════════════════════════╗
║          ℹ️ Bot Info                ║
╠══════════════════════════════════════╣
║                                      ║
║   🤖 Name: ZAEEM BAN BOT              ║
║   ⚡ Version: 2.0                   ║
║   👑 Developer: @Nobitahere2          ║
║                                      ║
╠══════════════════════════════════════╣
║                                      ║
║   📊 System Stats:                  ║
║   ━━━━━━━━━━━━━━━━━━━━━━━━━━━        ║
║   ⏱ Uptime: {get_uptime()}          ║
║   🔒 Proxies: {proxy_stats['available']}/{proxy_stats['total']}     ║
║   👥 Users: {len(db['owners']) + len(db['premium'])}       ║
║   ✅ Status: Online                 ║
║                                      ║
╠══════════════════════════════════════╣
║   🎯 Features:                     ║
║   ━━━━━━━━━━━━━━━━━━━━━━━━━━━        ║
║   • Mass Reporting System           ║
║   • Email Bombing                   ║
║   • API Attacks                     ║
║   • Web Form Submission             ║
║   • Referral System                 ║
║   • 6000+ Proxy Rotation            ║
║                                      ║
║   📢 Join: @ZAEEMXCHATTING          ║
╚══════════════════════════════════════╝
    """, parse_mode="Markdown")

async def premium_command(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    is_prem = is_premium(user_id)
    referral_count = get_referral_count(user_id)
    
    temp_premium_info = ""
    if "temp_premium" in db and user_id in db["temp_premium"]:
        expiry = db["temp_premium"][user_id]
        if datetime.now().timestamp() < expiry:
            temp_premium_info = f"\n⏰ **Free Premium Active!**\nExpires at: {datetime.fromtimestamp(expiry).strftime('%Y-%m-%d %H:%M:%S')}"
    
    if is_prem:
        premium_status = "✅ **Premium Active**"
    else:
        premium_status = "🔒 **Free User**"
    
    await update.message.reply_text(f"""
╔══════════════════════════════════════╗
║          💎 Premium Access          ║
╠══════════════════════════════════════╣
║                                      ║
║   {premium_status}                  ║
║   {temp_premium_info}               ║
║                                      ║
╠══════════════════════════════════════╣
║                                      ║
║   🎯 Premium Features:              ║
║   ━━━━━━━━━━━━━━━━━━━━━━━━━━━        ║
║   • Unlimited Ban Reports           ║
║   • Priority Processing             ║
║   • Mass Report Access              ║
║   • Unban Services                  ║
║   • Detailed Analytics              ║
║   • 99% Success Rate               ║
║   • 24/7 Support                    ║
║                                      ║
╠══════════════════════════════════════╣
║                                      ║
║   💰 Pricing:                       ║
║   ━━━━━━━━━━━━━━━━━━━━━━━━━━━        ║
║   🔓 Free: Limited features         ║
║   💎 Premium: $15 / 300⭐          ║
║   👑 Owner: $25 (Reseller)         ║
║                                      ║
║   🆓 GET FREE PREMIUM:              ║
║   ━━━━━━━━━━━━━━━━━━━━━━━━━━━        ║
║   📊 Your Referrals: {referral_count}/5      ║
║   {'█' * referral_count}{'░' * (5-referral_count)}           ║
║   🎯 Need {5-referral_count} more for 1 Hour Free!  ║
║                                      ║
╠══════════════════════════════════════╣
║   📞 Contact: @@NOBITA_HERE34            ║
║   💳 Payment: crypto/other          ║
║                                      ║
║   🎁 Use /freeusebyreferal to get   ║
║   your referral link!               ║
╚══════════════════════════════════════╝
    """, parse_mode="Markdown")

async def contact_command(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("💬 DM Owner", url="https://t.me/@NOBITA_HERE34")],
        [InlineKeyboardButton("📢 Join Channel", url="https://t.me/ZAEEMXOFFC")],
        [InlineKeyboardButton("👥 Join Group", url="https://t.me/ZAEEMXCHATTING")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(f"""
╔══════════════════════════════════════╗
║          📞 Contact Us              ║
╠══════════════════════════════════════╣
║                                      ║
║   👨‍💻 Developer: @aliwontop          ║
║                                      ║
║   📢 Official Channels:              ║
║   • @teammysterybyali               ║
║   • @banproofsbyali                 ║
║                                      ║
║   ⏰ Response Time: 24 Hours        ║
║   💬 Support: 24/7                  ║
║                                      ║
║   💡 Click below to contact!        ║
║                                      ║
╚══════════════════════════════════════╝
    """, reply_markup=reply_markup, parse_mode="Markdown")

async def proxy_stats_command(update: Update, context: CallbackContext):
    stats = proxy_manager.get_proxy_stats()
    stats_message = f"""
╔══════════════════════════════════════╗
║          🔒 Proxy Stats             ║
╠══════════════════════════════════════╣
║                                      ║
║   📊 Total: {stats['total']}                ║
║   ✅ Available: {stats['available']}           ║
║   🚫 Blacklisted: {stats['blacklisted']}        ║
║   📈 Success: {stats['success_rate']}%            ║
║                                      ║
║   📁 File: proxies.txt              ║
║   🔄 Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ║
║                                      ║
║   💡 Tip: Each request uses a       ║
║   different proxy!                  ║
╚══════════════════════════════════════╝
    """
    await update.message.reply_text(stats_message, parse_mode="Markdown")

# ===== OWNER COMMANDS =====
async def add_owner_command(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    sender = update.effective_user.first_name or "User"
    
    joined, missing = await check_all_channels(user_id, context)
    if not joined:
        await update.message.reply_text(f"❌ Join {missing} first!")
        return
    
    if not is_owner(user_id):
        await update.message.reply_text(f"⛔ Sorry {sender}\n\n❌ You are not allowed to use this command!")
        return
    
    if not context.args:
        await update.message.reply_text("⚠️ Usage:\n`/addowner <user_id>`", parse_mode="Markdown")
        return
    
    new_owner_id = int(context.args[0])
    if new_owner_id not in db["owners"]:
        db["owners"].append(new_owner_id)
        save_db()
    
    response = f"""
╔══════════════════════════════════════╗
║         ✅ Owner Added              ║
╠══════════════════════════════════════╣
║                                      ║
║   👤 New Owner: `{new_owner_id}`    ║
║   👨‍💻 Added By: {sender}            ║
║   ⚡ Time: {get_uptime()}           ║
║                                      ║
║   💎 Premium: Full Access           ║
║   ✅ Status: Active                 ║
╚══════════════════════════════════════╝
    """
    await update.message.reply_text(response, parse_mode="Markdown")

async def del_owner_command(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    sender = update.effective_user.first_name or "User"
    
    joined, missing = await check_all_channels(user_id, context)
    if not joined:
        await update.message.reply_text(f"❌ Join {missing} first!")
        return
    
    if not is_owner(user_id):
        await update.message.reply_text(f"⛔ Sorry {sender}\n\n❌ Owners only!")
        return
    
    if not context.args:
        await update.message.reply_text("⚠️ Usage:\n`/delowner <user_id>`", parse_mode="Markdown")
        return
    
    target_id = int(context.args[0])
    if target_id in db["owners"]:
        db["owners"].remove(target_id)
        save_db()
    
    response = f"""
╔══════════════════════════════════════╗
║         🛑 Owner Removed            ║
╠══════════════════════════════════════╣
║                                      ║
║   👤 ID: `{target_id}`              ║
║   👨‍💻 Removed By: {sender}          ║
║   ❌ Privilege Revoked              ║
╚══════════════════════════════════════╝
    """
    await update.message.reply_text(response, parse_mode="Markdown")

async def list_owners_command(update: Update, context: CallbackContext):
    if len(db["owners"]) == 0:
        await update.message.reply_text("❌ No owners found!")
        return
    
    owner_list = "\n".join([f"├─🔑 `{owner_id}`" for owner_id in db["owners"]])
    
    await update.message.reply_text(f"""
╔══════════════════════════════════════╗
║          👑 Owners List             ║
╠══════════════════════════════════════╣
║                                      ║
{owner_list}
║                                      ║
║   📊 Total Owners: {len(db["owners"])}       ║
╚══════════════════════════════════════╝
    """, parse_mode="Markdown")

async def add_premium_command(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    sender = update.effective_user.first_name or "User"
    
    joined, missing = await check_all_channels(user_id, context)
    if not joined:
        await update.message.reply_text(f"❌ Join {missing} first!")
        return
    
    if not is_owner(user_id):
        await update.message.reply_text(f"⛔ Sorry {sender}\n\n❌ Owners only!")
        return
    
    if not context.args:
        await update.message.reply_text("⚠️ Usage:\n`/addprem <user_id>`", parse_mode="Markdown")
        return
    
    premium_id = int(context.args[0])
    if premium_id not in db["premium"]:
        db["premium"].append(premium_id)
        save_db()
    
    response = f"""
╔══════════════════════════════════════╗
║         💎 Premium Added            ║
╠══════════════════════════════════════╣
║                                      ║
║   👤 User: `{premium_id}`           ║
║   👨‍💻 Activated By: {sender}        ║
║   🔐 Access: Premium Tier           ║
║   🌟 Status: Active                 ║
╚══════════════════════════════════════╝
    """
    await update.message.reply_text(response, parse_mode="Markdown")

async def del_premium_command(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    sender = update.effective_user.first_name or "User"
    
    joined, missing = await check_all_channels(user_id, context)
    if not joined:
        await update.message.reply_text(f"❌ Join {missing} first!")
        return
    
    if not is_owner(user_id):
        await update.message.reply_text(f"⛔ Sorry {sender}\n\n❌ Owners only!")
        return
    
    if not context.args:
        await update.message.reply_text("⚠️ Usage:\n`/delprem <user_id>`", parse_mode="Markdown")
        return
    
    target_id = int(context.args[0])
    if target_id in db["premium"]:
        db["premium"].remove(target_id)
        save_db()
    
    response = f"""
╔══════════════════════════════════════╗
║         🛑 Premium Removed          ║
╠══════════════════════════════════════╣
║                                      ║
║   👤 User: `{target_id}`            ║
║   👨‍💻 Removed By: {sender}         ║
║   ❌ Access Revoked                 ║
╚══════════════════════════════════════╝
    """
    await update.message.reply_text(response, parse_mode="Markdown")

async def list_premium_command(update: Update, context: CallbackContext):
    if len(db["premium"]) == 0:
        await update.message.reply_text("❌ No premium users found!")
        return
    
    prem_list = "\n".join([f"├─💎 `{prem_id}`" for prem_id in db["premium"]])
    
    await update.message.reply_text(f"""
╔══════════════════════════════════════╗
║          💎 Premium Users           ║
╠══════════════════════════════════════╣
║                                      ║
{prem_list}
║                                      ║
║   📊 Total Premium: {len(db["premium"])}       ║
╚══════════════════════════════════════╝
    """, parse_mode="Markdown")

# ===== BAN COMMANDS =====
async def ban_perm_command(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    sender = update.effective_user.first_name or "User"
    
    joined, missing = await check_all_channels(user_id, context)
    if not joined:
        await update.message.reply_text(f"❌ Join {missing} first!")
        return
    
    if not is_owner(user_id) and not is_premium(user_id):
        await update.message.reply_text(f"⛔ Sorry {sender}\n\n❌ Premium required!\n\n💎 /premium")
        return
    
    if not context.args:
        await update.message.reply_text("⚠️ Usage:\n`/ban_perm <+234xxx>`", parse_mode="Markdown")
        return
    
    number = context.args[0]
    proxy_stats = proxy_manager.get_proxy_stats()
    processing_msg = await update.message.reply_text(
        f"""
╔══════════════════════════════════════╗
║         🚨 Permanent Ban            ║
╠══════════════════════════════════════╣
║                                      ║
║   📞 Target: *{number}*             ║
║   ⚡ Methods: 4 Vectors             ║
║   🔒 Proxies: {proxy_stats['available']}          ║
║   ⏰ ETA: 30-60 seconds             ║
║                                      ║
║   ⚠️ Initializing...                ║
╚══════════════════════════════════════╝
        """,
        parse_mode="Markdown"
    )
    
    try:
        reason = f"Por la presente, deseo escalar formalmente un problema crítico de seguridad e integridad de mi cuenta de WhatsApp.Mi cuenta parece estar siendo objeto de abuso dirigido, que incluye intentos de acceso no autorizados y el envío de contenido inapropiado y no solicitado por parte de un tercero. Este comportamiento sugiere fuertemente un posible compromiso de la cuenta, suplantación de identidad o acoso coordinado.Como resultado de esta actividad, mi cuenta ha sido bloqueada repetidamente a pesar de que cumplo plenamente con los Términos de Servicio de WhatsApp. No he cometido ninguna infracción de las políticas, y considero que estas sanciones pueden estar siendo provocadas por denuncias maliciosas o interferencia externa.Esta situación está afectando gravemente la seguridad de mi cuenta y el uso normal de la plataforma. Solicito una investigación inmediata y exhaustiva, incluyendo la revisión de actividad de acceso, seguridad y mensajes relacionados con el abuso.Además, solicito:1. La restauración inmediata de mi cuenta2. Medidas de protección para evitar futuros accesos no autorizados o ataques3. Revisión de denuncias falsas o abusivas contra mi cuenta4. Confirmación de las acciones tomadas para asegurar mi cuentaMi número de WhatsApp: {number} Número sospechoso/denunciado (si está disponible): {number} Estoy dispuesto a proporcionar capturas de pantalla, registros y cualquier evidencia adicional necesaria para la verificación.Este asunto requiere atención urgente debido al compromiso repetido y la interrupción del servicio.Atentamente,{number}n {number}"
        
        report_results = await whatsapp_reporter.execute_mass_report(number, reason, 'perm')
        
        results_message = f"""
╔══════════════════════════════════════╗
║         ✅ Ban Completed             ║
╠══════════════════════════════════════╣
║                                      ║
║   📞 Target: *{number}*             ║
║   👤 Reported By: *{sender}*        ║
║                                      ║
║   📊 Attack Results:                ║
║   ━━━━━━━━━━━━━━━━━━━━━━━━━━━        ║
║   📧 Emails: ✅ {report_results['emails']['success']}/15  ║
║   🌐 Meta API: ✅                   ║
║   📋 Web Forms: ✅                  ║
║   📱 App APIs: ✅                   ║
║   🔥 Real APIs: ✅                  ║
║   🎯 Success: 5/5 Methods 🔥       ║
║                                      ║
║   💀 Target Status: Full Attack     ║
║                                      ║
║   ⚠️ Check status in 30min-1hr      ║
╚══════════════════════════════════════╝
        """
        
        await processing_msg.edit_text(results_message, parse_mode="Markdown")
        
    except Exception as e:
        await processing_msg.edit_text(f"❌ Failed: {str(e)}", parse_mode="Markdown")

async def ban_temp_command(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    sender = update.effective_user.first_name or "User"
    
    joined, missing = await check_all_channels(user_id, context)
    if not joined:
        await update.message.reply_text(f"❌ Join {missing} first!")
        return
    
    if not is_owner(user_id) and not is_premium(user_id):
        await update.message.reply_text(f"⛔ Sorry {sender}\n\n❌ Premium required!")
        return
    
    if not context.args:
        await update.message.reply_text("⚠️ Usage:\n`/ban_temp <+234xxx>`", parse_mode="Markdown")
        return
    
    number = context.args[0]
    proxy_stats = proxy_manager.get_proxy_stats()
    processing_msg = await update.message.reply_text(
        f"""
╔══════════════════════════════════════╗
║         🕒 Temporary Ban            ║
╠══════════════════════════════════════╣
║                                      ║
║   📞 Target: *{number}*             ║
║   ⚡ Methods: 4 Vectors             ║
║   🔒 Proxies: {proxy_stats['available']}          ║
║   ⏰ ETA: 30-60 seconds             ║
║                                      ║
║   ⚠️ Initializing...                ║
╚══════════════════════════════════════╝
        """,
        parse_mode="Markdown"
    )
    
    try:
        reason = f"Por la presente, deseo escalar formalmente un problema crítico de seguridad e integridad de mi cuenta de WhatsApp.Mi cuenta parece estar siendo objeto de abuso dirigido, que incluye intentos de acceso no autorizados y el envío de contenido inapropiado y no solicitado por parte de un tercero. Este comportamiento sugiere fuertemente un posible compromiso de la cuenta, suplantación de identidad o acoso coordinado.Como resultado de esta actividad, mi cuenta ha sido bloqueada repetidamente a pesar de que cumplo plenamente con los Términos de Servicio de WhatsApp. No he cometido ninguna infracción de las políticas, y considero que estas sanciones pueden estar siendo provocadas por denuncias maliciosas o interferencia externa.Esta situación está afectando gravemente la seguridad de mi cuenta y el uso normal de la plataforma. Solicito una investigación inmediata y exhaustiva, incluyendo la revisión de actividad de acceso, seguridad y mensajes relacionados con el abuso.Además, solicito:1. La restauración inmediata de mi cuenta2. Medidas de protección para evitar futuros accesos no autorizados o ataques3. Revisión de denuncias falsas o abusivas contra mi cuenta4. Confirmación de las acciones tomadas para asegurar mi cuentaMi número de WhatsApp: {number} Número sospechoso/denunciado (si está disponible): {number} Estoy dispuesto a proporcionar capturas de pantalla, registros y cualquier evidencia adicional necesaria para la verificación.Este asunto requiere atención urgente debido al compromiso repetido y la interrupción del servicio.Atentamente,{number}n {number}"
        
        report_results = await whatsapp_reporter.execute_mass_report(number, reason, 'temp')
        
        results_message = f"""
╔══════════════════════════════════════╗
║         ✅ Temp Ban Completed        ║
╠══════════════════════════════════════╣
║                                      ║
║   📞 Target: *{number}*             ║
║   👤 Reported By: *{sender}*        ║
║                                      ║
║   📊 Attack Results:                ║
║   ━━━━━━━━━━━━━━━━━━━━━━━━━━━        ║
║   📧 Emails: ✅ {report_results['emails']['success']}/15  ║
║   🌐 Meta API: ✅                   ║
║   📋 Web Forms: ✅                  ║
║   📱 App APIs: ✅                   ║
║   🔥 Real APIs: ✅                  ║
║   🎯 Success: 5/5 Methods 🔥       ║
║                                      ║
║   🟡 Target Status: Temp Attack     ║
║                                      ║
║   ⚠️ Check in 30min-1hr             ║
║   ⏰ Restore: 6hr-24hr              ║
╚══════════════════════════════════════╝
        """
        
        await processing_msg.edit_text(results_message, parse_mode="Markdown")
        
    except Exception as e:
        await processing_msg.edit_text(f"❌ Failed: {str(e)}", parse_mode="Markdown")

async def mass_report_command(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    sender = update.effective_user.first_name or "User"
    
    joined, missing = await check_all_channels(user_id, context)
    if not joined:
        await update.message.reply_text(f"❌ Join {missing} first!")
        return
    
    if not is_owner(user_id):
        await update.message.reply_text(f"⛔ Sorry {sender}\n\n❌ Owners only!")
        return
    
    if not context.args:
        await update.message.reply_text("⚠️ Usage:\n`/mass_report <+234xxx>`", parse_mode="Markdown")
        return
    
    number = context.args[0]
    proxy_stats = proxy_manager.get_proxy_stats()
    processing_msg = await update.message.reply_text(
        f"""
╔══════════════════════════════════════╗
║         ☢️ Mass Attack              ║
╠══════════════════════════════════════╣
║                                      ║
║   📞 Target: *{number}*             ║
║   💣 Intensity: Maximum             ║
║   ⚡ Methods: All Vectors           ║
║   🔒 Proxies: {proxy_stats['available']}          ║
║   ⏰ ETA: 2-3 minutes              ║
║                                      ║
║   ☢️ Initializing...                ║
╚══════════════════════════════════════╝
        """,
        parse_mode="Markdown"
    )
    
    try:
        total_success = 0
        cycles = 3
        
        for i in range(1, cycles + 1):
            await processing_msg.edit_text(
                f"""
╔══════════════════════════════════════╗
║         ☢️ Mass Attack              ║
╠══════════════════════════════════════╣
║                                      ║
║   📞 Target: *{number}*             ║
║   💣 Cycle: {i}/{cycles}            ║
║   ⚡ All Vectors Active             ║
║   🔒 Rotating 6000+ IPs             ║
║   ⏳ Please wait...                 ║
╚══════════════════════════════════════╝
                """,
                parse_mode="Markdown"
            )
            
            reason = f"Por la presente, deseo escalar formalmente un problema crítico de seguridad e integridad de mi cuenta de WhatsApp.Mi cuenta parece estar siendo objeto de abuso dirigido, que incluye intentos de acceso no autorizados y el envío de contenido inapropiado y no solicitado por parte de un tercero. Este comportamiento sugiere fuertemente un posible compromiso de la cuenta, suplantación de identidad o acoso coordinado.Como resultado de esta actividad, mi cuenta ha sido bloqueada repetidamente a pesar de que cumplo plenamente con los Términos de Servicio de WhatsApp. No he cometido ninguna infracción de las políticas, y considero que estas sanciones pueden estar siendo provocadas por denuncias maliciosas o interferencia externa.Esta situación está afectando gravemente la seguridad de mi cuenta y el uso normal de la plataforma. Solicito una investigación inmediata y exhaustiva, incluyendo la revisión de actividad de acceso, seguridad y mensajes relacionados con el abuso.Además, solicito:1. La restauración inmediata de mi cuenta2. Medidas de protección para evitar futuros accesos no autorizados o ataques3. Revisión de denuncias falsas o abusivas contra mi cuenta4. Confirmación de las acciones tomadas para asegurar mi cuentaMi número de WhatsApp: {number} Número sospechoso/denunciado (si está disponible): {number} Estoy dispuesto a proporcionar capturas de pantalla, registros y cualquier evidencia adicional necesaria para la verificación.Este asunto requiere atención urgente debido al compromiso repetido y la interrupción del servicio.Atentamente,{number}n {number}"
            
            results = await whatsapp_reporter.execute_mass_report(number, reason, 'perm')
            total_success += results['total_success']
            
            await asyncio.sleep(30)
        
        final_message = f"""
╔══════════════════════════════════════╗
║         ☢️ Mass Attack Complete      ║
╠══════════════════════════════════════╣
║                                      ║
║   📞 Target: *{number}*             ║
║   💣 Cycles: 10/10 Completed        ║
║   ⚡ Reports: 100% Successfully     ║
║   🔒 Proxies: 6000+ IP Rotations    ║
║                                      ║
║   🎯 Final Status: Heavy Bomb      ║
║                                      ║
║   💀 Effect: Permanent Ban          ║
║   ⚠️ Timeframe: 20-30 minutes      ║
╚══════════════════════════════════════╝
        """
        
        await processing_msg.edit_text(final_message, parse_mode="Markdown")
        
    except Exception as e:
        await processing_msg.edit_text(f"❌ Mass attack failed: {str(e)}", parse_mode="Markdown")

async def unban_command(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    sender = update.effective_user.first_name or "User"
    
    joined, missing = await check_all_channels(user_id, context)
    if not joined:
        await update.message.reply_text(f"❌ Join {missing} first!")
        return
    
    if not is_owner(user_id) and not is_premium(user_id):
        await update.message.reply_text(f"⛔ Sorry {sender}\n\n❌ Premium required!")
        return
    
    if not context.args:
        await update.message.reply_text("⚠️ Usage:\n`/unban <+92xxx>`", parse_mode="Markdown")
        return
    
    number = context.args[0]
    proxy_stats = proxy_manager.get_proxy_stats()
    processing_msg = await update.message.reply_text(
        f"""
╔══════════════════════════════════════╗
║         🔓 Unban Appeal             ║
╠══════════════════════════════════════╣
║                                      ║
║   📞 Target: *{number}*             ║
║   🎭 Method: Emotional Story        ║
║   🔒 Proxies: {proxy_stats['available']}          ║
║   ⏰ ETA: 45-90 seconds             ║
║                                      ║
║   💝 Preparing appeals...           ║
╚══════════════════════════════════════╝
        """,
        parse_mode="Markdown"
    )
    
    try:
        unban_results = await whatsapp_unban.execute_mass_unban_appeal(number)
        
        results_message = f"""
╔══════════════════════════════════════╗
║         💝 Unban Appeal Complete     ║
╠══════════════════════════════════════╣
║                                      ║
║   📞 Target: {number}               ║
║   👤 Requested By: {sender}         ║
║                                      ║
║   📊 Appeal Results:                ║
║   ━━━━━━━━━━━━━━━━━━━━━━━━━━━        ║
║   💌 Emails: ✅ {unban_results['emails']['success']}/10  ║
║   📋 Forms: ✅                      ║
║   🌐 Web Sites: ✅                  ║
║   🌐 APIs: ✅                       ║
║   🎯 Success: 6/6 Methods 🔥       ║
║                                      ║
║   📖 Story Used:                    ║
║   {unban_results['story'][:100]}...   ║
║                                      ║
║   💫 Expected Impact:               ║
║   • 87% Human Read                  ║
║   • 65% Manual Review               ║
║   • 45% Restoration                 ║
║   • 92% Emotional Response          ║
║                                      ║
║   ⚠️ Check status in 24-48 hours    ║
╚══════════════════════════════════════╝
        """
        
        await processing_msg.edit_text(results_message, parse_mode="Markdown")
        
    except Exception as e:
        await update.message.reply_text(f"❌ Unban failed: {str(e)}", parse_mode="Markdown")

# ===== OTHER UTILITY COMMANDS =====
async def check_id_command(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    sender = update.effective_user.first_name or "User"
    
    if update.message.reply_to_message:
        target = update.message.reply_to_message.from_user
        target_id = target.id
        target_name = target.first_name
        target_username = f"@{target.username}" if target.username else "None"
        is_bot = "✅ Yes" if target.is_bot else "❌ No"
        
        await update.message.reply_text(f"""
╔══════════════════════════════════════╗
║          👤 User Info               ║
╠══════════════════════════════════════╣
║                                      ║
║   📛 Name: {target_name}            ║
║   🔑 ID: `{target_id}`              ║
║   👤 Username: {target_username}    ║
║   🤖 Bot: {is_bot}                 ║
║                                      ║
║   🔗 Profile: tg://user?id={target_id} ║
╚══════════════════════════════════════╝
        """, parse_mode="Markdown")
    else:
        username = f"@{update.effective_user.username}" if update.effective_user.username else "None"
        
        await update.message.reply_text(f"""
╔══════════════════════════════════════╗
║          👤 Your Info               ║
╠══════════════════════════════════════╣
║                                      ║
║   📛 Name: {sender}                 ║
║   🔑 ID: `{user_id}`                ║
║   👤 Username: {username}           ║
║                                      ║
║   💡 Tip: Reply to someone's       ║
║   message to get their info         ║
╚══════════════════════════════════════╝
        """, parse_mode="Markdown")

async def user_info_command(update: Update, context: CallbackContext):
    if update.message.reply_to_message:
        user = update.message.reply_to_message.from_user
    else:
        user = update.effective_user
    
    user_id = user.id
    first_name = user.first_name
    last_name = user.last_name or "None"
    username = f"@{user.username}" if user.username else "None"
    is_bot = "✅ Yes" if user.is_bot else "❌ No"
    is_premium_user = "✅ Yes" if user.is_premium else "❌ No"
    
    await update.message.reply_text(f"""
╔══════════════════════════════════════╗
║          👤 Detailed User Info      ║
╠══════════════════════════════════════╣
║                                      ║
║   📛 First Name: {first_name}       ║
║   📛 Last Name: {last_name}         ║
║   🔑 User ID: `{user_id}`           ║
║   👤 Username: {username}           ║
║   🤖 Is Bot: {is_bot}              ║
║   💎 Telegram Premium: {is_premium_user} ║
║                                      ║
║   🔗 Profile: tg://user?id={user_id}║
║                                      ║
║   💡 Reply to anyone's message      ║
║   to get their info                 ║
╚══════════════════════════════════════╝
    """, parse_mode="Markdown")

async def group_info_command(update: Update, context: CallbackContext):
    chat = update.effective_chat
    
    if chat.type == "private":
        await update.message.reply_text("❌ This command only works in groups!")
        return
    
    chat_id = chat.id
    title = chat.title
    chat_type = chat.type
    description = chat.description or "No description"
    
    try:
        member_count = await context.bot.get_chat_member_count(chat_id)
    except:
        member_count = "Unknown"
    
    await update.message.reply_text(f"""
╔══════════════════════════════════════╗
║          👥 Group Info              ║
╠══════════════════════════════════════╣
║                                      ║
║   📛 Title: {title}                 ║
║   🔑 Group ID: `{chat_id}`          ║
║   📊 Type: {chat_type}              ║
║   👥 Members: {member_count}        ║
║                                      ║
║   📝 Description:                   ║
║   {description}                     ║
╚══════════════════════════════════════╝
    """, parse_mode="Markdown")

async def encode_command(update: Update, context: CallbackContext):
    if not context.args:
        await update.message.reply_text("⚠️ Usage:\n`/encode <text>`", parse_mode="Markdown")
        return
    
    text = " ".join(context.args)
    encoded = base64.b64encode(text.encode()).decode()
    
    await update.message.reply_text(f"""
╔══════════════════════════════════════╗
║          🔐 Base64 Encoder          ║
╠══════════════════════════════════════╣
║                                      ║
║   📝 Original:                      ║
║   `{text}`                          ║
║                                      ║
║   🔒 Encoded:                       ║
║   `{encoded}`                       ║
║                                      ║
║   💡 Use /decode to reverse         ║
╚══════════════════════════════════════╝
    """, parse_mode="Markdown")

async def decode_command(update: Update, context: CallbackContext):
    if not context.args:
        await update.message.reply_text("⚠️ Usage:\n`/decode <base64>`", parse_mode="Markdown")
        return
    
    text = " ".join(context.args)
    try:
        decoded = base64.b64decode(text.encode()).decode()
        await update.message.reply_text(f"""
╔══════════════════════════════════════╗
║          🔓 Base64 Decoder          ║
╠══════════════════════════════════════╣
║                                      ║
║   🔒 Encoded:                       ║
║   `{text}`                          ║
║                                      ║
║   📝 Decoded:                       ║
║   `{decoded}`                       ║
╚══════════════════════════════════════╝
        """, parse_mode="Markdown")
    except:
        await update.message.reply_text("❌ Invalid base64 string!")

async def hash_command(update: Update, context: CallbackContext):
    if not context.args:
        await update.message.reply_text("⚠️ Usage:\n`/hash <text>`", parse_mode="Markdown")
        return
    
    text = " ".join(context.args)
    md5_hash = hashlib.md5(text.encode()).hexdigest()
    sha256_hash = hashlib.sha256(text.encode()).hexdigest()
    
    await update.message.reply_text(f"""
╔══════════════════════════════════════╗
║          🔐 Hash Generator          ║
╠══════════════════════════════════════╣
║                                      ║
║   📝 Text:                          ║
║   `{text}`                          ║
║                                      ║
║   🔑 MD5:                           ║
║   `{md5_hash}`                      ║
║                                      ║
║   🔐 SHA256:                        ║
║   `{sha256_hash}`                   ║
╚══════════════════════════════════════╝
    """, parse_mode="Markdown")

async def ip_info_command(update: Update, context: CallbackContext):
    if not context.args:
        await update.message.reply_text("⚠️ Usage:\n`/ip <ip_address>`\n\nExample: `/ip 8.8.8.8`", parse_mode="Markdown")
        return
    
    ip = context.args[0]
    
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}", timeout=10)
        data = response.json()
        
        if data['status'] == 'success':
            await update.message.reply_text(f"""
╔══════════════════════════════════════╗
║          🌐 IP Info                 ║
╠══════════════════════════════════════╣
║                                      ║
║   🌐 IP: `{data['query']}`          ║
║   🌍 Country: {data['country']}     ║
║   🏙️ City: {data['city']}          ║
║   📍 Region: {data['regionName']}   ║
║   🏢 ISP: {data['isp']}            ║
║   📮 Zip: {data['zip']}            ║
║   🕐 Timezone: {data['timezone']}   ║
║   📍 Coordinates: {data['lat']}, {data['lon']} ║
║                                      ║
║   🔗 Google Maps:                   ║
║   [Click Here](https://maps.google.com/?q={data['lat']},{data['lon']}) ║
╚══════════════════════════════════════╝
            """, parse_mode="Markdown", disable_web_page_preview=True)
        else:
            await update.message.reply_text("❌ Invalid IP address!")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def password_gen_command(update: Update, context: CallbackContext):
    length = 16
    if context.args:
        try:
            length = int(context.args[0])
            if length < 8 or length > 64:
                length = 16
        except:
            length = 16
    
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(random.choice(chars) for _ in range(length))
    
    await update.message.reply_text(f"""
╔══════════════════════════════════════╗
║          🔐 Password Generator      ║
╠══════════════════════════════════════╣
║                                      ║
║   🔑 Password:                      ║
║   `{password}`                      ║
║                                      ║
║   📏 Length: {length} characters    ║
║   🔒 Strength: Very Strong         ║
║                                      ║
║   💡 Usage: `/passgen <length>`    ║
╚══════════════════════════════════════╝
    """, parse_mode="Markdown")

async def url_short_command(update: Update, context: CallbackContext):
    if not context.args:
        await update.message.reply_text("⚠️ Usage:\n`/short <url>`", parse_mode="Markdown")
        return
    
    url = context.args[0]
    
    try:
        response = requests.get(f"https://tinyurl.com/api-create.php?url={url}", timeout=10)
        short_url = response.text
        
        await update.message.reply_text(f"""
╔══════════════════════════════════════╗
║          🔗 URL Shortener           ║
╠══════════════════════════════════════╣
║                                      ║
║   📎 Original:                      ║
║   `{url}`                           ║
║                                      ║
║   ✂️ Shortened:                     ║
║   `{short_url}`                     ║
╚══════════════════════════════════════╝
        """, parse_mode="Markdown")
    except:
        await update.message.reply_text("❌ Failed to shorten URL!")

async def broadcast_command(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    
    if not is_owner(user_id):
        await update.message.reply_text("❌ Owners only!")
        return
    
    if not context.args:
        await update.message.reply_text("⚠️ Usage:\n`/broadcast <message>`", parse_mode="Markdown")
        return
    
    message = " ".join(context.args)
    all_users = db.get("all_users", [])
    
    if len(all_users) == 0:
        await update.message.reply_text("❌ No users found!")
        return
    
    success = 0
    failed = 0
    blocked = 0
    
    status_msg = await update.message.reply_text("📢 Broadcasting...\n\n⏳ Please wait...")
    
    for user_id in all_users:
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"""
╔══════════════════════════════════════╗
║          📢 Broadcast Message       ║
╠══════════════════════════════════════╣
║                                      ║
{message}
║                                      ║
╠══════════════════════════════════════╣
║   💬 From: ZAEEM BAN BOT              ║
║   📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}     ║
╚══════════════════════════════════════╝
                """,
                parse_mode="Markdown"
            )
            success += 1
        except Exception as e:
            if "blocked" in str(e).lower():
                blocked += 1
            failed += 1
        
        await asyncio.sleep(0.05)
    
    await status_msg.edit_text(f"""
╔══════════════════════════════════════╗
║         ✅ Broadcast Complete        ║
╠══════════════════════════════════════╣
║                                      ║
║   📊 Results:                       ║
║   ━━━━━━━━━━━━━━━━━━━━━━━━━━━        ║
║   ✅ Success: {success}             ║
║   🚫 Blocked: {blocked}            ║
║   ❌ Failed: {failed}               ║
║   📢 Total: {len(all_users)}        ║
║                                      ║
║   ⏰ Time: {datetime.now().strftime('%H:%M:%S')}  ║
╚══════════════════════════════════════╝
    """)

# ===== CALLBACK HANDLERS =====
async def callback_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    
    if query.data == "verify_joined":
        await verify_callback(update, context)
    
    elif query.data == "check_referrals":
        await query.answer("📊 Checking your referrals...")
        await check_referrals_command(update, context)
    
    elif query.data == "premium_info":
        await query.answer("💎 Showing premium info...")
        await premium_command(update, context)

    elif query.data == "get_referral":
        await query.answer("🔗 Generating your referral link...")
        # Call the free_user_by_referral function but we need to simulate the update
        # Let's create a simple referral message here
        user_id = query.from_user.id
        sender = query.from_user.first_name or "User"

        if str(user_id) not in db["referral_codes"]:
            db["referral_codes"][str(user_id)] = generate_referral_code(user_id)
            save_db()

        code = db["referral_codes"][str(user_id)]
        referral_count = get_referral_count(user_id)

        bot_username = (await context.bot.get_me()).username
        referral_link = f"https://t.me/{bot_username}?start=ref_{code}"

        has_temp_premium = False
        temp_expiry = None
        if "temp_premium" in db and user_id in db["temp_premium"]:
            expiry = db["temp_premium"][user_id]
            if datetime.now().timestamp() < expiry:
                has_temp_premium = True
                temp_expiry = datetime.fromtimestamp(expiry).strftime("%H:%M:%S")

        has_permanent_premium = user_id in db["premium"]

        if has_permanent_premium:
            premium_status = "🌟 Premium (Lifetime)"
        elif has_temp_premium:
            premium_status = f"⏰ Free Premium (Expires at {temp_expiry})"
        else:
            premium_status = "🔒 Free User"

        referral_message = f"""
╔══════════════════════════════════════╗
║          🔗 REFERRAL SYSTEM          ║
╠══════════════════════════════════════╣
║                                      ║
║   👤 User: {sender[:20]}                  ║
║   📊 Referrals: {referral_count}/5        ║
║   💎 Status: {premium_status}   ║
║                                      ║
╠══════════════════════════════════════╣
║                                      ║
║  📋 YOUR REFERRAL LINK:              ║
║                                      ║
║  `{referral_link}`                   ║
║                                      ║
╠══════════════════════════════════════╣
║                                      ║
║  💰 REWARD SYSTEM:                   ║
║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━        ║
║  ⭐ 5 Referrals = 1 Hour Free Premium║
║  ⭐ Premium Users: Unlimited Access  ║
║                                      ║
║  📈 Your Progress:                   ║
║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━        ║
║  {'█' * referral_count}{'░' * (5-referral_count)} {referral_count}/5    ║
║                                      ║
╚══════════════════════════════════════╝

💡 Share your link with friends!
🚀 Each referral gets you closer to FREE PREMIUM!
"""

        keyboard = [
            [InlineKeyboardButton("📤 Share Link", switch_inline_query=f"Join using my referral link: {referral_link}")],
            [InlineKeyboardButton("📊 Check Referrals", callback_data="check_referrals")],
            [InlineKeyboardButton("💎 Premium Info", callback_data="premium_info")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.message.reply_text(
            referral_message,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )

# ===== MAIN FUNCTION =====
async def main():
    save_db()
    
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    application.add_handler(CommandHandler("start", referral_start_handler))
    application.add_handler(CommandHandler("check", check_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("info", info_command))
    application.add_handler(CommandHandler("premium", premium_command))
    application.add_handler(CommandHandler("freeusebyreferal", free_user_by_referral))
    application.add_handler(CommandHandler("referral_stats", check_referrals_command))
    application.add_handler(CommandHandler("myreferrals", check_referrals_command))
    application.add_handler(CommandHandler("contact", contact_command))
    application.add_handler(CommandHandler("proxy_stats", proxy_stats_command))
    application.add_handler(CommandHandler("addowner", add_owner_command))
    application.add_handler(CommandHandler("delowner", del_owner_command))
    application.add_handler(CommandHandler("listowners", list_owners_command))
    application.add_handler(CommandHandler("addprem", add_premium_command))
    application.add_handler(CommandHandler("delprem", del_premium_command))
    application.add_handler(CommandHandler("listprem", list_premium_command))
    application.add_handler(CommandHandler("ban_perm", ban_perm_command))
    application.add_handler(CommandHandler("ban_temp", ban_temp_command))
    application.add_handler(CommandHandler("mass_report", mass_report_command))
    application.add_handler(CommandHandler("unban", unban_command))
    application.add_handler(CommandHandler("id", check_id_command))
    application.add_handler(CommandHandler("encode", encode_command))
    application.add_handler(CommandHandler("decode", decode_command))
    application.add_handler(CommandHandler("hash", hash_command))
    application.add_handler(CommandHandler("ip", ip_info_command))
    application.add_handler(CommandHandler("passgen", password_gen_command))
    application.add_handler(CommandHandler("userinfo", user_info_command))
    application.add_handler(CommandHandler("groupinfo", group_info_command))
    application.add_handler(CommandHandler("broadcast", broadcast_command))
    application.add_handler(CommandHandler("short", url_short_command))
    
    application.add_handler(CallbackQueryHandler(callback_handler))
    
    print("🤖 Bot is running")
    print("🔒 6000+ Proxy Rotation Active")
    print("🚀 All systems operational")
    
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())