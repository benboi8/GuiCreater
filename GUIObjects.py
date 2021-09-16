import pygame as pg
from pygame import gfxdraw
from imageScaling import *
import math
import random
import json
import datetime as dt
import os

pg.init()
clock = pg.time.Clock()

sf = 2
gameState = "all"

running = True

fps = 60

allGUIObjects = []
allBoxs = []
allImageFrames = []
allLabels = []
allTextBoxs = []
allButtons = []
activeButtons = []
allSliders = []
allScrollbars = []
allSwitchs = []
allMultiButtons = []
allDropDowns = []
allMessageBoxs = []

black = (0, 0, 0)
white = (255, 255, 255)
lightGray = (205, 205, 205)
darkGray = (55, 55, 55)
red = (200, 0, 0)
green = (0, 200, 0)
blue = (0, 0, 200)
orange = (255, 145, 0)
lightRed = (184, 39, 39)
lightGreen = (0, 255, 48)
lightBlue = (20, 152, 215)
pink = (204, 126, 183)
lightBlack = (45, 45, 45)
darkWhite = (215, 215, 215)
yellow = (200, 200, 0)
gray = (170, 170, 170)

fontName = "arial"
fontSize = 12

nonAllowedKeysFilePath = "nonAllowedKeys.txt"
allowedKeysFilePath = "allowedKeys.txt"


def DrawRectOutline(surface, color, rect, width=1):
	x, y, w, h = rect
	width = max(width, 1)  # Draw at least one rect.
	width = min(min(width, w//2), h//2)  # Don't overdraw.

	# This draws several smaller outlines inside the first outline
	# Invert the direction if it should grow outwards.
	for i in range(int(width)):
		pg.gfxdraw.rectangle(surface, (x+i, y+i, w-i*2, h-i*2), color)


def DrawObround(surface, colors, rect, isFilled=False, additive=True, drawEdges=True, width=2, backgroundColor=darkGray):
	x, y, w, h = rect
	backgroundColor = backgroundColor
	if isFilled:
		colors = (colors[0], colors[0])

	# check if semicircles are added to the side or replace the side
	if w >= h:
		radius = h // 2
		if not additive:
			x += radius
			w -= radius * 2
		# checks if it should be filled
		for i in range(-width//2, width//2):
			pg.gfxdraw.filled_circle(surface, x, y + radius, radius, colors[1])
			pg.gfxdraw.filled_circle(surface, x + w, y + radius, radius, colors[1])
			if drawEdges:
				pg.gfxdraw.filled_circle(surface, x, y+radius, radius + width // 2 + 1, colors[0])
				pg.gfxdraw.filled_ellipse(surface, x + width//3, y+radius, radius, radius, colors[1])

				pg.gfxdraw.filled_circle(surface, x + w, y+radius, radius + width // 2 + 1, colors[0])
				pg.gfxdraw.filled_ellipse(surface, x + w - width//3, y+radius, radius, radius, colors[1])

				pg.draw.aaline(surface, colors[0], (x, y), (x + w, y))
				pg.draw.aaline(surface, colors[0], (x, y + h), (x + w, y + h))

				DrawRectOutline(surface, colors[0], (x+i, y+i, w+1-i*2, h+1-i*2), 2)
			pg.draw.rect(surface, colors[1], (x-1, y+1, w+4, h-1))

		pg.draw.aaline(surface, backgroundColor, (x, y-width//2-int(0.5*sf)), (x + w, y-width//2-int(0.5*sf)))
		pg.draw.aaline(surface, backgroundColor, (x, y+h+width//2+int(0.5*sf)), (x + w, y+h+width//2+int(0.5*sf)))
	else:
		radius = w // 2
		if not additive:
			y += radius
			h -= radius * 2
		for i in range(-width//2, width//2):
			pg.gfxdraw.filled_circle(surface, x + radius, y, radius, colors[1])
			pg.gfxdraw.filled_circle(surface, x + radius, y + h, radius, colors[1])
			if drawEdges:
				pg.gfxdraw.filled_circle(surface, x + radius, y, radius + width // 2, colors[0])
				pg.gfxdraw.filled_ellipse(surface, x + radius, y + width//3, radius, radius, colors[1])

				pg.gfxdraw.filled_circle(surface, x + radius, y + h, radius + width // 2, colors[0])
				pg.gfxdraw.filled_ellipse(surface, x + radius, y + h - width, radius, radius, colors[1])

				pg.draw.aaline(surface, colors[0], (x, y), (x, y + h))
				pg.draw.aaline(surface, colors[0], (x + w, y), (x + w, y + h))

				DrawRectOutline(surface, colors[0], (x+i, y+i, w+1-i*2, h+1-i*2), 2)
			pg.draw.rect(surface, colors[1], (x+1, y-1, w-1, h+4))

		pg.draw.aaline(surface, backgroundColor, (x-width//2-int(0.5*sf), y), (x - width//2-int(0.5*sf), y + h))
		pg.draw.aaline(surface, backgroundColor, (x+w+width//2+int(0.5*sf), y), (x+w+width//2+int(0.5*sf), y + h))


def DrawRoundedRect(surface, colors, rect, roundness=5, width=1, activeCorners={}, isFilled=False):
	x, y, w, h = rect
	if isFilled:
		colors = (colors[1], colors[1])

	topLeft = activeCorners.get("topLeft", True)
	topRight = activeCorners.get("topRight", True)
	bottomLeft = activeCorners.get("bottomLeft", True)
	bottomRight = activeCorners.get("bottomRight", True)

	width = int(width)

	# which corners to draw
	if topLeft:
		pg.draw.circle(surface, colors[1], (x+roundness, y+roundness), roundness, width)
		pg.gfxdraw.filled_circle(surface, x+roundness+width, y+roundness+width-1, roundness+int(0.5*sf), colors[0])
		pg.draw.rect(surface, colors[0], (x+roundness, y, roundness, roundness))
		pg.draw.rect(surface, colors[0], (x, y+roundness, roundness, roundness))
	else:
		pg.draw.rect(surface, colors[1], (x, y, roundness*2, roundness*2))
		pg.draw.rect(surface, colors[0], (x + width, y + width, roundness*2, roundness*2))

	if topRight:
		pg.draw.circle(surface, colors[1], (x+w-roundness, y+roundness), roundness, width)
		pg.gfxdraw.filled_circle(surface, x+w-roundness-width-1, y+roundness+width-1, roundness+int(0.5*sf), colors[0])
		pg.draw.rect(surface, colors[0], (x+w-roundness*2, y, roundness, roundness))
		pg.draw.rect(surface, colors[0], (x+w-roundness, y+roundness, roundness, roundness))
	else:
		pg.draw.rect(surface, colors[1], (x+w-roundness*2+1, y, roundness*2, roundness*2))
		pg.draw.rect(surface, colors[0], (x+w-roundness*2+1 - width, y + width, roundness*2, roundness*2))

	if bottomLeft:
		pg.draw.circle(surface, colors[1], (x+roundness, y+h-roundness), roundness, width)
		pg.gfxdraw.filled_circle(surface, x+roundness+width, y+h-roundness-width, roundness+int(0.5*sf), colors[0])
		pg.draw.rect(surface, colors[0], (x+roundness, y+h-roundness, roundness, roundness))
		pg.draw.rect(surface, colors[0], (x, y+h-roundness*2, roundness, roundness))
	else:
		pg.draw.rect(surface, colors[1], (x, y+h-roundness*2+1, roundness*2, roundness*2))
		pg.draw.rect(surface, colors[0], (x + width, y+h-roundness*2 - width+1, roundness*2, roundness*2))

	if bottomRight:
		pg.draw.circle(surface, colors[1], (x+w-roundness, y+h-roundness), roundness, width)
		pg.gfxdraw.filled_circle(surface, x+w-roundness-width-1, y+h-roundness-width, roundness+int(0.5*sf), colors[0])
		pg.draw.rect(surface, colors[0], (x+w-roundness*2, y+h-roundness, roundness, roundness))
		pg.draw.rect(surface, colors[0], (x+w-roundness, y+h-roundness*2, roundness, roundness))
	else:
		pg.draw.rect(surface, colors[1], (x+w-roundness*2-width+1, y+h-roundness*2-width+1, roundness*2+width, roundness*2+width))
		pg.draw.rect(surface, colors[0], (x+w-roundness*2-width+1, y+h-roundness*2-width+1, roundness*2, roundness*2))

	pg.draw.rect(surface, colors[0], (x, y+roundness, w, h-(roundness*2)))
	pg.draw.rect(surface, colors[0], (x+roundness, y, w-(roundness*2), h))

	for i in range(width):
		pg.draw.aaline(surface, colors[1], (x+i, y+roundness), (x+i, y+h-roundness))
		pg.draw.aaline(surface, colors[1], (x+w-i, y+roundness), (x+w-i, y+h-roundness))
		pg.draw.aaline(surface, colors[1], (x+roundness, y+i), (x+w-roundness, y+i))
		pg.draw.aaline(surface, colors[1], (x+roundness, y+h-i), (x+w-roundness, y+h-i))


def Rescale(newScale, rescaleScreen=True):
	global width, height, screen, sf
	sf = newScale

	if rescaleScreen:
		width, height = 640, 360
		if sf == 3:
			screen = pg.display.set_mode((width * sf, height * sf), pg.FULLSCREEN)
		else:
			screen = pg.display.set_mode((width * sf, height * sf))

	for box in allBoxs:
		box.Rescale()

	for imageFrame in allImageFrames:
		imageFrame.Rescale()

	for label in allLabels:
		label.Rescale()

	for button in allButtons:
		button.Rescale()

	for scrollBar in allScrollbars:
		scrollBar.Rescale()

	for slider in allSliders:
		slider.Rescale()

	for textBox in allTextBoxs:
		textBox.Rescale()

	for switch in allSwitchs:
		switch.Rescale()

	for button in allMultiButtons:
		button.Rescale()

	for dropDown in allDropDowns:
		dropDown.Rescale()

	return sf


def ChangeSf():
	if sf + 1 > 3:
		return 1
	else:
		return sf + 1


def MoveRectWithoutCenter(startPos, startRect):
	# get current mouse pos
	mouseX, mouseY = pg.mouse.get_pos()

	# get difference from start x and start y to mouse cursor for movement
	differenceX = startPos[0] - startRect.x
	differenceY = startPos[1] - startRect.y

	# get new pos
	x = mouseX - differenceX
	y = mouseY - differenceY

	return pg.Rect(x, y, startRect.w, startRect.h)


def AlignText(rect, textSurface, alignment="center", width=2):
	x, y, w, h = rect

	# get horizontal and vertical alignments
	alignment = str(alignment).lower().strip()

	if "-" in alignment:
		align = alignment.split("-")
		horizontal, vertical = align[0], align[1]

	else:
		if alignment == "center":
			horizontal, vertical = alignment, alignment
		elif alignment == "left" or alignment == "right":
			horizontal, vertical = alignment, "center"
		elif alignment == "top" or alignment == "bottom":
			horizontal, vertical = "center", alignment
		else:
			horizontal, vertical = "center", "center"

	# check horizontal alignment
	if horizontal == "center":
		x += w // 2 - textSurface.get_width() // 2
	elif horizontal == "left":
		x += (width + 2) * sf
	elif horizontal == "right":
		x += w - textSurface.get_width() - ((width + 2) * sf)

	# check vertical alignment
	if vertical == "center":
		y += h // 2 - textSurface.get_height() // 2
	elif vertical == "top":
		y += (width + 2) * sf
	elif vertical == "bottom":
		y += h - textSurface.get_height() - ((width + 2) * sf)


	return pg.Rect(x, y, w, h)


class Box:
	def __init__(self, surface, name, rect, colors, drawData={}, lists=[allBoxs]):
		# which surface should be drawn to
		self.activeSurface = drawData.get("activeSurface", "all")
		self.surface = surface
		self.ogRect = pg.Rect(rect)

		self.backgroundColor = colors[0]
		self.foregroundColor = colors[1]

		self.colors = colors

		self.name = name
		self.drawBorder = drawData.get("drawBorder", True)
		self.ogBorderWidth = drawData.get("borderWidth", 1)
		self.isFilled = drawData.get("isFilled", False)
		self.roundedEdges = drawData.get("roundedEdges", False)
		self.roundedCorners = drawData.get("roundedCorners", False)
		self.roundness = drawData.get("roundness", 10)
		self.activeCorners = drawData.get("activeCorners", {})

		if self.roundedEdges and self.roundedCorners:
			self.roundedCorners = False

		self.drawBackground = drawData.get("drawBackground", True)
		self.additive = drawData.get("additive", False)

		self.Rescale()
		self.lists = lists
		for listToAppend in lists:
			if type(listToAppend) == list:
				listToAppend.append(self)
			elif type(listToAppend) == dict:
				listToAppend[self.name] = self

		allGUIObjects.append(self)

	def Rescale(self):
		self.rect = pg.Rect(self.ogRect.x * sf, self.ogRect.y * sf, self.ogRect.w * sf, self.ogRect.h * sf)
		self.borderWidth = self.ogBorderWidth * sf

	def Zoom(self, zoomAmount):
		self.rect.x = (self.ogRect.x * sf) * zoomAmount
		self.rect.y = (self.ogRect.y * sf) * zoomAmount

	def Draw(self):
		if not self.roundedEdges and not self.roundedCorners:
			if self.drawBackground:
				pg.draw.rect(self.surface, self.backgroundColor, self.rect)

			if not self.isFilled:
				if self.drawBorder:
					DrawRectOutline(self.surface, self.foregroundColor, self.rect, self.borderWidth)
			else:
				pg.draw.rect(self.surface, self.foregroundColor, self.rect)

		elif self.roundedEdges and not self.roundedCorners:
			DrawObround(self.surface, (self.foregroundColor, self.backgroundColor), self.rect, self.isFilled, self.additive, self.drawBorder, self.borderWidth)
		else:
			DrawRoundedRect(self.surface, (self.backgroundColor, self.foregroundColor), self.rect, self.roundness, self.borderWidth, self.activeCorners, self.isFilled)

	def UpdateColors(self, backgroundColor, foregroundColor):
		self.backgroundColor = backgroundColor
		self.foregroundColor = foregroundColor

	def UpdateRect(self, rect):
		self.ogRect = pg.Rect(rect)
		self.Rescale()


class ImageFrame(Box):
	def __init__(self, surface, name, rect, colors, imageData={}, drawData={}, lists=[allImageFrames]):
		self.isAnimation = imageData.get("isAnimation", False)
		self.numOfFrames = imageData.get("numOfFrames", 0)
		self.frameRate = imageData.get("frameRate", fps)

		super().__init__(surface, name, rect, colors, drawData, lists)

		self.imageName = imageData.get("filePath", None)
		self.ogSize = imageData.get("size", (self.ogRect.w, self.ogRect.h))

		self.RescaleImage()

	def Rescale(self):
		self.rect = pg.Rect(self.ogRect.x * sf, self.ogRect.y * sf, self.ogRect.w * sf, self.ogRect.h * sf)
		self.borderWidth = self.ogBorderWidth * sf

	def RescaleImage(self):
		if self.ogSize != (0, 0):
			self.size = (self.ogSize[0] * sf, self.ogSize[1] * sf)
		else:
			self.size = (self.ogRect.w * sf, self.ogRect.h * sf)

		self.CreateScaledAssetsFolder()

		if self.imageName != None:
			ScaleImage("assets/" + self.imageName, self.size, "assets/scaledAssets/" + self.imageName)
		try:
			self.image = pg.image.load("assets/scaledAssets/" + self.imageName).convert_alpha()
		except:
			self.image = None

	def CreateScaledAssetsFolder(self):
		try:
			if not os.path.isdir("assets/scaledAssets/"):
				os.mkdir("assets/scaledAssets")
		except:
			pass

	def UpdateImage(self, imageData):
		self.imageName = imageData.get("filePath", None)
		self.ogSize = imageData.get("size", (0, 0))

		self.isAnimation = imageData.get("isAnimation", False)
		self.numOfFrames = imageData.get("numOfFrames", 0)
		self.frameRate = imageData.get("frameRate", fps)

		self.RescaleImage()

	def DrawImage(self):
		if self.image != None:
			self.surface.blit(self.image, self.rect)

	def Draw(self):
		if not self.roundedEdges and not self.roundedCorners:
			if self.drawBackground:
				pg.draw.rect(self.surface, self.backgroundColor, self.rect)

			if not self.isFilled:
				if self.drawBorder:
					DrawRectOutline(self.surface, self.foregroundColor, self.rect, self.borderWidth)
			else:
				pg.draw.rect(self.surface, self.foregroundColor, self.rect)

		elif self.roundedEdges and not self.roundedCorners:
			DrawObround(self.surface, (self.foregroundColor, self.backgroundColor), self.rect, self.isFilled, self.additive, self.drawBorder, self.borderWidth)
		else:
			DrawRoundedRect(self.surface, (self.backgroundColor, self.foregroundColor), self.rect, self.roundness, self.borderWidth, self.activeCorners, self.isFilled)

		self.DrawImage()


class Label(ImageFrame):
	def __init__(self, surface, name, rect, colors, text, font, textData={}, drawData={}, imageData={}, lists=[allLabels]):
		self.name = name
		self.text = text
		self.ogFontObj = font
		self.fontName = font[0]
		self.fontColor = font[2]

		self.ogFontSize = textData.get("fontSize", font[1])
		self.alignText = textData.get("alignText", "center")
		self.drawText = textData.get("drawText", True)
		self.multiline = textData.get("multiline", False)
		self.scrollable = textData.get("isScrollable", self.multiline)
		self.scrollAmount = textData.get("scrollAmount", pg.font.SysFont(self.fontName, self.ogFontSize*sf).render(text, True, self.fontColor).get_height())

		self.textObjs = []

		super().__init__(surface, name, rect, colors, imageData, drawData, lists)

		if self.multiline:
			self.GetTextObjects()

	def GetTextObjects(self):
		self.textObjs = []
		self.text = str(self.text)
		if "\\n" in self.text:
			text = self.text.split("\\n")
		else:
			text = self.text.split("\n")

		rect = self.rect
		for i, t in enumerate(text):
			textSurface = self.font.render(str(t), True, self.fontColor)
			self.textObjs.append((textSurface, AlignText(pg.Rect(rect.x, rect.y + (i * textSurface.get_height()), rect.w, rect.h), textSurface, self.alignText, self.borderWidth)))

	def HandleEvent(self, event):
		if event.type == pg.MOUSEBUTTONDOWN:
			if self.rect.collidepoint(pg.mouse.get_pos()):
				if self.scrollable:
					# up
					if event.button == 4:
						self.Scroll(1)
					# down
					if event.button == 5:
						self.Scroll(-1)

	def Scroll(self, direction, scrollAmount=0):
		if scrollAmount == 0:
			scrollAmount = self.scrollAmount

		for textObj in self.textObjs:
			# scroll up
			if direction == 1:
				if self.textObjs[0][1].y + scrollAmount * direction <= AlignText(self.rect, self.textObjs[0][0], self.alignText, self.borderWidth).y:
					if self.textObjs.index(textObj) != 0:
						textObj[1].y += scrollAmount * direction
			#scroll down
			else:
				if self.textObjs[-1][1].y + scrollAmount * direction >= self.rect.y + self.rect.h + (scrollAmount * direction) - self.textObjs[0][0].get_height():
					textObj[1].y += scrollAmount * direction

		if direction == 1:
			if self.textObjs[0][1].y + scrollAmount * direction <= AlignText(self.rect, self.textObjs[0][0], self.alignText, self.borderWidth).y:
				self.textObjs[0][1].y += scrollAmount * direction

	def Rescale(self):
		self.rect = pg.Rect(self.ogRect.x * sf, self.ogRect.y * sf, self.ogRect.w * sf, self.ogRect.h * sf)
		self.borderWidth = self.ogBorderWidth * sf
		self.fontSize = int(self.ogFontSize) * sf
		try:
			self.font = pg.font.Font(str(self.fontName), int(self.fontSize))
		except:
			self.font = pg.font.SysFont(str(self.fontName), int(self.fontSize))

		self.UpdateTextRect()
		self.GetTextObjects()

	def UpdateTextRect(self):
		self.textSurface = self.font.render(str(self.text), True, self.fontColor)
		self.textRect = AlignText(self.rect, self.textSurface, self.alignText, self.borderWidth)

	def Draw(self):
		if not self.roundedEdges and not self.roundedCorners:
			pg.draw.rect(self.surface, self.backgroundColor, self.rect)

			if not self.isFilled:
				if self.drawBorder:
					DrawRectOutline(self.surface, self.foregroundColor, self.rect, self.borderWidth)
			else:
				pg.draw.rect(self.surface, self.foregroundColor, self.rect)

		elif self.roundedEdges and not self.roundedCorners:
			DrawObround(self.surface, (self.foregroundColor, self.backgroundColor), self.rect, self.isFilled, self.additive, self.drawBorder, self.borderWidth)
		else:
			DrawRoundedRect(self.surface, (self.backgroundColor, self.foregroundColor), self.rect, self.roundness, self.borderWidth, self.activeCorners, self.isFilled)

		if not self.multiline:
			if self.drawText:
				self.surface.blit(self.textSurface, self.textRect)
		else:
			self.GetTextObjects()
			if self.drawText:
				for textObj in self.textObjs:
					if textObj[1].y >= self.rect.y and textObj[1].y + textObj[0].get_height() <= self.rect.y + self.rect.h:
						self.surface.blit(textObj[0], textObj[1])
		self.DrawImage()

	def UpdateText(self, text, font):
		self.text = str(text)
		self.ogFontObj = font
		self.fontName = font[0]
		self.ogFontSize = font[1]
		self.fontColor = font[2]

		self.Rescale()
		self.GetTextObjects()


class TextInputBox(Label):
	def __init__(self, surface, name, rect, colors, font, inputData={}, textData={}, drawData={}, imageData={}, lists=[allTextBoxs]):
		self.backgroundColor = colors[0]
		self.inactiveColor = colors[1]
		self.activeColor = colors[2]
		self.foregroundColor = self.inactiveColor

		self.textColor = font[2]

		self.charLimit = inputData.get("charLimit", -1)
		self.splashText = inputData.get("splashText", "Type here.")

		self.growRect = drawData.get("growRect", False)
		self.header = drawData.get("header", False)
		self.replaceSplashText = drawData.get("replaceSplashText", True)

		super().__init__(surface, name, rect, colors, self.splashText, font, textData, drawData, imageData, lists)

		self.nonAllowedKeysFilePath = inputData.get("nonAllowedKeysFile", None)
		self.allowedKeysFilePath = inputData.get("allowedKeysFile", None)

		self.nonAllowedKeysList = inputData.get("nonAllowedKeysList", [])
		self.allowedKeysList = inputData.get("allowedKeysList", [])

		self.nonAllowedKeys = set()
		self.allowedKeys = set()

		self.pointer = len(self.text)

		self.GetKeys()

		if type(self.header) == str:
			self.MakeHeader()

		self.active = False

	def Rescale(self):
		self.rect = pg.Rect(self.ogRect.x * sf, self.ogRect.y * sf, self.ogRect.w * sf, self.ogRect.h * sf)
		self.borderWidth = self.ogBorderWidth * sf
		self.RescaleText()

	def RescaleText(self):
		self.fontSize = self.ogFontSize * sf
		try:
			self.font = pg.font.Font(self.fontName, self.fontSize)
		except:
			self.font = pg.font.SysFont(self.fontName, self.fontSize)
		self.textSurface = self.font.render(str(self.text), True, self.fontColor)
		self.textRect = AlignText(self.rect, self.textSurface, self.alignText, self.borderWidth)
		try:
			if type(self.header) == str:
				self.headerRect = AlignText(self.rect, self.headerTextSurface, "center-top", self.borderWidth)
		except:
			pass

	def MakeHeader(self):
		self.headerTextSurface = self.font.render(self.header, True, self.textColor)
		self.headerRect = AlignText(self.rect, self.headerTextSurface, "center-top", self.borderWidth)
		self.ogRect.h += self.headerTextSurface.get_height() // 2
		try:
			if self.alignText.split("-")[1] == "top":
				self.alignText = self.alignText.split("-")[0]
		except:
			pass
		self.Rescale()

	def GetKeys(self):
		if self.nonAllowedKeysFilePath != None:
			with open(self.nonAllowedKeysFilePath, "r") as nonAllowedKeysFile:
				nonAllowedKeysText = nonAllowedKeysFile.read()
				for char in nonAllowedKeysText:
					self.nonAllowedKeys.add(char)

		for char in self.nonAllowedKeysList:
			self.nonAllowedKeys.add(char)

		if self.allowedKeysFilePath != None:
			with open(self.allowedKeysFilePath, "r") as allowedKeysFile:
				allowedKeysText = allowedKeysFile.read()
				for char in allowedKeysText:
					self.allowedKeys.add(char)

		for char in self.allowedKeysList:
			self.allowedKeys.add(char)

	def HandleEvent(self, event):
		if event.type == pg.MOUSEBUTTONDOWN:
			if event.button == 1:
				if self.rect.collidepoint(pg.mouse.get_pos()):
					self.pointer = len(self.text)
					self.active = not self.active
					if self.active:
						self.foregroundColor = self.activeColor
					else:
						self.foregroundColor = self.inactiveColor
				else:
					self.active = False
					self.foregroundColor = self.inactiveColor

		if event.type == pg.KEYDOWN:
			if event.key == pg.K_RETURN:
				self.active = False
				self.foregroundColor = self.inactiveColor

			if event.key == pg.K_RIGHT:
				self.pointer = min(len(self.text), self.pointer + 1)
			if event.key == pg.K_LEFT:
				if not self.replaceSplashText:
					self.pointer = max(len(self.splashText), self.pointer - 1)
				else:
					self.pointer = max(0, self.pointer - 1)

		if self.active:
			self.HandleKeyboard(event)

	def HandleKeyboard(self, event):
		if self.active:
			if self.replaceSplashText:
				textLength = len(self.text)
			else:
				textLength = len(self.text) - len(self.splashText)

			if event.type == pg.KEYDOWN:
				if event.key == pg.K_BACKSPACE:
					if textLength != 0 and self.text != self.splashText:
						self.text = self.text[: self.pointer - 1] + self.text[self.pointer :]
						self.pointer = max(len(self.splashText), self.pointer - 1)
				elif event.key == pg.K_DELETE:
					if textLength != 0 and self.text != self.splashText:
						self.text = self.text[: self.pointer] + self.text[self.pointer + 1:]
				else:
					if event.key != pg.K_LEFT and event.key != pg.K_RIGHT:
						self.FilterText(event.unicode)

				if self.text == "":
					self.text = self.splashText
				self.textSurface = self.font.render(self.text, True, self.textColor)
				if self.growRect:
					self.rect.w = max(self.rect.w, self.textSurface.get_width() + 6*sf)

	def FilterText(self, key):
		if self.replaceSplashText:
			textLength = len(self.text)
		else:
			textLength = len(self.text) - len(self.splashText)

		if textLength + 1 <= self.charLimit or self.charLimit == -1:
			if self.replaceSplashText:
				if self.text == self.splashText:
					self.text = ""

			if len(self.nonAllowedKeys) == 0:
				if len(self.allowedKeys) == 0:
					if self.pointer == len(self.text):
						self.text += key
					else:
						self.text = self.text[: self.pointer] + key + self.text[self.pointer:]
					self.pointer = min(len(self.text), self.pointer + 1)

				else:
					if key in self.allowedKeys:
						if self.pointer == len(self.text):
							self.text += key
						else:
							self.text = self.text[: self.pointer] + key + self.text[self.pointer :]
						self.pointer = min(len(self.text), self.pointer + 1)

			else:
				if len(self.allowedKeys) == 0:
					if key not in self.nonAllowedKeys:
						if key in self.allowedKeys:
							if self.pointer == len(self.text):
								self.text += key
							else:
								self.text = self.text[: self.pointer] + key + self.text[self.pointer :]
							self.pointer = min(len(self.text), self.pointer + 1)

				else:
					if key not in self.nonAllowedKeys:
						if self.pointer == len(self.text):
							self.text += key
						else:
							self.text = self.text[: self.pointer] + key + self.text[self.pointer :]
						self.pointer = min(len(self.text), self.pointer + 1)

	def Draw(self):
		self.RescaleText()
		if not self.roundedEdges and not self.roundedCorners:
			pg.draw.rect(self.surface, self.backgroundColor, self.rect)

			if not self.isFilled:
				if self.drawBorder:
					DrawRectOutline(self.surface, self.foregroundColor, self.rect, self.borderWidth)
			else:
				pg.draw.rect(self.surface, self.foregroundColor, self.rect)

		elif self.roundedEdges and not self.roundedCorners:
			DrawObround(self.surface, (self.foregroundColor, self.backgroundColor), self.rect, self.isFilled, self.additive, self.drawBorder, self.borderWidth)
		else:
			DrawRoundedRect(self.surface, (self.backgroundColor, self.foregroundColor), self.rect, self.roundness, self.borderWidth, self.activeCorners, self.isFilled)

		if self.drawText:
			if self.active:
				if dt.datetime.now().microsecond % 1000000 > 500000:
					pg.draw.rect(self.surface, self.textColor, (self.textRect.x + (self.textSurface.get_width() / max(1, len(self.text)) * self.pointer), self.textRect.y, 1*sf, self.textSurface.get_height()))
			self.surface.blit(self.textSurface, self.textRect)

			if type(self.header) == str:
				self.surface.blit(self.headerTextSurface, self.headerRect)
		self.DrawImage()


class Button(Label):
	def __init__(self, surface, name, rect, colors, text, font, isHoldButton=False, textData={}, drawData={}, imageData={}, lists=[allButtons], inputData={}):
		super().__init__(surface, name, rect, (colors[0], colors[1]), text, font, textData, drawData, imageData, lists)
		self.active = inputData.get("active", False)
		self.backgroundColor = colors[0]
		self.inactiveColor = colors[1]
		self.activeColor = colors[2]
		self.foregroundColor = self.inactiveColor
		self.isHoldButton = isHoldButton

	def HandleEvent(self, event):
		if event.type == pg.MOUSEBUTTONDOWN:
			if event.button == 1:
				if self.rect.collidepoint(pg.mouse.get_pos()):
					self.active = not self.active
					self.SwapColors(True)
					if self.active:
						self.OnClick()
					else:
						self.OnRelease()

		if self.isHoldButton:
			if event.type == pg.MOUSEBUTTONUP:
				if event.button == 1:
					self.active = False
					self.OnRelease()
					self.SwapColors(False)
		else:
			self.SwapColors(self.active)

	def SwapColors(self, active=None):
		if active == None:
			if self.foregroundColor == self.inactiveColor:
				self.foregroundColor = self.activeColor
			else:
				self.foregroundColor = self.inactiveColor
		else:
			if active:
				self.foregroundColor = self.activeColor
			else:
				self.foregroundColor = self.inactiveColor

	def OnClick(self):
		activeButtons.append((self, False))

	def OnRelease(self):
		if (self, True) in activeButtons:
			activeButtons.remove((self, True))
		if (self, False) in activeButtons:
			activeButtons.remove((self, False))

	def Draw(self):
		if not self.roundedEdges and not self.roundedCorners:
			pg.draw.rect(self.surface, self.backgroundColor, self.rect)

			if not self.isFilled:
				if self.drawBorder:
					DrawRectOutline(self.surface, self.foregroundColor, self.rect, self.borderWidth)
			else:
				pg.draw.rect(self.surface, self.foregroundColor, self.rect)

		elif self.roundedEdges and not self.roundedCorners:
			DrawObround(self.surface, (self.foregroundColor, self.backgroundColor), self.rect, self.isFilled, self.additive, self.drawBorder, self.borderWidth)
		else:
			DrawRoundedRect(self.surface, (self.backgroundColor, self.foregroundColor), self.rect, self.roundness, self.borderWidth, self.activeCorners, self.isFilled)

		if self.drawText:
			self.surface.blit(self.textSurface, self.textRect)

		self.DrawImage()

	def UpdateColors(self, backgroundColor, activeColor, inactiveColor):
		self.backgroundColor = backgroundColor
		self.inactiveColor = inactiveColor
		self.activeColor = activeColor


class Slider(Label):
	def __init__(self, surface, name, rect, colors, text, font, textData={}, drawData={}, inputData={}, imageData={}, lists=[allSliders]):
		super().__init__(surface, name, rect, colors, text, font, textData, drawData, imageData, lists)
		self.isVertical = inputData.get("isVertical", False)
		self.scrollObj = inputData.get("scrollObj", None)
		self.startValue = inputData.get("startValue", 0.0)
		self.value = self.startValue
		self.moveText = drawData.get("moveText", False)
		self.sliderSize = drawData.get("sliderSize", (0, 0))
		self.isFilled = drawData.get("isFilled", False)
		self.colors = colors
		self.fontObj = font
		self.textData = textData
		self.drawData = drawData
		self.inputData = inputData
		self.imageData = imageData

		self.sliderObj = None
		self.CreateSliderButton()

	def CreateSliderButton(self):
		if self.sliderObj != None:
			if self.sliderObj in allGUIObjects:
				allGUIObjects.remove(self.sliderObj)

			if self.sliderObj in allButtons:
				allButtons.remove(self.sliderObj)

		rect = self.ogRect

		if self.sliderSize == (0, 0):
			if self.ogRect.w > self.ogRect.h:
				self.sliderSize = ((self.ogRect.w * sf) // 5, self.ogRect.h)
			else:
				self.sliderSize = (self.ogRect.w, (self.ogRect.h * sf) // 5)

		if not self.isVertical:
			drawData = self.drawData
			drawData["isFilled"] = True
			if self.roundedCorners:
				self.sliderObj = Button(self.surface, "", (rect[0] + self.borderWidth + 1, rect[1] + self.borderWidth + 1, self.sliderSize[0] - (self.borderWidth+1) * 2, self.sliderSize[1] - (self.borderWidth+1) * 2), self.colors, "", self.fontObj, True, self.textData, self.drawData, self.imageData)
			else:
				self.sliderObj = Button(self.surface, "", (rect[0] + self.borderWidth, rect[1] + self.borderWidth, self.sliderSize[0] - self.borderWidth * 2, self.sliderSize[1] - self.borderWidth*2), self.colors, "", self.fontObj, True, self.textData, self.drawData, self.imageData)
		else:
			drawData = self.drawData
			drawData["isFilled"] = True
			if self.roundedCorners:
				self.sliderObj = Button(self.surface, "", (rect[0] + self.borderWidth + 1, rect[1] + self.borderWidth + 1, self.sliderSize[0] - (self.borderWidth+1)*2, self.sliderSize[1] - (self.borderWidth+1)*2), self.colors, "", self.fontObj, True, self.textData, self.drawData, self.imageData)
			else:
				self.sliderObj = Button(self.surface, "", (rect[0] + self.borderWidth, rect[1] + self.borderWidth, self.sliderSize[0] - self.borderWidth*2, self.sliderSize[1] - self.borderWidth*2), self.colors, "", self.fontObj, True, self.textData, self.drawData, self.imageData)

	def Rescale(self):
		self.rect = pg.Rect(self.ogRect.x * sf, self.ogRect.y * sf, self.ogRect.w * sf, self.ogRect.h * sf)
		self.borderWidth = self.ogBorderWidth * sf
		self.fontSize = self.ogFontSize * sf
		try:
			self.font = pg.font.Font(self.fontName, self.fontSize)
		except:
			self.font = pg.font.SysFont(self.fontName, self.fontSize)

		self.textSurface = self.font.render(self.text, True, self.fontColor)
		self.textRect = AlignText((self.rect.x, self.rect.y - (self.textSurface.get_height() + 2 * sf), self.rect.w, self.rect.h), self.textSurface, self.alignText, self.borderWidth)
		self.GetTextObjects()

	def Draw(self):
		if not self.roundedEdges and not self.roundedCorners:
			pg.draw.rect(self.surface, self.backgroundColor, self.rect)

			if self.drawBorder:
				DrawRectOutline(self.surface, self.foregroundColor, self.rect, self.borderWidth)

		elif self.roundedEdges and not self.roundedCorners:
			DrawObround(self.surface, (self.foregroundColor, self.backgroundColor), self.rect, self.isFilled, self.additive, self.drawBorder, self.borderWidth)
		else:
			DrawRoundedRect(self.surface, (self.backgroundColor, self.foregroundColor), self.rect, self.roundness, self.borderWidth, self.activeCorners, self.isFilled)

		self.sliderObj.Draw()

		if self.drawText:
			self.surface.blit(self.textSurface, self.textRect)

		self.DrawImage()

	def HandleEvent(self, event):
		if event.type == pg.MOUSEBUTTONDOWN:
			if self.rect.collidepoint(pg.mouse.get_pos()):
				# up
				if event.button == 4:
					self.Scroll(1)
					self.GetValue()

				# down
				if event.button == 5:
					self.Scroll(-1)
					self.GetValue()

		mousePos = pg.mouse.get_pos()
		if self.sliderObj.active:
			if not self.isVertical:
				if mousePos[0] < self.rect.x + self.rect.w - self.sliderObj.rect.w // 2 - self.borderWidth*2:
					if mousePos[0] > self.rect.x + self.sliderObj.rect.w // 2 + self.borderWidth*2:
						self.sliderObj.rect.x = mousePos[0] - self.sliderObj.rect.w // 2
						if self.moveText:
							self.sliderObj.textRect = AlignText(self.sliderObj.rect, self.sliderObj.textSurface, self.sliderObj.alignText, self.sliderObj.borderWidth)
						if self.scrollObj != None:
							if pg.mouse.get_rel()[0] > 1:
								self.scrollObj.Scroll(1, self.sliderObj.rect.w / len(self.scrollObj.textObjs))
							else:
								self.scrollObj.Scroll(-1, self.sliderObj.rect.w / len(self.scrollObj.textObjs))
						else:
							self.GetValue()
			else:
				if mousePos[1] < self.rect.y + self.rect.h - self.sliderObj.rect.h // 2 - self.borderWidth*2:
					if mousePos[1] > self.rect.y + self.sliderObj.rect.h // 2 + self.borderWidth*2:
						self.sliderObj.rect.y = mousePos[1] - self.sliderObj.rect.h // 2
						if self.moveText:
							self.sliderObj.textRect = AlignText(self.sliderObj.rect, self.sliderObj.textSurface, self.sliderObj.alignText, self.sliderObj.borderWidth)
						if self.scrollObj != None:
							if pg.mouse.get_rel()[1] < 0:
								self.scrollObj.Scroll(1, 1)
							else:
								self.scrollObj.Scroll(-1, 1)
						else:
							self.GetValue()

	def GetValue(self):
		if not self.isVertical:
			self.value = round(abs(self.sliderObj.rect.x - self.rect.x) / abs(self.sliderObj.rect.w - self.rect.w), 1)
		else:
			self.value = round(abs(self.sliderObj.rect.y - self.rect.y) / abs(self.sliderObj.rect.h - self.rect.h), 1)
		if __name__ == "__main__":
			print(self.value * 10)

	def UpdateRect(self):
		if not self.isVertical:
			self.sliderObj.rect.x = (self.startValue * (self.rect.w - (self.sliderObj.rect.w + self.borderWidth + 1))) + self.rect.x
		else:
			self.sliderObj.rect.y = (self.startValue * (self.rect.h - (self.sliderObj.rect.h + self.borderWidth + 1))) + self.rect.y

	def RemoveFromList(self):
		for l in self.lists:
			if self in l:
				l.remove(self)
			if self.sliderObj in l:
				l.remove(self.sliderObj)

	def Update(self):
		self.Rescale()
		self.drawData = {
			"drawBorder": self.drawBorder,
			"ogBorderWidth": self.ogBorderWidth,
			"isFilled": self.isFilled,
			"roundedEdges": self.roundedEdges,
			"roundedCorners": self.roundedCorners,
			"roundness": self.roundness,
			"activeCorners": self.activeCorners,
			"drawBackground": self.drawBackground,
			"additive": self.additive,
			"moveText": self.moveText,
			"sliderSize": self.sliderSize,
			"isFilled": self.isFilled
		}

		for l in self.lists:
			if self.sliderObj in l:
				l.remove(self.sliderObj)

		if not self.isVertical:
			drawData = self.drawData
			drawData["isFilled"] = True
			if self.roundedCorners:
				self.sliderObj = Button(self.surface, "", (self.ogRect[0] + self.borderWidth + 1, self.ogRect[1] + self.borderWidth + 1, self.sliderSize[0] - (self.borderWidth+1)*2, self.sliderSize[1] - (self.borderWidth+1)*2), self.colors, "", self.fontObj, True, self.textData, self.drawData, self.imageData, self.lists)
			else:
				self.sliderObj = Button(self.surface, "", (self.ogRect[0] + self.borderWidth, self.ogRect[1] + self.borderWidth, self.sliderSize[0] - self.borderWidth*2, self.sliderSize[1] - self.borderWidth*2), self.colors, "", self.fontObj, True, self.textData, self.drawData, self.imageData, self.lists)
		else:
			drawData = self.drawData
			drawData["isFilled"] = True
			if self.roundedCorners:
				self.sliderObj = Button(self.surface, "", (self.ogRect[0] + self.borderWidth + 1, self.ogRect[1] + self.borderWidth + 1, self.sliderSize[0] - (self.borderWidth+1)*2, self.sliderSize[1] - (self.borderWidth+1)*2), self.colors, "", self.fontObj, True, self.textData, self.drawData, self.imageData, self.lists)
			else:
				self.sliderObj = Button(self.surface, "", (self.ogRect[0] + self.borderWidth, self.ogRect[1] + self.borderWidth, self.sliderSize[0] - self.borderWidth*2, self.sliderSize[1] - self.borderWidth*2), self.colors, "", self.fontObj, True, self.textData, self.drawData, self.imageData, self.lists)


class Switch(Button):
	def __init__(self, surface, name, rect, colors, text, font, textData={}, drawData={}, imageData={}, lists=[allSwitchs]):
		self.optionsText = textData.get("optionsText", ["", ""])
		self.optionsFontColor = textData.get("optionsFontColor", [colors[2], colors[1]])
		self.optionsAlignText = textData.get("optionsAlignText", ["center", "center"])
		self.optionsFont = textData.get("optionsFont", (fontName, 8*sf))
		self.optionsFontName = self.optionsFont[0]
		self.ogOptionsFontSize = self.optionsFont[1]
		self.activeOption = self.optionsText[0]
		super().__init__(surface, name, rect, colors, text, font, False, textData, drawData, imageData, lists)
		self.Rescale()

	def HandleEvent(self, event):
		if event.type == pg.MOUSEBUTTONDOWN:
			if event.button == 1:
				if self.rect.collidepoint(pg.mouse.get_pos()):
					self.active = not self.active
					self.SwapColors(True)
					if self.active:
						self.OnClick()
					else:
						self.OnRelease()

		if self.isHoldButton:
			if event.type == pg.MOUSEBUTTONUP:
				if event.button == 1:
					self.active = False
					self.OnRelease()
					self.SwapColors(False)
		else:
			self.SwapColors(self.active)

		if self.active:
			self.activeOption = self.optionsText[1]
		else:
			self.activeOption = self.optionsText[0]

	def Rescale(self):
		self.rect = pg.Rect(self.ogRect.x * sf, self.ogRect.y * sf, self.ogRect.w * sf, self.ogRect.h * sf)
		self.borderWidth = self.ogBorderWidth * sf
		self.fontSize = self.ogFontSize * sf
		try:
			self.font = pg.font.Font(self.fontName, self.fontSize)
		except:
			self.font = pg.font.SysFont(self.fontName, self.fontSize)

		self.textSurface = self.font.render(self.text, True, self.fontColor)
		self.textRect = AlignText(self.rect, self.textSurface, self.alignText, self.borderWidth)

		self.optionsFontSize = self.ogOptionsFontSize * sf
		try:
			self.optionsFont = pg.font.Font(self.optionsFontName, self.optionsFontSize)
		except:
			self.optionsFont = pg.font.SysFont(self.optionsFontName, self.optionsFontSize)

	def Draw(self):
		self.SwapColors(self.active)

		if not self.roundedEdges and not self.roundedCorners:
			pg.draw.rect(self.surface, self.backgroundColor, self.rect)

			if not self.isFilled:
				if self.drawBorder:
					DrawRectOutline(self.surface, self.foregroundColor, self.rect, self.borderWidth)
			else:
				pg.draw.rect(self.surface, self.foregroundColor, self.rect)

			if self.active:
				pg.draw.rect(self.surface, self.foregroundColor, (self.rect.x + self.rect.w // 2, self.rect.y, self.rect.w // 2, self.rect.h))
			else:
				pg.draw.rect(self.surface, self.foregroundColor, (self.rect.x, self.rect.y, self.rect.w // 2, self.rect.h))

		elif self.roundedEdges and not self.roundedCorners:
			DrawObround(self.surface, (self.foregroundColor, self.backgroundColor), self.rect, self.isFilled, self.additive, self.drawBorder)
			radius = self.rect.h // 2
			if self.active:
				DrawObround(self.surface, (self.foregroundColor, self.foregroundColor), (self.rect.x + self.rect.w // 2, self.rect.y, self.rect.w//2, self.rect.h), self.isFilled, self.additive, self.drawBorder)
			else:
				DrawObround(self.surface, (self.foregroundColor, self.foregroundColor), (self.rect.x, self.rect.y, self.rect.w//2, self.rect.h), self.isFilled, self.additive, self.drawBorder)

		else:
			DrawRoundedRect(self.surface, (self.backgroundColor, self.foregroundColor), self.rect, self.roundness, self.borderWidth, self.activeCorners, self.isFilled)
			if self.active:
				DrawRoundedRect(self.surface, (self.foregroundColor, self.foregroundColor), (self.rect.x + self.rect.w // 2, self.rect.y, self.rect.w // 2, self.rect.h), self.roundness, self.borderWidth, self.activeCorners, self.isFilled)
			else:
				DrawRoundedRect(self.surface, (self.foregroundColor, self.foregroundColor), (self.rect.x, self.rect.y, self.rect.w // 2, self.rect.h), self.roundness, self.borderWidth, self.activeCorners, self.isFilled)

		if self.drawText:
			textRect = pg.Rect(self.rect.x + 10*sf, (self.textRect.y - self.textRect.h*1.5) + 5*sf, self.textRect.w-20*sf, self.textRect.h)
			if not self.roundedEdges and not self.roundedCorners:
				pg.draw.rect(self.surface, self.backgroundColor, textRect)
				DrawRectOutline(self.surface, self.foregroundColor, textRect, self.borderWidth)
			elif self.roundedEdges and not self.roundedCorners:
				DrawObround(self.surface, (self.foregroundColor, self.backgroundColor), textRect, self.isFilled, self.additive, self.drawBorder)
			else:
				DrawRoundedRect(self.surface, (self.backgroundColor, self.foregroundColor), textRect, self.roundness, self.borderWidth, self.activeCorners, self.isFilled)

			self.surface.blit(self.textSurface, AlignText(textRect, self.textSurface, self.alignText, self.borderWidth))

			self.surface.blit(self.optionsFont.render(self.optionsText[0], True, self.optionsFontColor[0]), AlignText((self.rect.x, self.rect.y, self.rect.w // 2, self.rect.h), self.optionsFont.render(self.optionsText[1], True, self.optionsFontColor[1]), self.optionsAlignText[0], self.borderWidth))
			self.surface.blit(self.optionsFont.render(self.optionsText[1], True, self.optionsFontColor[1]), AlignText((self.rect.x + self.rect.w // 2, self.rect.y, self.rect.w // 2, self.rect.h), self.optionsFont.render(self.optionsText[0], True, self.optionsFontColor[0]), self.optionsAlignText[1], self.borderWidth))
		self.DrawImage()


class MultiSelectButton(Button):
	def __init__(self, surface, name, rect, colors, text, font, inputData={}, textData={}, drawData={}, imageData={}, lists=[allMultiButtons]):
		super().__init__(surface, name, rect, colors, text, font, False, textData, drawData, imageData, lists)

		self.textData = textData
		self.optionNames = inputData.get("optionNames", [])
		self.numOfOptions = len(self.optionNames)
		self.optionAlignText = inputData.get("optionAlignText", self.alignText)
		self.startActiveOption = inputData.get("activeOption", 0)
		self.optionsSize = inputData.get("optionsSize", None)
		self.relativePos = inputData.get("relativePos", "center")
		self.isScrollable = inputData.get("isScrollable", False)
		self.allowNoSelection = inputData.get("allowNoSelection", False)

		self.activeOption = None
		self.changed = False
		self.options = []
		self.CreateOptions()

	def CreateOptions(self):
		for obj in self.options:
			if obj in allGUIObjects:
				allGUIObjects.remove(obj)
		self.options = []

		if self.optionsSize == None:
			rect = pg.Rect(self.ogRect.x + self.borderWidth + 2, self.ogRect.y + (self.textSurface.get_height() // sf) * 2, self.ogRect.w - (self.borderWidth + 4), (self.textSurface.get_height() // sf))
			self.optionsSize = (self.ogRect.w - (self.borderWidth + 4), (self.textSurface.get_height() // sf))
		else:
			if self.optionsSize[0] == 0:
				self.optionsSize = (self.ogRect.w - (self.borderWidth + 4), self.optionsSize[1])
			if self.optionsSize[1] == 0:
				self.optionsSize = (self.optionsSize[0], (self.textSurface.get_height() // sf))

			if self.relativePos == "left":
				rect = pg.Rect(self.ogRect.x + self.borderWidth + 2, self.ogRect.y + (self.textSurface.get_height() // sf) * 2, self.optionsSize[0] - (self.borderWidth + 4), max(self.optionsSize[1], self.textSurface.get_height() // sf))
			if self.relativePos == "center":
				rect = pg.Rect(self.ogRect.x + self.borderWidth + 2 + self.ogRect.w // 2 - ((self.optionsSize[0] - (self.borderWidth + 4)) // 2), self.ogRect.y + (self.textSurface.get_height() // sf) * 2, self.optionsSize[0] - ((self.borderWidth + 4) * 2), max(self.optionsSize[1], self.textSurface.get_height() // sf))
			if self.relativePos == "right":
				rect = pg.Rect(self.ogRect.x + self.borderWidth + 2 + self.ogRect.w - self.optionsSize[0] - (self.borderWidth + 4), self.ogRect.y + (self.textSurface.get_height() // sf) * 2, self.optionsSize[0] - (self.borderWidth + 4), max(self.optionsSize[1], self.textSurface.get_height() // sf))

		for i in range(self.numOfOptions):
			textData = self.textData
			textData["alignText"] = self.optionAlignText
			Button(self.surface, self.name, rect, (self.backgroundColor, self.inactiveColor, self.activeColor), self.optionNames[i], (self.fontName, self.fontSize//sf, self.fontColor), textData=textData, drawData={"drawBorder": True, "drawBackground": True, "roundedEdges": self.roundedEdges, "roundedCorners": self.roundedCorners, "roundness": self.roundness, "borderWidth": self.borderWidth//sf}, lists=[self.options])
			rect = pg.Rect(rect.x, rect.y + rect.h + 4, rect.w, rect.h)
		self.lowestY = rect.y * sf
		try:
			self.activeOption = self.options[self.startActiveOption]
			self.activeOption.active = True
		except:
			self.activeOption = None

		for option in self.options:
			if option.active:
				self.activeOption = option
				self.activeOption.SwapColors(True)
				self.changed = True

	def Draw(self):
		if not self.roundedEdges and not self.roundedCorners:
			if self.drawBackground:
				pg.draw.rect(self.surface, self.backgroundColor, self.rect)

			if not self.isFilled:
				if self.drawBorder:
					DrawRectOutline(self.surface, self.foregroundColor, self.rect, self.borderWidth)
			else:
				pg.draw.rect(self.surface, self.foregroundColor, self.rect)

		elif self.roundedEdges and not self.roundedCorners:
			DrawObround(self.surface, (self.foregroundColor, self.backgroundColor), self.rect, self.isFilled, self.additive, self.drawBorder, self.borderWidth)
		else:
			DrawRoundedRect(self.surface, (self.backgroundColor, self.foregroundColor), self.rect, self.roundness, self.borderWidth, self.activeCorners, self.isFilled)

		if self.drawText:
			self.surface.blit(self.textSurface, self.textRect)

		for option in self.options:
			if self.isScrollable:
				if pg.Rect(self.rect.x, self.rect.y + self.textSurface.get_height() + self.borderWidth, self.rect.w, self.rect.h - self.textSurface.get_height() + self.borderWidth).contains(option.rect):
					option.Draw()
			else:
				option.Draw()

		self.DrawImage()

	def HandleEvent(self, event):
		if self.isScrollable:
			if event.type == pg.MOUSEBUTTONDOWN:
				if self.rect.collidepoint(pg.mouse.get_pos()):
					# up
					if event.button == 4:
						self.Scroll(1)
					# down
					if event.button == 5:
						self.Scroll(-1)

		active = False
		if event.type == pg.MOUSEBUTTONDOWN:
			if event.button == 1:
				for option in self.options:
					if option.rect.collidepoint(pg.mouse.get_pos()):
						active = True
						option.SwapColors(True)
						if self.allowNoSelection:
							optionPressed = False
							for option in self.options:
								if option.rect.collidepoint(pg.mouse.get_pos()) and option.active:
									optionPressed = True
							if optionPressed:
								for option in self.options:
									option.active = False
									option.SwapColors(False)
									self.activeOption = None
								return

				if active:
					for option in self.options:
						option.active = False
						option.SwapColors(False)

				for option in self.options:
					option.HandleEvent(event)
					if option.active:
						self.activeOption = option
						self.activeOption.SwapColors(True)
						self.changed = True

	def Scroll(self, direction, scrollAmount=0):
		if scrollAmount == 0:
			try:
				scrollAmount = self.options[0].rect.h + 4 * sf
			except:
				scrollAmount = 0

		for option in self.options:
			# scroll up
			if direction == 1:
				if self.options[0].rect.y + scrollAmount * direction <= (self.rect.y + self.textSurface.get_height() * 2):
					if self.options.index(option) != 0:
						option.rect.y += scrollAmount * direction
			# scroll down
			else:
				if self.options[-1].rect.y + scrollAmount * direction >= self.rect.y + self.rect.h + (scrollAmount * direction) - self.options[0].rect.h:
					option.rect.y += scrollAmount * direction

		if direction == 1:
			if self.options[0].rect.y + scrollAmount * direction <= (self.rect.y + self.textSurface.get_height() * 2):
				self.options[0].rect.y += scrollAmount * direction

		for option in self.options:
			option.UpdateTextRect()

	def RemoveOption(self, optionName):
		for option in self.options:
			if option.text == optionName:
				self.optionNames.remove(option.text)

				self.options.remove(option)
				self.numOfOptions -= 1

				self.CreateOptions()
				break


class DropDownMenu(MultiSelectButton):
	def __init__(self, surface, name, rect, colors, text, font, inputData={}, textData={}, drawData={}, imageData={}, lists=[allDropDowns]):
		self.expandUpwards = drawData.get("expandUpwards", False)
		self.inputIsHoldButton = inputData.get("inputIsHoldButton", False)
		self.inactiveSize = drawData.get("inactiveY", 5)
		super().__init__(surface, name, rect, colors, text, font, inputData, textData, drawData, imageData, lists)

	def CreateOptions(self):
		for obj in self.options:
			if obj in allGUIObjects:
				allGUIObjects.remove(obj)

		self.options = []

		if self.optionsSize == None:
			self.optionsSize = [self.ogRect.w, self.textSurface.get_height()//2]
		else:
			if self.optionsSize[0] == 0:
				self.optionsSize = [self.ogRect.w, self.optionsSize[1]]
			if self.optionsSize[1] == 0:
				self.optionsSize = [self.optionsSize[0], self.textSurface.get_height()//2]

		if not self.expandUpwards:
			rect = pg.Rect(self.ogRect.x + 3 * sf, self.ogRect.y + 2 * sf, self.optionsSize[0] - round(1.5 * sf), self.optionsSize[1])
			for i in range(self.numOfOptions):
				rect = pg.Rect(rect.x, rect.y + rect.h + 1 * sf, rect.w, rect.h)
				Button(self.surface, self.name, rect, (self.backgroundColor, self.inactiveColor, self.activeColor), self.optionNames[i], (self.fontName, self.fontSize // sf, self.fontColor), isHoldButton=self.inputIsHoldButton, textData={"alignText": "center"}, drawData={"drawBorder": True, "drawBackground": True, "roundedEdges": self.roundedEdges, "roundedCorners": self.roundedCorners, "roundness": self.roundness, "borderWidth": self.borderWidth / sf}, lists=[self.options])
		else:
			rect = pg.Rect(self.ogRect.x + 3 * sf, self.ogRect.y, self.optionsSize[0] - 6 * sf, self.optionsSize[1])
			for i in range(1, self.numOfOptions + 1):
				rect = pg.Rect(rect.x, rect.y - (rect.h + 1 * sf), rect.w, rect.h)
				Button(self.surface, self.name, rect, (self.backgroundColor, self.inactiveColor, self.activeColor), self.optionNames[-i], (self.fontName, self.fontSize // sf, self.fontColor), isHoldButton=self.inputIsHoldButton, textData={"alignText": "center"}, drawData={"drawBorder": True, "drawBackground": True, "roundedEdges": self.roundedEdges, "roundedCorners": self.roundedCorners, "roundness": self.roundness, "borderWidth": self.borderWidth / sf}, lists=[self.options])
		if len(self.options) != 0:
			if not self.allowNoSelection:
				if self.expandUpwards:
					self.activeOption = self.options[-1]
				else:
					self.activeOption = self.options[0]
				self.activeOption.active = True
		self.lowestY = rect.y * sf

	def HandleEvent(self, event):
		activeOptions = []
		active = False
		if event.type == pg.MOUSEBUTTONDOWN:
			if event.button == 1:
				if self.active:
					for option in self.options:
						if option.rect.collidepoint(pg.mouse.get_pos()):
							active = True
							option.SwapColors(True)
							break
				if active:
					for option in self.options:
						option.active = False
						option.SwapColors(False)
				else:
					if self.rect.collidepoint(pg.mouse.get_pos()):
						if pg.Rect(pg.Rect(self.ogRect.x * sf, self.ogRect.y * sf, self.rect.w, self.textSurface.get_height() + self.inactiveSize * sf)).collidepoint(pg.mouse.get_pos()):
							self.active = not self.active

						if self.active:
							self.OnClick()
						else:
							self.OnRelease()

					if self.isHoldButton:
						if event.type == pg.MOUSEBUTTONUP:
							if event.button == 1:
								self.active = False
								self.OnRelease()

		if self.active:
			for option in self.options:
				option.HandleEvent(event)
				if option.active:
					self.activeOption = option
					option.SwapColors(True)
					break
				else:
					self.activeOption = None
					option.SwapColors(False)

	def Draw(self):
		if not self.roundedEdges and not self.roundedCorners:
			pg.draw.rect(self.surface, self.backgroundColor, self.rect)

			if not self.isFilled:
				if self.drawBorder:
					DrawRectOutline(self.surface, self.foregroundColor, self.rect, self.borderWidth)
			else:
				pg.draw.rect(self.surface, self.foregroundColor, self.rect)

		elif self.roundedEdges and not self.roundedCorners:
			DrawObround(self.surface, (self.foregroundColor, self.backgroundColor), self.rect, self.isFilled, self.additive, self.drawBorder, self.borderWidth)
		else:
			DrawRoundedRect(self.surface, (self.backgroundColor, self.foregroundColor), self.rect, self.roundness, self.borderWidth, self.activeCorners, self.isFilled)

		if self.drawText:
			self.surface.blit(self.textSurface, (self.textRect.x, self.textRect.y + 1 * sf))

		if self.active:
			if self.expandUpwards:
				self.rect.h = self.ogRect.h * sf
				self.rect.y = (self.ogRect.y * sf) - self.rect.h + self.textSurface.get_height() + self.inactiveSize * sf

			else:
				self.rect.h = self.ogRect.h * sf

			for option in self.options:
				option.Draw()
		else:
			if self.expandUpwards:
				self.rect.y = self.ogRect.y * sf
			self.rect.h = self.textSurface.get_height() + self.inactiveSize * sf
		self.DrawImage()


class MessageBox(Label):
	def __init__(self, surface, name, rect, colors, title, text, font, textData={}, drawData={}, imageData={}, inputData={}, lists=[allMessageBoxs]):
		super().__init__(surface, name, rect, colors, title, font, textData, drawData, imageData, lists)

		drawData = inputData["messageDraw"]
		textData = inputData["messageText"]
		self.message = Label(surface, name, ((self.rect.x // sf) + 5, (self.rect.y // sf) + self.textSurface.get_height(), (self.rect.w // sf) - 10, (self.rect.h // sf) - self.textSurface.get_height() - 30), colors, text, font, textData, drawData, imageData, lists=[])

		drawData = inputData["confirmDraw"]
		textData = inputData["confirmText"]
		self.confirmButton = Button(surface, name + "-Confirm", ((self.rect.x // sf) + (self.rect.w // sf) - 65, (self.rect.y // sf) + (self.rect.h // sf) - 25, 60, 20), colors, "Confirm", font, True, textData, drawData, imageData, lists=[])

		drawData = inputData["cancelDraw"]
		textData = inputData["cancelText"]
		self.cancelButton = Button(surface, name + "-Cancel", ((self.rect.x // sf) + (self.rect.w // sf) - 130, (self.rect.y // sf) + (self.rect.h // sf) - 25, 60, 20), colors, "Cancel", font, True, textData, drawData, imageData, lists=[])

	def HandleEvent(self, event):
		self.message.HandleEvent(event)
		self.confirmButton.HandleEvent(event)
		self.cancelButton.HandleEvent(event)

	def Draw(self):
		if not self.roundedEdges and not self.roundedCorners:
			pg.draw.rect(self.surface, self.backgroundColor, self.rect)

			if not self.isFilled:
				if self.drawBorder:
					DrawRectOutline(self.surface, self.foregroundColor, self.rect, self.borderWidth)
			else:
				pg.draw.rect(self.surface, self.foregroundColor, self.rect)

		elif self.roundedEdges and not self.roundedCorners:
			DrawObround(self.surface, (self.foregroundColor, self.backgroundColor), self.rect, self.isFilled, self.additive, self.drawBorder, self.borderWidth)
		else:
			DrawRoundedRect(self.surface, (self.backgroundColor, self.foregroundColor), self.rect, self.roundness, self.borderWidth, self.activeCorners, self.isFilled)

		if not self.multiline:
			if self.drawText:
				self.surface.blit(self.textSurface, self.textRect)
		else:
			self.GetTextObjects()
			if self.drawText:
				for textObj in self.textObjs:
					if textObj[1].y >= self.rect.y and textObj[1].y + textObj[0].get_height() <= self.rect.y + self.rect.h:
						self.surface.blit(textObj[0], textObj[1])
		self.DrawImage()

		self.message.Draw()
		self.confirmButton.Draw()
		self.cancelButton.Draw()


def DrawGui():
	hoverInput = False
	for obj in allGUIObjects:
		if gameState in obj.activeSurface or obj.activeSurface == "all":
			if type(obj) == TextInputBox:
				if obj.rect.collidepoint(pg.mouse.get_pos()):
					pg.mouse.set_system_cursor(pg.SYSTEM_CURSOR_IBEAM)
					hoverInput = True

				if hoverInput:
					break

	if not hoverInput:
		pg.mouse.set_system_cursor(pg.SYSTEM_CURSOR_ARROW)

	for box in allBoxs:
		if gameState in box.activeSurface or box.activeSurface == "all":
			box.Draw()

	for imageFrame in allImageFrames:
		if gameState in imageFrame.activeSurface or imageFrame.activeSurface == "all":
			imageFrame.Draw()

	for label in allLabels:
		if gameState in label.activeSurface or label.activeSurface == "all":
			label.Draw()

	for button in allButtons:
		if gameState in button.activeSurface or button.activeSurface == "all":
			button.Draw()

	for textInputBox in allTextBoxs:
		if gameState in textInputBox.activeSurface or textInputBox.activeSurface == "all":
			textInputBox.Draw()

	for slider in allSliders:
		if gameState in slider.activeSurface or slider.activeSurface == "all":
			slider.Draw()

	for scrollBar in allScrollbars:
		if gameState in scrollBar.activeSurface or scrollBar.activeSurface == "all":
			scrollBar.Draw()

	for switch in allSwitchs:
		if gameState in switch.activeSurface or switch.activeSurface == "all":
			switch.Draw()

	for button in allMultiButtons:
		if gameState in button.activeSurface or button.activeSurface == "all":
			button.Draw()

	for dropDown in allDropDowns:
		if gameState in dropDown.activeSurface or dropDown.activeSurface == "all":
			dropDown.Draw()

	for messageBox in allMessageBoxs:
		if gameState in messageBox.activeSurface or messageBox.activeSurface == "all":
			messageBox.Draw()


def HandleGUI(event):
	for label in allLabels:
		if gameState in label.activeSurface or label.activeSurface == "all":
			label.HandleEvent(event)

	for button in allButtons:
		if gameState in button.activeSurface or button.activeSurface == "all":
			button.HandleEvent(event)

	for textInputBox in allTextBoxs:
		if gameState in textInputBox.activeSurface or textInputBox.activeSurface == "all":
			textInputBox.HandleEvent(event)

	for slider in allSliders:
		if gameState in slider.activeSurface or slider.activeSurface == "all":
			slider.HandleEvent(event)

	for scrollBar in allScrollbars:
		if gameState in scrollBar.activeSurface or scrollBar.activeSurface == "all":
			scrollBar.HandleEvent(event)

	for switch in allSwitchs:
		if gameState in switch.activeSurface or switch.activeSurface == "all":
			switch.HandleEvent(event)

	for button in allMultiButtons:
		if gameState in button.activeSurface or button.activeSurface == "all":
			button.HandleEvent(event)

	for dropDown in allDropDowns:
		if gameState in dropDown.activeSurface or dropDown.activeSurface == "all":
			dropDown.HandleEvent(event)

	for messageBox in allMessageBoxs:
		if gameState in messageBox.activeSurface or messageBox.activeSurface == "all":
			messageBox.HandleEvent(event)


def ButtonPress():
	for buttonData in activeButtons:
		if buttonData[0].name == "rescaleButton" and buttonData[1] == False:
			Rescale(ChangeSf())
			activeButtons[activeButtons.index(buttonData)] = (buttonData[0], True)
			buttonData[0].OnRelease()


if __name__ == "__main__":
	Rescale(sf)
	gameState = "Load character menu"
	options = []
	for i in range(0, 50):
		options.append(str(i))

	def DrawLoop():
		screen.fill(darkGray)
		DrawGui()
		pg.display.update()

	def CreateAllObjects():
		Box(screen, "boxDemo", (10, 10, 40, 40), (lightBlack, darkWhite), drawData={"roundedCorners": True, "roundness": 15, "borderWidth": 2})
		ImageFrame(screen, "imageFrameDemo", (60, 10, 40, 40), (lightBlack, darkWhite), drawData={"borderWidth": 2}, imageData={"filePath": "imageDemo.jpg", "size": (40, 40)})
		Label(screen, "labelDemo", (110, 10, 40, 40), (lightBlack, darkWhite), "Label\ndemo", ("arial", 10, white), drawData={"borderWidth": 2}, textData={"alignText": "center-top", "multiline": True})
		TextInputBox(screen, "texInputBoxDemo", (160, 10, 100, 20), (lightBlack, gray, white), ("arial", 10, white), drawData={"borderWidth": 2, "replaceSplashText": False}, textData={"alignText": "left"}, inputData={"charLimit": 11, "splashText": "PIN: "})
		Button(screen, "buttonDemo", (270, 10, 40, 40), (lightBlack, gray, white), "Button", ("arial", 10, white), drawData={"borderWidth": 2, "roundedCorners": True, "roundness": 15})
		Slider(screen, "sliderDemo", (320, 10, 150, 40), (lightBlack, gray, white), "", ("arial", 10, white), drawData={"borderWidth": 2, "roundedCorners": True, "roundness": 10, "moveText": True, "sliderSize": (50, 38)})
		Switch(screen, "switchDemo", (480, 50, 130, 40), (lightBlack, darkWhite, darkWhite), "Switch", ("arial", 10, white), drawData={"borderWidth": 2, "roundedCorners": True, "roundness": 15}, textData={"optionsText": ["option 1", "option 2"], "optionsFont": ("arial", 10), "optionsFontColor": [lightRed, lightBlue]})
		MultiSelectButton(screen, "MultiSelectButtonDemo", (10, 60, 80, 100), (lightBlack, darkWhite, lightRed), "MultiSelectButton", ("arial", 10, white), drawData={"borderWidth": 2, "roundedCorners": True, "roundness": 12}, textData={"alignText": "center-top"}, inputData={"optionNames": ["option 1", "option 2", "option 3"], "optionsSize": (80, 20)})
		DropDownMenu(screen, "dropDownMenuDemo", (110, 60, 80, 100), (lightBlack, darkWhite, lightRed), "DropDownMenu", ("arial", 10, white), drawData={"borderWidth": 2, "roundedCorners": True, "roundness": 12, "inactiveY": 15}, textData={"alignText": "center-top"}, inputData={"optionNames": ["option 1", "option 2", "option 3"], "optionsSize": (70, 20)})
		MessageBox(screen, "messageDemo", (200, 100, 200, 90), (lightBlack, darkWhite, lightRed), "Message title", "Message demo text", ("arial", 10, white), drawData={"borderWidth": 2}, textData={"alignText": "center-top"}, inputData={"messageDraw": {"borderWidth": 1}, "messageText": {"alignText": "center-top"}, "confirmDraw": {"borderWidth": 1}, "confirmText": {"alignText": "center-top"}, "cancelDraw": {"borderWidth": 1}, "cancelText": {"alignText": "center-top"}})

	CreateAllObjects()

	while running:
		for event in pg.event.get():
			if event.type == pg.QUIT:
				running = False
			if event.type == pg.KEYDOWN:
				if event.key == pg.K_ESCAPE:
					running = False

				if pg.key.get_pressed()[pg.K_1] and pg.key.get_pressed()[pg.K_LCTRL]:
					Rescale(1)
				if pg.key.get_pressed()[pg.K_2] and pg.key.get_pressed()[pg.K_LCTRL]:
					Rescale(2)
				if pg.key.get_pressed()[pg.K_3] and pg.key.get_pressed()[pg.K_LCTRL]:
					Rescale(3)

			HandleGUI(event)

		ButtonPress()
		DrawLoop()
