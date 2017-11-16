# -*- coding: utf-8 -*-
from flask import jsonify, Flask,make_response,request
import pymysql,sys
import ConfigParser
reload(sys)
sys.setdefaultencoding('utf-8')

app = Flask(__name__)

cf = ConfigParser.ConfigParser()
path = 'db.config'
cf.read(path)
secs = cf.sections()
_host= cf.get("database","dbhost")
_port= cf.get("database","dbport")
_dbname=cf.get("database","dbname")
_dbuser=cf.get("database","dbuser")
_dbpassword=cf.get("database","dbpassword")
_path=cf.get("path","filepath")

config ={
        'host':_host,
        'port':int(_port),
        'user':_dbuser,
        'passwd':_dbpassword,
        'db':_dbname,
        'charset':'utf8',
        }

#定义异常返回请求
methods_not_found = {"msg": "请求方式不存在"}
domain_not_found = {"msg": "请求接口地址不存在"}
domain_without_methods = {"msg": "请求接口地址与请求方式不匹配"}

def checksize(domain,method):
    conn = pymysql.connect(**config)
    cur = conn.cursor()
    size = cur.execute('select * from mock_config where domain=%s', (domain))  # 校验domain是否存在
    size1 = cur.execute('select * from mock_config where methods=%s', (method))  # 校验method是否存在
    all_size1 = cur.execute('select * from mock_config where domain=%s and methods=%s', (domain, method))
    conn.close()
    if size == 0:
        return "domain not found"
    elif size1 == 0:
        return "methods not found"
    elif all_size1 == 0:
        return "domain without methods"

    # if size == 0:
    #     return jsonify({"msg": "请求方法不存在"})
    # elif size1 == 0:
    #     return jsonify({"msg": "请求方法名称不存在"})

def checkpath(domain,varsvalue,method):
    method=method.lower()
    varsvalue.sort()
    checkvalue = checksize(domain,method)
    #print ("domain is %s,method is %s" % (domain,method))
    #判断请求方法和模式是否匹配
    if checkvalue == "domain not found":
        return jsonify(domain_not_found)
    elif checkvalue == "methods not found":
        return jsonify(methods_not_found)
    elif checkvalue == "domain without methods":
        return jsonify(domain_without_methods)
    else:
        conn = pymysql.connect(**config)
        cur = conn.cursor()
        cur.execute('select resparams from mock_config where status=0 and domain=%s and methods=%s', (domain, method))
        resparams = cur.fetchone()
        conn.close()
        if len(varsvalue) == 0:
            if resparams[0] != '':
                return jsonify({"msg": "对应请求的参数与数据库配置不匹配"})
            else:
                return resparams[0].encode("utf-8")
        else:
            varsvalue1=getvar(varsvalue)#实际请求
            conn = pymysql.connect(**config)
            cur = conn.cursor()
            cur.execute('select reqparams,resparams,methods,ischeck from mock_config where status=0 and domain=%s and methods=%s',(domain, method))
            reqparams = cur.fetchall()
            if reqparams == ():
                return jsonify({"msg": u"请求方法和参数不匹配"})
            elif reqparams[0][3]==1:
                return reqparams[0][1]
            else:
                rdata=checkparams(reqparams,varsvalue1)
            return rdata

def checkparams(reqparams,varsvalue1):
    varsvalue2 = reqparams[0][0]  # 数据库中的预期请求参数
    if reqparams[0][2].lower()=='get' or (reqparams[0][2].lower()=='post' and varsvalue1[0] != '}' and varsvalue1[-2] != '}'):
        arr = varsvalue2.split('&')
        for i in range(len(arr)):
            arr[i] = arr[i] + '&'
        arr.sort(reverse=True)
        str = ''.join(arr)[0:-1]
        if str==varsvalue1:
            return reqparams[0][1].encode("utf-8")
        if reqparams[0][0] == '':
            return jsonify({"msg": u"对应请求没有配置预期返回值"})
        else:
            return jsonify({"msg": u"请求方法和参数不匹配"})
    elif reqparams[0][2].lower()=='post':
        varsvalue1 = varsvalue1.replace("\t", "").replace("\r", "").strip()[:-1]
        varsvalue2 = varsvalue2.replace("\t", "").replace("\r", "").strip()
        if varsvalue1 == varsvalue2:
            return reqparams[0][1].encode("utf-8")
    else:
        return jsonify({"msg": u"暂不支持该类型请求方法"})

def getvar(value):
    value=value[::-1]
    result = ''
    f = 0
    for i in range(len(value)):
        for j in range(len(value[i])):
            if f % 2 == 0:
                result = result + value[i][j] + '='
                f = f + 1
            else:
                result = result + value[i][j] + '&'
                f = f + 1
    return result[0:-1]


# @app.route('/<path:path>/<path:path1>', methods=['GET','POST'])
# def get_all_task(path,path1):
#     npath='/' + path + '/' + path1
#     print npath
#     if request.method=='GET':
#         varsvalue = request.args.items()
#         print "11111111"
#         print varsvalue
#     else:
#         varsvalue = request.form.items()
#     r = checkpath(npath, varsvalue, request.method)
#     return r

@app.route('/<path:path>', methods=['GET','POST'])
def get_all_task1(path):
    path = '/' + path
    if request.method=='GET':
        varsvalue = request.args.items()
    else:
        varsvalue = request.form.items()
    r = checkpath(path, varsvalue, request.method)
    return r


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'msg':'fail','error': '404 Not found'}), 404)

@app.errorhandler(500)
def not_found(error):
    return make_response("程序报错,无法访问", 500)

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True, port=8089,threaded=True)
