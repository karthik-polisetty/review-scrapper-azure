from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import pandas as pd
import logging

logging.basicConfig(filename="scrapper.log",filemode='w',level=logging.DEBUG,format= '%(asctime)s:%(levelname)s:%(message)s')

application = Flask(__name__)
app = application

@app.route("/", methods = ['GET'])
def homepage():
    return render_template('index.html')

@app.route("/review", methods = ['POST', 'GET'])
def scrapper():
    if request.method == 'POST':
        try:
            searchstring = request.form.get('content').replace(" ","")
            flipkart_url = 'https://www.flipkart.com/search?q=' + searchstring
            uclient = uReq(flipkart_url)
            flipkartpage= uclient.read()
            uclient.close()
            flipkart_html = bs(flipkartpage,'html.parser')
            bigboxes = flipkart_html.findAll('div', {'class':"_1AtVbE col-12-12"})
            del bigboxes[0:3]
            box = bigboxes[0]
            productlink = 'https://www.flipkart.com' + box.div.div.div.a['href']
            prodreq = requests.get(productlink)
            prod_html = bs(prodreq.text,'html.parser')
            comment_boxes = prod_html.find_all('div', {'class': "_16PBlm"})

            # filename = searchstring + ".csv"
            # f = open(filename,'w')
            # headers = 'Product, CustomerName, Rating, Heading, Comment\n'
            # f.write(headers)
            reviews=[]
            for comment in comment_boxes:
                try:
                    name  = comment.div.div.find_all('p',{'class':"_2sc7ZR _2V5EHH"})[0].text
                except Exception as e:
                    logging.info("some error occurred while logging name")
                    logging.error(e)

                    

                try:
                    rating = comment.div.div.div.div.text
                except Exception as e:
                    logging.info("some error occurred while logging rating")
                    logging.error(e)

                try:
                    heading = comment.div.div.div.p.text
                except Exception as e:
                    logging.info("some error occurred while logging heading")
                    logging.error(e)

                try:
                    commenttext = comment.div.div.find_all('div', {'class': ""})[0].div.text
                except Exception as e:
                    logging.info("some error occurred while logging comment")
                    logging.error(e)

                mydict = {"Product":searchstring, "Name":name,"Rating":rating,"CommentHead":heading,"Comment":commenttext}
                reviews.append(mydict)

            data= pd.DataFrame(reviews)
            data.to_csv(f"{searchstring}here.csv")
            logging.info('file csv successfully saved')
            logging.info(f'{reviews} is the logged data')
            return render_template('result.html', reviews = reviews[0:(len(reviews)-1)])
        
        except Exception as e:
            
            logging.info(e)
            return 'something is wrong'
    else:
        return render_template('index.html')



    
    

if __name__=="__main__":
    app.run(debug=True)
