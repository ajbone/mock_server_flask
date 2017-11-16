## mock_server_flask文件说明：

1、sql文件为mysql中表结构文件

2、mock_server.py为实际mock文件。

3、mock_web.py为web管理页面所用server。

4、mock文件夹中为管理页面,在indexJQ.js文件中配置mock_web.py访问地址。

## 需要安装依赖

flask,pymysql,xlrd,flask_restful,flask_cors

## 操作步骤简述：

1、执行sql脚本建表

2、修改db.config数据库配置文件

3、安装需要的第三方依赖库，运行mock_server.py。

4、运行mock_web.py。

5、把web项目拷贝到web容器中正常访问，修改mock/js/config.js接口访问地址为mock_web的地址和端口。

6、打开index页，添加/导入自己需要的mock数据。


## Example:
curl --request POST  --url 'http://127.0.0.1:8089/server/login?username=qa&passwd=123456'

curl --request GET   --url 'http://127.0.0.1:8089/v1/callback?params=qatest'

curl --request POST --url http://127.0.0.1:8089/auth/bankCardVerified  --header 'content-type: application/json'  --data '{ "transType":"300002", "appid":"123456" }'

## 相关说明
1.web地址：http://192.168.202.24:8080/mock/ 

2.接口访问地址：http://192.168.202.24:8089/ + 配置的路径

3.请求参数支持json，form

4.请求方法目前只支持get/post

5.返回结果目前支持返回json
