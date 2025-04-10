import os
import sys
import re
import json
import time
import requests
import base64
import uuid
from rich import print as prints

ew = "[reset]"
dG = "[bold #00fe00]"
RW = "[bold #ff0b50]"


def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_cookie():
    if os.path.exists("cok.txt"):
        with open("cok.txt", "r") as file:
            return file.read().strip()
    return None


def save_cookie(cookie):
    with open("cok.txt", "w") as file:
        file.write(cookie)

def validate_cookie(cookie):
    response = requests.get(
        "https://business.facebook.com/business_locations",
        headers={"user-agent": "Mozilla/5.0", "cookie": cookie}
    )
    token = re.search("(EAAG\\w+)", response.text)
    return token is not None


def get_cookie_file():
    cookie_file = input("🔑 Masukkan nama file berisi cookie untuk auto like: ")
    return cookie_file

def choose_reaction():
    print("Kamu Mau Apa")
    print("1. Like (Suka)")
    print("2. Love (Cinta)")
    print("3. Haha (Tertawa)")
    print("4. Wow (Kaget)")
    print("5. Sad (Sedih)")
    print("6. Angry (Marah)")
    print("7. Care (Peduli)")
    
    choice = int(input("Pilih nomor reaksi: "))
    reaction_ids = {
        1: "1635855486666999",
        2: "1678524932434102",
        3: "115940658764963",
        4: "478547315650144",
        5: "908563459236466",
        6: "444813342392137",
        7: "613557422527858"
    }
    
    return reaction_ids.get(choice, None)

def GetDate(req):
    if not req:
        print("❌ ERROR: Response kosong atau tidak valid!")
        return None

    def extract(pattern, text, default=None):
        match = re.search(pattern, text)
        return match.group(1) if match else default

    return {
        "av": extract(r'"actorID":"(\d+)"', req, "Tidak ditemukan"),
        "__aaid": "0",
        "__user": extract(r'"actorID":"(\d+)"', req, "Tidak ditemukan"),
        "__a": "1",
        "__req": "25",
        "__hs": extract(r'"haste_session":"(.*?)"', req, "Tidak ditemukan"),
        "dpr": "1",
        "__ccg": extract(r'"connectionClass":"(.*?)"', req, "Tidak ditemukan"),
        "__rev": extract(r'"__spin_r":(\d+)', req, "Tidak ditemukan"),
        "__s": extract(r'"__s":"(\d+)"', req, "Tidak ditemukan"),
        "__hsi": extract(r'"hsi":"(\d+)"', req, "Tidak ditemukan"),
        "__dyn": extract(r'"__dyn":"(\d+)"', req, "Tidak ditemukan"),
        "__hsdp": extract(r'"__hsdp":"(\d+)"', req, "Tidak ditemukan"),
        "__hblp": extract(r'"__hblp":"(\d+)"', req, "Tidak ditemukan"),
        "__csr": extract(r'"__csr":"(\d+)"', req, "Tidak ditemukan"),
        "__comet_req": extract(r'__comet_req=(\d+)', req, "Tidak ditemukan"),
        "fb_dtsg": extract(r'"DTSGInitData",\[\],{"token":"(.*?)",', req, "Tidak ditemukan"),
        "jazoest": extract(r'jazoest=(\d+)', req, "Tidak ditemukan"),
        "lsd": extract(r'"LSD",\[\],{"token ":" (.*?)"', req, "Tidak ditemukan"),
        "__spin_r": extract(r'"__spin_r":(\d+)', req, "Tidak ditemukan"),
        "__spin_b": extract(r'"__spin_b":"(.*?)"', req, "Tidak ditemukan"),
        "__spin_t": extract(r'"__spin_t":(\d+)', req, "Tidak ditemukan"),
    }

def extract_feedback_id(url):
    match = re.search(r'[?&]fbid=(\d+)', url)
    if match:
        return match.group(1)
    match = re.search(r'fbid=(\d+)', url)
    if match:
        return match.group(1)
    match = re.search(r'videos/(\d+)', url)
    if not match:
        match = re.search(r'posts/(\d+)', url)
    if not match:
        match = re.search(r'(pfbid[0-9a-zA-Z]+)', url)
    if not match:
        match = re.search(r'reel/(\d+)', url)
    if match:
        return match.group(1) if len(match.groups()) > 0 else match.group(0)
    print(f"Gagal mengekstrak ID dari URL: {url}")
    return None


def encode_feedback_id(feedback_id):
    raw_string = f"feedback:{feedback_id}"
    encoded_bytes = base64.b64encode(raw_string.encode("utf-8"))
    return encoded_bytes.decode("utf-8")


class Facebook:
    def __init__(self, cookie):
        self.r = requests.Session()
        self.cok = cookie
        self.collected_ids = set()
        self.feedback_list = []

    def login(self):
        response = requests.get(
            "https://business.facebook.com/business_locations",
            headers={"user-agent": "Mozilla/5.0", "cookie": self.cok}
        )
        token = re.search("(EAAG\\w+)", response.text)
        return token is not None

    def dump(self, url):
        feedback_id = extract_feedback_id(url)
        if not feedback_id:
            prints(f"{RW}❌ Gagal mengekstrak feedback_id dari {url}.")
            return
        encoded_feedback_id = encode_feedback_id(feedback_id)
        cursor = None
        total_collected = 0 
        while True:
            try:
                headers = {
                    'accept': '*/*',
                    'accept-language': 'en-US,en;q=0.9,id;q=0.8',
                    'content-type': 'application/x-www-form-urlencoded',
                    'origin': 'https://www.facebook.com',
                    'priority': 'u=1, i',
                    'referer': url,
                    'sec-ch-prefers-color-scheme': 'dark',
                    'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
                    'sec-ch-ua-full-version-list': '"Chromium";v="134.0.6998.89", "Not:A-Brand";v="24.0.0.0", "Google Chrome";v="134.0.6998.89"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-model': '""',
                    'sec-ch-ua-platform': '"Windows"',
                    'sec-ch-ua-platform-version': '"10.0.0"',
                    'sec-fetch-dest': 'empty',
                    'sec-fetch-mode': 'cors',
                    'sec-fetch-site': 'same-origin',
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, seperti Gecko) Chrome/134.0.0.0 Safari/537.36',
                    'x-asbd-id': '359341',
                    'x-fb-friendly-name': 'CommentsListComponentsPaginationQuery',
                }
                
                self .req = self.r.get(url, headers=headers, cookies={"cookie": self.cok}).text
                data = GetDate(self.req)
                variables = {
                    "commentsAfterCount": 50,
                    "commentsAfterCursor": cursor,
                    "commentsBeforeCount": None,
                    "commentsBeforeCursor": None,
                    "commentsIntentToken": "RANKED_UNFILTERED_CHRONOLOGICAL_REPLIES_INTENT_V1",
                    "feedLocation": "PERMALINK",
                    "focusCommentID": None,
                    "scale": 1,
                    "useDefaultActor": False,
                    "id": encoded_feedback_id,
                    "__relay_internal__pv__IsWorkUser  relayprovider": False
                }
                
                data.update({
                    "fb_api_caller_class": "RelayModern",
                    "fb_api_req_friendly_name": "CommentsListComponentsPaginationQuery",
                    "variables": json.dumps(variables),
                    "server_timestamps": "true",
                    "doc_id": "28658896553757134"
                })
                response = self.r.post("https://www.facebook.com/api/graphql/", headers=headers, data=data, cookies={"cookie": self.cok})
                response_json = response.json()
                comments = response_json.get("data", {}).get("node", {}).get("comment_rendering_instance_for_feed_location", {}).get("comments", {}).get("edges", [])
                if not comments:
                    prints(f"\n\r{RW}❌ Tidak ada data komentar lagi untuk {url}.")
                    break
                
                for comment in comments:
                    node = comment.get("node", {})
                    author = node.get("author", {})
                    feedback_data = node.get("feedback", {})
                    if isinstance(author, dict):
                        uid = author.get("id")
                        name = author.get("name")
                        feedback_id = feedback_data.get("id")
                        if uid and name and feedback_id and uid not in self.collected_ids:
                            self.collected_ids.add(uid)
                            self.feedback_list.append((feedback_id, name))
                            total_collected += 1
                            print(f"{total_collected}. {name}")
                cursor = response_json.get("data", {}).get("node", {}).get("comment_rendering_instance_for_feed_location", {}).get("comments", {}).get("page_info", {}).get("end_cursor")
                if not cursor:
                    sys.stdout.write(f"\nBerhasil Dump ({total_collected}) ID Dari Komen\n")
                    break
            except KeyboardInterrupt:
                prints(f"\n{RW}❌ Proses dump dihentikan.")
                break
            except requests.exceptions.ConnectionError:
                prints(f"{RW}⚠️ Koneksi terputus")
                time.sleep(30)
            except requests.exceptions.RequestException as e:
                prints(f"{RW}⚠️ Error pada request: {e}")
                break
            except json.JSONDecodeError:
                prints(f"{RW}❌ Gagal menguraikan JSON, mungkin Facebook membatasi akses sementara.")
                break

    def react(self, url, reactionid, feedback_id_target, cookies):
        for index, cookie in enumerate(cookies):
            print(f"Mencoba like menggunakan Cookie {index + 1}...")
            self.cok = cookie.strip()
            if not self.login():
                prints(f"{RW}❌ Gagal login dengan Cookie {index + 1}.")
                continue
            try:
                headers = {
                    'accept': '*/*',
                    'accept-language': 'en-US,en;q=0.9,id;q=0.8',
                    'content-type': 'application/x-www-form-urlencoded',
                    'origin': 'https://www.facebook.com',
                    'priority': 'u=1, i',
                    'referer': url,
                    'sec-ch-prefers-color-scheme': 'dark',
                    'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
                    'sec-ch-ua-full-version-list': '"Chromium";v="134.0.6998.89", "Not:A-Brand";v="24.0.0.0", "Google Chrome";v="134.0.6998.89"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-model': '""',
                    'sec-ch-ua-platform': '"Windows"',
                    'sec-ch-ua-platform-version': '"10.0.0"',
                    'sec-fetch-dest': 'empty',
                    'sec-fetch-mode': 'cors',
                    'sec-fetch-site': 'same-origin',
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, seperti Gecko) Chrome/134.0.0.0 Safari/537.36',
                    'x-asbd-id': '359341',
                    'x-fb-friendly-name': 'CometUFIFeedbackReactMutation',
                }
                self.req = self.r.get(url, headers=headers, cookies={"cookie": self.cok}).text
                self.uid = re.search(r'__user=(\d+)', self.req).group(1)
                self.client = re.search('"clientID":"(.*?)"', str(self.req)).group(1)
                data = GetDate(self.req)
                variables = {
                    "input": {
                        "attribution_id_v2": "CometSinglePostDialogRoot.react,comet.post.single_dialog,via_cold_start,1742397242648,180970,,,",
                        "feedback_id": feedback_id_target,
                        "feedback_reaction_id": reactionid,
                        "feedback_source": "OBJECT",
                        "is_tracking_encrypted": True,
                        "tracking": None,
                        "session_id": str(uuid.uuid4()),
                        "downstream_share_session_id": str(uuid.uuid4()),
                        "downstream_share_session_origin_uri": url,
                        "downstream_share_session_start_time": "1742397246518",
                        "actor_id": self.uid,
                        "client_mutation_id": self.client
                    },
                    "useDefaultActor": False,
                    "__relay_internal__pv__CometUFIReactionsEnableShortNamerelayprovider": False
                }
                data.update({
                    "fb_api_caller_class": "RelayModern",
                    "fb_api_req_friendly_name": "CometUFIFeedbackReactMutation",
                    "variables": json.dumps(variables),
                    "server_timestamps": "true",
                    "doc_id": "9232085126871383"
                })
                cuki = self.r.post("https://www.facebook.com/api/graphql/", headers=headers, data=data, cookies={"cookie": self.cok})
                cuki = cuki.json()
                if "errors" not in cuki:
                    prints(f"{dG}✅ Berhasil Mengirim Reaction")
                else:
                    prints(f"{RW}❌ Gagal mengirim Reaction")
                time.sleep(7)
            except Exception as e:
                print(e)
def main():
    clear_terminal()
    
    cookie = get_cookie()
    
    if cookie and validate_cookie(cookie):
        prints(f"{dG}✅ Cookie valid, melanjutkan...")
    else:
        while True:
            cookie = input("🔑 Masukkan Cookie: ")
            if validate_cookie(cookie):
                save_cookie(cookie)
                prints(f"{dG}✅ Cookie berhasil disimpan.")
                break
            else:
                prints(f"{RW}❌ Cookie tidak valid, silakan coba lagi.")

    clear_terminal()
    
    reactionid = choose_reaction()
    if not reactionid:
        prints(f"{RW}❌ Pilihan reaksi tidak valid.")
        return

    urls = input("🔍 Masukkan URL (pisahkan dengan koma): ").split(",")
    urls = [url.strip() for url in urls if url.strip()]
    if not urls:
        prints(f"{RW}❌ Tidak ada URL yang valid, keluar...")
        return

    cookie_file = input("🔑 Masukkan nama file berisi cookie untuk melakukan auto like: ")
    if not os.path.exists(cookie_file):
        prints(f"{RW}❌ File cookie tidak ditemukan.")
        return

    with open(cookie_file, "r") as file:
        cookies = file.readlines()

    for url in urls:
        fb = Facebook(cookie)
        fb.dump(url)
        if not fb.feedback_list:
            prints(f"{RW}❌ Tidak ada feedback ID yang ditemukan.")
            continue
        
        feedback_choice = int(input("Masukkan nomor feedback ID yang ingin digunakan: ")) - 1
        if feedback_choice < 0 or feedback_choice >= len(fb.feedback_list):
            prints(f"{RW}❌ Pilihan tidak valid.")
            continue
        
        feedback_id_target = fb.feedback_list[feedback_choice][0]
        fb.react(url, reactionid, feedback_id_target, cookies)

if __name__ == "__main__":
    main()