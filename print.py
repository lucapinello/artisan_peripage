import os
import subprocess
import sys
import time

from PyPDF2 import PdfFileWriter, PdfFileReader
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate


import sys, os.path, time, logging
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler


def update_report(artisan_pdf='artisan_report.pdf',output_pdf='artisan_report_with_padding.pdf'):

    input = PdfFileReader(open(artisan_pdf, "rb"))
    input2 = PdfFileReader(open("spacer.pdf", "rb"))
    output = PdfFileWriter()
    input_page = input.getPage(0)
    input2_page= input2.getPage(0)

    #generate spacer for padding
    c = canvas.Canvas("spacer.pdf")
    c.setPageSize((100,  input_page.mediaBox.getHeight()))
    c.drawString(50,int(input_page.mediaBox.getHeight())/2,'|')
    c.showPage()
    c.save()




    page = output.addBlankPage(
            input_page.mediaBox.getWidth() + 100,
            input_page.mediaBox.getHeight())

    page.mergeScaledTranslatedPage(input_page, 1, 0, 0)

    page.mergeScaledTranslatedPage(input2_page, 1, input_page.mediaBox.getWidth()+10, 0)
    #output.addPage(page)

    output_file = open(output_pdf, "wb")

    output.write(output_file)

    output_file.close()


def print_report(pdf_filename='artisan_report_with_padding.pdf'):
    args = '"C:\\\\Program Files\\\\gs\\\\gs9.27\\\\bin\\\\gswin64c" ' \
           '-sDEVICE=mswinpr2 ' \
           '-dBATCH ' \
           '-dNOPAUSE ' \
           '-dNoCancel ' \
           '-dFitPage ' \
           '-dDEVICEWIDTHPOINTS=164.41 ' \
           '-dDEVICEHEIGHTPOINTS=595.28 ' \
           '-dQueryUser=3 ' \
           '-c "<</PageOffset [-135 0]  /Margins [0 -30] /.HWMargins [0 10 0 0] >> setpagedevice" -f ' #\
           #' -sOutputFile="\\\\spool\\Peri" '
    ghostscript = args + os.path.join(os.getcwd(), pdf_filename).replace('\\', '\\\\')
    print(ghostscript)
    subprocess.call(ghostscript, shell=True)


old = 0

class MyEventHandler(PatternMatchingEventHandler):
    def on_moved(self, event):
        super(MyEventHandler, self).on_moved(event)
        logging.info("File %s was just moved" % event.src_path)

    def on_created(self, event):
        super(MyEventHandler, self).on_created(event)
        logging.info("File %s was just created" % event.src_path)

    def on_deleted(self, event):
        super(MyEventHandler, self).on_deleted(event)
        logging.info("File %s was just deleted" % event.src_path)

    def on_modified(self, event):
        global old
        super(MyEventHandler, self).on_modified(event)
        #logging.info("File %s was just modified" % event.src_path)



        statbuf = os.stat(event.src_path)
        new = statbuf.st_mtime
        if (new - old) > 0.5:
            print("Received modified event - %s." % event.src_path)
            time.sleep(1)
            update_report()
            time.sleep(1)
            print_report()
            # Do any action here.
        old = new

def watchFile(file_path=None):
    logging.basicConfig(level=logging.INFO,
        format='%(asctime)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    watched_dir = os.path.split(file_path)[0]
    print ('watched_dir = {watched_dir}'.format(watched_dir=watched_dir))
    patterns = [file_path]
    print ('patterns = {patterns}'.format(patterns=', '.join(patterns)))
    event_handler = MyEventHandler(patterns=patterns)
    observer = Observer()
    observer.schedule(event_handler, watched_dir, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    watchFile('./artisan_report.pdf')
