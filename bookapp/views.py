import jieba
import matplotlib.pyplot as plt
import requests
from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.cache import never_cache
# 爬虫工具
from lxml import etree
# 自然语言处理
from snownlp import SnowNLP

from bookapp import models
# 导入数据库
from .models import Ebook, BookComment

# 伪装浏览器访问网站
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
}


# 通过ModelForm组件自动在前端页面生成输入框
class BookForm(forms.ModelForm):
    book_name = forms.CharField(label='书名',
                                widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入书名'}))
    autor = forms.CharField(label='作者', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入作者'}))
    publisher = forms.CharField(label='出版社',
                                widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入出版社'}))
    publisher_data = forms.CharField(label='出版日期',
                                     widget=forms.DateInput(
                                         attrs={'class': 'form-control', 'placeholder': '请选择出版日期', 'type': 'date'}))
    price = forms.DecimalField(label='价格',
                               widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '请输入价格'}))
    comment = forms.CharField(label='短评',
                              widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': '请输入短评'}))

    class Meta:
        model = Ebook
        fields = ['book_name', 'autor', 'publisher', 'publisher_data', 'price', 'comment']


class EbookFrom(forms.ModelForm):
    class Meta:
        model = Ebook
        fields = ['book_name', 'autor', 'publisher', 'publisher_data', 'price', 'comment', 'is_published']


# Create your views here.
# 加载local host将其重定向去爬虫页面
def index(request):
    return redirect('/admin/message/')


# 情感分析
def analyze_sentiment(text):
    words = jieba.lcut(text)
    seg_text = ' '.join(words)
    s = SnowNLP(seg_text)
    sentiment_score = s.sentiments
    return sentiment_score


def analyze(request):
    comments = BookComment.objects.all()
    # 对已有评论进行情感分析
    data = []
    for comment in comments:
        sentiment_score = analyze_sentiment(comment.short_comm)
        data.append({'comment': comment.short_comm, 'score': sentiment_score})

    # 统计用户评分数据
    sentiments = []
    for i in comments:
        sentiments_ = i.star
        sentiments.append(sentiments_)

    # 统计好评、中评和差评的数量
    positive_count = len([sentiment for sentiment in sentiments if sentiment in ['力荐', '推荐']])
    avg_count = len([sentiment for sentiment in sentiments if sentiment in ['一般', '还行']])
    negative_count = len([sentiment for sentiment in sentiments if sentiment in ['较差', '很差']])

    non_empty_sentiments = [sentiment for sentiment in sentiments if sentiment is not None]
    non_empty_count = len(non_empty_sentiments)

    # 计算非空值的好评、中评和差评的比例
    positive_ratio = round((positive_count / non_empty_count) * 100, 2) if non_empty_count != 0 else 0.0
    avg_ratio = round((avg_count / non_empty_count) * 100, 2) if non_empty_count != 0 else 0.0
    negative_ratio = round((negative_count / non_empty_count) * 100, 2) if non_empty_count != 0 else 0.0

    # 绘制饼图
    labels = ['recommend', 'average', 'bad']
    sizes = [positive_ratio, avg_ratio, negative_ratio]
    colors = ['#66b3ff', '#ffcc99', '#ff9999']

    plt.figure(figsize=(6, 6))
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    plt.axis('equal')
    plt.title('SENTIMENTS COMMENT')
    plt.draw()
    # 保存画好的图像
    plt.savefig("bookapp/static/image.png")
    plt.close()

    return render(request, 'analyze_comm.html', {'data': data})


# 管理图书账户
def account(request):
    # 获取form表单里的input框的name属性
    query = request.GET.get('search')
    if query:
        # 模糊匹配
        books = models.Ebook.objects.filter(book_name__icontains=query)
    else:
        books = models.Ebook.objects.all()
    return render(request, 'account.html', {'books': books})


# 图书信息爬取
def message(request):
    book_data_ = models.Ebook.objects.all()

    if book_data_.exists():
        # 防止数据存在时再次获取数据
        request.session['data_fetched'] = True
        book_data = models.Ebook.objects.all()
    else:
        # 防止数据不存在时无法获取数据
        request.session['data_fetched'] = False
        if request.method == 'POST':
            # 获取输入框链接爬取数据
            net = request.POST.get("net")
            # 避免反复获取数据，导致数据重复无法将参数传递给下一个页面
            # 获取10页的分页数据
            for j in range(10):
                link = net + "?start=" + str(j * 25)
                get_book(link)
        book_data = models.Ebook.objects.all()

    return render(request, 'message.html', {"book_data": book_data})


# 图书评论
def comment(request, bookNums, ebookid):
    # 将获取的id转换为int类型
    ebook = int(ebookid)
    book_num = int(bookNums)
    # 根据图书信息已经爬取的书籍id来获取数据
    book = get_object_or_404(Ebook, book_num=bookNums)
    book_id = get_object_or_404(Ebook, id=ebook)
    # 获取图书名
    book_names = book_id.book_name
    values = request.GET.get('percent_type')
    # 根据携带的参数过滤每一本不同的书
    comments = models.BookComment.objects.filter(ebook_id=book_id.id)

    # 判断是否已经获取了某本书的数据
    if comments.exists():

        percent_type = models.BookComment.objects.filter(percent_type__isnull=True)
        # 获取图书图片,防止没爬取到对应数据时报空值
        one_img_ = models.BookComment.objects.filter(ebook_id=book_id.id)[:1].get()
        if one_img_:
            one_img = one_img_.book_img
        return render(request, 'comment.html',
                      {'book': book, 'comments': comments, 'one_img': one_img, 'book_names': book_names,
                       'book_nums': bookNums, 'book_id': ebookid, 'percent_type': percent_type})
    else:
        # 将爬取到图书特有编号参数，从而爬取评论
        link = f"https://book.douban.com/subject/{book.book_num}/comments/"
        get_comment(link, book_id, values)
        # 对图片进行切片
        one_img_ = models.BookComment.objects.filter(ebook_id=book_id.id)[:1].get()
        if one_img_:
            one_img = one_img_.book_img
        return render(request, 'comment.html',
                      {'book': book, 'comments': comments, 'one_img': one_img, 'book_names': book_names,
                       'book_nums': book_num, 'book_id': ebookid})


# 不携带参数时跳转的页面
def comments(request):
    return render(request, 'comment.html')


# 新增图书
def add(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/admin/account/')
    else:
        form = BookForm()
    return render(request, 'book_add.html', {'form': form})


def edit(request, book_id):
    bookId = get_object_or_404(Ebook, id=book_id)
    book = models.Ebook.objects.filter(id=bookId.id).first()

    if request.method == 'POST':
        form = EbookFrom(request.POST, instance=book)
        if form.is_valid():
            ebook = form.save(commit=False)
            ebook.is_published = form.cleaned_data['is_published']
            ebook.save()
            return redirect('/admin/account/')
    else:
        form = EbookFrom(instance=book)

    return render(request, 'edit.html', {'form': form})


def dele(request, book_id):
    bookId = get_object_or_404(Ebook, id=book_id)
    book = models.Ebook.objects.filter(id=bookId.id).first()
    book.delete()
    return redirect('/admin/account')


# 已上架的图书
def up(request):
    # 过滤上架数据列是否为1，1代表上架
    published = Ebook.objects.filter(is_published=1)

    return render(request, 'up.html', {'published': published})


# 不同评论中的写法大同小异介绍好评就行
# 好评
@never_cache
def good(request, booknum, bookid, value):
    # 将获取的id转换为int类型
    ebookid = int(bookid)
    # book_num_ = models.Ebook.objects.filter(book_num=booknum)
    book_num = str(booknum)
    # 获取对应表的id
    book_id = get_object_or_404(Ebook, id=ebookid)
    # 获取图书名
    get_books = models.Ebook.objects.get(id=book_id.id)
    book_names = get_books.book_name
    # 根据携带的参数过滤每一本不同的书
    comments = models.BookComment.objects.filter(percent_type='h')
    if comments.exists():
        # 获取图书图片,防止没爬取到对应数据时报空值
        one_img_ = models.BookComment.objects.filter(ebook_id=book_id.id)[:1].get()
        if one_img_:
            one_img = one_img_.book_img
        return render(request, 'god.html',
                      {'comments': comments, 'one_img': one_img, 'book_names': book_names,
                       'book_nums': book_num, 'book_id': ebookid, 'percent_type': value})
    else:
        # 爬取的链接booknum是爬取的书本特有编号，value有h（爬取好评），m（爬取一般评论），l（爬取差评）
        link = f"https://book.douban.com/subject/{book_num}/comments/?percent_type={value}"
        # 调用定义好的爬虫函数（384行）
        get_comment(link, book_id, value)
        one_img_ = models.BookComment.objects.filter(ebook_id=book_id.id)[:1].get()
        if one_img_:
            one_img = one_img_.book_img

        return render(request, 'god.html',
                      {'comments': comments, 'one_img': one_img, 'book_names': book_names,
                       'book_nums': book_num, 'book_id': ebookid, 'percent_type': value})


# 一般
@never_cache
def avg(request, booknum, bookid, value):
    # 将获取的id转换为int类型
    ebookid = int(bookid)

    # # 根据图书信息已经爬取的书籍id来获取数据
    # book_num_ = models.Ebook.objects.filter(book_num=booknum)
    book_num = str(booknum)
    # 获取对应表的id
    book_id = get_object_or_404(Ebook, id=ebookid)
    # 获取图书名
    get_books = models.Ebook.objects.get(id=book_id.id)
    book_names = get_books.book_name
    # 根据携带的参数过滤每一本不同的书
    comments = models.BookComment.objects.filter(percent_type='m')
    if comments.exists():
        # 获取图书图片,防止没爬取到对应数据时报空值
        one_img_ = models.BookComment.objects.filter(ebook_id=book_id.id)[:1].get()
        if one_img_:
            one_img = one_img_.book_img
        return render(request, 'avg.html',
                      {'comments': comments, 'one_img': one_img, 'book_names': book_names,
                       'book_nums': booknum, 'book_id': ebookid, 'percent_type': value})
    else:
        link = f"https://book.douban.com/subject/{book_num}/comments/?percent_type={value}"
        get_comment(link, book_id, value)
        one_img_ = models.BookComment.objects.filter(ebook_id=book_id.id)[:1].get()
        if one_img_:
            one_img = one_img_.book_img
        return render(request, 'avg.html',
                      {'comments': comments, 'one_img': one_img, 'book_names': book_names,
                       'book_nums': book_num, 'book_id': ebookid, 'percent_type': value})


# 差评
@never_cache
def bad(request, booknum, bookid, value):
    # 将获取的id转换为int类型
    ebookid = int(bookid)
    # book_num_ = models.Ebook.objects.filter(book_num=booknum)
    book_num = str(booknum)
    # 获取对应表的id
    book_id = get_object_or_404(Ebook, id=ebookid)
    # 获取图书名
    get_books = models.Ebook.objects.get(id=book_id.id)
    book_names = get_books.book_name
    # 根据携带的参数过滤每一本不同的书
    comments = models.BookComment.objects.filter(percent_type='l')
    one_img_ = models.BookComment.objects.filter(ebook_id=book_id.id)[:1].get()
    if comments.exists():
        # 获取图书图片,防止没爬取到对应数据时报空值
        if one_img_:
            one_img = one_img_.book_img
        return render(request, 'bad.html',
                      {'comments': comments, 'one_img': one_img, 'book_names': book_names, 'book_nums': book_num,
                       'book_id': ebookid, 'percent_type': value})
    else:
        link = f"https://book.douban.com/subject/{book_num}/comments/?percent_type={value}"
        get_comment(link, book_id, value)
        if one_img_:
            one_img = one_img_.book_img
        return render(request, 'bad.html',
                      {'comments': comments, 'one_img': one_img, 'book_names': book_names, 'book_nums': book_num,
                       'book_id': ebookid, 'percent_type': value})


# 爬取豆瓣读书的数据
def get_book(url):
    response = requests.get(url, headers=headers)
    html = etree.HTML(response.text)
    books = html.xpath('//tr[@class="item"]')
    comment = []
    for book in books:
        comment_ = book.xpath('td/p[2]/span/text()')
        comment.append(comment_[0] if len(comment_) != 0 else ' ')
    book_nums = []
    book_nums_ = html.xpath('//div[@class="pl2"]/a/@href')
    for i in book_nums_:
        data = i.split('/')
        book_nums.append(data[-2])
    book_name = html.xpath('//div[@class="pl2"]/a/@title')
    rating_nums = html.xpath('//span[@class="rating_nums"]/text()')
    rating_people_ = html.xpath('//span[@class="pl"]/text()')
    rating_people = []
    for i in rating_people_:
        rating_people.append(i.strip('()\n 人评价'))
    book_infos = html.xpath('//p[@class="pl"]/text()')
    autor = []
    translator = []
    publisher = []
    publisher_data = []
    price = []
    for j in book_infos:
        data = j.split('/')
        autor.append(data[0])
        translator.append(data[1] if len(data) == 5 else ' ')
        publisher.append(data[-3])
        publisher_data.append(data[-2])
        price.append(data[-1])
    book_data = []
    for i in range(25):
        book = Ebook(
            book_name=book_name[i],
            autor=autor[i],
            translator=translator[i],
            publisher=publisher[i],
            publisher_data=publisher_data[i],
            price=price[i],
            rating_nums=rating_nums[i],
            rating_people=rating_people[i],
            comment=comment[i],
            book_num=book_nums[i],
        )
        book_data.append(book)

    # 将书籍数据保存到数据库
    Ebook.objects.bulk_create(book_data)


# 爬取豆瓣评论数据
def get_comment(url, bid, val):
    response = requests.get(url, headers=headers)
    html = etree.HTML(response.text)
    reader = html.xpath('//div[@class="comment"]/h3/span[@class="comment-info"]/a[1]/text()')
    star = html.xpath('//div[@class="comment"]/h3/span[@class="comment-info"]/span[1]/@title')
    time = html.xpath('//div[@class="comment"]/h3/span[@class="comment-info"]/a[2]/text()')
    short_comm = html.xpath('//div[@class="comment"]/p/span/text()')
    read_img = html.xpath('//div[@class="avatar"]/a/img/@src')
    book_img = html.xpath('//div[@class="indent subject-info"]/div/a/img/@src')
    book_data = []

    # 计算长度
    default_value = '无'

    # 将star列表补充到与其他列表相同的长度
    star.extend([default_value] * (len(reader) - len(star)))

    for i in range(20):
        book = BookComment(
            reader=reader[i],
            star=star[i],
            time=time[i],
            short_comm=short_comm[i],
            read_img=read_img[i],
            book_img=book_img[0],
            ebook=bid,
            percent_type=val
        )
        book_data.append(book)

    # 将获取的评论保存到数据库
    BookComment.objects.bulk_create(book_data)
