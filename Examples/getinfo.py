from vkReq import vkReq
api = vkReq('login','password')
api.login()
api.getInfo()
print(api.name)
