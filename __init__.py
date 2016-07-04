import  requests

class   AudioStation():
    def __init__( self, ip, login, password ):
        self.ip = ip
        self.airplay = None
        self.folder = None
        self.track = None
        self.path = None
        r = requests.get('http://%s:5000/webapi/auth.cgi?api=SYNO.API.Auth&version=2&method=login&account=%s&passwd=%s&session=AudioStation&format=cookie' % ( ip, login, password ) )
        self.cookies = { "stay_login": "1", "id": r.json()['data']['sid'] }
    def device( self, did ):
        self.airplay = did
    def play( self, value = None ):
        if self.airplay:
            cmd = 'http://%s:5000/webapi/AudioStation/remote_player.cgi?api=SYNO.AudioStation.RemotePlayer&method=control&id=%s&version=2&action=play' % ( self.ip, self.airplay )
            if value:
                cmd += '&value=%s' % value
            else:
                cmd += '&value=%s' % self.track
            r = requests.get( cmd, cookies=self.cookies ) 
            print self.folder, self.track, self.path
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
            print 'Search:', p
            path_now += '/%s' % p
            j = self.enter( path_now, j )
            if not j:
                return None
        return j
            
    def enter( self, path, j ):
        for p in j['data']['items']:
            if p['path'].encode('utf-8') == path:
                print 'Found', p['id']
                did = str(p['id'])
                if p['type'] == 'folder':
                    self.folder = p['id']
                    self.track = '0'
                    r = requests.get( 'http://%s:5000/webapi/AudioStation/folder.cgi?limit=1000&method=list&library=shared&api=SYNO.AudioStation.Folder&id=%s&additional=song_tag%%2Csong_audio%%2Csong_rating&version=2&sort_by=title&sort_direction=ASC' % ( self.ip, did ), cookies=self.cookies )
                    return r.json()
                elif p['type'] == 'file':
                    self.track = str( int(p['additional']['song_tag']['track']) - 1 )
                    return j
        print 'No found:'
        print j
        print path
        for p in j['data']['items']:
            print p['path'].encode('utf-8')
        return None

    def playlist( self ):
        if self.airplay and self.folder:
            cmd = 'http://%s:5000/webapi/AudioStation/remote_player.cgi?api=SYNO.AudioStation.RemotePlayer&method=updateplaylist&library=shared&id=%s&offset=0&limit=0&play=true&version=2&containers_json=%%5B%%7B%%22type%%22%%3A%%22folder%%22%%2C%%22id%%22%%3A%%22%s%%22%%2C%%22recursive%%22%%3Afalse%%2C%%22sort_by%%22%%3A%%22title%%22%%2C%%22sort_direction%%22%%3A%%22ASC%%22%%7D%%5D' % ( self.ip, self.airplay, self.folder )
            r = requests.get( cmd, cookies=self.cookies )
            #print r.json()

            cmd = 'http://%s:5000/webapi/AudioStation/remote_player.cgi?api=SYNO.AudioStation.RemotePlayer&method=getplaylist&id=%s&additional=song_tag%%2Csong_audio%%2Csong_rating&offset=0&limit=8192&version=2' % ( self.ip, self.airplay )
            r = requests.get( cmd, cookies=self.cookies )
            #print r.json()
            
