import json
import time
import requests

BEGIN = 9351000
#2020-01-25 23:03:45
END = 9532200 
#2020-02-22 16:58:33
#区块范围，研究的是第BEGIN个到第END-1个区块
fopen = open('ethin_record.txt','r')
flines = fopen.readlines()

shape_url = "https://shapeshift.io/txstat/"
etherscan_url1 = "https://api-cn.etherscan.com/api?module=account&action=txlist&address="
etherscan_url2 = "&startblock=0&endblock=99999999&sort=asc&apikey=XSN4UAHAZN9BCBA9TUATAQJ6HM4UT2RRYH"

reco = dict()
record = dict()
k = 0
for line in flines:
    k += 1
    c = 0
    item = json.loads(line)
    print("交易编号：" + str(k) + "  当前查找金额：" + str(item['amount']))
    for block_index0 in range(BEGIN, END):
        if block_index0 % 1000 == 0:
            print("当前区块高度：" + str(block_index0))
        fopen1 = open('区块' + str(block_index0) + '.txt','r')
        flines1 = fopen1.read()
        item1 = json.loads(flines1)
        block_time0 = int(item1['result']['timestamp'], 16)
        if int(block_time0) - int(item['timestamp']) > 0:
            for block_index in range(block_index0 - 10, block_index0):
                fopen2 = open('区块' + str(block_index) + '.txt','r')
                flines2 = fopen2.read()
                item2 = json.loads(flines2)
                block_time = int(item2['result']['timestamp'], 16)
                tx_list = item2['result']['transactions']
                for i in range(0, len(tx_list) - 1):
                    tx = tx_list[i]
                    v = int(tx['value'], 16)/1000000000000000000
                    if abs(v - item['amount']) <= 0.00000001:
                        print(tx['to'])
                        c2 = 0
                        while c2 == 0:
                            try:
                                r = requests.get(shape_url + str(tx['to']) + "/10000", timeout = 50)
                                shape_dic = json.loads(r.text)
                                if "0" in shape_dic.keys():
                                    c3 = 0
                                    while c3 == 0:
                                        try:
                                            r = requests.get(etherscan_url1 + str(tx['to']) + etherscan_url2, timeout = 50)
                                            r_text = json.loads(r.text) 
                                        except:
                                            print("Waiting for 3 seconds...")
                                            time.sleep(3)
                                        else:
                                            c3 = 1
                                    res = []
                                    for num in shape_dic.keys():
                                        num_dic = shape_dic[num]
                                        if num_dic['incomingCoin'] in res:
                                            continue
                                        res.append(num_dic['incomingCoin'])
                                        if (num_dic['status'] == 'complete' or num_dic['status'] == 'resolved') and num_dic['outgoingType'] == item['curOut'] and abs(num_dic['incomingCoin'] - item['amount']) <= 0.00000001:
                                            for t in r_text["result"]:
                                                if t["to"] == tx["to"] and abs(int(t["value"])/(10**18) - item['amount']) <= 0.00000001 and -120 < int(t["timeStamp"]) - int(item['timestamp']) < 0:
                                                    if int(t['blockNumber']) == block_index:
                                                        BEGIN = block_index - 20
                                                        print("成功追踪特殊交易！")
                                                        reco['status'] = num_dic['status']
                                                        reco['ethSS'] = tx['to']
                                                        reco['amount'] = num_dic['incomingCoin']
                                                        reco['timestamp'] = block_time
                                                        reco['t_d'] = int(t["timeStamp"]) - int(item['timestamp'])
                                                        reco['curOut'] = num_dic['outgoingType']
                                                        reco['curInaddr'] = tx['from']
                                                        reco['curOutaddr'] = num_dic['withdraw']
                                                        with open('ethin_succees.txt','a') as ft:
                                                            ft.write(json.dumps(reco)+"\n")
                                                        c += 1
                                elif (shape_dic['status'] == 'complete' or shape_dic['status'] == 'resolved') and shape_dic['outgoingType'] == item['curOut'] and abs(shape_dic['incomingCoin'] - item['amount']) <= 0.00000001:
                                    BEGIN = block_index - 20
                                    print("成功追踪交易！")
                                    reco['status'] = shape_dic['status']
                                    reco['ethSS'] = tx['to']
                                    reco['amount'] = shape_dic['incomingCoin']
                                    reco['timestamp'] = block_time
                                    reco['t_d'] = int(block_time) - int(item['timestamp'])
                                    reco['curOut'] = shape_dic['outgoingType']
                                    reco['curInaddr'] = tx['from']
                                    reco['curOutaddr'] = shape_dic['withdraw']
                                    with open('ethin_succees.txt','a') as ft:
                                        ft.write(json.dumps(reco)+"\n")
                                    c += 1
                            except:
                                print("Connection refused by shapeshift..")
                                time.sleep(3)
                                print("Was a nice sleep, now let me continue...")
                                continue
                            else:
                                c2 = 1           
            if c > 1:
                with open('ethin_succees.txt','a') as ft:
                    ft.write("以上重复 " + str(c) + " 次" + "\n")
            elif c == 0:
                with open('ethin_fails.txt','a') as ft:
                    ft.write(json.dumps(item)+"\n")
                BEGIN = block_index - 20
            break