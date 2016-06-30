import  requests

class   AudioStation():
    def __init__( self, ip, sid ):
        self.ip = ip
        self.cookies = { "stay_login": "1", "id": sid }
        self.device = None
    def device( self, did ):
        self.device = did
    def play( self ):
        if self.device:
            r = requests.get( 'http://%s:5000/webapi/AudioStation/remote_player.cgi?api=SYNO.AudioStation.RemotePlayer&method=control&id=%s&version=2&action=play' % ( self.ip, self.device ), cookies=self.cookies ) 
    def stop( self ):
        if self.device:
            r = requests.get( 'http://%s:5000/webapi/AudioStation/remote_player.cgi?api=SYNO.AudioStation.RemotePlayer&method=control&id=%s&version=2&action=stop' % ( self.ip, self.device ), cookies=self.cookies ) 
    def next( self ):
        if self.device:
            r = requests.get( 'http://%s:5000/webapi/AudioStation/remote_player.cgi?api=SYNO.AudioStation.RemotePlayer&method=control&id=%s&version=2&action=next' % ( self.ip, self.device ), cookies=self.cookies ) 
    def prev( self ):
        if self.device:
            r = requests.get( 'http://%s:5000/webapi/AudioStation/remote_player.cgi?api=SYNO.AudioStation.RemotePlayer&method=control&id=%s&version=2&action=prev' % ( self.ip, self.device ), cookies=self.cookies ) 
    def goto( self, path ):
        s = path.split( '/' )
        r = requests.get( 'http://%s:5000/webapi/AudioStation/folder.cgi?limit=1000&method=list&library=shared&api=SYNO.AudioStation.Folder&additional=song_tag%%2Csong_audio%%2Csong_rating&version=2&sort_by=title&sort_direction=ASC' % self.ip, cookies=self.cookies )
        j = r.json()
        print j
        for p in s[1:]:
            print 'Search:', p
            j = self.enter( p, j )
            print j
    def enter( self, name, j ):
        for p in j['data']['items']:
            if p['title'] == name:
                print 'Found', p['id']
                did = str(p['id'])
                r = requests.get( 'http://%s:5000/webapi/AudioStation/folder.cgi?limit=1000&method=list&library=shared&api=SYNO.AudioStation.Folder&id=%s&additional=song_tag%%2Csong_audio%%2Csong_rating&version=2&sort_by=title&sort_direction=ASC' % ( self.ip, did ), cookies=self.cookies )
                return r.json()
        



            




