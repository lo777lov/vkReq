import requests
import time
import json
import re

class vkReq:
    VK_LINK = 'vk.com'
    verify = True
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0"
    isLoggedIn = False
    def __init__(self,login,password):
        self.s = requests.Session()
        self.username = login.rstrip()
        self.password = password.rstrip()



    def login(self):
        self.SendRequest('/',login = True)
        #print(type(self.LastResponse.text))
        iph = (re.findall(r'name="ip_h" value="*([a-z0-9]+)',self.LastResponse.text))[0]
        lgh = (re.findall(r'name="lg_h" value="*([a-z0-9]+)',self.LastResponse.text))[0]
        #print(iph,lgh)
        data = {"act": "login",
                "role": "al_frame",
                "_origin": "https://vk.com",
                "ip_h": iph,
                "lg_h": lgh,
                "email": self.username,
                "pass": self.password,}
        self.SendRequest(predomain='login.',endpoint='/?act=login',post=data,login = True)
        #print(self.LastResponse)
        #print(self.LastResponse.text)
        if 'parent.onLoginFailed' in self.LastResponse.text:
            raise Exception("Bad login or password!\n")

        elif 'parent.onLoginDone' in self.LastResponse.text:
            self.userid = re.findall(r'"uid":"*([0-9]+)', self.LastResponse.text)[0]
            print('Succes, user_id = ',self.userid)
            self.isLoggedIn = True
            return True

    def getInfo(self):
        self.SendRequest('/id'+ str(self.userid))
        #print(self.LastResponse.text)
        self.name = re.findall(r'class=\"page_name\">*([\D]+)<',self.LastResponse.text)[0]

    def sendMessage(self,peer,text):
        data = {"act": "a_start",
                "al": "1",
                "block": "true",
                "gid": "0",
                "history": "false",
                "im_v": "2",
                "msgid": "false",
                "peer": peer
                }
        self.SendRequest('/al_im.php',post = data)
        hash = (re.findall(r'"hash":"*([a-z0-9_]+)',self.LastResponse.text))[0]
        data = {"act": "a_send",
                "al": "1",
                "hash": hash,
                "gid": "0",
                "msg": text,
                "im_v": "2",
                "to": peer}
        self.SendRequest('/al_im.php', post=data)
        return (True)


    def create_chat(self,peers,title):
        self.SendRequest('/im')
        hash =  re.findall(r'"writeHash":"*([a-z0-9_]+)',self.LastResponse.text)
        data = {"act": "a_multi_start",
                "al": "1",
                "hash": hash,
                "im_v": "2",
                "peers": (','.join(map(str,peers))),
                "title": title,
                }
        self.SendRequest('/al_im.php',post=data)
        chatid = re.findall(r'"peerId":*([0-9]+)', self.LastResponse.text)[0]
        return chatid

    def get_friends(self):
        data = {"act": "load_friends_silent",
                "al": "1",
                "gid": "0",
                "id" : self.userid
                }
        self.SendRequest('/al_friends.php',post = data)
        b = json.loads(self.LastResponse.text[4:])
        b = b['payload'][1][0]
        b = json.loads(b)
        b = b['all']
        friends_list = []
        for i in b:
            friends_list.append(i[0])
        return friends_list
    
    def SendRequest(self,endpoint,predomain = '',post = None,login = False):
        self.s.headers.update({'Connection': 'close',
                               'Accept': '*/*',
                               'Content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                               'Accept-Language': 'en-US',
                               'User-Agent': self.USER_AGENT})


        if (self.isLoggedIn == False and login == False):
            raise Exception("Not logged in!\n")

        while True:
            try:
                if (post is not None):
                    response = self.s.post('https://' +  predomain + self.VK_LINK + endpoint, data=post, verify=self.verify)
                else:
                    response = self.s.get('https://' + predomain + self.VK_LINK + endpoint, verify=self.verify)
                break
            except Exception as e:
                print('Except on SendRequest (wait 60 sec and resend): ' + str(e))
                time.sleep(60)

        if response.status_code == 200:
            self.LastResponse = response
            return True

    def setProxy(self, proxy=None):
        if proxy is not None:
            print('Set proxy!')
            proxies = {'http': proxy, 'https': proxy}
            self.s.proxies.update(proxies)