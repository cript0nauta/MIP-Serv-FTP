#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Programa a usar si te cambió la IP pública y estás usando Mip-Serv FTP
#by sh4r3m4n(http://sh4r3m4n.webcindario.com)
#Esta aplicacion se encuentra bajo licensia Creative Commons, visible en
#http://creativecommons.org/licenses/by/2.5/ar/

#Importa librerías
import sys,socket

#Comprueba que estén bien los parámetros o muestra la ayuda
if(len(sys.argv)!=3):
  print 'Changer remoto de IP pasiva Mip-Serv FTP\nUso:\n\t'+sys.argv[0]+' <host> <puerto>'
  exit()
else:
  try:
    x=int(sys.argv[2])
    del(x)
  except:
    print 'Changer remoto de IP pasiva Mip-Serv FTP\nUso:\n\t'+sys.argv[0]+' <host> <puerto>'
    exit()

sock=socket.socket()
try:
  sock.connect((sys.argv[1],int(sys.argv[2])))
  sock.send('SITE CHANGEIP\n')
  sock.settimeout(20)
  respuesta220=	    sock.recv(1024)
  respuestachangeip=sock.recv(1024)
  print 'IP cambiada correctamente. Respuesta:',respuestachangeip,
except:
  print 'Error al cambiar IP'
  exit()