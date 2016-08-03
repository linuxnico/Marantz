#!/usr/bin/python3
# -*- coding:utf-8 -*-
DEBUG=False
import sys
import telnetlib
import signal

from flask import Flask
from flask.globals import request
from flask import render_template

HOST = "192.168.0.3"

app=Flask(__name__)
app.secret_key = '2d9-E2.)f&é,A5754f54g6$p@fpa+zSU03êû9_'

class switch(object):
    def __init__(self, value):
        self.value = value
        self.fall = False

    def __iter__(self):
        """Return the match method once, then stop"""
        yield self.match
        raise StopIteration
    
    def match(self, *args):
        """Indicate whether or not to enter a case suite"""
        if self.fall or not args:
            return True
        elif self.value in args: # changed for v1.5, see below
            self.fall = True
            return True
        else:
            return False


def signal_handler(signal, frame):
    print('You pressed Ctrl+C!')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


#creation lien telent
tn = telnetlib.Telnet()
def envoiCommande(sessionTelnet,commande):
    try:
        tn.open(HOST, 23,5)
    except Exception as err:
        print("erreur de connection: ",err)
    #print(b'comm envoye='+commande.encode('ASCII'))
    tn.write(commande.encode('ASCII'))
    res=tn.read_until(b"\r",5)
    tn.close()
    print(res)
    return res

def test_envoiCommande(a,b):
    print("commande normalement envoyee:",b)
    return False

def mute():
    ret=envoiCommande(tn, "MU?\r")
    if ret.decode().strip()=="MUON": return "MUOFF"
    else: return "MUON"
    
def power():
    ret=envoiCommande(tn, "PW?\r")
    if ret.decode().strip()=="PWON": return "PWSTANDBY"
    else: return "PWON"    
    

def traiteRetour(commande,arg):
    commande=commande.upper()
    arg=arg.upper()
    comm=""
    for case in switch(commande):
        if case('MV'):
            comm='MV'+arg
            break
        if case('PW'):
            comm=power()
            break
        if case('MU'):
            comm=mute()
            break
        if case('SI'):
            comm="SI"+arg
            break
        if case('NS'):
            comm="NS"+arg
            break
    return comm+"\r"
            
def activeSource(comm):
    active=["","",""]
    if comm.strip()=="SIIRADIO": 
            active[0]="disabled"
            active[1]=""
            active[2]=""
    elif comm.strip()=="SIBLUETOOTH": 
            active[0]=""
            active[1]="disabled"
            active[2]=""
    elif comm.strip()=="SIUSB": 
            active[0]=""
            active[1]=""
            active[2]="disabled"
    print("active:",active)
    return active


def recupSource():    
    return envoiCommande(tn,"SI?\r").decode()


@app.route('/')
def index():
    if DEBUG: 
        sources=["","",""]
        return render_template("page.html",titre="marantz",si=sources,table=["marantz","nico","jJ"])
    if request.args.get('commande') is not None: sources=commande()
    else: sources=activeSource(recupSource())
    return render_template("page.html",titre="marantz",si=sources,table=["marantz","nico","jJ"])




#@app.route('/com',methods=['GET','POST'])
def commande():
    print(request.method)
    if request.method=='GET':        
        msg=request.args['commande'].upper()
        arg=request.args['arg'].upper()
        #print("com=",msg+"+"+arg)
        argumentCommande=traiteRetour(msg, arg)
        sourceActive=activeSource(recupSource())
        if DEBUG: 
            test_envoiCommande(tn, argumentCommande)
            return sourceActive #"Retour: "+str(test_envoiCommande(tn, argumentCommande))
        else: 
            envoiCommande(tn, argumentCommande)
            return sourceActive #"Retour: "+str(envoiCommande(tn, traiteRetour(msg, arg)))
    return "NOK"
    
    
if __name__=='__main__':
    app.run("0.0.0.0")




