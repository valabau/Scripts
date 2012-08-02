#! /usr/bin/env python

import dbus, urllib, re
bus = dbus.SessionBus()
proxy = bus.get_object("org.kde.klipper","/klipper")
klipper = dbus.Interface(proxy,"org.kde.klipper.klipper")

query = klipper.getClipboardContents()
query = re.sub('\s+', ' ', query) 
url="http://www.linguee.es/espanol-ingles/search?source=auto&query=%s" % urllib.quote(query)

import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *


app = QApplication(sys.argv)
web = QWebView()
web.quit = QShortcut(QKeySequence("Ctrl+W"), web, activated = web.close)
web.load(QUrl(url))
web.show()
sys.exit(app.exec_())
