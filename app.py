#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os,re,sys,time,random,requests
from playwright.sync_api import sync_playwright

COOKIE_VALUE  = os.environ.get('COOKIE_VALUE') or ""
EMAIL         = os.environ.get('EMAIL') or ""
PASSWORD      = os.environ.get('PASSWORD') or ""
TG_BOT_TOKEN  = os.environ.get('TG_BOT_TOKEN') or ""
TG_CHAT_ID    = os.environ.get('TG_CHAT_ID') or ""
WX_PUSH_TOKEN = os.environ.get('WX_PUSH_TOKEN') or "" # 新增微信推送 Token

BASE_URL = "https://dash.hidencloud.com"
LOGIN_URL = f"{BASE_URL}/auth/login"

IS_PROXY      = os.environ.get('IS_PROXY', 'false').lower() == 'true'
PROXY_SERVER  = os.environ.get('PROXY_SERVER') or "socks5://127.0.0.1:1080"
REQUESTS_PROXIES = {"http": PROXY_SERVER, "https": PROXY_SERVER} if IS_PROXY else None

def log(message):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}", flush=True)

STEALTH_JS = """
Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
window.chrome = { runtime: {} };
"""

def get_current_ip(proxy_server=None):
    proxies = {"http": proxy_server, "https": proxy_server} if (proxy_server and IS_PROXY) else None
    try:
        resp = requests.get("https://api.ip.sb/ip", proxies=proxies, timeout=15)
        if resp.status_code == 200:
            return resp.text.strip()
        return "获取失败"
    except Exception as e:
        log(f"❌ 获取出口IP失败: {e}")
        return "获取失败"

def format_push_content(status, old_due, new_due):
    local_time = time.gmtime(time.time() + 8 * 3600)
    now = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
    if '@' in EMAIL:
        name, domain = EMAIL.split('@', 1)
        masked_email = f"{name[:2]}****{name[-2:]}@{domain}" if len(name) > 4 else f"{name}@{domain}"
    else:
        masked_email = EMAIL[:2] + '****' 

    title = f"HidenCloud {status}"
    content = (
        f"👤 账号: {masked_email}\n"
        f"📅 续期前：{old_due}\n"
        f"📅 续期后：{new_due}\n"
        f"🕒 时间：{now}"
    )
    return title, content

def send_telegram_notification(status, old_due, new_due):
    if not TG_BOT_TOKEN or not TG_CHAT_ID:
        return False
    title, content = format_push_content(status, old_due, new_due)
    text = f"🎉 {title}\n\n{content}"
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    try:
        resp = requests.post(url, json={"chat_id": TG_CHAT_ID, "text": text, "parse_mode": "HTML"}, timeout=10, proxies=REQUESTS_PROXIES)
        if resp.status_code == 200:
            log("✅ Telegram 通知发送成功")
            return True
        log(f"❌ Telegram 通知失败: {resp.text}")
    except Exception as e:
        log(f"❌ Telegram 通知异常: {e}")
    return False

def send_wechat_notification(status, old_due, new_due):
    if not WX_PUSH_TOKEN:
        log("⚠️ 微信 Token 未配置，跳过推送")
        return False
    title, content = format_push_content(status, old_due, new_due)
    url = "http://www.pushplus.plus/send"
    payload = {
        "token": WX_PUSH_TOKEN,
        "title": title,
        "content": content.replace('\n', '<br>'),
        "template": "html"
    }
    try:
        # 微信推送走国内直连更稳定，不经过代理
        resp = requests.post(url, json=payload, timeout=10)
        if resp.status_code == 200 and resp.json().get('code') == 200:
            log("✅ 微信 PushPlus 通知发送成功")
            return True
        log(f"❌ 微信通知失败: {resp.text}")
    except Exception as e:
        log(f"❌ 微信通知异常: {e}")
    return False

def handle_cloudflare(page):
    iframe_selector = 'iframe[src*="challenges.cloudflare.com"]'
    if page.locator(iframe_selector).count() == 0:
        return True
    start_time = time.time()
    while time.time() - start_time < 60:
        if page.locator(iframe_selector).count() == 0:
            return True
        try:
            frame = page.frame_locator(iframe_selector)
            checkbox = frame.locator('input[type="checkbox"]')
            if checkbox.is_visible():
                time.sleep(random.uniform(0.5, 1.5))
                checkbox.click()
                time.sleep(5)
            else:
                time.sleep(1)
        except:
            pass
    return False

def login(page):
    if COOKIE_VALUE:
        try:
            page.context.add_cookies([{
                'name': 'remember_web_59ba36addc2b2f9401580f014c7f58ea4e30989d',
                'value': COOKIE_VALUE,
                'domain': 'dash.hidencloud.com',
                'path': '/',
                'expires': int(time.time()) + 3600 * 24 * 365,
                'httpOnly': True,
                'secure': True,
                'sameSite': 'Lax'
            }])
            page.goto(f"{BASE_URL}/dashboard", wait_until="domcontentloaded", timeout=60000)
            handle_cloudflare(page)
            if "auth/login" not in page.url:
                log("✅ Cookie 登录成功！")
                return True
        except:
            pass

    if not EMAIL or not PASSWORD:
        return False
    try:
        page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=60000)
        handle_cloudflare(page)
        page.fill('input[name="email"]', EMAIL)
        page.fill('input[name="password"]', PASSWORD)
        time.sleep(0.5)
        handle_cloudflare(page)
        page.click('button[type="submit"]')
        time.sleep(3)
        handle_cloudflare(page)
        page.wait_for_url(f"{BASE_URL}/*", timeout=30000)
        page.goto(f"{BASE_URL}/dashboard", wait_until="domcontentloaded", timeout=60000)
        handle_cloudflare(page)
        if "auth/login" not in page.url:
            log("✅ 账号密码登录成功！")
            return True
    except:
        pass
    return False

def get_server_id(page):
    try:
        handle_cloudflare(page)
        time.sleep(3)
        html = page.content()
        matches = re.findall(r'/service/(\d+)/manage', html)
        if matches:
            return matches[0]
        matches = re.findall(r'#(\d{4,})', html)
        if matches:
            return matches[0]
    except:
        pass
    return None

def get_due_date(page):
    try:
        if SERVICE_URL not in page.url:
            page.goto(SERVICE_URL, wait_until="domcontentloaded", timeout=60000)
        handle_cloudflare(page)
        body_text = page.locator("body").inner_text()
        patterns = [r"Due date\s+(\d{1,2}\s+[A-Za-z]{3}\s+\d{4})", r"Due date\s*\n\s*(\d{1,2}\s+[A-Za-z]{3}\s+\d{4})", r"Due date.*?(\d{1,2}\s+[A-Za-z]{3}\s+\d{4})"]
        for pattern in patterns:
            match = re.search(pattern, body_text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()
    except:
        pass
    return "未知"

def renew_service(page):
    try:
        if page.url != SERVICE_URL:
            page.goto(SERVICE_URL, wait_until="domcontentloaded", timeout=60000)
        handle_cloudflare(page)
        renew_btn = page.locator('button:has-text("Renew")')
        create_btn = page.locator('button:has-text("Create Invoice")')

        modal_opened = False
        for i in range(3):
            try:
                renew_btn.wait_for(state="visible", timeout=10000)
                renew_btn.scroll_into_view_if_needed()
                renew_btn.click()
                time.sleep(2)
                page_text = page.locator("body").inner_text()
                if "Renewal Restricted" in page_text or "can only renew" in page_text.lower():
                    return "NOT_TIME"
                try:
                    create_btn.wait_for(state="visible", timeout=5000)
                    modal_opened = True
                    break
                except:
                    time.sleep(2)
            except:
                pass
        if not modal_opened: return False

        handle_cloudflare(page)
        create_btn.click()
        new_invoice_url = None
        start_wait = time.time()
        while time.time() - start_wait < 90:
            if "/payment/invoice/" in page.url:
                new_invoice_url = page.url
                break
            if page.locator('iframe[src*="challenges.cloudflare.com"]').count() > 0:
                handle_cloudflare(page)
            time.sleep(1)
        
        if not new_invoice_url: return False
        if page.url != new_invoice_url: page.goto(new_invoice_url)
        handle_cloudflare(page)
        
        pay_btn = page.locator('a:has-text("Pay"):visible, button:has-text("Pay"):visible').first
        pay_btn.wait_for(state="visible", timeout=30000)
        pay_btn.click()
        time.sleep(5)
        page.goto(SERVICE_URL, wait_until="domcontentloaded", timeout=60000)
        handle_cloudflare(page)
        return True
    except:
        return False

def main():
    if not COOKIE_VALUE and not (EMAIL and PASSWORD):
        log("❌ 缺少登录凭证")
        sys.exit(1)
    global SERVICE_URL
    with sync_playwright() as p:
        try:
            current_ip = get_current_ip(PROXY_SERVER)
            log(f"🎯 当前出口IP: {current_ip}")
            browser = p.chromium.launch(channel="chrome", headless=False, args=['--no-sandbox', '--disable-blink-features=AutomationControlled', '--disable-infobars'])
            context = browser.new_context(viewport={'width': 1920, 'height': 1080}, user_agent='Mozilla/5.0 (X11; Linux x86_64)', proxy={"server": PROXY_SERVER} if IS_PROXY else None)
            page = context.new_page()
            page.add_init_script(STEALTH_JS)

            if not login(page): sys.exit(1)
            server_id = get_server_id(page)
            if not server_id: sys.exit(1)
            
            SERVICE_URL = f"{BASE_URL}/service/{server_id}/manage"
            old_due = get_due_date(page)
            renew_result = renew_service(page)

            new_due = old_due
            if renew_result == "NOT_TIME":
                status = "⏳ 未到续期时间"
            elif renew_result is False:
                status = "❌ 续期失败"
            else:
                new_due = get_due_date(page)
                status = "✅ 续期成功"

            # 触发双路推送
            send_telegram_notification(status, old_due, new_due)
            send_wechat_notification(status, old_due, new_due)

            if renew_result == "NOT_TIME": sys.exit(0)
            elif renew_result is False: sys.exit(1)
            else: sys.exit(0)
        except Exception as e:
            log(f"❌ 运行出错: {e}")
            sys.exit(1)
        finally:
            if 'browser' in locals() and browser: browser.close()
                
if __name__ == "__main__":
    main()
