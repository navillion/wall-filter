# Created by Navillion

import os
from flask import Flask, jsonify
from threading import Thread
from time import sleep as wait
import requests

# Set your variables in .ENV or Secrets
group = os.environ["group"]
cookie = os.environ["cookie"]
key = os.environ["key"]
webhook = os.environ["webhook"]

# Set your images for your webhook or leave blank ("")
webhookUsername = "set a username"
webhookImage = "image link here"

# Group Wall Filter List
FilterList = [
  "𝚁𝙾𝙱𝚄𝚇",
  "⬇️",
  "➡️",
  "𝐬𝐢𝐭𝐞",
  "💰",
  "Ⓡⓞⓑⓤⓧ",
  "𝑹𝑶𝑩𝑼𝑿",
  "💸",
  "𝗥𝗢𝗕𝗨𝗫",
  "https://www.roblox.com/games/",
  "https://www.roblox.com/groups/",
  "https://web.roblox.com/games/",
  "This is an official message from Roblox",
  "This is a official message from Roblox"
]


def GetToken():
  authurl = "https://auth.roblox.com/v2/logout"

  try:
    xcsrf = requests.post(authurl, cookies={'.ROBLOSECURITY': cookie}).headers["x-csrf-token"]
  except:
    print("No token error! Aborting")
    return None

  return xcsrf

def FilterWall():
  numberPosts = 25
  print(f"Checking top {numberPosts} posts for banned words")
  session = requests.Session()
  session.cookies[".ROBLOSECURITY"] = cookie

  xcsrf = GetToken()
  if not xcsrf:
    print("Session Failure: Failed to get token")
    return "Failed to get token"
  session.headers["X-CSRF-TOKEN"] = xcsrf
  session.headers["Content-Type"] = "application/json"

  
  robloxUrl = f"https://groups.roblox.com/v1/groups/{group}/wall/posts?limit={numberPosts}&sortOrder=Desc"
  response = session.get(robloxUrl)

  if response.status_code == 200:
    posts = response.json()["data"]
    for post in range(len(posts)):
      hasBannedWord = False
      detectedWord = None
      bodyText = posts[post]["body"]
      for filtered_word in FilterList:
        if bodyText.find(filtered_word) != -1:
          print(f"Found a banned word!: {filtered_word}")
          hasBannedWord = True
          detectedWord = filtered_word
          break
      if hasBannedWord:
        print(f"Banned word found in \'{bodyText}\'")
        postId = posts[post]["id"]
        username = posts[post]["poster"]["username"]
        userId = posts[post]["poster"]["userId"]

        deleteUrl = f"https://groups.roblox.com/v1/groups/{group}/wall/posts/{postId}"

        deleteResponse = session.delete(deleteUrl)
        if deleteResponse.status_code == 200:
          print("Deleted filtered message!")

          discordData = {
            "username":webhookUsername,
            "avatar_url":webhookImage,
            "content": "**Messaged Filtered from Group Wall!**",
            "embeds": [
              {
                "type": "rich",
                "title": f"{username}'s Message was Removed!",
                "description": f"**Message Body**\n```{bodyText}```\n**Filtered String:** `{detectedWord}`\n\n**Profile Link**\nhttps://www.roblox.com/users/{userId}/profile\n",
                "color": "16711902"
                
              }
            ]
          }

          
          requests.post(webhook, json = discordData)

    
        
        #print(deleteResponse.content)

    print(f"Checked {numberPosts} posts!")
  else:
    print(f"An error {response.status_code} occurred getting group wall posts: {response.content}")


def RunFilter():
  print("Run filter connected.")
  seconds = 0
  while True:
    wait(1)
    if seconds % 180 == 0:
      print(f"Been alive for {seconds/60} minutes!")
      FilterWall()
    seconds+=1