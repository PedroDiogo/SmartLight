import argparse, curses, json
from SmartLight import *

def usage():
    pass

def main():
    camera = -1
    display = False
    output = "output/camera.png"
        
    # Parse the input arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--camera', type=int, dest='camera', default=-1, help='Manually specifies the camera number (e.g. if the camera is /dev/video1 then you should add -c 1). Default is automatic camera discovery')
    parser.add_argument('-d', '--display', dest='display', action='store_true', help='If active a Display window will show the current image')
    parser.add_argument('-o', '--output', dest='output', action='store_true', help='If active an image and information will by saved in a file (see -i and -f)')
    parser.add_argument('-i', '--image', dest='image', default="output/camera.png", help='Specifies the filename were the image will be saved. Default is output/camera.png')
    parser.add_argument('-f', '--info', dest='info', default="output/info.json", help='Specifies the filename were the information about the program will be saved. Default is output/info.json')
    args = parser.parse_args()

    # Start SmartLight
    smartlight = SmartLight(args.camera, 200)
    
    if args.display:
      from SimpleCV import Display
      display = Display()
    
    # Init Curses
    screen = curses.initscr()
    screen.nodelay(1)
    curses.cbreak()
    curses.noecho()
    
    # Loop until infinity! (or until someone presses quit...)
    while True:
      info = smartlight.run()
      
      if args.output:
        # Dump info to JSON file
        with open(args.info, 'wb') as fp: json.dump(info, fp)
        # Save image to file
        smartlight.saveImage(args.image)
      
      # If option was provided, print to display
      if args.display:
        smartlight.saveImage(display)
      
      screen.erase()
      screen.addstr(1, 2, "FPS: {0:.2f}".format(info["FPS"]))
      screen.addstr(2, 2, "Motion: {0} ({1:.2f})".format(info["motion"], info["motionValue"]))
      screen.addstr(3, 2, "People: {0} ({1:.2f})".format(info["people"], info["skinValue"]))
      screen.addstr(4, 2, "Lights: {0} ({1})".format(info["lights"], info["timer"]))
      screen.addstr(6, 10, "-- Press Q to exit --")
      screen.move(7, 0)
      
      ch = screen.getch()
      if ch == 81 or ch == 113:
        break

    screen.nodelay(0)
    curses.nocbreak()
    curses.echo()
    curses.endwin() 

if __name__ == "__main__":
  main()
