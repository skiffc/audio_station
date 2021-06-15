import  requests

class   AudioStation():
    def __init__( self, ip, login, password, priority=[], forbidden=[] ):
        self.ip = ip
        self.airplay = None
        self.folder = None
        self.music = None
        self.track = None
        self.num = None
        self.path = None
        self.priority = priority
        self.forbidden = forbidden
        self.volume = 50
        self.login = login
        self.password = password
        self.cookies = None
        self.token = '--------' 
    def connect( self ):
        r = requests.get('http://%s:5000/webapi/auth.cgi?api=SYNO.API.Auth&version=2&method=login&account=%s&passwd=%s&session=AudioStation&format=cookie' % ( self.ip, self.login, self.password ) )
        self.cookies = { "stay_login": "1", "id": r.json()['data']['sid'] }

    def test_connection( self ):
        cmd = 'http://%s:5000/webapi/AudioStation/remote_player.cgi?api=SYNO.AudioStation.RemotePlayer&method=list&type=all&additional=subplayer_list&version=2' % self.ip
        try:
            r = requests.get( cmd, cookies=self.cookies, timeout=5 )
        except requests.exceptions.ConnectTimeout:
            return False 
        except requests.exceptions.ConnectionError:
            return False 
 
        j = r.json()
        if 'error' in j:
            print(j)
            self.connect()
        return True
        
    def device( self, did ):
        self.airplay = did
    def auto_device( self ):
        l = self.scan_device()
        print(l)
        for p in self.priority:
            if p in l:
                self.device( p )
                return p
        else:
            if l:
                self.device( l[0] )
                return l[0]
        return None
    def play( self, value = None ):
        if self.airplay:
            #cmd = 'http://%s:5000/webapi/AudioStation/remote_player.cgi?api=SYNO.AudioStation.RemotePlayer&method=control&id=%s&version=2&action=play' % ( self.ip, self.airplay )
            if value == None:
                value = self.track

            cmd = f'http://{self.ip}:5000/webapi/AudioStation/remote_player.cgi?api=SYNO.AudioStation.RemotePlayer&method=control&id={self.airplay}&version=3&action=play&value={value}'
            r = requests.get( cmd, cookies=self.cookies ) 
            print("{} {} {}".format(self.folder,self.track, self.path))
            print(cmd)
            print(r.json())
    def repeat( self ):
        if self.airplay:
            r = requests.get( 'http://%s:5000/webapi/AudioStation/remote_player.cgi?api=SYNO.AudioStation.RemotePlayer&method=control&id=%s&version=2&action=set_repeat&value=one' % ( self.ip, self.airplay ), cookies=self.cookies ) 
    def no_repeat( self ):
        if self.airplay:
            r = requests.get( 'http://%s:5000/webapi/AudioStation/remote_player.cgi?api=SYNO.AudioStation.RemotePlayer&method=control&id=%s&version=2&action=set_repeat&value=all' % ( self.ip, self.airplay ), cookies=self.cookies ) 
    def info( self ):
        if self.airplay:
            r = requests.get( 'http://%s:5000/webapi/AudioStation/remote_player_status.cgi?SynoToken=%s&api=SYNO.AudioStation.RemotePlayerStatus&method=getstatus&id=%s&additional=song_tag%%2Csong_audio%%2Csubplayer_volume&version=1' % ( self.ip, self.token, self.airplay ), cookies=self.cookies )
            print(r.json())
            if r.json()['success']:
                return r.json()['data']
            else:
                return {}

    def stop( self ):
        if self.airplay:
            r = requests.get( 'http://%s:5000/webapi/AudioStation/remote_player.cgi?api=SYNO.AudioStation.RemotePlayer&method=control&id=%s&version=2&action=stop' % ( self.ip, self.airplay ), cookies=self.cookies ) 
    def next( self ):
        if self.airplay:
            r = requests.get( 'http://%s:5000/webapi/AudioStation/remote_player.cgi?api=SYNO.AudioStation.RemotePlayer&method=control&id=%s&version=2&action=next' % ( self.ip, self.airplay ), cookies=self.cookies ) 
    def prev( self ):
        if self.airplay:
            r = requests.get( 'http://%s:5000/webapi/AudioStation/remote_player.cgi?api=SYNO.AudioStation.RemotePlayer&method=control&id=%s&version=2&action=prev' % ( self.ip, self.airplay ), cookies=self.cookies ) 
    def goto( self, path ):
        self.path = path
        s = path.split( '/' )
        r = requests.get( 'http://%s:5000/webapi/AudioStation/folder.cgi?limit=1000&method=list&library=shared&api=SYNO.AudioStation.Folder&additional=song_tag%%2Csong_audio%%2Csong_rating&version=2&sort_by=title&sort_direction=ASC' % self.ip, cookies=self.cookies )
        j = r.json()
        path_now = ''
        for p in s[1:]:
            print('Search: '+ p)
            path_now += '/%s' % p
            j = self.enter( path_now, j )
            if not j:
                return None
        return j
            
    def enter( self, path, j ):
        file_cnt = 0
        for p in j['data']['items']:
            if p['path'] == path:
                print ('Found '+p['id'])
                did = str(p['id'])
                if p['type'] == 'folder':
                    self.folder = p['id']
                    self.track = '0'
                    r = requests.get( 'http://%s:5000/webapi/AudioStation/folder.cgi?limit=1000&method=list&library=shared&api=SYNO.AudioStation.Folder&id=%s&additional=song_tag%%2Csong_audio%%2Csong_rating&version=2&sort_by=title&sort_direction=ASC' % ( self.ip, did ), cookies=self.cookies )
                    return r.json()
                elif p['type'] == 'file':
                    self.music = p['id']
                    self.track = str( file_cnt ) 
                    return j
            if p['type'] == 'file':
                file_cnt += 1
        print('No found:')
        print(j)
        for p in j['data']['items']:
            print(p['path'].encode('utf-8'))
        return None

    def get_num( self ):
        r = requests.get( 'http://{}:5000/webapi/AudioStation/folder.cgi?limit=1000&method=list&library=shared&api=SYNO.AudioStation.Folder&id={}&additional=song_tag%%2Csong_audio%%2Csong_rating&version=2&sort_by=title&sort_direction=ASC'.format( self.ip, self.folder ), cookies=self.cookies )
        j = r.json()
        if not j:
            print('Cannot find {}'.format( self.folder ))
            return 0

        file_cnt = j['data']['total'] - j['data']['folder_total']
        print('Total file number: {}'.format(file_cnt))
        return file_cnt

    def set_last( self ):
        file_cnt = self.get_num()
        if file_cnt > 0:
            self.track = str( file_cnt - 1 )
        else:
            self.track = '0'

    def playlist( self, limit = 0 ):
        if self.airplay and self.folder:
            if limit == 0:
                limit = self.get_num()

            if limit == 1:
                cmd = f'http://{self.ip}:5000/webapi/AudioStation/remote_player.cgi?api=SYNO.AudioStation.RemotePlayer&method=updateplaylist&library=shared&id={self.airplay}&offset=0&limit=1&play=true&version=3&keep_shuffle_order=false&songs={self.music}&containers_json=%5B%5D'
            else:
                cmd = f'http://{self.ip}:5000/webapi/AudioStation/remote_player.cgi?api=SYNO.AudioStation.RemotePlayer&method=updateplaylist&library=shared&id={self.airplay}&offset=0&limit={limit}&play=true&version=3&keep_shuffle_order=false&containers_json=%5B%7B%22type%22%3A%22folder%22%2C%22id%22%3A%22{self.folder}%22%2C%22recursive%22%3Afalse%2C%22sort_by%22%3A%22title%22%2C%22sort_direction%22%3A%22ASC%22%7D%5D'
                #cmd = 'http://%s:5000/webapi/AudioStation/remote_player.cgi?api=SYNO.AudioStation.RemotePlayer&method=updateplaylist&library=shared&id=%s&offset=0&limit=%d&play=true&version=2&containers_json=%%5B%%7B%%22type%%22%%3A%%22folder%%22%%2C%%22id%%22%%3A%%22%s%%22%%2C%%22recursive%%22%%3Afalse%%2C%%22sort_by%%22%%3A%%22title%%22%%2C%%22sort_direction%%22%%3A%%22ASC%%22%%7D%%5D' % ( self.ip, self.airplay, limit, self.folder )
            print(cmd)
            r = requests.get( cmd, cookies=self.cookies )
            print(r.json())

            #cmd = 'http://%s:5000/webapi/AudioStation/remote_player.cgi?api=SYNO.AudioStation.RemotePlayer&method=getplaylist&id=%s&additional=song_tag%%2Csong_audio%%2Csong_rating&offset=0&limit=8192&version=2' % ( self.ip, self.airplay)
            cmd = f'http://{self.ip}:5000/webapi/AudioStation/remote_player.cgi?api=SYNO.AudioStation.RemotePlayer&method=getplaylist&id={self.airplay}&additional=song_tag%2Csong_audio%2Csong_rating&offset=0&limit={limit}&version=3'
            print(cmd)
            r = requests.get( cmd, cookies=self.cookies )
            print(r.json())
             
    def set_volume( self, v ):
        if v == '+':
            self.volume = min( 100, self.volume + 25 )
        elif v == '-':
            self.volume = max( 0, self.volume - 25 )
        else:
            try:
                v = max( 0, min( 100, int( v ) ) )
            except:
                return
            
        print(self.volume)
        cmd = 'http://%s:5000/webapi/AudioStation/remote_player.cgi?api=SYNO.AudioStation.RemotePlayer&method=control&id=%s&version=2&action=set_volume&value=%d' % ( self.ip, self.airplay, self.volume )
        r = requests.get( cmd, cookies=self.cookies )
           
    def scan_device( self ):
        cmd = 'http://%s:5000/webapi/AudioStation/remote_player.cgi?api=SYNO.AudioStation.RemotePlayer&method=list&type=all&additional=subplayer_list&version=2' % self.ip
        r = requests.get( cmd, cookies=self.cookies )
        print(r.content)
        d = []
        j = r.json()
        for p in j['data']['players']:
            if p['type'] == 'airplay' and p['id'] != '__SYNO_Multiple_AirPlay__' and p['id'] not in self.forbidden:
                d.append( p['id'] )
        return d
