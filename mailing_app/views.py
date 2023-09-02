from __future__ import print_function

# Django imports
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.core.mail import EmailMessage
from django.core.files.storage import FileSystemStorage
from django.core.mail import EmailMultiAlternatives
from django.contrib import messages

#Email fetch extras
from email.utils import getaddresses, parseaddr
import re
from pprint import pprint as pp
# ADDR_PATTERN = re.compile("<(.+)>") 
ADDR_PATTERN = re.compile('<(.*?)>') 


# Standard package imports
import os
import datetime

# Third-party imports
import xlrd

# Project imports
from ircell import settings

#Fetching mails using IMAP (inbox)
import imaplib
import email
from email.header import decode_header
import webbrowser
import os

#Gmail API used to send
# import os.path
# from googleapiclient.discovery import build
# from google_auth_oauthlib.flow import InstalledAppFlow
# from google.auth.transport.requests import Request
# from google.oauth2.credentials import Credentials

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']



# account credentials
username = "testing25199080@gmail.com"
password = "kk123456kk123hitheres"




THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
abpath = settings.BASE_DIR



def indexrepeatt(request, itr):
    print("testing......... testing testing.........")
    user = request.user
    # create an IMAP4 class with SSL 
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    # authenticate
    imap.login(username, password)
    status, messages = imap.select("[Gmail]/Spam")
    itr= int (itr)
    # number of top emails to fetch
    N = 4
    stop = 0
    l,m,n,time,eid,ccall,ccall2,id,indicator=[],[],[],[],[],[],[],[],[]
    #SS={1:l, 2:m, 3:n}
    #SS={'sub':'', 'fro':'', 'bod':''}
    # total number of emails
    messages = int(messages[0])
    messages = messages - itr
    for i in range(messages, messages-N, -1):
    # fetch the email message by ID
        print(i)
        id.append(i)
        res, msg = imap.fetch(str(i), "(RFC822)")
        for response in msg:
            if isinstance(response, tuple):
                indicator.append(0)
                # parse a bytes email into a message object
                msg = email.message_from_bytes(response[1])
                # decode the email subject
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    # if it's a bytes, decode to str
                    subject = subject.decode(encoding)
                # decode email sender
                From, encoding = decode_header(msg.get("From"))[0]
                if isinstance(From, bytes):
                    From = From.decode(encoding)
                Date, encoding = decode_header(msg.get("Date"))[0]
                if isinstance(From, bytes):
                    Date = Date.decode(encoding)
                # print("Subject:", subject)
                # print("From:", From)

                tos = msg.get_all('to', [])
                ccs = msg.get_all('cc', [])
                # resent_tos = msg.get_all('resent-to', [])
                # resent_ccs = msg.get_all('resent-cc', [])
                all_recipients = getaddresses(tos + ccs)
                # print("Subject:", subject)
                # print("From:", From)
                # print(tos)
                # print(all_recipients)

                # if the email message is multipart
                if msg.is_multipart():
                    # iterate over email parts
                    for part in msg.walk():
                        # extract content type of email
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        try:
                            # get the email body
                            body = part.get_payload(decode=True).decode()
                        except:
                            pass
                        if content_type == "text/plain" and "attachment" not in content_disposition:
                            # print text/plain emails and skip attachments
                            # print(body)
                            body2 = body
                        #elif content_type == "text/html" and "attachment" not in content_disposition:
                            #print(body)
                        elif "attachment" in content_disposition:
                            # download attachment
                            filename = part.get_filename()
                            if filename:
                                folder_name = clean(subject)
                                indicator.pop()
                                indicator.append(1)
                                # if not os.path.isdir(folder_name):
                                    # make a folder for this email (named after the subject)
                                    # os.mkdir(folder_name)
                                # filepath = os.path.join(folder_name, filename)
                                # download attachment and save it
                                # open(filepath, "wb").write(part.get_payload(decode=True))
                else:
                    # extract content type of email
                    content_type = msg.get_content_type()
                    # get the email body
                    body = msg.get_payload(decode=True).decode()
                    if content_type == "text/plain":
                        # print only text email parts
                        # print(body)
                        body2 = body
                if content_type == "text/html":
                    # if it's HTML, create a new HTML file and open it in browser
                    folder_name = clean(subject)
                    # if not os.path.isdir(folder_name):
                        # make a folder for this email (named after the subject)
                        # os.mkdir(folder_name)
                    filename = "index.html"
                    # filepath = os.path.join(folder_name, filename)
                    # write the file
                    # open(filepath, "w").write(body)
                    # open in the default browser
                    # webbrowser.open(filepath)
                print("="*100)
        #SS['sub']+=subject
        #SS['fro']+=From 
        #SS['bod']+=body
        pos1 = From.find("<") + 1
        pos2 = From.find(">")
        if(pos2 == -1):
            emailid = From[pos1:]
            # print(emailid)
        else:
            emailid = From[pos1:pos2]
        l.append(subject)
        m.append(From)
        n.append(body)
        time.append(Date)
        eid.append(emailid)
        x = [0,1,2,3]
        # print(body2)
        for ii in all_recipients:
            ccall.append(ii[1])
        ccall2.append(ccall)
        ccall=[]
        if(i==1 or i==2):
            i=0
            break

    #SS={1: l, 2: m, 3:n}
    #print(SS)
    # print(n[2])
    myL=zip(l,m,n,time,x,eid,ccall2,id,indicator)
    #print(myL)
    itr+=4
    itr2=itr-8
    if(i==0):
        stop = 1
    context={'myL':myL,'subject':l,'content':n,'from':m,'time':time,'itr':itr,'itr2':itr2,'stop':stop,'ccall':ccall2,'ids':id}
    #context={''}
    # print(context)
    # close the connection and logout
    imap.close()
    imap.logout()
    if user.is_irc:
        return render(request, 'MailsInSpamFolder.html', context)
    else:
        return HttpResponse("<h1>You don't have permission to view this page</h1>")

# Features to be worked upon the spam folder
# Marking the mail as not spam
# Throws error when there's no mail in the spam folder - done
def spamm(request):
    try:
        user = request.user

        # [Gmail]/Spam

        # create an IMAP4 class with SSL 
        imap = imaplib.IMAP4_SSL("imap.gmail.com")
        # authenticate
        imap.login(username, password)
        status, messages = imap.select("[Gmail]/Spam")
        # number of top emails to fetch
        N = 4
        l,m,n,time,eid,ccall,ccall2,id,indicator=[],[],[],[],[],[],[],[],[]
        #SS={1:l, 2:m, 3:n}
        #SS={'sub':'', 'fro':'', 'bod':''}
        # total number of emails
        itr=0
        messages = int(messages[0])
        print("######## ########## messages", messages)
        
        for i in range(messages, messages-N, -1):
        # fetch the email message by ID
            print(i)
            id.append(i)
            res, msg = imap.fetch(str(i), "(RFC822)")
            for response in msg:
                if isinstance(response, tuple):
                    indicator.append(0)
                    # parse a bytes email into a message object
                    msg = email.message_from_bytes(response[1])
                    # decode the email subject
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        # if it's a bytes, decode to str
                        subject = subject.decode(encoding)
                    # decode email sender
                    From, encoding = decode_header(msg.get("From"))[0]
                    if isinstance(From, bytes):
                        From = From.decode(encoding)
                    Date, encoding = decode_header(msg.get("Date"))[0]
                    if isinstance(From, bytes):
                        Date = Date.decode(encoding)

                    tos = msg.get_all('to', [])
                    ccs = msg.get_all('cc', [])
                    # resent_tos = msg.get_all('resent-to', [])
                    # resent_ccs = msg.get_all('resent-cc', [])
                    all_recipients = getaddresses(tos + ccs)
                    # print("Subject:", subject)
                    # print("From:", From)
                    # print(tos)
                    # print(all_recipients)
                    # if the email message is multipart

                    if msg.is_multipart():
                        # iterate over email parts
                        for part in msg.walk():
                            # extract content type of email
                            content_type = part.get_content_type()
                            content_disposition = str(part.get("Content-Disposition"))
                            try:
                                # get the email body
                                body = part.get_payload(decode=True).decode()
                            except:
                                pass
                            if content_type == "text/plain" and "attachment" not in content_disposition:
                                # print text/plain emails and skip attachments
                                # print(body)
                                body2 = body
                            #elif content_type == "text/html" and "attachment" not in content_disposition:
                                #print(body)
                            elif "attachment" in content_disposition:
                                # download attachment
                                filename = part.get_filename()
                                if filename:
                                    folder_name = clean(subject)
                                    indicator.pop()
                                    indicator.append(1)
                                    # if not os.path.isdir(folder_name):
                                        # make a folder for this email (named after the subject)
                                        # os.mkdir(folder_name)
                                    # filepath = os.path.join(folder_name, filename)
                                    # download attachment and save it
                                    # open(filepath, "wb").write(part.get_payload(decode=True))
                                                
                    else:
                        # extract content type of email
                        content_type = msg.get_content_type()
                        # get the email body
                        body = msg.get_payload(decode=True).decode()
                        if content_type == "text/plain":
                            # print only text email parts
                            # print(body)
                            body2 = body
                    if content_type == "text/html":
                        # if it's HTML, create a new HTML file and open it in browser
                        folder_name = clean(subject)
                        # if not os.path.isdir(folder_name):
                            # make a folder for this email (named after the subject)
                            # os.mkdir(folder_name)
                        # filename = "index.html"
                        # filepath = os.path.join(folder_name, filename)
                        # write the file
                        # open(filepath, "w").write(body)
                        # open in the default browser
                        # webbrowser.open(filepath)
                    print("="*100)
            #SS['sub']+=subject
            #SS['fro']+=From 
            #SS['bod']+=body
            pos1 = From.find("<") + 1
            pos2 = From.find(">") 
            if(pos2 == -1):
                emailid = From[pos1:]
            else:
                emailid = From[pos1:pos2]
            # print(emailid)
            eid.append(emailid)
            l.append(subject)
            m.append(From)
            n.append(body)
            time.append(Date)
            x = [0,1,2,3]
            for ii in all_recipients:
                # print("HOLA LOOP", ii[1])
                ccall.append(ii[1])
            ccall2.append(ccall)
            ccall=[]
            if(i==1 or i==2):
                break
            # print(body2)
        #SS={1: l, 2: m, 3:n}
        #print(SS)
        # print(n[2])
        myL=zip(l,m,n,time,x,eid,ccall2,id,indicator)
        #print(myL)
        itr+=4
        stop=0
        itr2=0
    
        context={'myL':myL,'subject':l,'content':n,'from':m,'time':time,'itr':itr,'itr2':itr2,'stop':stop,'ccall':ccall2,'ids':id}
        #context={''}
        # print(context)
        # close the connection and logout
        imap.close()
        imap.logout()
        # print("HOLA=   ",ccall2)
        if user.is_irc and messages!=0:
            return render(request, 'MailsInSpamFolder.html', context)
        # elif not user.is_irc and messages==0:
        #     return HttpResponse("<h1>No mails in Spam Folder</h1>")
        else:
            return HttpResponse("<h1>You don't have permission to view this page</h1>")
    except:
        return HttpResponse("<h1>No mails in Spam Folder</h1>")

def searchh(request):
    user = request.user
    # create an IMAP4 class with SSL 
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    # authenticate
    imap.login(username, password)
    status, messages = imap.select("INBOX")
    # number of top emails to fetch
    N = 4
    l,m,n,time,eid,ccall,ccall2,id,indicator=[],[],[],[],[],[],[],[],[]
    #SS={1:l, 2:m, 3:n}
    #SS={'sub':'', 'fro':'', 'bod':''}
    # total number of emails
    itr=0
    messages = int(messages[0])
    for i in range(messages, messages-N, -1):
    # fetch the email message by ID
        #print(i)
        id.append(i)
        print(len(id))
        res, msg = imap.fetch(str(i), "(RFC822)")
        for response in msg:
            if isinstance(response, tuple):
                indicator.append(0)
                # parse a bytes email into a message object
                msg = email.message_from_bytes(response[1])
                # decode the email subject
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    # if it's a bytes, decode to str
                    subject = subject.decode(encoding)
                # decode email sender
                From, encoding = decode_header(msg.get("From"))[0]
                if isinstance(From, bytes):
                    From = From.decode(encoding)
                Date, encoding = decode_header(msg.get("Date"))[0]
                if isinstance(From, bytes):
                    Date = Date.decode(encoding)

                tos = msg.get_all('to', [])
                ccs = msg.get_all('cc', [])
                # resent_tos = msg.get_all('resent-to', [])
                # resent_ccs = msg.get_all('resent-cc', [])
                all_recipients = getaddresses(tos + ccs)
                # print("Subject:", subject)
                # print("From:", From)
                # print(tos)
                # print(all_recipients)
                # if the email message is multipart

                if msg.is_multipart():
                    # iterate over email parts
                    for part in msg.walk():
                        # extract content type of email
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        try:
                            # get the email body
                            body = part.get_payload(decode=True).decode()
                        except:
                            pass
                        if content_type == "text/plain" and "attachment" not in content_disposition:
                            # print text/plain emails and skip attachments
                            # print(body)
                            body2 = body
                        #elif content_type == "text/html" and "attachment" not in content_disposition:
                            #print(body)
                        elif "attachment" in content_disposition:
                            # download attachment
                            filename = part.get_filename()
                            if filename:
                                folder_name = clean(subject)
                                indicator.pop()
                                indicator.append(1)
                                # if not os.path.isdir(folder_name):
                                    # make a folder for this email (named after the subject)
                                    # os.mkdir(folder_name)
                                # filepath = os.path.join(folder_name, filename)
                                # download attachment and save it
                                # open(filepath, "wb").write(part.get_payload(decode=True))
                                            
                else:
                    # extract content type of email
                    content_type = msg.get_content_type()
                    # get the email body
                    body = msg.get_payload(decode=True).decode()
                    if content_type == "text/plain":
                        # print only text email parts
                        # print(body)
                        body2 = body
                if content_type == "text/html":
                    # if it's HTML, create a new HTML file and open it in browser
                    folder_name = clean(subject)
                    # if not os.path.isdir(folder_name):
                        # make a folder for this email (named after the subject)
                        # os.mkdir(folder_name)
                    # filename = "index.html"
                    # filepath = os.path.join(folder_name, filename)
                    # write the file
                    # open(filepath, "w").write(body)
                    # open in the default browser
                    # webbrowser.open(filepath)
                print("="*100)
        #SS['sub']+=subject
        #SS['fro']+=From 
        #SS['bod']+=body
        pos1 = From.find("<") + 1
        pos2 = From.find(">") 
        if(pos2 == -1):
            emailid = From[pos1:]
        else:
            emailid = From[pos1:pos2]
        # print(emailid)
        eid.append(emailid)
        l.append(subject)
        m.append(From)
        print(len(m))
        n.append(body)
        time.append(Date)
        x = [0,1,2,3]
        for ii in all_recipients:
            # print("HOLA LOOP", ii[1])
            ccall.append(ii[1])
        ccall2.append(ccall)
        ccall=[]
        if(i==1 or i==2):
            break
        # print(body2)
    #SS={1: l, 2: m, 3:n}
    #print(SS)
    # print(n[2])
    searchli=[]
    
    #print(myL)
    itr+=4
    stop=0
    itr2=0
    if 'q' in request.GET:
        q=request.GET['q']
        for mmq in m:
            mmq=mmq.lower()
            if q==mmq: 
                id_ofmail = mmq.find(q)
                searchli.append(id_ofmail)
    myL=zip(l,m,n,time,x,eid,ccall2,id,indicator, searchli)
    context={'myL':myL,'subject':l,'content':n,'from':m,'time':time,'itr':itr,'itr2':itr2,'stop':stop,'ccall':ccall2,'ids':id, 'searchli':searchli}
    #context={''}
    # print(context)
    # close the connection and logout
    imap.close()
    imap.logout()
    # print("HOLA=   ",ccall2)
    if user.is_irc:
        return render(request, 'index_naya.html', context)
    else:
        return HttpResponse("<h1>You don't have permission to view this page</h1>")      

# sample = open('log.txt', 'w')

# This function will convert this message into django html and save it as a file in templates dir
# def to_html(static, title, message):
#     tag_loads = "{% extends 'base.html' %}\n" + "{% load " + static + " %}\n\n"
#     title = "{% block title %}\n" + title + "\n{% endblock %}\n\n"
#     message = "{% block content %}\n" + "<p>" + message + "</p>" + "\n{% endblock %}\n"
#     content = tag_loads + title + message
#     with open('templates/mail.html', mode='w') as file:
#         file.write(content)
#     return 0

def clean(text):
    # clean text for creating a folder
    return "".join(c if c.isalnum() else "_" for c in text)

import itertools 

# def index2(request):
#     user = request.user
#     creds = None
#     # The file token.json stores the user's access and refresh tokens, and is
#     # created automatically when the authorization flow completes for the first
#     # time.
#     if os.path.exists('token.json'):
#         creds = Credentials.from_authorized_user_file('token.json', SCOPES)
#     # If there are no (valid) credentials available, let the user log in.
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file(
#                 'credentials.json', SCOPES)
#             creds = flow.run_local_server(port=0)
#         # Save the credentials for the next run
#         with open('token.json', 'w') as token:
#             token.write(creds.to_json())

#     service = build('gmail', 'v1', credentials=creds)

#     # Call the Gmail API
#     results = service.users().labels().list(userId='me').execute()
#     labels = results.get('labels', [])

#     if not labels:
#         print('No labels found.')
#     else:
#         print('Labels:')
#         for label in labels:
#             print(label['name'])
#     if not user.is_irc:
#         return render(request, 'index_naya.html')
#     else:
#         return HttpResponse("<h1>You don't have permission to view this page</h1>")


def delete_mail(request):
    user = request.user
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    # authenticate
    imap.login(username, password)
    status, messages = imap.select("INBOX") 
    if request.method == 'POST':
        i = request.POST['mainidcopy']
        print(i)
        id_final = i
        typ, data = imap.search(None, 'ALL')
        for num in data[0].split():
            print(id_final)
            print(num)
            # print(type(num))
            # print(type(id_final))
            res = bytes(id_final, 'utf-8') 
            print(res)
            
            if(num==res):
                # print("HEyyyyyyyyy")
                # imap.store(res, '+FLAGS', '\\Deleted')
                imap.store(res, '+X-GM-LABELS', '\\Trash')
        # imap.store(id_final, '+FLAGS', '\\Deleted')
        # imap.expunge()

    else:
        pass
    if user.is_irc:
        return redirect('massmail')
    else:
        return HttpResponse("<h1>You don't have permission to view this page</h1>")  

def attachment_open(request):
    user = request.user
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    # authenticate
    imap.login(username, password)
    status, messages = imap.select("INBOX")    
    if request.method == 'POST':
        i = request.POST['mainid']
        res, msg = imap.fetch(str(i), "(RFC822)")
        for response in msg:
            if isinstance(response, tuple):
                # parse a bytes email into a message object
                msg = email.message_from_bytes(response[1])
                # decode the email subject
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    # if it's a bytes, decode to str
                    subject = subject.decode(encoding)
                # if the email message is multipart

                if msg.is_multipart():
                    # iterate over email parts
                    for part in msg.walk():
                        # extract content type of email
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        if "attachment" in content_disposition:
                            # download attachment
                            filename = part.get_filename()
                            if filename:
                                folder_name = clean(subject)
                                if not os.path.isdir(folder_name):
                                    # make a folder for this email (named after the subject)
                                    os.mkdir(folder_name)
                                filepath = os.path.join(folder_name, filename)
                                # download attachment and save it
                                open(filepath, "wb").write(part.get_payload(decode=True))
                                webbrowser.open(filepath)           
    else:
        pass
    if user.is_irc:
        return HttpResponse("<h1>Your attachment downloaded as well as opened successfully</h1>")
    else:
        return HttpResponse("<h1>You don't have permission to view this page</h1>")      



def index(request):
    user = request.user
    # create an IMAP4 class with SSL 
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    # authenticate
    imap.login(username, password)
    status, messages = imap.select("INBOX")
    # number of top emails to fetch
    N = 4
    l,m,n,time,eid,ccall,ccall2,id,indicator=[],[],[],[],[],[],[],[],[]
    #SS={1:l, 2:m, 3:n}
    #SS={'sub':'', 'fro':'', 'bod':''}
    # total number of emails
    itr=0
    messages = int(messages[0])
    for i in range(messages, messages-N, -1):
    # fetch the email message by ID
        #print(i)
        id.append(i)
        print(len(id))
        res, msg = imap.fetch(str(i), "(RFC822)")
        for response in msg:
            if isinstance(response, tuple):
                indicator.append(0)
                # parse a bytes email into a message object
                msg = email.message_from_bytes(response[1])
                # decode the email subject
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    # if it's a bytes, decode to str
                    subject = subject.decode(encoding)
                # decode email sender
                From, encoding = decode_header(msg.get("From"))[0]
                if isinstance(From, bytes):
                    From = From.decode(encoding)
                Date, encoding = decode_header(msg.get("Date"))[0]
                if isinstance(From, bytes):
                    Date = Date.decode(encoding)

                tos = msg.get_all('to', [])
                ccs = msg.get_all('cc', [])
                # resent_tos = msg.get_all('resent-to', [])
                # resent_ccs = msg.get_all('resent-cc', [])
                all_recipients = getaddresses(tos + ccs)
                # print("Subject:", subject)
                # print("From:", From)
                # print(tos)
                # print(all_recipients)
                # if the email message is multipart

                if msg.is_multipart():
                    # iterate over email parts
                    for part in msg.walk():
                        # extract content type of email
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        try:
                            # get the email body
                            body = part.get_payload(decode=True).decode()
                        except:
                            pass
                        if content_type == "text/plain" and "attachment" not in content_disposition:
                            # print text/plain emails and skip attachments
                            # print(body)
                            body2 = body
                        #elif content_type == "text/html" and "attachment" not in content_disposition:
                            #print(body)
                        elif "attachment" in content_disposition:
                            # download attachment
                            filename = part.get_filename()
                            if filename:
                                folder_name = clean(subject)
                                indicator.pop()
                                indicator.append(1)
                                # if not os.path.isdir(folder_name):
                                    # make a folder for this email (named after the subject)
                                    # os.mkdir(folder_name)
                                # filepath = os.path.join(folder_name, filename)
                                # download attachment and save it
                                # open(filepath, "wb").write(part.get_payload(decode=True))
                                            
                else:
                    # extract content type of email
                    content_type = msg.get_content_type()
                    # get the email body
                    body = msg.get_payload(decode=True).decode()
                    if content_type == "text/plain":
                        # print only text email parts
                        # print(body)
                        body2 = body
                if content_type == "text/html":
                    # if it's HTML, create a new HTML file and open it in browser
                    folder_name = clean(subject)
                    # if not os.path.isdir(folder_name):
                        # make a folder for this email (named after the subject)
                        # os.mkdir(folder_name)
                    # filename = "index.html"
                    # filepath = os.path.join(folder_name, filename)
                    # write the file
                    # open(filepath, "w").write(body)
                    # open in the default browser
                    # webbrowser.open(filepath)
                print("="*100)
        #SS['sub']+=subject
        #SS['fro']+=From 
        #SS['bod']+=body
        pos1 = From.find("<") + 1
        pos2 = From.find(">") 
        if(pos2 == -1):
            emailid = From[pos1:]
        else:
            emailid = From[pos1:pos2]
        # print(emailid)
        eid.append(emailid)
        l.append(subject)
        m.append(From)
        print(len(m))
        n.append(body)
        time.append(Date)
        x = [0,1,2,3]
        for ii in all_recipients:
            # print("HOLA LOOP", ii[1])
            ccall.append(ii[1])
        ccall2.append(ccall)
        ccall=[]
        if(i==1):
            break
        # print(body2)
    #SS={1: l, 2: m, 3:n}
    #print(SS)
    # print(n[2])
    myL=zip(l,m,n,time,x,eid,ccall2,id,indicator)
    #print(myL)
    itr+=4
    stop=0
    itr2=0
   
    context={'myL':myL,'subject':l,'content':n,'from':m,'time':time,'itr':itr,'itr2':itr2,'stop':stop,'ccall':ccall2,'ids':id}
    #context={''}
    # print(context)
    # close the connection and logout
    imap.close()
    imap.logout()
    # print("HOLA=   ",ccall2)
    if user.is_irc:
        return render(request, 'index_naya.html', context)
    else:
        return HttpResponse("<h1>You don't have permission to view this page</h1>")

def indexrepeat(request, itr):
    user = request.user
    # create an IMAP4 class with SSL 
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    # authenticate
    imap.login(username, password)
    status, messages = imap.select("INBOX")
    itr= int (itr)
    # number of top emails to fetch
    N = 4
    stop = 0
    l,m,n,time,eid,ccall,ccall2,id,indicator=[],[],[],[],[],[],[],[],[]
    #SS={1:l, 2:m, 3:n}
    #SS={'sub':'', 'fro':'', 'bod':''}
    # total number of emails
    messages = int(messages[0])
    messages = messages - itr
    for i in range(messages, messages-N, -1):
    # fetch the email message by ID
        print(i)
        id.append(i)
        res, msg = imap.fetch(str(i), "(RFC822)")
        for response in msg:
            if isinstance(response, tuple):
                indicator.append(0)
                # parse a bytes email into a message object
                msg = email.message_from_bytes(response[1])
                # decode the email subject
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    # if it's a bytes, decode to str
                    subject = subject.decode(encoding)
                # decode email sender
                From, encoding = decode_header(msg.get("From"))[0]
                if isinstance(From, bytes):
                    From = From.decode(encoding)
                Date, encoding = decode_header(msg.get("Date"))[0]
                if isinstance(From, bytes):
                    Date = Date.decode(encoding)
                # print("Subject:", subject)
                # print("From:", From)

                tos = msg.get_all('to', [])
                ccs = msg.get_all('cc', [])
                # resent_tos = msg.get_all('resent-to', [])
                # resent_ccs = msg.get_all('resent-cc', [])
                all_recipients = getaddresses(tos + ccs)
                # print("Subject:", subject)
                # print("From:", From)
                # print(tos)
                # print(all_recipients)

                # if the email message is multipart
                if msg.is_multipart():
                    # iterate over email parts
                    for part in msg.walk():
                        # extract content type of email
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        try:
                            # get the email body
                            body = part.get_payload(decode=True).decode()
                        except:
                            pass
                        if content_type == "text/plain" and "attachment" not in content_disposition:
                            # print text/plain emails and skip attachments
                            # print(body)
                            body2 = body
                        #elif content_type == "text/html" and "attachment" not in content_disposition:
                            #print(body)
                        elif "attachment" in content_disposition:
                            # download attachment
                            filename = part.get_filename()
                            if filename:
                                folder_name = clean(subject)
                                indicator.pop()
                                indicator.append(1)
                                # if not os.path.isdir(folder_name):
                                    # make a folder for this email (named after the subject)
                                    # os.mkdir(folder_name)
                                # filepath = os.path.join(folder_name, filename)
                                # download attachment and save it
                                # open(filepath, "wb").write(part.get_payload(decode=True))
                else:
                    # extract content type of email
                    content_type = msg.get_content_type()
                    # get the email body
                    body = msg.get_payload(decode=True).decode()
                    if content_type == "text/plain":
                        # print only text email parts
                        # print(body)
                        body2 = body
                if content_type == "text/html":
                    # if it's HTML, create a new HTML file and open it in browser
                    folder_name = clean(subject)
                    # if not os.path.isdir(folder_name):
                        # make a folder for this email (named after the subject)
                        # os.mkdir(folder_name)
                    filename = "index.html"
                    # filepath = os.path.join(folder_name, filename)
                    # write the file
                    # open(filepath, "w").write(body)
                    # open in the default browser
                    # webbrowser.open(filepath)
                print("="*100)
        #SS['sub']+=subject
        #SS['fro']+=From 
        #SS['bod']+=body
        pos1 = From.find("<") + 1
        pos2 = From.find(">")
        if(pos2 == -1):
            emailid = From[pos1:]
            # print(emailid)
        else:
            emailid = From[pos1:pos2]
        l.append(subject)
        m.append(From)
        n.append(body)
        time.append(Date)
        eid.append(emailid)
        x = [0,1,2,3]
        # print(body2)
        for ii in all_recipients:
            ccall.append(ii[1])
        ccall2.append(ccall)
        ccall=[]
        if(i==1):
            i=0
            break

    #SS={1: l, 2: m, 3:n}
    #print(SS)
    # print(n[2])
    myL=zip(l,m,n,time,x,eid,ccall2,id,indicator)
    #print(myL)
    itr+=4
    itr2=itr-8
    if(i==0):
        stop = 1
    context={'myL':myL,'subject':l,'content':n,'from':m,'time':time,'itr':itr,'itr2':itr2,'stop':stop,'ccall':ccall2,'ids':id}
    #context={''}
    # print(context)
    # close the connection and logout
    imap.close()
    imap.logout()
    if user.is_irc:
        return render(request, 'index_naya.html', context)
    else:
        return HttpResponse("<h1>You don't have permission to view this page</h1>")

def replymail(request):
    user = request.user
    if request.method == 'POST':
        emailid = request.POST['mainemailid']
        subject = request.POST['mainsubject']
        subject = "Re: " + subject
    else:
        pass
    if user.is_irc:
        return render(request, 'replymail.html', {'emailid':emailid,'subject':subject})
    else:
        return HttpResponse("<h1>You don't have permission to view this page</h1>")  

def replymailall(request):
    user = request.user
    if request.method == 'POST':
        emailids = request.POST['mainemailids']
        subject = request.POST['mainsubject2']
        subject = "Re: " + subject
    else:
        pass
    if user.is_irc:
        return render(request, 'replymail.html', {'emailid':emailids,'subject':subject})
    else:
        return HttpResponse("<h1>You don't have permission to view this page</h1>")  

def replymailsend(request):
	if request.method == 'POST':
		mails_sent = 0
		error_message = "No Errors"		
		email = request.POST['emailid']
		subject = request.POST['subject']
		message = request.POST['message']
		if(email.find("[")!=-1):
			email = email [1:len(email)-1]
			email = email.replace("'","")
			email = email.split(", ")
		else:
			email = [email]
		print(subject)
		print(message)
		print(email)
		try:
			email2 = EmailMultiAlternatives(
				subject, message, settings.EMAIL_HOST_USER, to=email
			)
		except:
			email2 = EmailMultiAlternatives(
				subject, message, settings.EMAIL_HOST_USER, to=email
			)
		email2.attach_alternative(message, "text/html")
		try:
			email2.send(fail_silently=True)
			mails_sent += 1
		except Exception as e:
			print("Failed")

		# log = "[" + datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "] Reply Mail | " + email + \
		# 		" | " + str(mails_sent) + " mails sent | " + error_message + "</br>"
		# logfile = open(os.path.join(settings.BASE_DIR, 'templates/logs/dashboard_log.html'), "a")
		# logfile = open("logs/dashboard_log.html", "a")
		# logfile.write(log)
		# logfile.close()
		user = request.user
		if user.is_irc:
			# return redirect("/")
			return HttpResponse("<h1>Your mail has been sent successfully</h1>")
		else:
		    return HttpResponse("<h1>You don't have permission to view this page</h1>")



def composemail(request):
    user = request.user
    if user.is_irc:
        return render(request, 'index.html')
    else:
        return HttpResponse("<h1>You don't have permission to view this page</h1>")   





# Saves message in mail.html
def to_html(message):
    message = "{% autoescape off %}\n" + message + "\n{% endautoescape %}\n"
    with open(abpath+'/templates/mail.html', mode='w') as file:
        file.write(message)
    return 0


def find_first(sheet):
    # Finding row first
    for i in range(sheet.nrows):
        for j in range(sheet.ncols):
            if sheet.cell_value(i, j) == '':
                continue
            else:
                return i, j
    return None


def values_of_row(sheet, row, first_row, first_column):
    return [sheet.row_values(row)[i] for i in range(first_column, sheet.ncols)]

# Create your views here.


def mail(request):
    user = request.user
    if user.is_irc:
        print('starting mail')
        if request.method == 'POST':
            print('Inside if of mail')
            #form = MailForm(request.POST, request.FILES)
            sheet = request.FILES["sheet"]
            subject = request.POST["subject"]
            message = request.POST["message"]
            purpose = request.POST["purpose"]
            count = 0

            print(subject, purpose)
            to_html(message)

            #wb = xlrd.open_workbook(sheet)
            # Saving the uploaded file at pathname == workbook_date.extension
            extension = os.path.splitext(sheet.name)[1]
            pathname = "workbook_" + datetime.datetime.now().strftime("%d-%b-%Y_%I:%M%p") + \
                extension
            print(pathname)
            fs = FileSystemStorage()
            fs.save(abpath+'/media/'+pathname, sheet)
            print('Opened file')
            # Opening the saved workbook file
            wb = xlrd.open_workbook(abpath+"/media/"+pathname)
            # Selecting the first sheet from the given workbook
            sheet = wb.sheet_by_index(0)
            # Creating a dictionary of data
            temp = find_first(sheet)
            if temp is None:
                return HttpResponse("<h1>Sheet is empty</h1>")
            first_row, first_column = temp
            keys = values_of_row(sheet, first_row, first_row, first_column)
            print('header:', keys)
            # This block will be in a loop and uses readed variables from the file to render the html file
            mails_sent = 0
            error_message = "No Errors"
            for i in range(first_row+1, sheet.nrows):
                values = values_of_row(sheet, i, first_row, first_column)
                #print('row:', values)
                data = {keys[k]: values[k] for k in range(len(keys))}
                # This line renders mail content into a string
                rendered_message = render_to_string('mail.html', data)
                # print(rendered_message)
                # finding email as the dict keys are case sensitive strings
                for k, v in data.items():
                    if k.lower() == 'email':
                        email = v
                if purpose == 'testing':
                    if count == 5:
                        return HttpResponse("<h1>Successfully sent the top 5 emails to " + settings.TEST_EMAIL + " </h1>")
                    else:
                        email = settings.TEST_EMAIL
                        count = count + 1
                #print('sending email to', email)
                # Creates an EmailMessage object
                email_object = EmailMultiAlternatives(
                    subject, rendered_message, settings.EMAIL_HOST_USER, to=[
                        email]
                )
                # Sending the email
                email_object.attach_alternative(rendered_message, "text/html")

                try:
                    email_object.send(fail_silently=False)
                    mails_sent += 1
                except Exception as e:
                    error_message = str(e.args) + "For recipient: " + email
                    break
                # print('email sent')
            # Loop should end here
            log = "[" + datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "] Mass_mailing | " + user.username + \
                  " | " + str(mails_sent) + " mails sent | " + \
                error_message + "</br>"
            logfile = open("logs/dashboard_log.html", "a")
            logfile.write(log)
            logfile.close()
            # Deleting the ,file = sampletemporarily stored excel sheet
            # fs.delete(pathname)
            if error_message != "No Errors":
                return HttpResponse("<h1>All emails were not sent successfully. Check logs.</h1>")
            else:
                return HttpResponse("<h1>Successfully sent the emails</h1>")
        else:
            return redirect("/")
    else:
        return HttpResponse("<h1>You don't have permission to view this page</h1>")


def step0(request):
    return render(request, 'step1.html')


def step1(request):
    if request.method == 'POST':
        sheet = request.FILES["sheet"]
        extension = os.path.splitext(sheet.name)[1]
        pathname = "workbook_" + datetime.datetime.now().strftime("%d-%b-%Y_%I:%M%p") + \
            extension
        fs = FileSystemStorage()
        fs.save(pathname, sheet)

        # Opening the saved workbook file
        wb = xlrd.open_workbook(abpath + "/media/" + pathname)
        # Selecting the first sheet from the given workbook
        sheet = wb.sheet_by_index(0)
        # Creating a dictionary of data
        temp = find_first(sheet)
        if temp is None:
            return HttpResponse("<h1>Sheet is empty</h1>")
        first_row, first_column = temp
        keys = values_of_row(sheet, first_row, first_row, first_column)
        print('header:', keys)
        return render(request, 'step2.html', {'variables': keys})
    else:
        return redirect("/")


def step3(request):
    pass
