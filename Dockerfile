FROM python:3.6
ENV PATH /usr/local/bin:$PATH
ADD . /code
WORKDIR /code
RUN pip install -i http://pypi.douban.com/simple --trusted-host pypi.douban.com -r requirements.txt
WORKDIR /code/sikuyiproject/spiders
CMD  scrapy runspider sikuyi.py