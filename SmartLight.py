from SimpleCV import Camera, Color
from datetime import datetime

class SmartLight():    
    # = Constants =
    alpha = 0.1
    
    # == Motion Variables & Constants ==
    motionColorThreshold = 2
    motionThreshold = 0.25
    motionGuessThreshold = 0.5
    
    motionValue = 0
    motionGuess = [0, 0.0]

    # == Skintone Variables & Constants ==
    skinBlobArea = 25
    skinBlobRatio = 0.5
    skinThreshold = 0.5
    
    skinValue = 0
    
    # == FPS Variables ==
    FPS = 0
    FPSTime = datetime.now()
    
    # == Timer Variables ==
    timerInitValue = 10 # Value in Seconds
    
    timerValue = 0
    
    # == Camera Variables ==
    camera = None
    image = None
    
    # Methods
    
    def detectMotion(self, previousFrame, currentFrame):
      
      # Detect changes from this previous to this frame
      diff = previousFrame.grayscale() - currentFrame.grayscale()
      
      # Motion! We consider we have motion if the mean color is greater than a certain threshold
      return diff.meanColor()[0] > self.motionColorThreshold
    
    def detectSkintone(self, frame):
      maxRatio = 0
      skinBlobs = frame.findSkintoneBlobs()

      if skinBlobs is not None:
        for blob in skinBlobs:
          ratio = blob.area() / (blob.minRectHeight() * blob.minRectWidth())
          if blob.area() > self.skinBlobArea and ratio > self.skinBlobRatio:
            if ratio > maxRatio: maxRatio = ratio
            blob.drawMinRect(color=Color.GREEN, width=2)

      return maxRatio > self.skinBlobRatio
    
    def saveImage(self, filename):
      self.image.save(filename)
    
    def run(self):
      # Update timer
      if self.timerValue > 0: self.timerValue -= 1
      
      # Get new image from camera
      previousImage = self.image
      self.image = self.camera.getImage()
      
      # Exponential smoothing of both motion and skin detectors
      self.motionValue = self.alpha * self.detectMotion(previousImage, self.image) + (1 - self.alpha) * self.motionValue
      self.skinValue = self.alpha * self.detectSkintone(self.image) + (1 - self.alpha) * self.skinValue
      
      # Calculate the prevision of wheather or not to turn the lights on if there's movement
      if self.motionValue > self.motionThreshold:
        self.motionGuess[0] += 1
        self.motionGuess[1] += ((self.skinValue > self.skinThreshold) - self.motionGuess[1])/self.motionGuess[0]
        
      # Turn on the Lights (or not...)!
      if self.skinValue > self.skinThreshold or (self.motionValue > self.motionThreshold and self.motionGuess > self.motionGuessThreshold):
          self.timerValue = int(self.timerInitValue * self.FPS)
        
      # Calculate the new FPS rate
      FPSCurrTime = datetime.now()
      FPSTimeDiff = (FPSCurrTime - self.FPSTime).seconds + (FPSCurrTime - self.FPSTime).microseconds*1e-6
      
      # Exponential smoothing of FPS
      self.FPS = self.alpha * 1/FPSTimeDiff + (1 - self.alpha) * self.FPS
      
      # Update the new time
      self.FPSTime = FPSCurrTime
       
      return {"motion": self.motionValue > self.motionThreshold, "motionValue": self.motionValue, "motionGuess": self.motionGuess > self.motionGuessThreshold, "motionGuessValue": self.motionGuess, "people": self.skinValue > self.skinThreshold, "skinValue": self.skinValue, "lights": self.timerValue > 0, "timer": self.timerValue, "FPS": self.FPS}
    
    def __init__(self, cameraID = -1, skinBlobArea = None):
      self.camera = Camera(cameraID)
      self.image = self.camera.getImage()
      if skinBlobArea is not None: self.skinBlobArea = skinBlobArea
    
    
