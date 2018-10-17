#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import sqlite3, os, requests
import xml.etree.ElementTree as ET
from datetime import datetime
from time import strftime
import os
from os import listdir
from os.path import exists, join


def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
    # Print New Line on Complete
    if iteration == total:
        print()

def br(val):
    return "'"+str(val).replace("'","''")+"'"

def select(sql):
    conn = sqlite3.connect('categories.db')
    c = conn.cursor()
    c.execute(sql)
    data = c.fetchall()
    conn.commit()
    conn.close()
    return data

def execute(sql):
    conn = sqlite3.connect('categories.db')
    c = conn.cursor()
    c.execute(sql)
    conn.commit()
    conn.close()

def delete_db():
    categories = os.path.dirname(os.path.realpath(__file__))+'\\'+'categories.db' #defining path of categories
    if os.path.exists(categories):
        os.remove(categories)
    execute('CREATE TABLE categories (CategoryID integer primary key, CategoryName text, CategoryLevel integer, BestOfferEnabled integer, CategoryParentID integer)')

def rebuild():
    print('\n\trender')
    print('\t--------------------------------------------------------\n')
    print('\tdeleting database categories.')
    delete_db()
    request_headers = {
        'X-EBAY-API-CALL-NAME': 'GetCategories',
        'X-EBAY-API-APP-NAME': 'EchoBay62-5538-466c-b43b-662768d6841',
        'X-EBAY-API-CERT-NAME': '00dd08ab-2082-4e3c-9518-5f4298f296db',
        'X-EBAY-API-DEV-NAME': '16a26b1b-26cf-442d-906d-597b60c41c19',
        'X-EBAY-API-SITEID': str(0),
        'X-EBAY-API-COMPATIBILITY-LEVEL': str(861)
    }

    data_xml = '''
        <?xml version="1.0" encoding="utf-8"?>
        <GetCategoriesRequest xmlns="urn:ebay:apis:eBLBaseComponents">
            <CategorySiteID>0</CategorySiteID>
            <ViewAllNodes>True</ViewAllNodes>
            <DetailLevel>ReturnAll</DetailLevel>
            <RequesterCredentials>
            <eBayAuthToken>AgAAAA**AQAAAA**aAAAAA**PlLuWA**nY+sHZ2PrBmdj6wVnY+sEZ2PrA2dj6wFk4GlDpaDpAudj6x9nY+seQ**LyoEAA**AAMAAA**wSd/jBCbxJHbYuIfP4ESyC0mHG2Tn4O3v6rO2zmnoVSF614aVDFfLSCkJ5b9wg9nD7rkDzQayiqvwdWeoJkqEpNQx6wjbVQ1pjiIaWdrYRq+dXxxGHlyVd+LqL1oPp/T9PxgaVAuxFXlVMh6wSyoAMRySI6QUzalepa82jSQ/qDaurz40/EIhu6+sizj0mCgjcdamKhp1Jk3Hqmv8FXFnXouQ9Vr0Qt+D1POIFbfEg9ykH1/I2CYkZBMIG+k6Pf00/UujbQdne6HUAu6CSj9wGsqQSAEPIXXvEnVmtU+6U991ZUhPuA/DMFEfVlibvNLBA7Shslp2oTy2T0wlpJN+f/Jle3gurHLIPc6EkEmckEpmSpFEyuBKz+ix4Cf4wYbcUk/Gr3kGdSi20XQGu/ZnJ7Clz4vVak9iJjN99j8lwA2zKW+CBRuHBjZdaUiDctSaADHwfz/x+09bIU9icgpzuOuKooMM5STbt+yJlJZdE3SRZHwilC4dToTQeVhAXA4tFZcDrZFzBmJsoRsJYrCdkJBPeGBub+fqomQYyKt1J0LAQ5Y0FQxLHBIp0cRZTPAuL/MNxQ/UXcxQTXjoCSdZd7B55f0UapU3EsqetEFvIMPxCPJ63YahVprODDva9Kz/Htm3piKyWzuCXfeu3siJvHuOVyx7Q4wyHrIyiJDNz5b9ABAKKauxDP32uqD7jqDzsVLH11/imKLLdl0U5PN+FP30XAQGBAFkHf+pAvOFLrdDTSjT3oQhFRzRPzLWkFg</eBayAuthToken>
            </RequesterCredentials>
        </GetCategoriesRequest>
    '''
    print('\tretrieving GetCategories eBay API.')
    r =requests.post('https://api.sandbox.ebay.com/ws/api.dll', headers=request_headers, data=data_xml)
    root = ET.fromstring(r.text.encode('utf-8'))
    categories = root.find('{urn:ebay:apis:eBLBaseComponents}CategoryArray')
    print('\tcreating and inserting values into new database categories.\n')
    conn = sqlite3.connect('categories.db')
    c = conn.cursor()

    count = len(categories)
    printProgressBar(0, count, prefix = '\tprogress:', suffix = '', length = 50)
    i = 0

    for category in categories:
        CategoryID          = category.find('{urn:ebay:apis:eBLBaseComponents}CategoryID').text
        CategoryName        = category.find('{urn:ebay:apis:eBLBaseComponents}CategoryName').text
        CategoryLevel       = category.find('{urn:ebay:apis:eBLBaseComponents}CategoryLevel').text
        CategoryParentID    = category.find('{urn:ebay:apis:eBLBaseComponents}CategoryParentID').text
        BestOfferEnabled    = category.find('{urn:ebay:apis:eBLBaseComponents}BestOfferEnabled')
        if hasattr(BestOfferEnabled, 'text'):BestOfferEnabled = BestOfferEnabled.text
        else: BestOfferEnabled = ''

        i += 1
        printProgressBar(i, count, prefix = '\tprogress:', suffix = '', length = 50)

        sql = """ INSERT INTO categories (CategoryID, CategoryName, CategoryLevel, BestOfferEnabled, CategoryParentID) VALUES (%s, %s, %s, %s, %s)
        """ % (br(CategoryID),br(CategoryName),br(CategoryLevel),br(BestOfferEnabled),br(CategoryParentID))

        c.execute(sql)
        conn.commit()
    conn.close()
    count = select("select count(CategoryID) from categories")[0][0]
    print('\trebuild complete '+str(count)+ ' categories added')

def render_html(CategoryID,CategoryName, content, timestamp):
    html = '''
        <!DOCTYPE html>
        <html lang="en" dir="ltr">
          <head>
            <meta charset="utf-8">
            <title></title>
            <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">
            <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap-theme.min.css" integrity="sha384-rHyoN1iRsVXV4nD0JutlnGaslCJuC7uwjduW9SVrLvRYooPp2bWYgmgJQIXwl/Sp" crossorigin="anonymous">

            <link href="https://fonts.googleapis.com/css?family=Roboto:300" rel="stylesheet">
            <style media="screen">
              body {font-family: 'Roboto', sans-serif;}
              img {max-height: 50px}
              .dir{cursor: pointer}
              .blue{color: #009FE3}
            </style>

          </head>
          <body>
            <div class="container" style="width:50%">
              <br>
              <br>
              <div class="row">
                <div class="col-md-12">

                    <div class="pull-left">
                     <!-- <img style="margin-top:15px" src="" alt=""> -->
                      <h2>Result GetCategories Ebay</h2>
                      <h4>CategoryID: '''+str(CategoryID)+' | '+ str(CategoryName)+ '''</h4>
                      <h5 style="color:#009FE3">Created: '''+str(timestamp)+'''</h5>
                    </div>
                </div>
              </div>
              <hr>
              <div class="row">
                <div class="col-md-12">
                     '''+str(content)+'''
                </div>
              </div>
            </div>
          </body>
          <footer>
            <script src="https://code.jquery.com/jquery-3.3.1.min.js" integrity="sha256-FgpCb/KJQlLNfOu91ta32o/NMZxltwRo8QtmkMRdAu8=" crossorigin="anonymous"></script>
            <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js" integrity="sha384-Tc5IQib027qvyjSMfHjOMaLkfuWVxZxUPnCJA7l2mCWNIpG9mGCD8wGNIcPD7Txa" crossorigin="anonymous"></script>
            <script type="text/javascript">
              $('.dir').click(function(e) {e.stopPropagation(); $(this).children().slideToggle();});
            </script>
          </footer>
        </html>
    '''
    return html

def get_child(categories=[]):
    list =[]
    list.append('<ul>')
    for category in categories:
        CategoryID       = category[0]
        CategoryName     = category[1]
        CategoryLevel    = category[2]
        BestOfferEnabled = category[3]
        children = select('''select CategoryID, CategoryName, CategoryLevel, BestOfferEnabled from categories  where CategoryID != CategoryParentID  and CategoryParentID = %s''' % (br(CategoryID)))
        count = len(children)
        collapsable = 'class ="dir blue"'
        if str(count) =='0':
            collapsable = 'class ="dir" style="color:black;cursor:auto"'
        list.append(' <li '+str(collapsable)+'>'+str(CategoryID)+' '+str(CategoryName)+' | '+str(roman(int(CategoryLevel)))+' | Offer: '+str(BestOfferEnabled)+' ('+str(count)+')')
        if children !=[]:
            list.append(get_child(children))
    list.append('   </li>')
    list.append('</ul>')
    return '\n'.join(list)

def get_tree(CategoryID=''):
    filter, list ='', []

    if CategoryID !='':filter = 'and CategoryID = %s' % (br(CategoryID))
    categories = select('select CategoryID, CategoryName, CategoryLevel, BestOfferEnabled from categories  where CategoryID = CategoryParentID %s' % (filter))
    if categories !=[]:
        list.append(get_child(categories))
        return '\n'.join(list)
    else:
        categories = select('''select CategoryID, CategoryName, CategoryLevel, BestOfferEnabled from categories  where CategoryID != CategoryParentID  and CategoryID = %s''' % (br(CategoryID)))
        if categories !=[]:
            list.append(get_child(categories))
            return '\n'.join(list)
        else:
            return 'noCategoryID'

def render(CategoryID=''):
    print('\n\trender')
    print('\t--------------------------------------------------------\n')
    path = os.path.dirname(os.path.realpath(__file__))
    print('\tpath: '+str(path))
    print('\tretrieving tree for CategoryID...')
    tree = get_tree(CategoryID)
    if tree =='noCategoryID':
        print ('\n\tCategoryID %s not found, no file to create' % (CategoryID))
    else:
        print('\ttree for CategoryID retrieved')
        CategoryName = select('''select CategoryName from categories  where CategoryID = %s''' % (br(CategoryID)))[0][0]
        content = render_html(CategoryID, CategoryName, tree, datetime.now().strftime('%d/%m/%Y %H:%M'))
        print('\trendering '+str(CategoryID)+'.html')
        f = open(path+'\\'+str(CategoryID)+'.html','w', encoding='utf-8')
        f.write(content)
        f.close()
        print ('\n\tcompleted: '+str(CategoryID)+'.html with CategoryID: '+str(CategoryID)+' | '+str(CategoryName))

def remove_html(CategoryID=''):
    print('\n\tremove_html')
    print('\t--------------------------------------------------------\n')
    path = os.path.dirname(os.path.realpath(__file__))
    print('\tpath: '+str(path))
    files = [f.lower() for f in os.listdir(path) if f.endswith('.html')]
    print('\tfiles: '+str(files))
    if files ==[]:
        print ('\tno files to remove in current path')
    else:
        if CategoryID!='all':
            html = (str(CategoryID)+'.html')
            if html in files:
                os.remove(path+'\\'+html)
                print('\tremoved %s' % (html))
            else:
                print ('\tno %s in current path' % (html))
        elif CategoryID=='all':
            print('\n\tabout to remove all.html files')
            q = ''
            q = input('\tare you sure? y/n : ')
            if q =='y':
                for file in files:
                    os.remove(path+'\\'+file)
                    print('\tremoved %s' % (file))
            else:
                print('\tremove_html aborted')


def help():
    print('\n\tplease provide an argument e.g.\n')
    print('\t--rebuild')
    print('\t--render <category_id>')
    print('\t--remove_html <category_id>')
    print('\t--remove_html all')

def missing_render():
    print('\n\tmissing argument <category_id> after --render')
    print('\t--render <category_id>')

def missing_remove_html():
    print('\n\tmissing argument <category_id> | <all> after --remove_html')
    print('\t--remove_html <category_id> | <all>')


numerals = [
        {'letter': 'M', 'value': 1000},
        {'letter': 'D', 'value': 500},
        {'letter': 'C', 'value': 100},
        {'letter': 'L', 'value': 50},
        {'letter': 'X', 'value': 10},
        {'letter': 'V', 'value': 5},
        {'letter': 'I', 'value': 1},
    ]

num_map = [(1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'), (100, 'C'), (90, 'XC'),(50, 'L'), (40, 'XL'), (10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')]

def roman(num):
    roman = ''
    while num > 0:
        for i, r in num_map:
            while num >= i:
                roman += r
                num -= i
    return roman

if __name__ == "__main__":
    # os.system('')
    # os.system('cls')
    try:argument_1 = (sys.argv[1])
    except:argument_1=''
    try:argument_2 = (sys.argv[2])
    except:argument_2=''

    print('\n\CHALLENGE')
    print('\t-----------------------------------------------------------------')
    print('\tAuthor  : Stephan M. Semerad')
    print('\tWritten : 11/Jul/2018')


    if argument_1 =='':
        help()
    elif argument_1 =='' and argument_2 =='':
        help()
    elif argument_1 =='--rebuild':
        rebuild()
    elif argument_1 =='--remove_html' and argument_2 !='':
        remove_html(argument_2)
    elif argument_1 =='--remove_html' and argument_2 =='':
        missing_remove_html()
    elif argument_1 =='--render' and argument_2 =='':
        missing_render()
    elif argument_1 =='--render' and argument_2 !='':
        render(argument_2)
