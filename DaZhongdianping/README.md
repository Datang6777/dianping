# DaZhongdianping
对大众点评网的各个城市的TOP100热门餐厅数据进行获取，主要抓取了上海，北京，广州，深圳，天津，杭州，南京，苏州，成都，武汉，重庆，西安等城市。
同时使用pyecharts对所抓取结果进行数据分析，看看这些网红店铺，万一我们去旅游的时候有福分能吃一趟呢，也不错，哈哈。
# 新增前端字体加密解决
更新于2018/12/20
以前大众评论部分字体未加密，后面博客中经常有人问到怎么取完整评论信息，打开发现部分字体做了加密处理，显示并不完整，研究之后做了更新，可抓取完整评论内容，文章可去csdn查看。
# 文件说明
base：目录为MySQL连接组件<br> 
bin：目录为数据分析文件，主要有：
1.各大城市餐厅星级统计
2.各大城市口味，环境，服务，及综合指数
3.各大城市饭店集中区域
4.菜品分类
5.综合评价
分析，同时对应各类结果图表（见HTML），可直接查看。<br>
data：目录为最终结果集分析，以及MySQL数据。<br>
spider：抓取爬虫，大众点评评论抓取，更新于2018/12/20。
## 新增
新增加大众点评 点评信息抓取：spider/dazhongdianpin.py 抓取存储至data/Stu_csv.csv文件
新增加大众点评完整评论抓取：spider/dazhongdianping.py 更新于2018/12/20，解决前端字体样式加密

