import base64

data = 'V0hreFpreFdPSFJZTVRobldIa3dkRmd4T0hSWWVUQm5XSGt3ZEZneE9XWlllVEJuV0hrd2RGaDVNSFJZZVRCbldIa3habGg1TVdaWU1UaG5XREU0ZEV4V09IUllNVGhuV0hreFpsZ3hPV1pNVXpBOQ=='

data = base64.b64decode(data)
data = base64.b64decode(data)
data = base64.b64decode(data)

data = data.replace(b'_', b'0')
data = data.replace(b'-', b'1')

flag = ''

for i in range(7):
    flag += chr(int(data[:8], 2))
    data = data[9:]

print(flag)