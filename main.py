# download files from youtube via cmd(youtube-dl)
# convert to mp3 using cmd(ffmpeg) (maybe dont need, yt-dl have it)
# create folder, rename, set song details (author, album, song number, art)
# ...
# n_entries, upload_date, average_rating, album, track, artist, playlist_index, filesize, ext
# yt api search for song name
# https://regex101.com/
# https://github.com/ytdl-org/youtube-dl/blob/3e4cedf9e8cd3157df2457df7274d0c842421945/youtube_dl/YoutubeDL.py
# https://googleapis.github.io/google-api-python-client/docs/dyn/youtube_v3.html
# https://stackoverflow.com/questions/8948/accessing-mp3-metadata-with-python
# https://pypi.org/project/tkcalendar/#documentation
# add options 'donwloaded' in self songs

import regex as re
import Pmw
import urllib.request
import api
import io
import PIL.Image
import PIL.ImageTk
from win32api import GetSystemMetrics
from tkinter import *
import os
import youtube_dl
# from tkcalendar import DateEntry
# import win32clipboard as cb
# import requests
# from threading import Thread
# import subprocess
from tkinter import ttk, filedialog

FONT = 'Roboto 10'
COLORS = ['#9a69cb', '#451473', '#24093e', '#00a000', '#a30000']
LYRICS = '''[Verse 1]
Ay yo
It's the master wicked
Terror creepin' in ya kitchen
Takin' pictures of your bitch then
Dippin' with a vengeance
I'll slice you and dice you
Entice you to get loose
Then stitch you back together
With the laces from ya dads boots

I'm the super cooch cougar
Fingerin' ya mom inside an uber
Going backwards
Fuck backwoods
I'm pullin' on a flask
Full of premium gas
In the back of ya class
Rockin' an all black ski mask

Comin' with the shits that make you vomit
I see you on my dick well hop up off it
I'm solo dolo for the profit
She make my cock spit (who tho?)
Ya bitch do yo
She on my boat right now
Let's see if she can float
I'm sick in the head
Twisted like a dread
Terror comin' back from the dead
With a baggie full of lead
And red lasers
Settin' fire to ya neighbors
Immune to tazers
Cut ya throat and then I eat the razor

[Chorus]
I'm on the other side
Drank too much bleach
Finally I died
Everytime you look into the sky
You will see my eyes
Starin' back at you
With a .32 cocked
5 knives in my shoes
And a holographic mewtwo

I'm on the other side
Popped too many pills
I thought I'd never die
Fuckin' the reality I left behind
There is no after life just another knife
Waitin' for the psychopathic addict hiding in ya
Attic plannin' when he's next attackin'
[Verse 2]
The pathologic deranged homicidal prophet
Obnoxious enough to stash a kilo in the cockpit
I got that sick shit ya hoe be fuckin' with
Knuckle bust ya lip
On a acid trip with all my lasers on my hip

Call me king koopa the chemical abusa
I'm pullin' up on ya ass with the .44 to shoot ya
I got the juice like bishop
Comin' to fix your bitches makeup
Then make her hiccup in ya bed before ya wake up

I'm goin' off like a mothafuckin' sprinkler
Make ya knees weak before I cut you with a cleaver
And put ya body in my back pack
Strapped with a fat gat
And a dead cat hangin' from my fanny pack

Doin' about a hundred with you in the trunk
Now hold on tight becuz I'm bout to hit this gnarly speed bump
Hear you scream and beg for mercy but I told you not to snitch
If you actin' like a bitch
You get fucked like a bitch

[Chorus]
I'm on the other side
Drank too much bleach
Finally I died
Everytime you look into the sky
You will see my eyes
Starin back at you
With a .32 cocked
5 knives in my shoes
And a holographic mewtwo
I'm on the other side
Popped too many pills
I thought I'd never die
Fuckin' the reality I left behind
There is no after life just another knife
Waitin' for the psychopathic addict hiding in ya
Attic plannin' when he's next attackin'
'''


class MyLogger(object):  # usar isso pra fazer um loading...
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)
        return self


class ToolWindow(Toplevel):
    def __init__(self, master, search_list):
        Toplevel.__init__(self, master)
        self.res_w = 240
        self.res_h = (len(search_list.values()) + 1) * 24
        self.x, self.y = int(GetSystemMetrics(0)/2 - self.res_w), int(GetSystemMetrics(1)/2 - self.res_h)
        self.geometry(f'{self.res_w}x{self.res_h}+{self.x}+{self.y}')
        self['background'] = COLORS[2]
        self.overrideredirect(1)
        self.grab_set()

        self.value = StringVar
        self.top_frame = Frame(self, bg=COLORS[0])
        self.search_frame = Frame(self)
        self.win_title_lb = Label(self.top_frame, text='                        Pesquisa - Genius', fg=COLORS[2]
                                  , bg=COLORS[0])
        self.search_entry = ttk.Entry(self.search_frame, width=35)
        self.top_frame.pack(fill=BOTH)
        self.win_title_lb.grid()
        self.search_frame.pack(fill=BOTH)
        # self.search_entry.pack(anchor=W)
        for key, value in search_list.items():
            new_button = Button(self.search_frame, text=key, width=self.res_w, command=self.choose,
                                activebackground=COLORS[1], activeforeground=COLORS[2],
                                bg=COLORS[1], fg=COLORS[0], font=FONT, padx=2, bd=0, anchor=W)
            new_button.message = value
            new_button.bind('<ButtonRelease>', self.test)
            new_button.pack()

        # Window Movement.
        self._off_set_x = 0
        self._off_set_y = 0
        self.top_frame.bind('<Button-1>', self.click_win)
        self.top_frame.bind('<B1-Motion>', self.drag_win)
        self.win_title_lb.bind('<Button-1>', self.click_win)
        self.win_title_lb.bind('<B1-Motion>', self.drag_win)
        self.bind('<Escape>', lambda x: self.destroy())

    def test(self, event):
        self.value = event.widget.message

    def choose(self):
        # MainWindow.info_genius(self.master, self.value)
        self.destroy()

    def drag_win(self, event):
        self.x = self.winfo_pointerx() - self._off_set_x
        self.y = self.winfo_pointery() - self._off_set_y
        self.geometry('+{x}+{y}'.format(x=self.x, y=self.y))
        return event

    def click_win(self, event):
        self._off_set_x = event.x
        self._off_set_y = event.y


# MainWindow window.
class MainWindow(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.res_w, self.res_h = 636, 570  # carregar do arquivo de usuarios
        self.x, self.y = int(GetSystemMetrics(0)/2 - self.res_w), int(GetSystemMetrics(1)/2 - self.res_h/2)
        master.geometry(f'{self.res_w}x{self.res_h}+{self.x}+{self.y}')
        master['background'] = COLORS[2]
        # master.iconbitmap(resource_path('images/icon.ico'))
        master.focus_force()
        # self.master.overrideredirect(1)
        # master.resizable(0, 0)
        master.title('3PM')

        # Variables.
        self.full_album_cover = ''
        self.blur_album_cover = ''
        self.empty_cover = PIL.Image.open('empty_cover.png')
        self.empty_album_cover = PIL.ImageTk.PhotoImage(self.empty_cover)
        # self.label_list = [line for line in LYRICS.split('\n')]
        # self.songs = dict()
        self.selected_song = dict()
        self.songs = {'KEa2JU3sySQ': {'link': 'KEa2JU3sySQ', 'date': '06/07/2017',
                                      'youtube_title': 'ERRA - Skyline (Official Music Video)',
                                      'genius_title': '', 'genius_artist': '', 'genius_album': '',
                                      'genius_album_art': '', 'genius_lyrics': '', 'genius_track': ''}}
        self.selected_song = self.songs['KEa2JU3sySQ']
        self.lyrics_index = 0
        self.lyrics_list = [line for line in LYRICS.split('\n')]  # mudar de acordo com a musica selecionada na funcao
        self.folder_path = StringVar()
        self.folder_path.set('E:/MUSIC')  # set to saved loc
        self.date_var = StringVar()
        self.title_values = [x['youtube_title'] for x in self.songs.values()]
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'logger': MyLogger(),
            'progress_hooks': [my_hook], }
        # self.ydl = youtube_dl.YoutubeDL(self.ydl_opts)
        # self.style_chk = ttk.Style()
        # self.style_chk.configure('TCheckbutton', foreground=COLORS[0], background=COLORS[2], font=FONT)
        # self.pl_len = '?'
        # self.folder_chk_var = IntVar(0)
        # self.playlist_chk_var = IntVar(0)

        # Widgets.
        # Frames.
        self.main_frame = Frame(master, bg=COLORS[2])
        self.current_song_frame = Frame(master, bg=COLORS[2])
        self.songs_frame = Frame(master, bg=COLORS[2])
        self.status_frame = Frame(master, bg=COLORS[2])

        # self.songs_scr_frame = Pmw.ScrolledFrame
        # self.songs_canvas = Canvas(self.songs_frame, width=230, height=200, bg=COLORS[0], bd=0,
        #                            highlightthickness=0, relief='ridge')
        # set_mousewheel(self.songs_canvas, self.songs_canvas_scroll)

        # Labels.
        self.link_lb = _label(self.main_frame, 'Link ou ID: ')
        self.path_lb = _label(self.main_frame, 'Salvar em: ')
        self.genius_lb = _label(self.main_frame, 'Título no Youtube: ')
        self.album_art_lb = Label(self.main_frame, fg=COLORS[1], bg=COLORS[2], compound=CENTER)

        self.details_lb = _label(self.current_song_frame, 'Detalhes: ')
        self.info_id_lb = _label(self.current_song_frame, 'ID: ')
        self.info_id_result_lb = _label(self.current_song_frame, '')
        self.info_title_lb = _label(self.current_song_frame, 'Any Colour You Like')  # Genius
        self.info_artist_lb = _label(self.current_song_frame, 'Pink Floyd', font='Roboto 8')  # Genius
        self.info_album_lb = _label(self.current_song_frame, 'The Dark Side of The Moon', font='Roboto 8')  # Genius
        self.info_date_lb = _label(self.current_song_frame, 'Data: ')
        # self.info_track_lb = _label(self.info_frame, f'{self.pl_len}')
        self.info_track_lb = _label(self.current_song_frame, 'Track: ')
        self.lyrics_label = Label(self.current_song_frame, text='aaa', anchor=NW, compound=CENTER, width=-350,
                                  wraplength=300, justify=CENTER, image=self.empty_album_cover, font='Roboto 10 bold',
                                  bg=COLORS[2], fg=COLORS[2])
        set_mousewheel(self.lyrics_label, lambda e: self.scroll_command(e))

        self.test_lb = _label(self.status_frame, 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa: ')

        # Entries.
        self.link_entry = _entry(self.main_frame)  # validate url as user types
        self.link_entry.insert(0, 'KEa2JU3sySQ')
        self.path_entry = _entry(self.main_frame)
        self.path_entry['state'] = 'readonly'
        self.path_entry['textvariable'] = self.folder_path
        self.song_type_entry = ttk.Combobox(self.main_frame, height=5, width=4,
                                            values=['-', 'mp3', 'webm', 'wav', 'm4a'])
        self.song_type_entry.current(0)
        self.genius_title_entry = ttk.Combobox(self.main_frame, width=28,# state='readonly',
                                               values=self.title_values, postcommand=self.update_combobox)

        # self.song_date_entry = DateEntry(self.current_song_frame, font=FONT, textvariable=self.date_var, date_pattern='mm/dd/y',
        #                                  background=COLORS[2], headersbackground=COLORS[0], selectbackground=COLORS[2])
        # self.song_title_entry = Entry(self.current_song_frame, bg=COLORS[2], fg=COLORS[0], width=28,
        #                               border=0, insertwidth=1, font=FONT)
        # self.song_artist_entry = Entry(self.current_song_frame, bg=COLORS[2], fg=COLORS[0], width=28,
        #                                border=0, insertwidth=1, font=FONT)
        # self.song_album_entry = Entry(self.current_song_frame, bg=COLORS[2], fg=COLORS[0], width=28,
        #                               border=0, insertwidth=1, font=FONT)
        # self.track_entry = Entry(self.current_song_frame, bg=COLORS[2], fg=COLORS[0],
        #                          border=0, insertwidth=1, font=FONT, width=2)  # validate command only int
        # self.song_lyrics_text = Text(self.info_frame, bg=COLORS[2], fg=COLORS[0], width=40, height=24,  # add search cm
        #                              border=0, insertwidth=1, font=FONT, undo=True, wrap=WORD)
        # self.lyrics_scrollbar = Scrollbar(self.info_frame, orient=VERTICAL, command=self.__scroll_handler)

        # Buttons.
        self.search_bt = _button(self.main_frame, 2, 1, 'S')
        self.search_bt['command'] = self.info_yt
        self.genius_bt = _button(self.main_frame, 2, 1, 'G')
        self.genius_bt['command'] = self.choose_result
        self.path_bt = _button(self.main_frame, 2, 1, 'D')
        self.path_bt['command'] = self.get_dir
        self.download_bt = _button(self.main_frame, 4, 1, 'DOWN')
        # self.download_bt['command'] = self.download_ydl
        self.download_bt['command'] = self.update_art
        self.save_bt = _button(self.current_song_frame, 4, 1, 'Save')
        # self.save_bt['command'] = self.edit_song
        # self.folder_chk = ttk.Checkbutton(self.main_frame, text='Criar pasta', variable=self.folder_chk_var
        #                                   , style='TCheckbutton', underline=0)

        # Binds.
        self.link_entry.bind('<Button-3>', self.r_click_link)
        # self.songs_canvas.bind_all('<MouseWheel>', self.songs_canvas_scroll)
        # master.bind('<Escape>', self.f_quit)
        # self.genius_title_entry.bind('<<ComboboxSelected>>', self.set_song)
        # self.song_title_entry.bind('<Enter>', self.update_values)

        # Packing.
        # Main Frame.
        self.main_frame.grid(row=0, column=0, padx=4, pady=4, sticky=N)
        self.link_lb.grid(sticky='w')
        self.link_entry.grid()
        self.search_bt.grid(row=1, column=1, sticky='w', padx=4)
        self.genius_lb.grid(sticky='w')
        self.genius_title_entry.grid(sticky='w')
        self.genius_bt.grid(row=3, column=1)
        self.path_lb.grid(sticky='w')
        self.path_entry.grid()
        self.path_bt.grid(row=5, column=1)
        # self.download_bt.grid(row=6, column=1, pady=16)
        # self.album_art_lb.grid(row=7, columnspan=2, sticky=NSEW)
        # self.folder_chk.grid(sticky='w')
        # self.song_type_entry.grid(row=5, sticky='e')

        # Info Frame.
        self.current_song_frame.grid(row=0, column=1, rowspan=4, padx=4, pady=4)
        self.lyrics_label.grid(row=0, column=0)
        # self.details_lb.grid(row=0, column=0, sticky='e')
        # self.info_id_lb.grid(row=1, column=0, sticky='e')
        # self.info_id_result_lb.grid(row=1, column=1, sticky='w')
        self.info_title_lb.grid(row=1, column=0)
        self.info_artist_lb.grid(row=2, column=0)
        self.info_album_lb.grid(row=3, column=0)
        # self.info_track_lb.grid(row=5, column=0, sticky='e')
        # self.info_date_lb.grid(row=6, column=0, sticky='e')
        # self.save_bt.grid(row=6, column=1, sticky='e')
        # self.song_lyrics_text.grid(row=7, column=1, sticky=NSEW)
        # self.lyrics_scrollbar.grid(row=7, column=2, sticky=NS)
        # self.song_lyrics_text['yscrollcommand'] = self.lyrics_scrollbar.set
        self.test_lb.grid()

        # Songs Frame.
        self.songs_frame.grid(row=1, column=0, padx=4)
        # self.songs_canvas.grid(row=0, column=0, sticky=N, columnspan=2)

        # Status Frame.
        self.status_frame.grid(columnspan=2, sticky=EW)
        self.update_combobox()

    def scroll_command(self, e):
        """make END/HOME binds"""
        if e.delta < 0 and self.lyrics_index <= len(self.lyrics_list) - 18:
            lyrics_showing = '\n'.join(self.lyrics_list[self.lyrics_index:(self.lyrics_index + 18)])
            self.lyrics_label.config(text=lyrics_showing)
            self.lyrics_index = self.lyrics_index + 1
        elif e.delta > 0 and self.lyrics_index >= 1:
            lyrics_showing = '\n'.join(self.lyrics_list[self.lyrics_index - 1:(self.lyrics_index + 18 - 1)])
            self.lyrics_label.config(text=lyrics_showing)
            self.lyrics_index = self.lyrics_index - 1

    def del_song(self):
        youtube_id = self.info_id_result_lb.cget('text')
        self.title_values.remove(self.songs[youtube_id]['youtube_title'])
        self.songs.pop(youtube_id, None)
        pass

    def set_song(self, event=None):  # selected song will be given by list in the songs frame (soon)
        self.selected_song = self.genius_title_entry.get()
        for music_info in self.songs.values():
            if music_info['youtube_title'] == self.genius_title_entry.get():
                self.info_id_result_lb.configure(text=music_info['link'])
                # self.update_info(song_info=music_info)
        print(self.songs)

    def update_art(self, art_link='https://t2.genius.com/unsafe/221x221/https%3A%2F%2Fimages.rapgenius.com%2F8343e2520f0914e6c57cea07500a3b7e.800x800x1.jpg'):
        req = urllib.request.Request(art_link, None, api.header)
        raw_data = urllib.request.urlopen(req).read()
        album_art_img = PIL.Image.open(io.BytesIO(raw_data)).resize((380, 380), PIL.Image.ANTIALIAS)
        self.full_album_cover = PIL.ImageTk.PhotoImage(album_art_img)
        blur_img = PIL.Image.open('blur.png')
        album_art_img.paste(blur_img, (0, 0), blur_img)
        self.blur_album_cover = PIL.ImageTk.PhotoImage(album_art_img)
        self.lyrics_label.configure(image=self.blur_album_cover)

    # def edit_song(self):
    #     song_id = self.info_id_result_lb.cget('text')
    #     if self.song_title_entry.get() != self.songs[song_id]['genius_title']:
    #         self.songs[song_id]['genius_title'] = self.song_title_entry.get()
    #         print('titulo mudou')
    #     if self.song_artist_entry.get() != self.songs[song_id]['genius_artist']:
    #         self.songs[song_id]['genius_artist'] = self.song_artist_entry.get()
    #         print('artista mudou')
    #     if self.song_album_entry.get() != self.songs[song_id]['genius_album']:
    #         self.songs[song_id]['genius_album'] = self.song_album_entry.get()
    #         print('album mudou')
    #     if self.track_entry.get() != self.songs[song_id]['genius_track']:
    #         self.songs[song_id]['genius_track'] = self.track_entry.get()
    #         print('track mudou')
    #     if self.song_date_entry.get() != self.songs[song_id]['date']:
    #         self.songs[song_id]['date'] = self.song_date_entry.get()
    #         print('data mudou')
    #     # if self.song_lyrics_text.get('1.0', END) != self.songs[song_id]['genius_lyrics']:
    #     #     self.songs[song_id]['genius_lyrics'] = self.song_lyrics_text.get('1.0', END)
    #         print('letras mudaram')

    def r_click_link(self, event):
        clipboard = self.clipboard_get()
        self.link_entry.delete(0, END)
        self.link_entry.insert(0, clipboard)

    # def songs_canvas_scroll(self, event):
    #     self.songs_canvas.yview_scroll(-1 * int((event.delta / 120)), "units")

    # def __scroll_handler(self, *args):
    #     op, how_many = args[0], args[1]
    #     if op == 'scroll':
    #         units = args[2]
    #         self.song_lyrics_text.yview_scroll(how_many, units)
    #     elif op == 'moveto':
    #         self.song_lyrics_text.yview_moveto(how_many)

    def update_combobox(self):
        # self.title_values.append(value)
        self.genius_title_entry.configure(values=self.title_values)

    def update_info(self, song_info):  # pega info de self songs... fazer as funcões salvarem info la
        self.info_title_lb.config(text=f'{song_info["genius_track"]}. {song_info["genius_title"]}')
        self.info_title_lb.config(text=song_info['genius_artist'])
        self.info_title_lb.config(text=song_info['genius_album'])

    def get_dir(self):
        file_path = filedialog.askdirectory()
        self.path_entry.delete(0, END)
        if len(re.findall('/', file_path)) > 1:
            reg = '(.*?:).*/*(/.*$)'
            root = re.search(reg, file_path).group(1)
            last_folder = re.search(reg, file_path).group(2)
            # self.path_entry.insert(0, f'{root}...{last_folder}')
            self.folder_path.set(f'{root}...{last_folder}')
        else:
            self.path_entry.insert(0, file_path)
        print(file_path)

    def add_music(self, info):
        # pattern = {'id': '', 'title': '', 'artist': '', 'date': '', 'album': '', 'album_art': '',
        #            'lyrics': '', 'track': ''}
        if 'youtu' in info['link']:
            youtube_id = api.link_to_id(info['link'])
            print('if')
        else:
            youtube_id = info['link']
            print('else')
        print(youtube_id)
        if youtube_id not in self.songs:
            # self.song_artist_entry.delete(0, END)
            # self.song_album_entry.delete(0, END)
            # self.track_entry.delete(0, END)
            # self.title_values.insert(0, title)
            self.title_values.append(info['youtube_title'])
            self.genius_title_entry.set(info['youtube_title'])  # atualizar a lista
            dt = str(info['youtube_month'] + '/' + info['youtube_day'] + '/' + info['youtube_year'])
            # self.song_date_entry.set_date(dt)
            self.info_id_result_lb.configure(text=info['link'])
            self.songs.update({youtube_id: {'link': youtube_id, 'date': dt, 'youtube_title': info['youtube_title'],
                                            'genius_title': '', 'genius_artist': '', 'genius_album': '',
                                            'genius_album_art': '', 'genius_lyrics': '', 'genius_track': ''}})
            self.set_song()
            print(self.songs)
        else:
            print('titulo ja existente!')

    def download_ydl(self):  # adicionar um indicador caso ja tenha sido baixada.
        if len(self.songs.keys()) > 0:
            if self.path_entry.get() != '':
                for key, value in self.songs.items():
                    song_name = value["genius_title"] if value["genius_title"] != '' else value['youtube_title']
                    self.ydl_opts['outtmpl'] = f'{self.folder_path.get()}/{song_name}.%(ext)s'
                    with youtube_dl.YoutubeDL(self.ydl_opts) as ydl:
                        print(self.ydl_opts)
                        ydl.download([f'http://www.youtube.com/watch?v={key}'])
                        if value['genius_album_art'] != '':
                            art_link = value['genius_album_art']
                            req = urllib.request.Request(art_link, None, api.header)
                            raw_data = urllib.request.urlopen(req).read()
                        else:
                            raw_data = ''
                        api.set_properties(song_info=value, song_path=f'{self.folder_path.get()}/{song_name}.mp3',
                                           song_cover=raw_data)
            else:
                print('definir caminho')
        else:
            print('lista vazia')

    def info_yt(self):  # lidar com erro na pesquisa
        if self.link_entry.get() != '':
            try:
                song_info = api.youtube_get_info(link=self.link_entry.get())
                self.add_music(song_info)
            except NameError:
                raise NameError('Link ou ID inválido.')
        else:
            raise NameError('Empty link entry.')

    def info_genius(self, search):
        song_info = api.genius_get_info(search_result=search)
        all_info = {**self.songs[self.info_id_result_lb.cget('text')], **song_info}
        self.songs[self.info_id_result_lb.cget('text')] = all_info
        self.update_info(song_info=all_info)  # só atualizar se for diferente?

    def choose_result(self):
        if self.genius_title_entry.get() != '': # fazer uma condição levando em conta se a musica ja foi pesquisada.
            ToolWindow(self, api.genius_search(title=self.genius_title_entry.get()))
        else:
            print('sem titulo')

    def f_quit(self, event=None):
        self.quit()
        return event


def set_mousewheel(widget, command):
    """Activate / deactivate mousewheel scrolling when
    cursor is over / not over the widget respectively."""
    widget.bind("<Enter>", lambda _: widget.bind_all('<MouseWheel>', command))
    widget.bind("<Leave>", lambda _: widget.unbind_all('<MouseWheel>'))


def _label(frame, text, font=FONT):
    label = Label(frame, text=text, fg=COLORS[0],
                  bg=COLORS[2], font=font,
                  anchor='w')
    return label


def _entry(frame, show='', style="TEntry"):
    entry = ttk.Entry(
        frame, show=show, width=26,
        font=FONT, style=style)
    return entry


def _button(frame, w, h, text):
    button = Button(
        frame, width=w, height=h, bd=0, text=text,
        activebackground=COLORS[1],
        activeforeground=COLORS[2],
        bg=COLORS[1], fg=COLORS[2],
        font=FONT, padx=2)
    return button


def my_hook(d):
    print(d['status'])
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def main():
    root = Tk()
    # root.protocol('WM_DELETE_WINDOW', lambda: del_win(root))
    root_window = MainWindow(root)
    root.mainloop()
    return root_window


if __name__ == '__main__':
    main()
