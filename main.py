import socket
from _thread import *
import sys
import random
import json
import time

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server = "localhost"
port = 5555
server_ip = socket.gethostbyname(server)
try:
    s.bind((server, port))
except socket.error as e:
    print(str(e))
mappath = "server/map.json"

mapData = []
map_ = json.load(open(mappath))
x, y = 0, 0
for i in map_:
    for k in i:
        if k == 1:
            mapData.append([x, y])
        x += 32
    x = 0
    y += 32

s.listen(10)
print("Waiting for a connection")

players = {}
bullets = {}


def movePlayer(x, y) -> bool:
    for mapx, mapy in mapData:
        if (
            x in range(mapx - 16, mapx + 32 + 16)
            and y in range(mapy - 16, mapy + 32 + 16)
            or x > 800 - 16
            or y > 600 + 16
            or x < 0 + 16
            or y < 0 + 16
        ):
            return False
    return True


def threaded_client(conn, addr):
    global players
    players[
        str(addr)
    ] = f"name:{addr}||id:{addr}||x:{random.randint(0, 800)}||y:{random.randint(0, 600)}||health:100||rotation:0"
    conn.send(str.encode(players[str(addr)]))
    while True:
        try:
            data = conn.recv(2048)
            reply = data.decode("utf-8")
            if not data:
                conn.send(str.encode("Goodbye"))
                break
            else:
                reply = reply.split("||")
                if reply[0].split(":")[1] == "get":
                    conn.send(str.encode(players[str(addr)]))

                elif reply[0].split(":")[1] == "update":
                    edit = reply[1].split(":")
                    shouldMove = movePlayer(int(edit[0]), int(edit[1]))
                    if shouldMove:
                        p = f"name:{addr}||id:{addr}||x:{edit[0]}||y:{edit[1]}||health:{edit[2]}||rotation:{edit[3]}"
                        players[str(addr)] = p
                        conn.send(str.encode(p))
                    else:
                        conn.send(str.encode(players[str(addr)]))

                elif reply[0].split(":")[1] == "get_all":
                    conn.send(str.encode(str(players)))

                elif reply[0].split(":")[1] == "get_map":
                    gameMap = str(json.load(open(mappath)))
                    print(gameMap)
                    conn.send(str.encode(gameMap))

                elif reply[0].split(":")[1] == "shoot":
                    data = reply[1].split(":")
                    x, y = (
                        players[str(addr)].split("||")[2].split(":")[1],
                        players[str(addr)].split("||")[3].split(":")[1],
                    )
                    if str(addr) in bullets:
                        if len(bullets[str(addr)]) < 10:
                            bullets[str(addr)].append(f"name:{addr}||x:{x}||y:{y}")
                    else:
                        bullets[str(addr)] = [f"name:{addr}||x:{x}||y:{y}"]
                    print(bullets)
                    conn.send(str.encode(str(bullets[str(addr)])))

                elif reply[0].split(":")[1] == "get_bullets":
                    conn.send(str.encode(str(bullets)))
        except Exception as e:
            print(e)
            break

    print("Connection Closed")
    conn.close()
    players.pop(str(addr))
    if str(addr) in bullets:
        bullets.pop(str(addr))


while True:
    conn, addr = s.accept()
    print("Connected to: ", addr)
    start_new_thread(threaded_client, (conn, addr))
