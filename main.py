import os, random, threading, json, uuid, base64, tls_client, time
from queue import Queue
from datetime import datetime
from typing import Optional
from colorama import Fore, Style, init

init(autoreset=True)

class Console:
    @staticmethod
    def ts():
        return datetime.now().strftime("%H:%M:%S")
    @staticmethod
    def info(msg, worker_id):
        print(f"{Fore.CYAN}[{Console.ts()}]{Fore.BLUE} • INFO    »{Style.RESET_ALL} {msg} [Worker #{worker_id}]")
    @staticmethod
    def success(msg, worker_id):
        print(f"{Fore.CYAN}[{Console.ts()}]{Fore.GREEN} • SUCCESS » {Style.RESET_ALL} {msg} [Worker #{worker_id}]")
    @staticmethod
    def warn(msg, worker_id):
        print(f"{Fore.CYAN}[{Console.ts()}]{Fore.YELLOW} • WARN    »{Style.RESET_ALL} {msg} [Worker #{worker_id}]")
    @staticmethod
    def error(msg, worker_id):
        print(f"{Fore.CYAN}[{Console.ts()}]{Fore.RED} • ERROR   »{Style.RESET_ALL} {msg} [Worker #{worker_id}]")
    @staticmethod
    def debug(msg, worker_id):
        print(f"{Fore.CYAN}[{Console.ts()}]{Fore.BLACK} • DEBUG   »{Style.RESET_ALL} {msg} [Worker #{worker_id}]")

class TokenTool:
    def __init__(self, threads: int = 10):
        self.threads = threads
        self.queue = Queue()
        self.console = Console()
        self.lock = threading.Lock()
        self.tokens = self._load_lines("input/tokens.txt")
        self.proxies = self._load_lines("input/proxies.txt")
        self._prepare_outputs()
        self.api_base = "https://discord.com/api/v9"
        super_properties = {
            "os": "Windows",
            "browser": "Chrome",
            "device": "",
            "system_locale": "en-US",
            "has_client_mods": False,
            "browser_user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
            "browser_version": "145.0.0.0",
            "os_version": "10",
            "referrer": "",
            "referring_domain": "",
            "referrer_current": "",
            "referring_domain_current": "",
            "release_channel": "stable",
            "client_build_number": 503231,
            "client_event_source": None,
            "client_launch_id": str(uuid.uuid4()),
            "launch_signature": str(uuid.uuid4()),
            "client_heartbeat_session_id": str(uuid.uuid4()),
            "client_app_state": "focused"
        }
        self.x_super_properties = base64.b64encode(json.dumps(super_properties).encode()).decode()
        self.headers_template = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'authorization': '',
            'content-type': 'application/json',
            'origin': 'https://discord.com',
            'priority': 'u=1, i',
            'referer': 'https://discord.com/channels/@me',
            'sec-ch-ua': '"Google Chrome";v="145", "Chromium";v="145", "Not A(Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'sec-gpc': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36',
            'x-debug-options': 'bugReporterEnabled',
            'x-discord-locale': 'en-US',
            'x-discord-timezone': 'Europe/Paris',
            'x-super-properties': self.x_super_properties,
        }

    def create_session(self, proxy: Optional[str] = None) -> Optional[tls_client.Session]:
        try:
            session = tls_client.Session(
                client_identifier="chrome145",
                random_tls_extension_order=True
            )

            if proxy:
                if "@" in proxy:
                    auth_part, server_part = proxy.split("@", 1)
                    username, password = auth_part.split(":", 1)
                    host, port = server_part.split(":", 1)
                    proxy_url = f"http://{username}:{password}@{host}:{port}"
                else:
                    host, port = proxy.split(":", 1)
                    proxy_url = f"http://{host}:{port}"

                session.proxies = {
                    "http": proxy_url,
                    "https": proxy_url
                }

            return session

        except Exception as e:
            Console.error(f"Failed to create session: {str(e)}")
            return None
        
    def getFingerprint(self, session: tls_client.Session) -> Optional[str]:
        try:
            response = session.get(f"{self.api_base}/experiments")
            if response.status_code == 200:
                data = response.json()
                fingerprint = data.get("fingerprint")
                return fingerprint
            else:
                self.console.error(f"Failed to get fingerprint: HTTP {response.status_code}")
                return None
        except Exception as e:
            self.console.error(f"Error getting fingerprint: {str(e)}")
            return None

    def _load_lines(self, path: str):
        if not os.path.exists(path):
            return []
        with open(path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]

    def _prepare_outputs(self):
        os.makedirs("output", exist_ok=True)
        for file in ["success.txt", "invalid.txt", "ratelimited.txt", "error.txt"]:
            open(f"output/{file}", "a", encoding="utf-8").close()

    def _write(self, filename: str, content: str):
        with self.lock:
            with open(f"output/{filename}", "a", encoding="utf-8") as f:
                f.write(content + "\n")

    def _extract_token(self, line: str):
        parts = line.split(":")
        if len(parts) >= 3:
            return parts[-1]
        return line

    def _get_proxy(self):
        if not self.proxies:
            return None
        return random.choice(self.proxies)

    def _make_request(self, token: str, proxy: Optional[str], retries: int = 3):
        for attempt in range(retries):
            try:
                session = self.create_session(proxy)
                if not session:
                    continue

                payload = {
                    "checkout_session_id": str(uuid.uuid4())
                }

                headers = self.headers_template.copy()
                headers["authorization"] = token

                session.get("https://discord.com", headers=headers)

                fingerprint = self.getFingerprint(session)
                if fingerprint:
                    headers["x-fingerprint"] = fingerprint

                response = session.post(
                    f"{self.api_base}/virtual-currency/skus/1342211853484429445/redeem",
                    json=payload,
                    headers=headers
                )

                # success → return immediately
                if response.status_code == 201:
                    return response.status_code, response.text

                # retry on ratelimit or server error
                if response.status_code in (429, 500, 502, 503):
                    time.sleep(1.5 * (attempt + 1))
                    continue

                # other responses → return directly
                return response.status_code, response.text

            except Exception as e:
                if attempt < retries - 1:
                    time.sleep(1.5 * (attempt + 1))
                    continue
                return None, str(e)

        return None, "Max retries exceeded"

    def worker(self, worker_id: int):
        while not self.queue.empty():
            try:
                line = self.queue.get_nowait()
            except:
                break

            success = 0
            error = 0
            ratelimited = 0
            invalid = 0

            token = self._extract_token(line)
            proxy = self._get_proxy()

            try:
                status1, rtext = self._make_request(token, proxy)

                if status1 == 201:
                    success += 1
                    self._write("success.txt", line)
                    self.console.success(f"Redeemed the orb badge [{token[:25]}*****]", worker_id)

                elif status1 == 401:
                    invalid += 1
                    self._write("invalid.txt", line)
                    self.console.warn(f"Invalid -> [{token[:25]}*****]", worker_id)

                elif status1 == 429:
                    ratelimited += 1
                    self._write("ratelimited.txt", line)
                    self.console.warn(f"Ratelimited -> [{token[:25]}*****]", worker_id)

                else:
                    error += 1
                    error_msg = f"Status: {status1} - Message: {rtext}"
                    self._write("error.txt", f"{line} | {error_msg}")
                    self.console.error(f"Error {error_msg} -> [{token[:25]}*****]", worker_id)

            except Exception as e:
                error += 1
                error_msg = str(e)
                self._write("error.txt", f"{line} | {error_msg}")
                self.console.error(f"Exception -> [{token[:25]}*****] | {error_msg}", worker_id)

            finally:
                self.queue.task_done()
                
    def run(self):
        for line in self.tokens:
            self.queue.put(line)

        threads = []
        for i in range(self.threads):
            t = threading.Thread(target=self.worker, args=(i + 1,))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

if __name__ == "__main__":
    os.system("cls" if os.name == "nt" else "clear")
    print(fr"""{Fore.CYAN}
 _____      _      ______         _                               
|  _  |    | |     | ___ \       | |                              
| | | |_ __| |__   | |_/ /___  __| | ___  ___ _ __ ___   ___ _ __ 
| | | | '__| '_ \  |    // _ \/ _` |/ _ \/ _ \ '_ ` _ \ / _ \ '__|
\ \_/ / |  | |_) | | |\ \  __/ (_| |  __/  __/ | | | | |  __/ |   
 \___/|_|  |_.__/  \_| \_\___|\__,_|\___|\___|_| |_| |_|\___|_|   
                                                                  
                                                                  {Style.RESET_ALL}""")
    try:
        threads = int(input(f"{Fore.CYAN}[{Console.ts()}]{Fore.BLUE}(~){Style.RESET_ALL} Threads (default 1): ").strip())
        if threads <= 0:
            raise ValueError
    except ValueError:
        print("Invalid thread count, using 1")
        threads = 1

    print(f"{Fore.CYAN}[{Console.ts()}]{Fore.BLUE}(~){Style.RESET_ALL} Starting with {threads} threads...")
    print()
    tool = TokenTool(threads=threads)
    tool.run()