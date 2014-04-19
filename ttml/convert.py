#!/usr/bin/python
# -*- coding: utf-8 -*-
'''

convert.py
on-three
Friday, April 18th 2014

Convert an (NHK specific?) .ttml file to a more usable format (.ass or .srt)

Currently only an .ass is dumped. .Srt is lacking

Example of the NHK format is below. It might be very unique, so this code
is probably of use to no one but myself.

<cuepoints x="170" y="450" font="ＭＳ ゴシック,Osaka−等幅,ヒラギノ角ゴ ProW3,Osaka" color="0xffffff" size="36" underline="false" bold="false" italic="false" ruby="false">
<cuepoint name="1" time="2.967"/>
<cuepoint name="2" time="3">
<subtitle id="201" x="210" y="450" xx="210" yy="560" background="0x000000" opacity="0.5" lang="jpn" letterspacing="4" substitution_string="♪" gaiji_pattern="000000000000000000000000F000000FFF00001FFFF00003FFF300003FE0300003800300003000300003007F000033FFF00003FFFF00003FF8300003C00300003000300003000300003000300003000300003000300003000300003000300003000300003000700003001F00003003F0000F007F0003F00FE0007E00FE000FE01FC001FC01F8001FC00F0003F80060003F00000001E00000000C0000000000000000" gaiji_width="36" gaiji_height="36" width="44" height="40">
<![CDATA[　]]>
</subtitle>
<subtitle id="202" x="254" y="450" xx="254" yy="560" background="0x000000" opacity="0.5" lang="jpn" letterspacing="4" width="67" height="40">
<![CDATA[｢お]]>


'''
from __future__ import print_function
from datetime import datetime
from bs4 import BeautifulSoup
import re
import argparse
import os
import codecs
import time
import datetime


def get_ext(filename):
  '''Get extension to normal file
  '''
  f, e = os.path.splitext(filename)
  return e.lower()

def to_ass_time(seconds_ms):
  '''convert strictly seconds string (may have fractional part)
    to a standard .ass file time: 00:00:33,381 --> 00:00:36,384
  '''
  m = '0'
  s = seconds_ms
  if '.' in seconds_ms:
    (s, m) = seconds_ms.split('.')
  sec = int(s)
  milliseconds = int(m)
  days = sec / 86400
  sec -= 86400*days

  hrs = sec / 3600
  sec -= 3600*hrs

  mins = sec / 60
  sec -= 60*mins

  return u'{h:02d}:{m:02d}:{s:02d},{ms:03d}'.format(h=hrs, m=mins, s=sec, ms=milliseconds)
  

class Style(object):
  def __init__(self):
    self.color = 0xffffff
    self.size = 36
    self.underline = False
    self.bold = False
    self.italic = False
    self.ruby = False
    self.font = 'ＭＳ ゴシック,Osaka−等幅,ヒラギノ角ゴ ProW3,Osaka'
    self.x = 170
    self.y = 450

class Scaling(object):
  '''Describe scaling from one screen resolution to another
  '''
  def __init__(self, initial_w, initial_h, final_w, final_h):
    self.iw = initial_w
    self.ih = initial_h
    self.fw = final_w
    self.fh = final_h

  def scale(self, x, y):
    '''Scale given x,y from inital to final screen coordinates 
    '''
    scale_w = self.fw/self.iw
    scale_h = self.fh/self.ih
    return (x*scale_w, scaled_y*scale_h)

class Subtitle(object):
  '''Encapsultate a given subtitle text and its format 
  '''
  def __init__(self, text, x=0, y=0, style=None):
    pass

def ConvertToAss(content, outfile_name):
  pass

def ConvertToSrt(content, outfile_name):
  '''Convert an NHK .ttml input file (contents string) to srt
  :param infile: string contents of input .ttml file 
  :type infile: str
  '''
  outfile = codecs.open(outfile_name,'w',encoding='utf8')
  soup = BeautifulSoup(content, features="xml")

  cuepoints = soup.cuepoints
  captions = cuepoints.find_all('cuepoint')

  caption_id = 1
  for i, caption in enumerate(captions[:-1]):
    #we need next caption to interpret the display time
    next_caption_time = captions[i+1]['time']
    #print caption.time
    subtitles = caption.find_all('subtitle')
    if not subtitles: continue

    #each .srt entry is designated by a identifier
    print(u'{id}'.format(id=caption_id), file=outfile)
    caption_id += 1

    #.ass time display
    #00:00:33,381 --> 00:00:36,384
    start_time_s = to_ass_time(caption['time'])
    end_time_s = to_ass_time(next_caption_time)
    print(u'{s} --> {e}'.format(s=start_time_s, e=end_time_s), file=outfile)
    
    #form caption text from 'subtitle' entries
    caption_text = u''
    for s in subtitles:
      blurb= s.contents[0].strip()
      #this subtitle may be a "gaiji" (actually DRCS) character. If so we'll just use the
      #provided substitution string
      blurb = s.get('substitution_string', blurb)
      
      if s.get('ruby', u'false') == u'false':
        print(blurb, file=outfile)
      else:
        pass
      '''
      print (u'{x},{y},{color},{background},{opacity},{ruby}-->{text}'.format(x=s['x'],
        y=s['y'], 
        color=s.get('color',u'0xffffff'),
        background=s['background'],
        opacity=s['opacity'],
        ruby=s.get('ruby', u'false'),
        text=blurb,), file=outfile)
      '''
    print(u'\n', file=outfile)

'''
Map output filetype extensions to output file converters
'''
SUPPORTED_OUTPUT_FILETYPES = {
  '.ass' : ConvertToAss,
  '.srt' : ConvertToSrt,
}


def main():
  parser = argparse.ArgumentParser(description='Convert (NHK?) .ttml closed caption file to another format.')
  parser.add_argument('infile', help='Input NHK .ttml source file.', type=str)
  parser.add_argument('-o', '--outfile', help='Output filename with extension. If supported extenstion is not present (.ass or .srt) a .srt file using input argument filename will be generated.', type=str, default=None)
  args = parser.parse_args()

  infile = args.infile
  outfile = '{infile}.srt'.format(infile=infile)
  if args.outfile:
    #check to see if user specified output filename has .mp4 extention
    outfile = args.outfile
    if get_ext(outfile) not in SUPPORTED_OUTPUT_FILETYPES:
      print('Sorry, unsupported file extension in output file.')
      return -1

  ext = get_ext(outfile)
  conversion_impl = SUPPORTED_OUTPUT_FILETYPES[ext]

  content_file = open(infile, 'r')
  content = content_file.read()
  return conversion_impl(content, outfile)
        

if __name__ == "__main__":
  main()
