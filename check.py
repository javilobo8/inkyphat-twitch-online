#!/usr/bin/python
import requests, json, sys, inkyphat, os
from time import gmtime, strftime
from PIL import Image, ImageFont, ImageDraw

config = {
  'MAX_CHANNELS': 8,
  'INVERTED': False,
  'FOREGROUND_COLOR': inkyphat.BLACK,
  'BACKGROUND_COLOR': inkyphat.WHITE,
  'FONT': 'visitor1.ttf',
}

if config['INVERTED']:
  aux = config['FOREGROUND_COLOR']
  config['FOREGROUND_COLOR'] = config['BACKGROUND_COLOR']
  config['BACKGROUND_COLOR'] = aux

__DIRNAME__ = os.path.dirname(os.path.abspath(__file__))

# Print constants
IMG_WIDTH = 212
IMG_HEIGHT = 104
IMG_SIZE = (IMG_WIDTH, IMG_HEIGHT)
TITLE = 'TWITCH ONLINE'
FONT_PATH = os.path.join(__DIRNAME__, 'fonts', config['FONT'])
FONT_SIZE = 10
MARGIN = 1
MARGIN_TOP = FONT_SIZE + MARGIN * 2

# Global
STATE = []
ARGUMENTS = sys.argv
ARGUMENTS.pop(0)
CLIENT_ID = ARGUMENTS.pop(0)
CHANNELS = ARGUMENTS

if len(CLIENT_ID) != 30:
  print 'Error: first argument Client-ID must be a string of 30 characters'
  sys.exit(1)

if len(CHANNELS) > config['MAX_CHANNELS']:
  print 'Error: Maximum channels is ' + str(config['MAX_CHANNELS'])
  sys.exit(1)

print 'Init'
NOW = strftime("%m/%d %H:%M", gmtime())

for channel in CHANNELS:
  sys.stdout.write('Loading '+channel+'...')
  response = requests.get('https://api.twitch.tv/kraken/streams/' + channel, headers={'Client-ID': CLIENT_ID})
  data = json.loads(response.text)
  online = data['stream'] != None

  item = {}
  item['channel'] = channel
  item['online'] = online
  if online:
    item['viewers'] = data['stream']['viewers']
  STATE.append(item)
  sys.stdout.write('Done\n')

img = Image.new('RGBA', IMG_SIZE)
fnt = ImageFont.truetype(FONT_PATH, FONT_SIZE)

title_text_w, title_text_h = fnt.getsize(TITLE)
date_text_w, date_text_h = fnt.getsize(NOW)

DATE_POSITION = ((IMG_WIDTH - date_text_w - MARGIN*2), MARGIN)
TITLE_POSITION = (MARGIN*2, MARGIN)

inkyphat.set_rotation(180)
inkyphat.set_border(config['FOREGROUND_COLOR'])
inkyphat.rectangle((0, 0, IMG_WIDTH, IMG_HEIGHT), fill=config['BACKGROUND_COLOR'])

inkyphat.rectangle((0, 0, IMG_WIDTH, MARGIN_TOP - MARGIN), fill=config['FOREGROUND_COLOR'])
inkyphat.text(DATE_POSITION, NOW, font=fnt, fill=config['BACKGROUND_COLOR'])
inkyphat.text(TITLE_POSITION, TITLE, font=fnt, fill=config['BACKGROUND_COLOR'])

index = 0
for stream in STATE:
  magic = (MARGIN*2)
  right_offset = 40
  text_x = MARGIN * 3 + FONT_SIZE + right_offset
  text_y = MARGIN_TOP + (FONT_SIZE + MARGIN) * index + magic

  circle_x1 = MARGIN + right_offset
  circle_y1 = text_y + 2 - magic
  circle_x2 = MARGIN + FONT_SIZE - 2 + right_offset
  circle_y2 = text_y + FONT_SIZE - magic
  circle_fill = config['BACKGROUND_COLOR']

  if stream['online']:
    circle_fill = config['FOREGROUND_COLOR']
    viewers = str(stream['viewers'])
    viewers_text_w, viewers_text_h = fnt.getsize(viewers)
    viewers_x = right_offset - MARGIN - viewers_text_w
    viewers_y = text_y
    inkyphat.text((viewers_x, viewers_y), viewers, font=fnt, fill=config['FOREGROUND_COLOR'])

  inkyphat.ellipse((circle_x1, circle_y1, circle_x2, circle_y2), fill=circle_fill, outline=config['FOREGROUND_COLOR'])
  inkyphat.text((text_x, text_y), stream['channel'].upper(), font=fnt, fill=config['FOREGROUND_COLOR'])
  index += 1

print 'Printing...'
inkyphat.show()
print 'Done!'
