from vkReq import vkReq
api = vkReq('login','password')
api.login()
api.sendMessage(id,'hello')
