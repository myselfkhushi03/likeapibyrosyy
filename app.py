#
# ╔══════════════════════════════════════════════════════════════════════╗
# ║                                                                      ║
# ║    ███████╗███████╗██╗  ██╗██╗  ██╗██╗   ██╗                         ║
# ║    ╚══███╔╝██╔════╝╚██╗██╔╝╚██╗██╔╝╚██╗ ██╔╝                         ║
# ║      ███╔╝ █████╗   ╚███╔╝  ╚███╔╝  ╚████╔╝                          ║
# ║     ███╔╝  ██╔══╝   ██╔██╗  ██╔██╗   ╚██╔╝                           ║
# ║    ███████╗███████╗██╔╝ ██╗██╔╝ ██╗   ██║                            ║
# ║    ╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝                            ║
# ║                                                                      ║
# ╠══════════════════════════════════════════════════════════════════════╣
# ║                   ⚡   Z E X X Y   ⚡                                ║
# ║                   ─────────────────                                  ║
# ║   👑  Author      :  Zexxy                                           ║
# ║   🚀  Framework   :  Flask  +  aiohttp                               ║
# ║   🎯  Purpose     :  Free Fire Like Sender (Multi-Server)            ║
# ║   🌍  Servers     :  IND · BR · US · SAC · NA · BD                   ║
# ║   💀  Credit      :  Zexxy — do not copy without permission          ║
# ║   🎨  Style       :  Zexxy Edition 💦                                ║
# ╚══════════════════════════════════════════════════════════════════════╝
#


from flask import Flask, request, jsonify
import asyncio
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from google.protobuf.json_format import MessageToJson
import binascii
import aiohttp
import requests
import json
import like_pb2
import uid_generator_pb2
import visit_count_pb2
from google.protobuf.message import DecodeError

app = Flask(__name__)
app.json.sort_keys = False

ZEXXY_BANNER = r"""
   ╔══════════════════════════════════════════════════════════╗
   ║              ⚡  Z E X X Y   A P I  ⚡                    ║
   ║              Like Sender — Zexxy Edition 💦               ║
   ║              © Zexxy — All Rights Reserved                ║
   ╚══════════════════════════════════════════════════════════╝
"""


# ═══════════════════════════════════════════════════════════════
#   TOKEN LOADER
# ═══════════════════════════════════════════════════════════════
def zexxyh4x_load_tokens(region):
    try:
        if region == "IND":
            with open("token_ind.json", "r") as f:
                tokens = json.load(f)
        elif region in {"BR", "US", "SAC", "NA"}:
            with open("token_br.json", "r") as f:
                tokens = json.load(f)
        else:
            with open("token_bd.json", "r") as f:
                tokens = json.load(f)
        return tokens
    except Exception as e:
        app.logger.error(f"[Zexxy] Error loading tokens for region {region}: {e}")
        return None


# ═══════════════════════════════════════════════════════════════
#   AES ENCRYPTION
# ═══════════════════════════════════════════════════════════════
def zexxyh4x_encrypt_message(plaintext):
    try:
        key = b'Yg&tc%DEuh6%Zc^8'
        iv  = b'6oyZDr22E3ychjM%'
        cipher = AES.new(key, AES.MODE_CBC, iv)
        padded = pad(plaintext, AES.block_size)
        encrypted = cipher.encrypt(padded)
        return binascii.hexlify(encrypted).decode('utf-8')
    except Exception as e:
        app.logger.error(f"[Zexxy] Error encrypting message: {e}")
        return None


# ═══════════════════════════════════════════════════════════════
#   PROTOBUF (LIKE)
# ═══════════════════════════════════════════════════════════════
def zexxyh4x_create_protobuf_message(user_id, region):
    try:
        message = like_pb2.like()
        message.uid = int(user_id)
        message.region = region
        return message.SerializeToString()
    except Exception as e:
        app.logger.error(f"[Zexxy] Error creating protobuf message: {e}")
        return None


# ═══════════════════════════════════════════════════════════════
#   ASYNC SEND REQUEST
# ═══════════════════════════════════════════════════════════════
async def zexxyh4x_send_request(encrypted_uid, token, url):
    try:
        edata = bytes.fromhex(encrypted_uid)
        headers = {
            'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_Z01QD Build/PI)",
            'Connection': "Keep-Alive",
            'Accept-Encoding': "gzip",
            'Authorization': f"Bearer {token}",
            'Content-Type': "application/x-www-form-urlencoded",
            'Expect': "100-continue",
            'X-Unity-Version': "2018.4.11f1",
            'X-GA': "v1 1",
            'ReleaseVersion': "OB55"
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=edata, headers=headers) as response:
                if response.status != 200:
                    app.logger.error(f"[Zexxy] Request failed with status: {response.status}")
                    return response.status
                return await response.text()
    except Exception as e:
        app.logger.error(f"[Zexxy] Exception in send_request: {e}")
        return None


# ═══════════════════════════════════════════════════════════════
#   MULTIPLE REQUESTS (Likes)
# ═══════════════════════════════════════════════════════════════
async def zexxyh4x_send_multiple_requests(uid, region, url):
    try:
        protobuf_message = zexxyh4x_create_protobuf_message(uid, region)
        if protobuf_message is None:
            app.logger.error("[Zexxy] Failed to create protobuf message.")
            return None
        encrypted_uid = zexxyh4x_encrypt_message(protobuf_message)
        if encrypted_uid is None:
            app.logger.error("[Zexxy] Encryption failed.")
            return None
        tasks = []
        tokens = zexxyh4x_load_tokens(region)
        if tokens is None:
            app.logger.error("[Zexxy] Failed to load tokens.")
            return None
        for i in range(220):
            token = tokens[i % len(tokens)]["token"]
            tasks.append(zexxyh4x_send_request(encrypted_uid, token, url))
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results
    except Exception as e:
        app.logger.error(f"[Zexxy] Exception in send_multiple_requests: {e}")
        return None


# ═══════════════════════════════════════════════════════════════
#   UID PROTOBUF BUILDER
# ═══════════════════════════════════════════════════════════════
def zexxyh4x_create_protobuf(uid):
    try:
        message = uid_generator_pb2.uid_generator()
        message.saturn_ = int(uid)
        message.garena = 1
        return message.SerializeToString()
    except Exception as e:
        app.logger.error(f"[Zexxy] Error creating UID protobuf: {e}")
        return None


def zexxyh4x_enc(uid):
    protobuf_data = zexxyh4x_create_protobuf(uid)
    if protobuf_data is None:
        return None
    return zexxyh4x_encrypt_message(protobuf_data)


# ═══════════════════════════════════════════════════════════════
#   MAKE REQUEST (GetPlayerPersonalShow)
# ═══════════════════════════════════════════════════════════════
def zexxyh4x_make_request(encrypt, region, token):
    try:
        if region == "IND":
            url = "https://client.ind.freefiremobile.com/GetPlayerPersonalShow"
        elif region in {"BR", "US", "SAC", "NA"}:
            url = "https://client.us.freefiremobile.com/GetPlayerPersonalShow"
        else:
            url = "https://clientbp.ppmainecoonghj.com/GetPlayerPersonalShow"
        edata = bytes.fromhex(encrypt)
        headers = {
            'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_Z01QD Build/PI)",
            'Connection': "Keep-Alive",
            'Accept-Encoding': "gzip",
            'Authorization': f"Bearer {token}",
            'Content-Type': "application/x-www-form-urlencoded",
            'Expect': "100-continue",
            'X-Unity-Version': "2018.4.11f1",
            'X-GA': "v1 1",
            'ReleaseVersion': "OB55"
        }
        response = requests.post(url, data=edata, headers=headers, verify=False)
        hex_data = response.content.hex()
        binary = bytes.fromhex(hex_data)
        decode = zexxyh4x_decode_protobuf(binary)
        if decode is None:
            app.logger.error("[Zexxy] Protobuf decoding returned None.")
        return decode
    except Exception as e:
        app.logger.error(f"[Zexxy] Error in make_request: {e}")
        return None


# ═══════════════════════════════════════════════════════════════
#   DECODE PROTOBUF
# ═══════════════════════════════════════════════════════════════
def zexxyh4x_decode_protobuf(binary):
    try:
        items = visit_count_pb2.Info()
        items.ParseFromString(binary)
        return items
    except DecodeError as e:
        app.logger.error(f"[Zexxy] Error decoding protobuf: {e}")
        return None
    except Exception as e:
        app.logger.error(f"[Zexxy] Unexpected decode error: {e}")
        return None


# ═══════════════════════════════════════════════════════════════
#   MAIN ROUTE — /like
# ═══════════════════════════════════════════════════════════════
@app.route('/like', methods=['GET'])
def zexxyh4x_handle_requests():
    uid = request.args.get("uid")
    region = request.args.get("region", "").upper()
    if not uid or not region:
        return jsonify({"error": "UID and region are required"}), 400

    try:
        def zexxyh4x_process_request():
            tokens = zexxyh4x_load_tokens(region)
            if tokens is None:
                raise Exception("Failed to load tokens.")
            token = tokens[0]['token']
            encrypted_uid = zexxyh4x_enc(uid)
            if encrypted_uid is None:
                raise Exception("Encryption of UID failed.")

            # --- Fetch player info BEFORE sending likes ---
            before = zexxyh4x_make_request(encrypted_uid, region, token)
            if before is None:
                raise Exception("Failed to retrieve initial player info.")
            try:
                jsone = MessageToJson(before)
            except Exception as e:
                raise Exception(f"Error converting 'before' protobuf to JSON: {e}")
            data_before = json.loads(jsone)
            before_like = data_before.get('AccountInfo', {}).get('Likes', 0)
            try:
                before_like = int(before_like)
            except Exception:
                before_like = 0
            app.logger.info(f"[Zexxy] Likes before command: {before_like}")

            # --- Like endpoint URL ---
            if region == "IND":
                url = "https://client.ind.freefiremobile.com/LikeProfile"
            elif region in {"BR", "US", "SAC", "NA"}:
                url = "https://client.us.freefiremobile.com/LikeProfile"
            else:
                url = "https://clientbp.ppmainecoonghj.com/LikeProfile"

            # --- Send likes ---
            asyncio.run(zexxyh4x_send_multiple_requests(uid, region, url))

            # --- Fetch player info AFTER sending likes ---
            after = zexxyh4x_make_request(encrypted_uid, region, token)
            if after is None:
                raise Exception("Failed to retrieve player info after like requests.")
            try:
                jsone_after = MessageToJson(after)
            except Exception as e:
                raise Exception(f"Error converting 'after' protobuf to JSON: {e}")
            data_after = json.loads(jsone_after)

            acct_after   = data_after.get('AccountInfo', {})
            after_like   = int(acct_after.get('Likes', 0))
            player_uid   = int(acct_after.get('UID', 0))
            player_name  = str(acct_after.get('PlayerNickname', ''))
            player_region = str(acct_after.get('PlayerRegion', region))   # ⭐ Player region (fallback to requested region)
            try:
                player_level = int(acct_after.get('Levels', 0))
            except Exception:
                player_level = 0

            like_given = after_like - before_like
            status = 1 if like_given != 0 else 2

            result = {
                "LikesGivenByAPI":     like_given,
                "LikesafterCommand":   after_like,
                "LikesbeforeCommand":  before_like,
                "PlayerNickname":      player_name,
                "Level":               player_level,
                "Region":              player_region,   # ⭐ NEW
                "UID":                 player_uid,
                "status":              status,
                "credit":              "Zexxy"
            }
            return result

        result = zexxyh4x_process_request()
        return app.response_class(
            response=json.dumps(result),
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        app.logger.error(f"[Zexxy] Error processing request: {e}")
        return jsonify({"error": str(e)}), 500


# ═══════════════════════════════════════════════════════════════
#   START SERVER
# ═══════════════════════════════════════════════════════════════
if __name__ == '__main__':
    print(ZEXXY_BANNER)
    app.run(debug=True, use_reloader=False)
