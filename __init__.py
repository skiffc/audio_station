import  requests

class   AudioStation():
    def __init__( self, ip, sid ):
        self.ip = ip
        self.cookies = { "stay_login": "1", "id": sid }
        self.airplay = None
    def device( self, did ):
        self.airplay = did
    def play( self, value = None ):
        if self.airplay:
            cmd = 'http://%s:5000/webapi/AudioStation/remote_player.cgi?api=SYNO.AudioStation.RemotePlayer&method=control&id=%s&version=2&action=play' % ( self.ip, self.airplay )
            if value:
                cmd += '&value=%s' % value
            r = requests.get( cmd, cookies=self.cookies ) 
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
        s = path.split( '/' )
        r = requests.get( 'http://%s:5000/webapi/AudioStation/folder.cgi?limit=1000&method=list&library=shared&api=SYNO.AudioStation.Folder&additional=song_tag%%2Csong_audio%%2Csong_rating&version=2&sort_by=title&sort_direction=ASC' % self.ip, cookies=self.cookies )
        j = r.json()
        print j
        for p in s[1:]:
            print 'Search:', p
            j = self.enter( p, j )
            if not j:
                return None
            print j
        return j
            
    def enter( self, name, j ):
        for p in j['data']['items']:
            if p['title'] == name:
                print 'Found', p['id']
                did = str(p['id'])
                r = requests.get( 'http://%s:5000/webapi/AudioStation/folder.cgi?limit=1000&method=list&library=shared&api=SYNO.AudioStation.Folder&id=%s&additional=song_tag%%2Csong_audio%%2Csong_rating&version=2&sort_by=title&sort_direction=ASC' % ( self.ip, did ), cookies=self.cookies )
                return r.json()
        return None
    def playlist( self, target ):
        if self.airplay:
            if 'dir' in target['data']['id']:
                cmd = 'http://%s:5000/webapi/AudioStation/remote_player.cgi?api=SYNO.AudioStation.RemotePlayer&method=updateplaylist&library=shared&id=%s&offset=0&limit=%s&play=true&version=2&containers_json=%%5B%%7B%%22type%%22%%3A%%22folder%%22%%2C%%22id%%22%%3A%%22%s%%22%%2C%%22recursive%%22%%3Afalse%%2C%%22sort_by%%22%%3A%%22title%%22%%2C%%22sort_direction%%22%%3A%%22ASC%%22%%7D%%5D' % ( self.ip, self.airplay, target['data']['total'], target['data']['id'] )
            r = requests.get( cmd, cookies=self.cookies )

            url = 'http://%s:5000/webapi/AudioStation/remote_player.cgi' % self.ip
            cmd = 'api=SYNO.AudioStation.RemotePlayer&method=getplaylist&id=%s&additional=song_tag%%2Csong_audio%%2Csong_rating&offset=0&limit=8192&version=2' % self.airplay
            r = requests.get( url + '?' + cmd, cookies=self.cookies )
            print r.json()
            
