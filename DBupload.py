###########################
## Author: AHgpyxA (c) 2009    #
## ICQ: 705093                 #
## E-mail: spargo32@gmail.com  #
## http://kustarnik.com        #
##                             #
## special for http://DBwap.ru #
############################
##           ______            #
##        .-"      "-.         #
##       /            \        #
##      |              |       #
##      |,  .-.  .-.  ,|       #
##      | )(__/  \__)( |       #
##      |/     /\     \|       #
##      (_     ^^     _)       #
##       \__|IIIIII|__/        #
##        |-\IIIIII/-|         #
##        \          /         #
##         `--------`          #
##                             #
## !!! All Rights Reserved !!! #
############################

version = '2.0'

import debugger
debugger.name=u'AHgpyxA'
debugger.email = u'spargo32@gmail.com'
debugger.comment = 'DBupload %s'%version

#--------------------------------
#--------------------------------
#--------------------------------
import appuifw2 as ui
ui.note(u'Loading...')
import e32, os
from sys import argv
import clipboard as cb
import lite_fm, progressbartw, time
import httplib, urllib
import md5, base64, zlib
import sysinfo


import keycapture as kc
c=None
#--------------------------------
#--------------------------------
#--------------------------------
def ru(x): return x.decode("utf-8")
def ur(x): return x.encode("utf-8")
(w, h,) = sysinfo.display_pixels()

def write_log(mess):
  try: mess = ru(mess)
  except: pass
  fl = open('D:\\dbupload_log.txt','a')
  fl.write(mess.encode('windows-1251')+'\n')
  fl.close()

#--------------------------------
#--------------------------------
#--------------------------------
# filenames

if e32.s60_version_info[0]<3:
  # os 7-8.1
  fn_dir = ru(os.path.split(argv[0])[0]+'\\')
else:
  #os 9.x
  fn_dir = u'C:\\System\\data\\dbupload\\'

fn_mail = fn_dir+u'upl_mail.ini'
fn_links = fn_dir+u'upl_links.ini'
fn_rek = fn_dir+u'upl_rek.ini'
# server data
host = 'io.dbwap.ru'
url = '/iod.php'
rek_url = 'http://io.dbwap.ru/rek.php'

#--------------------------------
#--------------------------------
#--------------------------------
def printout(mess, color=None, style=None, font=None, newline=True):
  global default_text_color
  
  try: mess=ru(mess)
  except: pass
  
  if color != None: ui.app.body.color = color
  else: ui.app.body.color = default_text_color
  if style != None: ui.app.body.style = style
  else: ui.app.body.style = 0
  if font != None: ui.app.body.font = font
  else: ui.app.body.font = u'LatinPlain12'
  
  ui.app.body.set_pos(ui.app.body.len())
  ui.app.body.add(mess)
  if newline: ui.app.body.add(u"\n")
  e32.ao_yield()

#--------------------------------
#--------------------------------
#--------------------------------
def exit():
  global lock
  print "Bye..."
  if ui.query(ru('Выход?'),'query')==1:
    lock.signal()
    os.abort()

#--------------------------------
#--------------------------------
#--------------------------------
def send_data(url, page, params="", method="POST"):
  headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain", "User-Agent": "Mozilko/6.66"}
  conn = httplib.HTTPConnection(url)
  conn.request(method, page, params, headers)
  e32.ao_yield()
  response = conn.getresponse()
  response = response.read()
  conn.close()
  return response

#--------------------------------
#--------------------------------
#--------------------------------
def cancel_upload():
  tmp=open('d:\\DBupload_cancel.tmp', 'w')
  tmp.write('stop this!')
  tmp.close()
  ui.note(ru('Отправка будет прервана после отправки очередной части файла.'))

#--------------------------------
#--------------------------------
#--------------------------------
def upload_file_to_url():
  global description, email, pwd, filename, menu
  
  if (os.path.isfile('d:\\DBupload_cancel.tmp')==1):
    os.unlink('d:\\DBupload_cancel.tmp')
  
  if filename=='' or filename==None:
    ui.note(ru('Сначала выберите файл!'),'error')
    return False
  
  ui.app.menu = [(ru('отменить'), cancel_upload)]
  
  description = description.replace('\n','<BR>')
  
  fd=open(filename,'rb').read()
  filehash = md5.md5(fd).hexdigest()
  filesize = len(fd)
  fl=open(filename,'rb')

  size=0
  file_info = base64.encodestring('%s::::%s::::%s::::%s'%(ur(description),ur(email),ur(pwd),filesize))

  global pbar
  pbar.set_fonts(text_font = 'dense',text_color=0x0,percent_font = 'normal',percent_color=0xef0000)
  pbar.set_colors(bar_color=0x0000ff,rect_color=0x0, back_color=0xffffff)
  pbar.set_window_attr(corner_type = 'square',shadow = 0)
  pbar.begin_progress(100, ru("Загрузка..."))
  pbar.set_window_size((160,36))
  pbar.do_progress(0)
  
  write_log('получаем рекламу')
  rek=urllib.urlopen(rek_url).read()
  if rek!='' and rek.find('<body')==-1:
    f=open(fn_rek,'w')
    f.write(ru(rek))
    f.close()
  
  check_update(False)
  
  params = urllib.urlencode(
    {
      'filename':   os.path.split(filename)[1], #filename
      'file_hash':  filehash, #md5-hash
      'file_info':  file_info, #file_descr,email,pwd,file_size
      'flag':       'upload_start',
      'imei':       sysinfo.imei()[6:]
    }
  )

  write_log('посылаем начальный запрос [%s]'%unicode(params))
  
  response = send_data(host, url, params).replace('\n','').split('##')
  
  write_log('получаем ответ [%s]'%unicode(response))
  
  if response[0]=='ERR':
    ui.note(ru(response[1]))
    pbar.hide()
    ui.app.menu = menu
    write_log('типа ошибка')
    pbar.end_progress()
    pbar.hide()
    return False
  elif response[0]=='RETR':
    size=int(response[1])
    write_log('сервер просит отправлять, начиная с %s байта'%unicode(size))
    part=fl.read(size)
    write_log('переходим к байту N%s'%unicode(size))
  elif response[0]=='OK':
    url0=response[1]
    url1=url0[:url0.rfind('/')]
    write_log('типа всё')
    pbar.do_progress(100)
    if cb.Set(url1)==1: ui.note(ru('УРЛ файла скопирован в буфер.'))
    links=open(fn_links,'a')
    links.write('%s@#@#%s@#@#%s@#@#%s\n'%(os.path.split(filename)[1],filesize,url1[url1.rfind('/')+1:],url0[url0.rfind('/')+1:]))
    links.close()
    response[1]=filesize
  else:
    write_log('сервер дал незапланированный ответ [%s]'%unicode(response))
    ui.note(ru('Не получено подтверждение от сервера! Рекомендуется повторить отправку файла!'))
    pbar.hide()
    ui.app.menu = menu
    return False
  
  pbar.begin_progress(100, ru('Отпр.: %s из %s Кб'%(size/1024,filesize/1024)))
  pbar.do_progress(int(size)*100/int(filesize))
  
  part=fl.read(part_size)
  write_log('читаем очередной кусок')
  size+=len(part)
  write_log('считаем, что отправлено %s байт'%unicode(size))
  
  while True:
    if (os.path.isfile('d:\\DBupload_cancel.tmp')==1):
      if ui.query(ru('Прервать отправку файла?'),'query')==1:
        os.unlink('d:\\DBupload_cancel.tmp')
        break
    
    #if len(part)<part_size: finish_flag='upload_finish'
    if size>=filesize:
      size=filesize
      finish_flag='upload_finish'
    else: finish_flag='upload_continue'

    params = urllib.urlencode(
      {
        'filename':   os.path.split(filename)[1], #filename
        'file_hash':  filehash, #md5-hash
        'file_send':  size,  # orpravleno vsego
        'part':       base64.encodestring(part), # part of file to send
        'flag':       finish_flag, # finish
        'imei':       sysinfo.imei()[6:]
        }
      )
    
    prms = urllib.urlencode( {
        'filename':   os.path.split(filename)[1], #filename
        'file_hash':  filehash, #md5-hash
        'file_send':  size,  # orpravleno vsego
        'part':       '_part_of_file_', # part of file to send
        'flag':       finish_flag, # finish
        'imei':       sys.imei()[6:]
        } )
    write_log('посылаем очередной запрос [%s]'%unicode(prms))
    
    response = send_data(host, url, params).replace('\n','').split('##')
    
    write_log('получаем ответ [%s]'%unicode(response))
    
    if response[0]=='ERR':
      ui.note(ru(response[1]))
      pbar.hide()
      ui.app.menu = menu
      write_log('типа ошибка')
      pbar.end_progress()
      pbar.hide()
      return False
    elif response[0]=='RETR':
      response[1]=int(response[1])
      pbar.begin_progress(100, ru('Отпр.: %s из %s Кб'%(response[1]/1024,filesize/1024)))
      pbar.do_progress(int(response[1])*100/int(filesize))
      write_log('сервер просит отправлять, начиная с %s байта'%unicode(response[1]))
    elif response[0]=='OK':
      url0=response[1]
      url1=url0[:url0.rfind('/')]
      write_log('типа всё [%s]'%unicode(response))
      pbar.do_progress(100)
      if cb.Set(url1)==1: ui.note(ru('УРЛ файла скопирован в буфер.'))
      links=open(fn_links,'a')
      links.write('%s@#@#%s@#@#%s@#@#%s\n'%(os.path.split(filename)[1],filesize,url1[url1.rfind('/')+1:],url0[url0.rfind('/')+1:]))
      links.close()
      response[1]=filesize
    else:
      write_log('сервер дал незапланированный ответ [%s]'%unicode(response))
      ui.note(ru('Не получено подтверждение от сервера! Рекомендуется повторить отправку файла!'))
      pbar.hide()
      ui.app.menu = menu
      return False
    
    write_log('читаем очередной кусок')
    part=fl.read(part_size)
    size+=len(part)
    write_log('считаем, что отправлено %s байт'%unicode(size))
    if len(part)==0: 
      write_log('если размер последнего куска = 0, то прерываемся')
      break
  
  pbar.end_progress()
  pbar.hide()
  ui.app.menu = menu

#--------------------------------
#--------------------------------
#--------------------------------
def back():
  global description, view, c
  if view == 'description':
    description = ui.app.body.get()
  main()
  c=None
  ui.app.focus=None

#--------------------------------
#--------------------------------
#--------------------------------
def input_email():
  global email
  e=ui.query(ru('e-mail'),'text',email)
  if e!=None:
    email=e
    f=open(fn_mail,'w+')
    f.write(email)
    f.close()

#--------------------------------
#--------------------------------
#--------------------------------
def input_pass():
  global pwd
  e=ui.query(ru('Password'),'text',pwd)
  if e!=None: pwd=e
  else: pwd=u''

#--------------------------------
#--------------------------------
#--------------------------------
def input_descr():
  global description, view
  view = 'description'
  if e32.s60_version_info[0]>=3:
    ui.app.body = ui.Text(skinned=True, scrollbar=True, word_wrap=True, t9=True, indicator=True)
  else:
    ui.app.body = ui.Text(skinned=False, scrollbar=True, word_wrap=True, t9=True, indicator=True)
  ui.app.title=ru('Описание файла')
  printout(description)
  ui.app.exit_key_handler=back
  ui.app.menu = [
    (ru('сохранить'), back)
  ]

#--------------------------------
#--------------------------------
#--------------------------------
def copy_url(file):
  cb.Set(u'http://dbwap.ru/%s'%file)
  ui.note(ru('URL скопирован в буфер обмена'))

#--------------------------------
#--------------------------------
#--------------------------------
#http://io.dbwap.ru/dow.php?file=639511
def down_progress(a, b, c):
  if a*b>=c:
    pbar.do_progress(100)
    pbar.begin_progress(100, ru('Загр.: %s из %s Кб'%(c/1024,c/1024)))
    pbar.end_progress()
    pbar.hide()
  else:
    #pbar.do_progress(a*b*100/c)
    pbar.begin_progress(100, ru
('Загр.: %s из %s Кб'%(a*b/1024,c/1024)))
    pbar.do_progress(a*b*100/c)
def download(file=None,pw=None):
  if file==None:
    file = ui.query(ru('Введите номер файла'),'number')
  if file==None:
    ui.note(ru('Выбор отменен.'))
    return
  params={'file': int(file),'imei': sysinfo.imei()[6:]}
  if pw != None:
    params['pass']=pw
  params=urllib.urlencode(params)
  write_log(host+'/dow.php'+'?'+params)
  resp = send_data(host,'/dow.php',params).replace('\n','').split('##')
  write_log(unicode(resp))

  if resp[0]=='DL':
    if resp[1]=='OK':
      t=resp[2].split('/')
      t=t[len(t)-1]
      if resp[3]=='': resp[3]='-'
      if int(resp[4])>1024*1024: resp[4]=('%sМб'%round(int(resp[4])/1024/1024.0,1))
      elif resp[4]>1024: resp[4]=('%sКб'%round(int(resp[4])/1024.0,1))
      else: resp[4]=('%sбайт'%resp[4])
      if ui.query(ru('Файл: %s\nОписание: %s\nРазмер: %s'%(t,resp[3],resp[4])),'query') != None:
        global pbar
        pbar.set_fonts(text_font = 'dense',text_color=0x0,percent_font = 'normal',percent_color=0xef0000)
        pbar.set_colors(bar_color=0x0000ff,rect_color=0x0, back_color=0xffffff)
        pbar.set_window_attr(corner_type = 'square',shadow = 0)
        pbar.begin_progress(100, ru("Загрузка..."))
        pbar.set_window_size((160,36))
        urllib.urlretrieve(resp[2],'e:\\Downloads\\%s'%t,down_progress)
    elif resp[1]=='PASS':
      pw = ui.query(ru('Введите пароль'),'text')
      if pw==None:
        ui.note(ru('Выбор отменен.'))
        return
      download(file,pw)
    else:
      ui.note(ru('Ошибка: %s'%resp[2]))
  else:
    ui.note(ru('Неизвестная ошибка!'),'error')
    write_log(unicode(resp))

#--------------------------------
#--------------------------------
#--------------------------------
def delete_file(x,y,c):
  params=urllib.urlencode({'file': int(x), 'del': int(y),'imei': sysinfo.imei()[6:]})
  write_log(host+url+'?'+params)
  resp = send_data(host,url,params).replace('\n','').split('##')
  write_log(unicode(resp))
  if resp[0]=='DEL':
    if resp[1]=='OK':
      ui.note(ru('Файл удален.'))
      f=open(fn_links,'r')
      links=f.readlines()
      f.close()
      f=open(fn_links,'w')
      for i in range(len(links)):
        if len(links)-i-1 != c: f.write(links[i])
      f.close()
    else:
      ui.note(ru('Ошибка: %s'%resp[2]))
      if ui.query(ru('Скорее всего файл отсутствует на сервере. Удалить файл из списка?'),'query')!=None:
        f=open(fn_links,'r')
        links=f.readlines()
        f.close()
        f=open(fn_links,'w')
        for i in range(len(links)):
          if len(links)-i-1 != c: f.write(links[i])
        f.close()
  else:
    ui.note(ru('Неизвестная ошибка!'),'error')
    write_log(unicode(resp))
#--------------------------------
#--------------------------------
#--------------------------------
def view_uploaded():
  global view
  view = 'uploaded'
  try:
    f=open(fn_links,'r')
    links=f.readlines()
    links.reverse()
    f.close()
  except:
    links=[]

  for i in range(len(links)): links[i]=links[i].split('@#@#')
  lb=ui.Listbox2(double=True)
  lb.begin_update()
  lb.extend([ui.Item(title=ru(x[0]), subtitle=ru('%s байт'%x[1])) for x in links])
  lb.end_update()
  lb.set_empty_list_text(ru('нет файлов'))
  ui.app.body=lb
  ui.app.title=ru('Ваши файлы')
  ui.app.exit_key_handler=back
  if len(lb)>0:  ui.app.menu = [
    (ru('копировать'), lambda:copy_url(links[lb.current()][2])),
    (ru('удалить'), lambda:delete_file(links[lb.current()][2],links[lb.current()][3],lb.current())),
    (ru('назад'), back)
  ]
  else: ui.app.menu = []

#--------------------------------
#--------------------------------
#--------------------------------
def select_file():
  global filename
  
  write_log('начало выбора файла')
  
  ui.app.title=ru('Выбор файла')
  filename = lite_fm.manager()
  if filename==None:
    ui.note(ru('Выбор файла отменён'))
    write_log('отмена выбора файла')
    return False
  
  redraw()
  write_log('файл выбран: %s'%filename)
  ui.app.title=ru('DBupload %s'%version)

#--------------------------------
#--------------------------------
#--------------------------------
def redraw(rect=None):
  global canv, im, im2, rekl, filename, description, pwd
  im2.clear(0x92C415)
  im2.blit(im)
  im2.text((2,h/3.47),rekl[0],rekl[1])
  if filename!=None: d=ru('Файл: Выбран')
  else: d=ru('Файл: Не выбран')
  im2.text((2,h/2.6),d)
  if len(description)>0: d=ru('Описание: Задано')
  else: d=ru('Описание: Не задано')
  im2.text((2,h/2.08),d)
  if len(pwd)>0: d=ru('Пароль: Установлен')
  else: d=ru('Пароль: Не установлен')
  im2.text((2,h/1.73),d)
  canv.blit(im2)
  
def main():
  global menu, canv, rekl
  
  #if e32.s60_version_info[0]>=3: ui.app.body = ui.Text_display(skinned=True, scrollbar=True, scroll_by_line=False)
  #else: ui.app.body = ui.Text_display(skinned=False, scrollbar=True, scroll_by_line=False)
  
  ui.app.title=ru('DBupload %s'%version)
  
  try:
    f=open(fn_rek,'r')
    rek=ru(f.read())
    f.close()
    if rek=='': rek=ru('DBwap.ru - лучший файлообменник!')
  except:
    rek=ru('DBwap.ru - лучший файлообменник!')
  
  clr=unicode(int(time.time()))[2:]
  clr2=u''
  for i in range(len(clr)): clr2 = clr[i]+clr2
  clr2=int(clr2)
  while int(clr2)>256*256*256: clr2=clr2/2
  rekl=[rek,clr2]
  
  canv = ui.Canvas(redraw)
  ui.app.body = canv
  
  redraw()
  
  ui.app.exit_key_handler=exit
  
  ui.app.menu = menu

#--------------------------------
#--------------------------------
#--------------------------------

class Egg:
  def __init__(s):
    from graphics import Image
    import random
    s.r=random
    s.block_size=w/5/10*10
    s.p_size=h/s.block_size+1
    s.cx=1
    s.speed=0.5
    s.score=0
    s.nn=0
    s.crash=False
    s.p=[]
    for x in range(s.p_size): s.p.append([0,0,0])
    s.im=Image.new((w,h))
    s.c=ui.Canvas(s.show)
    ui.app.body=s.c
    ui.app.screen='full'
    ui.app.exit_key_handler=s._exit_
    s.c.bind(52,lambda:s.step(-1))
    s.c.bind(54,lambda:s.step(1))
    s.l=e32.Ao_lock()
    s.t=e32.Ao_timer()
    s.colors=[0x0,0xff90,0xff6a00,0xb6ff00,0x6a6a00,0xffff,0xffa500,0x3aa500,0x3a00a3,0x5e3ba0,0xffffff,0xff00]
  def _exit_(s):
    s.t.cancel()
	if e32.s60_version_info[0]<3:
      switch(True)
    s.l.signal()
  def step(s,x):
    if s.cx+x<=2 and s.cx+x>=0: s.cx+=x
    s.show()
  def move(s):
    if s.crash:
      ui.note(u'You crashed the car!')
      s.c.bind(52,None)
      s.c.bind(54,None)
      return False
    s.nn=(s.nn+1)%3
    s.score+=1
    if s.score%100==0: s.speed=s.speed*0.9
    for i in range(s.p_size-1,0,-1):
      s.p[i]=s.p[i-1]
    if s.nn==0:
      fig=s.r.randint(1,6)
      if fig==1:   f=[0, 0, s.r.randint(1,len(s.colors)-1)]
      elif fig==2: f=[0, s.r.randint(1,len(s.colors)-1), 0]
      elif fig==3: f=[s.r.randint(1,len(s.colors)-1), 0, 0]
      elif fig==4: f=[0, s.r.randint(1,len(s.colors)-1), s.r.randint(1,len(s.colors)-1)]
      elif fig==5: f=[s.r.randint(1,len(s.colors)-1), s.r.randint(1,len(s.colors)-1), 0]
      elif fig==6: f=[s.r.randint(1,len(s.colors)-1), 0, s.r.randint(1,len(s.colors)-1)]
      s.p[0]=f
    else:
      s.p[0]=[0, 0, 0]
    s.t.after(s.speed,s. move)
    s.show()

  def show(s,rect=None):
    s.im.clear(0xffffff)
    s.im.rectangle((0,0,3*s.block_size+1,s.p_size*s.block_size+1),0x404040,0x404040)
    s.im.text((3*s.block_size+3,h/10.4),u'Score: %s'%s.score,0x0)
    s.im.text((3*s.block_size+3,h/5.2),u'Speed: %s'%(200*(1-s.speed)),0x0)
    s.im.text((3*s.block_size+3,h/2.6),u'4 - move left',0x0)
    s.im.text((3*s.block_size+3,h/2.08),u'6 - move right',0x0)
    for i in range(s.p_size):
      s.im.rectangle((s.block_size-1,i*s.block_size+(2-s.nn)*s.block_size/3,s.block_size+2,i*s.block_size+s.block_size/3+(2-s.nn)*s.block_size/3),0xffffff,0xffffff)
      s.im.rectangle((s.block_size*2-1,i*s.block_size+(2-s.nn)*s.block_size/3,s.block_size*2+2,i*s.block_size+s.block_size/3+(2-s.nn)*s.block_size/3),0xffffff,0xffffff)
    for i in range(s.p_size):
      for j in range(3):
        if s.p[i][j]==0:
          continue
        elif s.p[i][j]>0:
          try: col=s.colors[s.p[i][j]]
          except: col=0x999999
        if i==s.p_size-2 and j==s.cx:
          if s.p[i][j]>0:
            col=0xff0000
            s.crash=True
            s.c.bind(52,None)
            s.c.bind(52,None)
            #ui.note(u'You crashed the car!')
            s.draw_car(s.cx*s.block_size,(s.p_size-2)*s.block_size,0xff0000)
            s.c.blit(s.im)
            return
        s.draw_car(j*s.block_size,i*s.block_size,col)
    s.draw_car(s.cx*s.block_size,(s.p_size-2)*s.block_size,0x90ff)
    s.c.blit(s.im)
  def draw_car(s,x,y,c):
    if c==0xff0000:
      s.im.rectangle((x,y,x+s.block_size+1,y+s.block_size+1),c,c)
      return
    s.im.rectangle((x+w/44,y+h/41.6,x+w/6.77,y+h/19),0x0,0x0) # колёса передние
    s.im.rectangle((x+w/44,y+h/10.4,x+w/6.77,y+h/8),0x0,0x0) # колёса задние
    s.im.rectangle((x+w/25.1,y+h/104,x+w/7.65,y+h/7.17),c,c) # фюзеляж заливка
    s.im.polygon((x+w/29.3,y+h/69.3,x+w/29.3,y+h/7.7,x+w/25.1,y+h/7.43,x+w/22,y+h/7.17,x+w/8.38,y+h/7.17,x+w/7.65,y+h/7.7,x+w/7.65,y+h/69.3,x+w/8.38,y+h/20.8,x+w/22,y+h/20.8,x+w/29.3,y+h/69.3),0x0) # фюзеляж контур
    s.im.rectangle((x+w/19.5,y+h/7.43,x+w/13.5,y+h/7.17),0xff0000) # стопы
    s.im.rectangle((x+w/10.35,y+h/7.43,x+w/8.38,y+h/7.17),0xff0000)
    s.im.polygon((x+w/22,y+0,x+w/17.6,y+h/104,x+w/16,y+h/104,x+w/13.5,y+0),0xffdd00,0xffdd00) # фары
    s.im.polygon((x+w/11,y+0,x+w/9.77,y+h/104,x+w/9.26,y+h/104,x+w/8.38,y+0),0xffdd00,0xffdd00)
    s.im.line((x+w/19.5,y+h/52,x+w/19.5,y+h/23.11),0x0) # капот
    s.im.line((x+w/8.8,y+h/52,x+w/8.8,y+h/23.11),0x0)
    s.im.line((x+w/19.5,y+h/8,x+w/8.8,y+h/8),0x0) # антикрыло
    s.im.point((x+w/17.6,y+h/7.7),0x0)
    s.im.point((x+w/9.26,y+h/7.7),0x0)
    s.im.polygon((x+w/25.1,y+h/17.3,x+w/25.1,y+h/9.45,x+w/19.5,y+h/8.67,x+w/8.8,y+h/8.67,x+w/8,y+h/9.45,x+w/8,y+h/17.3,x+w/8.38,y+h/17.3,x+w/8.38,y+h/18.9,x+w/22,y+h/18.9,x+w/22,y+h/17.3,x+w/25.1,y+h/17.3),0x0) # крыша
    if c == 0xffffff:
      s.im.rectangle((x+w/22,y+h/13,x+w/11,y+h/10.4),0xff,0xff) # мигалка
      s.im.rectangle((x+w/11.7,y+h/13,x+w/8,y+h/10.4),0xff0000,0xff0000)
  def run(s):
    e32.ao_sleep(s.speed, s.move)
    s.l.wait()



def switch(fg):
  global c
  if fg: c.start()
  else: c.stop()
def egg(x):
  ui.note(ru('Ыыы'))
  old=[ui.app.body, ui.app.menu, ui.app.exit_key_handler,ui.app.screen]

  ui.app.menu = []
  if e32.s60_version_info[0]<3:
    switch(False)
  car=Egg().run()

  [ui.app.body, ui.app.menu, ui.app.exit_key_handler,ui.app.screen]=old

def about():
  global view
  view = 'about'
  if e32.s60_version_info[0]>=3:
    ui.app.body = ui.Text_display(skinned=True, scrollbar=True, scroll_by_line=False)
  else:
    ui.app.body = ui.Text_display(skinned=False, scrollbar=True, scroll_by_line=False)
  printout('Клиент для обменника dbwap.ru\nЗагрузка любых видов файлов!\nСкачка без любых проблем!\nhttp://dbwap.ru\n\n\n\nАвтор: АндрюхА\nICQ# 705093')
  ui.app.exit_key_handler=back
  if e32.s60_version_info[0]<3:
    ui.app.menu = [
      (ru('назад'), back)
    ]
    #easter egg
    #63586
    global c
    c=kc.KeyCapturer(egg)
    c.forwarding=1
    c.keys=[63586,8]
    c.start()
    ui.app.focus=switch
  else:
    ui.app.menu = [
      (ru('назад'), back),
      (ru('играть'), lambda: egg(1))
    ]


#--------------------------------
#--------------------------------
#--------------------------------
def convert_old_links():
  try:
    f=open(fn_links,'r')
    links=ru(f.read())
    f.close()
  except:
    links=u''
  if links.find(u'@#@#')==-1 and links!='':
   try:
    ui.note(ru('История загрузок в старом формате! Конвертирую...'))
    links=links.split(u'--------------\n')
    for i in range(len(links)-1):
      links[i]=links[i].split('\n')
      links[i]=links[i][0]+'@#@#'+links[i][1].split(': ')[1].split(' ')[0]+'@#@#'+links[i][3].split('/')[3]+'@#@#'+links[i][5].split('/')[4]+'@#@#'
    os.rename(fn_links,fn_links+'.old')
    f=open(fn_links,'w')
    for i in range(len(links)-1):
      f.write((links[i]+'\n'))
    f.close()
    ui.note(ru('Конвертация прошла успешно.'))
   except:
    ui.note(ru('Конвертация завершилась с ошибкой :('),'error')
    ui.note(ru('История загрузок будет очищена (копия сохранена)'),'error')
    f=open(fn_links,'w')
    f.close()

#--------------------------------
#--------------------------------
#--------------------------------
#http://io.dbwap.ru/update.php?ver=CLIENT_VERSION&imei=IMEI
# UPD##NEWEST
# UPD##NEW##АКТУАЛЬНАЯ_ВЕРСИЯ##РАЗМЕР_НОВЫХ_ФАЙЛОВ##УРЛЫ_РАЗДЕЛЁННЫЕ_ЗНАКОМ_@@_ДВЕСОБАКИ
def check_update(alarm = True):
  global version, fn_dir
  params=urllib.urlencode({'ver': version,'imei': sysinfo.imei()[6:]})
  write_log(host+'/update.php'+'?'+params)
  resp = send_data(host,'/update.php',params).replace('\n','').split('##')
  write_log(unicode(resp))
  if resp[0]=='UPD':
    if resp[1]=='NEWEST':
      if alarm:
        ui.note(ru('У Вас самая свежая версия'))
      return
    elif resp[1]=='NEW':
      if int(resp[3])>1024*1024: resp[3]=('%sМб'%round(int(resp[3])/1024/1024.0,1))
      elif resp[3]>1024: resp[3]=('%sКб'%round(int(resp[3])/1024.0,1))
      else: resp[3]=('%sбайт'%resp[3])
      if ui.query(ru('Актуальная версия: %s\nРазмер: %s\nСкачать?'%(resp[2],resp[3])),'query')!=None:
        ui.note(ru('Качаю'))
        urllib.urlretrieve(resp[4],'%s%s'%(fn_dir,u'update.zip'),down_progress)
        ui.note(ru('Скачал'))
        #ui.note(ru('Распаковываю'))
        #from zipfile import ZipFile
        #z=ZipFile(fn_dir+u'update.zip')
        #for i in range(len(z.filelist)):
          #ui.note(unicode(z.filelist[i].filename))
          #a=z.read(z.filelist[i].filename)
          #f=open(fn_dir+z.filelist[i].filename,'wb')
          #f.write(a)
          #f.close()
        ui.note(ru('Перезапустите программу!'))
      return
    else:
      ui.note(ru('Неизвестная ошибка!'),'error')
      write_log(unicode(resp))
  else:
    ui.note(ru('Неизвестная ошибка!'),'error')
    write_log(unicode(resp))
#--------------------------------
#--------------------------------
#--------------------------------

write_log('=================\n запуск')

#send_data(host,'/','')

convert_old_links()

part_size=1024*10 #step of progress

pbar = progressbartw.ProgressBarTW()
view = None
menu = [
  (ru('Аплоад'), (
    (ru('Дать описание'), input_descr),
    (ru('Задать e-mail'), input_email),
    (ru('Задать пароль'), input_pass),
    (ru('Выбрать файл'), select_file),
    (ru('Отправить файл'), upload_file_to_url))
  ),
    (ru('Скачать файл'), download),
    (ru('Мои файлы'), view_uploaded),
    (ru('Новые версии'), check_update),
    (ru('О программе'), about),
    (ru('Выход'), exit)
  ]

filename = None
pwd=u''

try:
  f=open(fn_mail,'r')
  email=ru(f.read())
  f.close()
except:
  email=u'Not defined'

if e32.s60_version_info[0]>=3: default_text_color=ui.get_skin_color(ui.EMainAreaTextColor)
else: default_text_color=0x0

description = ru('')



from graphics import Image
im=Image.open(fn_dir+u'banner.png');
im2=Image.new((w,h))
canv = None

rekl=[]

if not os.path.exists('e:\\Downloads'): os.mkdir('e:\\Downloads')

e32.ao_sleep(0, main)
lock=e32.Ao_lock()
lock.wait()
