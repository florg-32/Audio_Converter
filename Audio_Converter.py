import os, queue, time, threading, sys
from subprocess import call

FFMPEG_BIN = "ffmpeg.exe"
MAX_THREADS = 4

toConvertQueue = queue.Queue() # contains the filenames/paths to be converted
convertedQueue = queue.Queue() # contains the converted filenames for printing

def createFolders():
    if not os.path.exists("output"):
        os.mkdir("output")

    for folder in os.listdir("input"):
        if not os.path.exists("output\\"+folder):
            os.mkdir("output\\"+folder)

def scanFilenames():
    for path, subdirs, files in os.walk("input"):
        for name in files:
            toConvertQueue.put(os.path.join(path, name)[6:]) # cut "input/"

def worker():
    """Worker for threading, calls convert()"""
    timeout = 2
    while True:
        try:
            filename = toConvertQueue.get(True, timeout) # blocks if queue is empty
        except:
            print("Worker timedout!")
            return

        convertedQueue.put(convert(filename))
        toConvertQueue.task_done() # signal to release next obj in queue

def convert(path):
    """The function for calling ffmpeg"""
    command = [FFMPEG_BIN,
               "-loglevel", "0", # lower ffmpeg's verbosity
               "-i", "input\\" + path,
               "-codec:a", "libvorbis",
               "-q:a", "7", # increase the audio quality (standard = 3)
               "output\\" + path[:-4] + ".ogg"] # cut the old ending and add .ogg

    call(command)
    return "Converted {} to ogg!".format(path)

def printer():
    timeout = 5
    while True:
        try:
            print(convertedQueue.get(True, timeout))
        except:
            print("Printer timedout!")
            return
        convertedQueue.task_done()

def main():
    createFolders()
    scanFilenames()

    starttime = time.time()
    threads = []

    for i in range(MAX_THREADS):
        thread = threading.Thread(target = worker)
        thread.daemon = True
        threads.append(thread)
        thread.start()

    # spawn the printer thread
    thread = threading.Thread(target = printer)
    thread.daemon = True
    threads.append(thread)
    thread.start()

    toConvertQueue.join()
    convertedQueue.join()

    endtime = time.time()
    for t in threads:
        t.join()

    print("\nTask completed!\nThreadtime (before timeouts): {:.2f}s\nTotal duration: {:.2f}s".format(time.time()-endtime, time.time()-starttime))

if __name__ == "__main__":
    main()