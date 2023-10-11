import time
import json
import array
import math
import gc
import board
import busio
import audioio
import audiocore
import displayio
import digitalio
import os
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import bitmap_label as label
from adafruit_display_shapes.circle import Circle
from adafruit_button import Button
import adafruit_touchscreen
from adafruit_mcp9600 import MCP9600


class Oven:

    def __init__(self):

        # io init
        self.solenoid1 = digitalio.DigitalInOut(board.D4)
        self.solenoid1.direction = digitalio.Direction.OUTPUT

        # display init
        self.displayWidth = board.DISPLAY.width
        self.displayHeight = board.DISPLAY.height
        print(self.displayWidth)
        print(self.displayHeight)

        self.bitmap = displayio.Bitmap(self.displayWidth, self.displayHeight, 4)

        self.display = board.DISPLAY

        self.group = displayio.Group()
        self.display.show(self.group)

        # colors for bitmap
        palette = displayio.Palette(5)
        palette[0] = 0x000000
        palette[1] = 0xffffff
        palette[2] = 0xff0000
        palette[3] = 0x00ff00
        palette[4] = 0x0000ff

        tile_grid = displayio.TileGrid(self.bitmap, pixel_shader=palette)
        self.group.append(tile_grid)

        # fonts
        self.font1 = bitmap_font.load_font("/fonts/Px437_IBM_VGA_8x16-10-r.bdf")

        # profile vars
        self.profile = []
        self.rawProfile = []
        self.totalTime = 360 # total run time (seconds)

        # graphing boundaries
        self.gxMin = 75
        self.gXMax = self.displayWidth
        self.gyMin = 75
        self.gyMax = self.displayHeight # //remove max min vars
        self.gxBuff = self.displayWidth - 75
        self.gyBuff = self.displayHeight - 75

        # profile graph max range (eg. 360s & 280deg)
        self.maxX = 360
        self.maxY = 250

        # temperature vars
        self.currentTemp = None # //remove
        # temp ofset for increased accuracy
        self.tempOffset = 0
        #self.tempCal = None

        # profile log
        self.tempLog = []
        self.graphLog = None

        # sensor init
        sensorAddr = 103
        i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
        self.sensor = MCP9600(i2c, sensorAddr, "K")

        # loads objects
        self.buttons = []
        self.startButton = Button(x=0,
                                  y=self.displayHeight - 40,
                                  width=80,
                                  height=40,
                                  label="START",
                                  label_font=self.font1)

        self.buttons.append(self.startButton)
        for button in self.buttons:
            self.group.append(button)

        self.circle = Circle(308, 12, 8, fill=0)
        self.group.append(self.circle)

        # touch screen init
        self.ts = adafruit_touchscreen.Touchscreen(
            board.TOUCH_XL,
            board.TOUCH_XR,
            board.TOUCH_YD,
            board.TOUCH_YU,
            calibration=((5200, 59000), (5800, 57000)),
            size=(self.displayWidth, self.displayHeight),
        )

    def check_buttons_press_location(self, pressed, button_details):
        """
        checks button presses
        """
        for button in button_details:
            if button.contains(pressed):
                return button
        return None

    def load_profile(self, profile):

        """
        :param profile: profile name
        """

        self.profile = []

        file = open("reflow_profiles/" + str(profile) + ".txt", "r")
        lines = file.readlines()
        file.close()

        for line in lines:
            self.profile.append([int(item) for item in line.replace("\n", "").replace("\r", "").split(" ")])
            self.rawProfile.append([int(item) for item in line.replace("\n", "").replace("\r", "").split(" ")])
        print(self.profile)

        # invert y axis (y0 is top left)
        for point in range(len(self.profile)):
            #print("point - " + str(self.profile[point][1]))
            # profile for graphing
            self.profile[point][1] = self.gyMax - self.profile[point][1]
            # profile for temperature data

    def draw_line(self, x1, y1, x2, y2, color):

        """
        :param x1:x1
        :param y1:y1
        :param x2:x2
        :param y2:y2
        :paran color:palette

        renders first along x, then y axis to render all sub pixels when slope is greater than each render step
        """

        # sets slope to 1000 when line is vertical and slope is undef
        try:
            slope = (y2 - y1) / (x2 - x1)
        except ZeroDivisionError:
            slope = 10000

        b = y1 - (slope * x1)

        # x initial < x final
        if x1 > x2:
            xi = x2
            xf = x1
        else:
            xi = x1
            xf = x2

        # render in x axis
        for x in range(xi, xf):
            yPos = int((slope * x) + b)
            self.bitmap[x, yPos] = color

        # y initial < y final
        if y1 > y2:
            yi = y2
            yf = y1
        else:
            yi = y1
            yf = y2

        # render along y axis
        for y in range(yi, yf):
            xPos = int((y - b) / slope)
            self.bitmap[xPos, y] = color

    def draw_profile(self):

        """
        :param profile: profile name

        draws profile graph and grid
        """

        drawPoints = []



        # draws x grid (60 sec interval)
        for xBar in range(1, self.maxX, 60):
            self.draw_line(xBar / self.maxX * self.gxBuff, self.gyBuff, xBar / self.maxX * self.gxBuff, 1, 1)
        self.draw_line(self.gxBuff, self.gyBuff, self.gxBuff, 1, 1)

        # draws y grid (50 deg interval)
        for yBar in range(1, self.maxY, 50):
            self.draw_line(1, yBar / self.maxY * self.gyBuff, self.gxBuff, yBar / self.maxY * self.gyBuff, 1)
        self.draw_line(1, self.gyBuff, self.gxBuff, self.gyBuff, 1)

        # convert all profile points to scaled points for graph
        for point in range(len(self.profile)):
            #print([int((self.profile[point][0] / self.profile[len(self.profile) - 1][0]) * (self.gXMax - self.gxMin)), int((self.profile[point][1] / self.profile[len(self.profile) - 1][1]) * (self.gyMax - self.gyMin))])
            drawPoints.append([int(self.profile[point][0] / self.maxX * self.gxBuff),
                               int(self.profile[point][1] / self.maxY * self.gyBuff)])

        # draw lines between each point
        for point in range(0, len(self.profile) - 1):
            print(drawPoints[point][0], drawPoints[point][1], drawPoints[point + 1][0], drawPoints[point + 1][1])
            self.draw_line(drawPoints[point][0], drawPoints[point][1], drawPoints[point + 1][0], drawPoints[point + 1][1], 2)

    # def save_temp_log(self):
    #     """
    #
    #     """
    #
    #     file = open("reflow_logs/log.txt", "a")
    #     file.write(self.tempLog)
    #     file.close()

    def run_profile(self):

        """

        """

        # preheat
        # while self.sensor.temperature < 60:
        #     self.solenoid1.value = True
        # self.solenoid1.value = False


        print("##RUN##")

        # used for high accuracy dutycycle (converted ns to s, output precision = 1ms)
        iterStartTime = time.monotonic_ns() / 1000000000
        # reference for profile start time
        iterProfileStartTime = time.monotonic_ns() / 1000000000

        # sets initial calibration temperature
        tempCal = (32, time.time())
        time.sleep(1)

        # cycle state (0 = off, 1 = on, 2 = get new on off cycle)
        cycle = 2
        solenoidState = False

        time1 = time.monotonic_ns() / 1000000000
        time.sleep(1)
        print(time.monotonic_ns() / 1000000000)
        print(time.monotonic_ns() / 1000000000 - time1)
        print(self.sensor.temperature)
        print("##TIME##")


        firstCycle = True
        skipOffTime = False
        tempDiff = 0

        while (time.monotonic_ns() / 1000000000) - iterProfileStartTime <= self.totalTime:

            gc.collect()
            board.DISPLAY.refresh(target_frames_per_second=60)

            # check for stop button press
            pressed = self.ts.touch_point
            if pressed:
                if self.startButton.contains(pressed):
                    self.startButton.label = "START"
                    time.sleep(1)
                    break

            # get temperature and slopes

            # calculate duty cycle and graph most recent segment
            if cycle == 2:

                iterStartTime = (time.monotonic_ns() / 1000000000)
                currentTemp = (time.monotonic_ns() / 1000000000, self.sensor.temperature)
                #print("CT: " + str(currentTemp))

                # run a generic first cycle to get sensor data
                if firstCycle == True:
                    cycleOnTime = 0.5
                    cycleOffTime = 0.5
                else:
                    # draw segment from cycle
                    # print(int(currentTemp[0] - int(iterProfileStartTime)),
                    #                self.gyBuff - int(currentTemp[1]),
                    #                int(lastTemp[0] - int(iterProfileStartTime)),
                    #                self.gyBuff - int(lastTemp[1]))
                    self.draw_line(int((currentTemp[0] - iterProfileStartTime) / self.maxX * self.gxBuff),
                                   int((self.gyBuff - currentTemp[1]) / self.maxY * self.gyBuff) + 50,
                                   int((lastTemp[0] - iterProfileStartTime) / self.maxX * self.gxBuff),
                                   int((self.gyBuff - lastTemp[1]) / self.maxY * self.gyBuff) + 50,
                                   3)

                    for segment in range(len(self.rawProfile)):
                        if self.rawProfile[segment][0] >= int(iterStartTime - iterProfileStartTime):
                            print(self.rawProfile[segment - 1])
                            print(str(iterStartTime - iterProfileStartTime))
                            profileTempSlope = (self.rawProfile[segment][1] - self.rawProfile[segment - 1][1]) / (self.rawProfile[segment][0] - self.rawProfile[segment - 1][0])

                            # tempDiff = (M * X + (Y - M * X)) - currentTemp
                            #print("SL: " + str(profileTempSlope))
                            tempDiff = ((profileTempSlope * int(currentTemp[0] - iterProfileStartTime)) + (self.rawProfile[segment - 1][1] - (profileTempSlope * self.rawProfile[segment - 1][0]))) - currentTemp[1] + self.tempOffset
                            print(tempDiff)
                            print(((profileTempSlope * int(currentTemp[0] - iterProfileStartTime))))
                            print((self.rawProfile[segment - 1][1] - (profileTempSlope * self.rawProfile[segment - 1][0])))
                            print("TD: " + str(tempDiff))
                            print(currentTemp)
                            print(lastTemp)
                            break

                    # cycleOnTime = (3 * tempDiff^3 * M) / 1000
                    if tempDiff > 0:
                        cycleOnTime = (tempDiff ** 2) / 100
                        if cycleOnTime > 1:
                            cycleOnTime = 1
                            cycleOffTime = 0
                            skipOffTime = True
                        else:
                            cycleOffTime = 1 - cycleOnTime
                            skipOffTime = False
                    else:
                        cycleOnTime = 0
                        cycleOffTime = 1
                        skipOffTime = False

                lastTemp = (time.monotonic_ns() / 1000000000, self.sensor.temperature)
                firstCycle = False
                cycle = 0

                # on cycle
                self.circle.fill = 0xFF0000
                board.DISPLAY.refresh(target_frames_per_second=60)

                #print(tempDiff)
                #print(cycleOffTime)
                #print(cycleOnTime)
                #print("-")
                self.solenoid1.value = True


            # off cycle
            if cycle == 0 and cycleOnTime < (time.monotonic_ns() / 1000000000) - iterStartTime:
                cycle = 1
                if skipOffTime == False:
                    self.circle.fill = 0x0
                    self.solenoid1.value = False
                board.DISPLAY.refresh(target_frames_per_second=60)

            # both cycles elapsed, reset elapsed time to 0 and get new duty cycle
            if cycle == 1 and cycleOnTime + cycleOffTime < (time.monotonic_ns() / 1000000000) - iterStartTime:
                cycle = 2
                print("CYCLE RESTART")
                board.DISPLAY.refresh(target_frames_per_second=60)

        # profile finished, log data
        # //add file logging
        # //add server logging
        self.graphLog = self.bitmap
        #print(self.tempLog)
        self.startButton.label = "START"
        #print(tempDiff)

        #self.save_temp_log()

    def mainloop(self):
        """
        main loop

        also default view on oven start or while not in use
        """

        self.load_profile("SAC305")
        self.draw_profile()

        #display_group = displayio.Group()

        while True:

            gc.collect()
            board.DISPLAY.refresh(target_frames_per_second=60)
            pressed = self.ts.touch_point

            if pressed:
                if self.startButton.contains(pressed):
                    self.startButton.label = "STOP"
                    self.run_profile()
                    break
                time.sleep(1)


oven = Oven()
oven.mainloop()