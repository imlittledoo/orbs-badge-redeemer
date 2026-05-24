# 🎁 Discord Orb Redeemer

A multi-threaded command-line tool designed to **automate Discord virtual currency / reward redemption requests** using user tokens, with proxy support and fingerprint handling.

---

## ⚙️ Features

* 🧵 **Multi-threaded processing** – configurable worker threads
* 📥 **Queue-based system** – safe token distribution across workers
* 🌐 **Proxy support** – HTTP & authenticated proxy formats supported
* 🔑 **Fingerprint handling** – automatically fetches Discord fingerprint
* ⚡ **Fast redemption requests** – optimized API request flow
* 📊 **Status categorization** – success, invalid, rate-limited, errors
* 💾 **Auto file logging** – results saved instantly to output files
* 🔁 **Retry system** – automatic retries on unstable responses

---

## 🧠 How It Works

The tool reads tokens from:

```
input/tokens.txt
```

Each token is processed through Discord’s API flow:

1. Loads session using TLS client
2. Fetches `/experiments` fingerprint
3. Sends redemption request to:
```
/virtual-currency/skus/1342211853484429445/redeem
````
4. Categorizes response based on status code

---

## 🧰 Installation

```bash
git clone https://github.com/imlittledoo/discord-orb-redeemer.git
cd discord-orb-redeemer
pip install -r requirements.txt
````

---

## 📁 Input Setup

### `input/tokens.txt`

Supported formats:

```
token
email:password:token
```

---

### Optional `input/proxies.txt`

```
ip:port
username:password@ip:port
```

---

## ▶️ Usage

```bash
python main.py
```

Then enter:

```
Threads (default: 1)
```

---

## 📤 Output Files

All results are saved in:

```
output/
```

### Files generated:

* `success.txt` → successful redemptions
* `invalid.txt` → invalid tokens (401)
* `ratelimited.txt` → rate-limited requests (429)
* `error.txt` → other API / connection errors

---

## 🧵 Performance

* Queue-based worker system
* Multi-threaded execution
* Automatic retry delays on unstable responses
* Lightweight TLS session handling per request

---

## ⚠️ Disclaimer

This tool is intended for **educational and research purposes only**.
Use responsibly. The developer is not responsible for misuse or violations of Discord’s Terms of Service.

---

## 🧑‍💻 Author

Made by **ImLittledoo**
