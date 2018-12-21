#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from bs4 import BeautifulSoup
import pandas as pd
import re
import urllib
import http.cookiejar
import time

urlroot='http://www.toyodiy.com/parts/'
urlpage=[]

#KUN26L-PRMDYG and -HRMDY (one comes from Argentina and the other from Thailand). 
#The European equivalent is KUN26L-PRMDHW

urlpage.append('g_G_2015_TOYOTA_HILUX_KUN26L-PRMDYG.html')
urlpage.append('g_E_2015_TOYOTA_HILUX_KUN26R-PRMDYW.html')

#urlpage.append('g_G_2015_TOYOTA_HILUX_KUN26L-PRMDYG.html')
#urlpage.append('g_E_2005_TOYOTA_LAND+CRUISER+PRADO_KDJ120L-GKMEYW.html')


# In[ ]:


def open_url(url):
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    request = urllib.request.Request(url)
    response = opener.open(request)
    return response.read()


# In[ ]:


def get_url_list(url):
    href=[]
    
    html_string = open_url(url)
    print (html_string)
    soup = BeautifulSoup(html_string, 'html.parser')

    soup=soup.find('div', attrs={'class': 'msg1 vs2'})
    
    for link in soup.find_all('a'):
        href.append(link.get('href'))
    
    return href


# In[ ]:


def generate_parts(url):

    html_string = open_url(url)
    soup = BeautifulSoup(html_string, 'html.parser')

    href=[]
    txt=[]

    for link in soup.find('div', attrs={'class': 'diag-list'}):
        href.append(link.find('a')['href'])
        txt.append(link.find('a').text)

    df = pd.DataFrame({'Description': [], 'Part_Number' : []})
    #keylist = list(df.columns.values) --- this worked in a paragraph but not once in a function!!
    keylist=df.columns.values.tolist()

    for i in href:
        page = open_url(urlroot+i)
    
        soup = BeautifulSoup(page, 'html.parser')
    
        n=-1
        dict={}
        for i in soup.findAll('tbody')[0].findAll('tr'):
            n=n+1
            lim=i.findAll('td')[0].text
            if n==0:
            ### DESCRIPTION FIELD ###
            #if description starts with 5 digits and a -, then this is a part associated with description on line above
            #this is slicing syntax - slices are the places between the characters
                if 'STD. PART' in lim:
                        desc='STD. PART'
                        lim=lim[0:11]
                        n=2
                else:
                    if lim[0:5].isdigit() and lim[5:6]=='-':
                        lim=lim[0:11]
                        n=2
                    else:
                        lim=i.findAll('td')[1].text
                        start=re.search('\D', lim).start()
                        lim=lim[start:]
                        desc=lim
            if n==1:
            #grab 11 chars which should be part number
                lim=lim[0:11]
            if n!=2:
                dict[keylist[n]]=lim
            else:
                dict[keylist[0]]=desc
                dict[keylist[1]]=lim
            if n==1:
                df = df.append(dict, ignore_index=True)
                dict.clear()
                n=-1
            if n==2:
                df = df.append(dict, ignore_index=True)
                dict.clear()
                n=-1
    
        #pause to prevent auto download detection
        time.sleep(1)
    
    return df


# In[ ]:


urllist=get_url_list(urlroot+urlpage[0])

print(urllist[0])
df1=generate_parts(urlroot+urllist[0])
print(urllist[1])
df2=generate_parts(urlroot+urllist[1])
print(urllist[2])
df3=generate_parts(urlroot+urllist[2])
print(urllist[3])
df4=generate_parts(urlroot+urllist[3])

urllist=get_url_list(urlroot+urlpage[1])

print(urllist[0])
df5=generate_parts(urlroot+urllist[0])
print(urllist[1])
df6=generate_parts(urlroot+urllist[1])
print(urllist[2])
df7=generate_parts(urlroot+urllist[2])
print(urllist[3])
df8=generate_parts(urlroot+urllist[3])


# In[ ]:


bigdf1=df1.append([df2,df3,df4],ignore_index=True)
bigdf2=df5.append([df6,df7,df8],ignore_index=True)


# In[ ]:


#bigdf1=bigdf1.append({'Description':'TEST ITEM', 'Part_Number':'1234'}, ignore_index=True)


# In[ ]:


#indicator=True gives _merge column will show left_only if only left side exists in an outer join
df=pd.merge(bigdf1,bigdf2,on=['Part_Number'],how="outer",indicator=True)


# In[ ]:


dfleft=df[df['_merge']=='left_only']


# In[ ]:


dfright=df[df['_merge']=='right_only']


# In[ ]:


dfleft.to_csv('arg.csv')
dfright.to_csv('uk.csv')

