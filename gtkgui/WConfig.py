import os
import gtk
import ConfigParser
from os.path import expanduser

class GeneralWidget(gtk.HBox):
    label = 'General'
    def __init__(self,config):
        gtk.HBox.__init__(self)
        lblUrl = gtk.Label('url')
        self.__entUrl = gtk.Entry()
        self.__entUrl.set_text(config.get('General','host'))
        self.pack_start(lblUrl,0,0,5)
        self.pack_start(self.__entUrl,0,0,5)
        lblPort = gtk.Label('Port')
        self.__entPort = gtk.Entry()
        self.__entPort.set_text(config.get('General','port'))
        self.pack_start(lblPort,0,0,5)
        self.pack_start(self.__entPort,0,0,5)

    def save(self):
        settings = {}
        settings['host'] = self.__entUrl.get_text()
        settings['port'] = self.__entPort.get_text()

        return settings

class PrinterWidget(gtk.VBox):
    label = 'ESC/POS printer'
    ptype = {'USB':['USB (idVendor:idProduct)',('idVendor','idDevice')],
             'Network':['URL (192.168.1.2)',('host',)],
             'Serial': ['Serial (/dev/ttyS0)',('dev',)]
            }
    current_type = 'USB'
    config = None

    def __init__(self,config):

        self.config = config
        self.current_type = config.get('Printer','type')
        gtk.VBox.__init__(self)
        PrinterTypeBox = gtk.VBox()
        button = gtk.RadioButton(None,"USB")
        button.connect('toggled',self.toggled,'USB')
        if self.current_type == 'USB':
            button.set_active(True)

        PrinterTypeBox.pack_start(button,0,0,5)
        button = gtk.RadioButton(button,"Netowrk")
        button.connect('toggled',self.toggled,'Network')
        if self.current_type == 'Network':
            button.set_active(True)

        PrinterTypeBox.pack_start(button,0,0,5)
        button = gtk.RadioButton(button,"Serial")
        button.connect('toggled',self.toggled,'Serial') 
        PrinterTypeBox.pack_start(button,0,0,5)
        if self.current_type == 'Serial':
            button.set_active(True)

        self.pack_start(PrinterTypeBox,0,0,5)

        PrinterConfigBox = gtk.HBox()
        self.__lblTypeConfig = gtk.Label(self.ptype[self.current_type][0])
        self.__entTypeConfig = gtk.Entry()
        config_value=','.join([config.get('Printer',value)
                              for value in self.ptype[self.current_type][1]])
        self.__entTypeConfig.set_text(config_value)
        PrinterConfigBox.pack_start(self.__lblTypeConfig,0,0,5)
        PrinterConfigBox.pack_start(self.__entTypeConfig,0,0,5)
        self.pack_start(PrinterConfigBox,0,0,5)

        #Printer Fonts Widths and pxWidth
        #labels
        lblWidthA = gtk.Label("WidthA")
        lblWidthB = gtk.Label("WidthB")
        lblpxWidth = gtk.Label("pxWidth")
        lblcharSet = gtk.Label("charSet")
        #Entries
        self.__entWidthA = gtk.Entry()
        self.__entWidthA.set_text(self.config.get("Printer","WidthA"))
        self.__entWidthB = gtk.Entry()
        self.__entWidthB.set_text(self.config.get("Printer","WidthB"))
        self.__entpxWidth = gtk.Entry()
        self.__entpxWidth.set_text(self.config.get("Printer","pxWidth"))
        self.__entcharSet = gtk.Entry()
        self.__entcharSet.set_text(self.config.get("Printer","charSet"))
        PrinterSizeBox = gtk.Table(4,2,True)
        PrinterSizeBox.attach(lblWidthA,0,1,0,1)
        PrinterSizeBox.attach(lblWidthB,0,1,1,2)
        PrinterSizeBox.attach(lblpxWidth,0,1,2,3)
        PrinterSizeBox.attach(lblcharSet,0,1,3,4)
        PrinterSizeBox.attach(self.__entWidthA,1,2,0,1)
        PrinterSizeBox.attach(self.__entWidthB,1,2,1,2)
        PrinterSizeBox.attach(self.__entpxWidth,1,2,2,3)
        PrinterSizeBox.attach(self.__entcharSet,1,2,3,4)
        self.pack_start(PrinterSizeBox,0,0,5)

    def toggled(self,widget, data=None):
        if widget.get_active() == True:
            current_type = data
            self.__lblTypeConfig.set_label(self.ptype[data][0])
            config_value=','.join([self.config.get('Printer',value)
                                  for value in self.ptype[data][1]])
            self.__entTypeConfig.set_text(config_value)


    def save(self):
        settings = {}
        settings['type'] = self.current_type
        for ptype in self.ptype:
            if ptype == self.current_type:
                values = self.__entTypeConfig.get_text().split(',')
                for i, setting in enumerate(self.ptype[ptype][1]):
                    settings[setting] = values[i]
            else:
                for i, setting in enumerate(self.ptype[ptype][1]):
                    settings[setting] = self.config.get('Printer',setting)

        settings['WidthA'] = self.__entWidthA.get_text()
        settings['WidthB'] = self.__entWidthB.get_text()
        settings['pxWidth'] = self.__entpxWidth.get_text()
        settings['charSet'] = self.__entcharSet.get_text()

        return settings

pages ={ 'General': GeneralWidget,
         'Printer': PrinterWidget,
       }

class WConfig(gtk.Window):
    widgets = {}
    config_path = expanduser("~") +"/.proxypos/config"
    def __init__(self):
        gtk.Window.__init__(self)
        self.set_title("ESC/POS printer configuration")
        self.set_default_size(200,200)
        vbox = gtk.VBox()

        notebook = gtk.Notebook()
        vbox.pack_start(notebook,0,0,5)
        ControlBox = gtk.HBox()
        vbox.pack_start(ControlBox,0,0,5)
        btnCancel = gtk.Button("Cancel")
        btnCancel.connect('clicked',self.cancel)
        btnSave = gtk.Button("Save")
        btnSave.connect('clicked',self.save)
        ControlBox.pack_start(btnCancel,0,0,5)
        ControlBox.pack_start(btnSave,0,0,5)
        #Read current configuration
        config = ConfigParser.RawConfigParser()
        config.read(self.config_path +"/config.cfg")

        for page in ['General','Printer']:
            widget = pages[page](config)
            label = gtk.Label(widget.label)
            self.widgets[page] = widget
            notebook.append_page(widget,label)

        self.connect('destroy', lambda w: gtk.main_quit())

        self.add(vbox)
        self.show_all()

    def save(self, widget):
        new_config = ConfigParser.RawConfigParser()
        filename = self.config_path+"/config.cfg"
        new_config.add_section('General')
        new_config.add_section('Printer')
        for section in ['General','Printer']:
            settings = self.widgets[section].save()
            for setting in settings:
                print section, setting, settings[setting]
                new_config.set(section,setting,settings[setting])

        #Save new config values
        try:
            with open(filename,'wb') as configfile:
                new_config.write(configfile)
            gtk.main_quit()
        except Exception, ex:
            print ex

    def cancel(self, widget):
        gtk.main_quit()

def run():
    w = WConfig()
    gtk.main()

if __name__ == '__main__':
    w = WConfig()
    gtk.main()
