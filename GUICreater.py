import sys
sys.path.insert(1, '/Python Projects/GuiObjects')

from GUIObjects import *

import json

savePath = "saves/"

propertiesMenus = []
objectMenus = []
activeProperty = None

allObjects = []
saveObjs = {}

cam = None
inspectMode = False

width, height = 640, 360
sf = 2
screen = pg.display.set_mode((width * sf, height * sf))


objectShortcuts = {
	pg.K_1: "Box",
	pg.K_2: "ImageFrame",
	pg.K_3: "Label",
	pg.K_4: "TextInputBox",
	pg.K_5: "Button",
	pg.K_6: "Slider",

	pg.K_KP1: "Box",
	pg.K_KP2: "ImageFrame",
	pg.K_KP3: "Label",
	pg.K_KP4: "TextInputBox",
	pg.K_KP5: "Button",
	pg.K_KP6: "Slider",
}

objectShortcutDisplay = {
	"Box": "1",
	"ImageFrame": "2",
	"Label": "3",
	"TextInputBox": "4",
	"Button": "5",
	"Slider": "6",
	"Switch": "7",
	"MultiSelctButton": "8",
	"DropDownMenu": "9"
}


class Properties(DropDownMenu):
	def __init__(self, surface, name, rect, colors, text, font, inputData={}, textData={}, drawData={}, imageData={}, lists=[propertiesMenus]):
		super().__init__(surface, name, rect, colors, text, font, inputData, textData, drawData, imageData, lists)
		self.attributes = []
		self.parentObject = inputData.get("parentObject")
		self.objType = name

		for i, attribute in enumerate(inputData.get("attributes", [])):
			height = self.textSurface.get_height()//1.5
			if not self.expandUpwards:
				attributeRect = pg.Rect(self.rect.x + 3*sf, (self.rect.y + 2*sf) + (((height * sf) + 1*sf) * (i+1)) , self.rect.w - 6*sf, height*sf)
			else:
				attributeRect = pg.Rect(self.rect.x + 3*sf, self.rect.y - (((height * sf) + 1*sf) * (i+1)), self.rect.w - 6*sf, height*sf)
			attribute.surface = self.surface
			attribute.rect = attributeRect
			attribute.parentObject = self.parentObject
			attribute.parent = self
			attribute.CreateObject()
			attribute.UpdateRects()

			self.attributes.append(attribute)

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
			DrawRoundedRect(self.surface, (self.backgroundColor, self.foregroundColor), self.rect, self.roundness, self.borderWidth, self.corners, self.isFilled)

		if self.drawText:
			self.surface.blit(self.textSurface, (self.textRect.x, self.textRect.y + 1 * sf))

		if self.active:
			if self.expandUpwards:
				self.rect.h = self.ogRect.h * sf
				self.rect.y = (self.ogRect.y * sf) - self.rect.h + self.textSurface.get_height() + self.inactiveSize * sf
			else:
				self.rect.h = self.ogRect.h * sf

			for attribute in self.attributes:
				attribute.Draw()
		else:
			if self.expandUpwards:
				self.rect.y = self.ogRect.y * sf
			self.rect.h = self.textSurface.get_height() + self.inactiveSize * sf
		self.DrawImage()

	def HandleEvent(self, event):
		for attribute in self.attributes:
			if attribute.rect.y > self.textSurface.get_height() + self.inactiveSize * sf:
				attribute.HandleEvent(event)

		if self.isScrollable:
			if event.type == pg.MOUSEBUTTONDOWN:
				if self.rect.collidepoint(pg.mouse.get_pos()):
					if self.active:
						# up
						if event.button == 4:
							self.Scroll(1)
						# down
						if event.button == 5:
							self.Scroll(-1)

		activeOptions = []
		active = False
		if event.type == pg.MOUSEBUTTONDOWN:
			if event.button == 1:
				if pg.Rect(self.rect.x, self.rect.y, self.rect.w, self.textSurface.get_height() + self.inactiveSize*sf).collidepoint(pg.mouse.get_pos()):
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

		self.name = self.parentObject.name
		if self.parentObject.name != "":
			self.text = f"{self.parentObject.name} - Properties"
			self.UpdateTextRect()
		else:
			self.text = f"{self.objType} - Properties"
			self.UpdateTextRect()

	def Scroll(self, direction, scrollAmount=0):
		if scrollAmount == 0:
			scrollAmount = self.attributes[0].rect.h + 1*sf

		for attribute in self.attributes:
			# scroll up
			if direction == 1:
				if self.attributes[0].rect.y + scrollAmount * direction <= (self.rect.y + self.textSurface.get_height()//1.5 * 2*sf):
					if self.attributes.index(attribute) != 0:
						attribute.rect.y += scrollAmount * direction
			# scroll down
			else:
				if self.attributes[-1].rect.y + scrollAmount * direction >= self.rect.y + self.rect.h + (scrollAmount * direction) - (self.textSurface.get_height()//1.5 * 1*sf):
					attribute.rect.y += scrollAmount * direction

		if direction == 1:
			if self.attributes[0].rect.y + scrollAmount * direction <= (self.rect.y + self.textSurface.get_height()//1.5 * 2*sf):
				self.attributes[0].rect.y += scrollAmount * direction

		for attribute in self.attributes:
			attribute.UpdateRects()


class Attribute:
	def __init__(self, name, text, inputType, textColor, colors, textData={}, inputData={}, lists=[]):
		self.name = name
		self.text = text
		self.inputType = inputType
		self.textColor = textColor
		self.backgroundColor = colors[0]
		self.foregroundColor = colors[1]
		self.inputColor = colors[2]

		self.alignText = textData.get("alignText", "center-center")
		self.fontName = textData.get("fontName", "arial")
		self.fontSize = textData.get("fontSize", 12) * sf

		self.textData = textData
		self.inputData = inputData

		self.font = pg.font.SysFont(self.fontName, self.fontSize)
		self.textSurface = self.font.render(self.text, True, self.textColor)

		for l in lists:
			l.append(self)

	def CreateObject(self):
		self.objectRect = pg.Rect(self.rect.x, self.rect.y+2*sf, self.rect.w, self.rect.h - 4*sf)

		if self.inputType == "TextBox":
			self.objectRect.x += self.textSurface.get_width() + 10*sf
			self.objectRect.w -= self.textSurface.get_width() + 12*sf

			self.textBox = TextInputBox(self.surface, self.name, pg.Rect(self.objectRect.x//sf, self.objectRect.y//sf, self.objectRect.w//sf, self.objectRect.h//sf), (self.backgroundColor, self.foregroundColor, self.inputColor), (self.fontName, self.fontSize//sf, self.textColor), self.inputData, self.textData, {}, lists=[])

			if "pos" in self.name:
				if self.name.split("-")[1] == "X":
					self.textBox.text = str(self.parentObject.rect.x // sf)
				if self.name.split("-")[1] == "Y":
					self.textBox.text = str(self.parentObject.rect.y // sf)
				if self.name.split("-")[1] == "W":
					self.textBox.text = str(self.parentObject.rect.w // sf)
				if self.name.split("-")[1] == "H":
					self.textBox.text = str(self.parentObject.rect.h // sf)

			elif "Color" in self.name:
				if self.name.split("-")[0] in self.parentObject.__dict__:
					if self.name.split("-")[1] == "R":
						self.textBox.text = str(getattr(self.parentObject, self.name.split("-")[0])[0])
					if self.name.split("-")[1] == "G":
						self.textBox.text = str(getattr(self.parentObject, self.name.split("-")[0])[1])
					if self.name.split("-")[1] == "B":
						self.textBox.text = str(getattr(self.parentObject, self.name.split("-")[0])[2])

			else:
				if "drawData" in self.name or "textData" in self.name or "imageData" in self.name:
					if self.name.split("-")[1] == "ogSize":
						if self.name.split("-")[2] == "W":
							self.textBox.text = str(getattr(self.parentObject, self.name.split("-")[1])[0])
						elif self.name.split("-")[2] == "H":
							self.textBox.text = str(getattr(self.parentObject, self.name.split("-")[1])[1])
					else:
						self.textBox.text = str(getattr(self.parentObject, self.name.split("-")[1]))
				else:
					if "sliderSize" in self.name:
						if self.name.split("-")[1] == "W":
							self.textBox.text = str(getattr(self.parentObject, self.name.split("-")[0])[0])
						if self.name.split("-")[1] == "H":
							self.textBox.text = str(getattr(self.parentObject, self.name.split("-")[0])[1])
					else:
						self.textBox.text = str(getattr(self.parentObject, self.name))

		elif self.inputType == "CheckBox":
			self.checkBox = Button(self.surface, self.name, pg.Rect(self.objectRect.x//sf, self.objectRect.y//sf, self.objectRect.w//sf, self.objectRect.h//sf), (self.backgroundColor, self.foregroundColor, self.inputColor), self.text, (self.fontName, self.fontSize//sf, self.textColor), False, self.textData, {}, inputData=self.inputData, lists=[])

	def UpdateRects(self):
		self.objectRect = pg.Rect(self.rect.x, self.rect.y+2*sf, self.rect.w, self.rect.h - 4*sf)

		if self.inputType == "TextBox":
			self.objectRect.x += self.textSurface.get_width() + 10*sf
			self.objectRect.w -= self.textSurface.get_width() + 12*sf
			self.textBox.rect = self.objectRect
		elif self.inputType == "CheckBox":
			self.objectRect.x += 2*sf
			self.objectRect.w -= 4*sf
			self.checkBox.rect = self.objectRect

	def Draw(self):
		if pg.Rect(self.parent.rect.x, self.parent.rect.y + self.parent.textSurface.get_height() + self.parent.borderWidth, self.parent.rect.w, self.parent.rect.h - self.parent.textSurface.get_height() + self.parent.borderWidth).contains(self.rect):
			pg.draw.rect(self.surface, self.backgroundColor, self.rect)
			DrawRectOutline(self.surface, self.foregroundColor, self.rect, 1*sf)

			if self.inputType == "TextBox":
				self.textBox.Draw()
			elif self.inputType == "CheckBox":
				self.checkBox.Draw()

			self.surface.blit(self.textSurface, AlignText(self.rect, self.textSurface, self.alignText))

	def HandleEvent(self, event):
		global activeProperty
		isNum = False
		if self.name == "update":
			if self.checkBox.active:
				self.checkBox.active = False
				try:
					self.parentObject.Update()
				except AttributeError:
					return
				return

		if self.inputType == "TextBox":
			self.textBox.HandleEvent(event)
			if self.textBox.text != "":
				try:
					value = int(self.textBox.text)
					isNum = True
				except ValueError:
					pass
			else:
				value = self.textBox.text

			if isNum:
				if "pos" in self.name:
					for diff in cam.differences:
						if diff[2] == self.parentObject:
							index = cam.differences.index(diff)

					if self.name.split("-")[1] == "X":
						rect = getattr(self.parentObject, "ogRect")
						rect = pg.Rect((cam.rect.x//sf) + value, rect.y, rect.w, rect.h)
						setattr(self.parentObject, "ogRect", rect)
					if self.name.split("-")[1] == "Y":
						rect = getattr(self.parentObject, "ogRect")
						rect = pg.Rect(rect.x, (cam.rect.y//sf) + value, rect.w, rect.h)
						setattr(self.parentObject, "ogRect", rect)
					if self.name.split("-")[1] == "W":
						rect = getattr(self.parentObject, "ogRect")
						rect = pg.Rect(rect.x, rect.y, value, rect.h)
						setattr(self.parentObject, "ogRect", rect)
					if self.name.split("-")[1] == "H":
						rect = getattr(self.parentObject, "ogRect")
						rect = pg.Rect(rect.x, rect.y, rect.w, value)
						setattr(self.parentObject, "ogRect", rect)

			if self.textBox.active:
				if isNum:
					if self.name in self.parentObject.__dict__:
						if value != "":
							setattr(self.parentObject, self.name, int(value))
							try:
								if self.name == "text":
									self.parentObject.Rescale()
									self.parentObject.GetTextObjects()
							except TypeError:
								pass
					else:
						if "Color" in self.name:
							if self.name.split("-")[0] in self.parentObject.__dict__:
								if self.name.split("-")[1] == "R":
									color = getattr(self.parentObject, self.name.split("-")[0])
									color = (max(min(value, 255), 0), color[1], color[2])
									setattr(self.parentObject, self.name.split("-")[0], color)
								if self.name.split("-")[1] == "G":
									color = getattr(self.parentObject, self.name.split("-")[0])
									color = (color[0], max(min(value, 255), 0), color[2])
									setattr(self.parentObject, self.name.split("-")[0], color)
								if self.name.split("-")[1] == "B":
									color = getattr(self.parentObject, self.name.split("-")[0])
									color = (color[0], color[1], max(min(value, 255), 0))
									setattr(self.parentObject, self.name.split("-")[0], color)

						elif "drawData" in self.name or "textData" in self.name or "imageData" in self.name:
							if self.name.split("-")[1] in self.parentObject.__dict__:
								if self.name.split("-")[0] == "imageData":
									if self.name.split("-")[1] == "ogSize":
										if self.name.split("-")[2] == "W":
											setattr(self.parentObject, self.name.split("-")[1], value)
										elif self.name.split("-")[2] == "H":
											setattr(self.parentObject, self.name.split("-")[1], value)
									else:
										setattr(self.parentObject, self.name.split("-")[1], value)
								else:
									setattr(self.parentObject, self.name.split("-")[1], value)

					try:
						self.parentObject.UpdateTextRect()
					except AttributeError:
						pass

					try:
						self.parentObject.Rescale()
					except TypeError:
						pass
				else:
					value = self.textBox.text

					if self.name in self.parentObject.__dict__:
						setattr(self.parentObject, self.name, str(value))
						if self.name == "text":
							self.parentObject.Rescale()
							self.parentObject.GetTextObjects()

						if self.name == "name":
							setattr(self.parentObject, self.name, str(value))
							self.parentObject.Rescale()
							try:
								self.parentObject.GetTextObjects()
							except AttributeError:
								pass

		elif self.inputType == "CheckBox":
			self.checkBox.HandleEvent(event)
			value = self.checkBox.active

			if self.name == "delObject":
				if value:
					DestroyAttribute(self)

			elif "drawData" in self.name or "textData" in self.name or "imageData" in self.name:
				if self.name.split("-")[1] in self.parentObject.__dict__:
					if self.name.split("-")[0] == "imageData":
						if self.name.split("-")[1] == "ogSize":
							if self.name.split("-")[2] == "W":
								setattr(self.parentObject, self.name.split("-")[1], value)
							elif self.name.split("-")[2] == "H":
								setattr(self.parentObject, self.name.split("-")[1], value)
						else:
							setattr(self.parentObject, self.name.split("-")[1], value)
					else:
						if self.name.split("-")[1] != "activeCorners":
							setattr(self.parentObject, self.name.split("-")[1], value)
						else:
							corners = getattr(self.parentObject, self.name.split("-")[1])
							corners[self.name.split("-")[2]] = value
							setattr(self.parentObject, self.name.split("-")[1], corners)

			else:
				if self.name in self.parentObject.__dict__:
					setattr(self.parentObject, self.name, value)


class Camera(Box):
	def __init__(self, surface, name, rect, colors, drawData={}, lists=[]):
		self.moving = False
		self.gotStartPos = False
		self.canMove = False
		self.zoomAmount = 1
		self.zoomIncrease = 0.1
		self.zoomMax = 5
		self.zoomMin = 1
		self.ogForegroundColor = colors[1]
		self.colors = colors
		super().__init__(surface, name, rect, colors, drawData, lists)

		self.differences = []
		self.CreateDifferences()

	def CreateDifferences(self):
		self.differences = []
		for obj in allObjects:
			self.differences.append((obj.rect.x - self.rect.x, obj.rect.y - self.rect.y, obj))

	def HandleEvent(self, event):
		if event.type == pg.KEYDOWN:
			if event.mod and event.key == pg.K_LCTRL:
				self.canMove = True

		if self.canMove:
			if event.type == pg.MOUSEBUTTONDOWN:
				if event.button == 1:
					if self.rect.collidepoint(pg.mouse.get_pos()):
						self.moving = True
						self.CreateDifferences()
					else:
						self.moving = False

		if event.type == pg.MOUSEBUTTONUP:
			if event.button == 1:
				self.moving = False

		if event.type == pg.KEYUP:
			if event.mod and pg.K_LCTRL:
				self.canMove = False
				self.moving = False

	def Update(self):
		if self.moving:
			self.Move()
			for diff in self.differences:
				if diff[2] in allObjects:
					allObjects[allObjects.index(diff[2])].rect = pg.Rect(diff[0] + self.rect.x, diff[1] + self.rect.y, diff[2].rect.w, diff[2].rect.h)
					try:
						diff[2].UpdateTextRect()
					except AttributeError:
						pass
		else:
			self.gotStartPos = False

	def Move(self):
		if not self.gotStartPos:
			self.startPos = pg.mouse.get_pos()
			self.startRect = self.rect
			self.gotStartPos = True

		if self.gotStartPos:
			self.rect = MoveRectWithoutCenter(self.startPos, self.startRect)

	def SwitchColors(self):
		if self.backgroundColor == self.colors[0]:
			self.backgroundColor = self.colors[1]
			self.foregroundColor = self.colors[0]
		else:
			self.backgroundColor = self.colors[0]
			self.foregroundColor = self.colors[1]


def DestroyAttribute(attribute):
	global activeProperty
	if type(attribute.parentObject).__name__ == "Slider":
		attribute.parentObject.RemoveFromList()
	for l in attribute.parentObject.lists:
		if attribute.parentObject in l:
			l.remove(attribute.parentObject)
	propertiesMenus.remove(attribute.parent)
	activeProperty = None


def CreateObject(objType):
	rect = pg.Rect((cam.rect.x//sf + (cam.rect.w//sf)//2) - 60, (cam.rect.y//sf + (cam.rect.h//sf)//2) - 15, 120, 30)
	for obj in allObjects:
		if rect.colliderect(pg.Rect(obj.rect.x // sf, obj.rect.y // sf, obj.rect.w // sf, obj.rect.h // sf)):
			rect.y += rect.h

	if objType == "Box":
		obj = Box(screen, "", rect, (lightBlack, darkWhite, lightRed), lists=[allObjects, allBoxs])
	elif objType == "ImageFrame":
		obj = ImageFrame(screen, "", rect, (lightBlack, darkWhite, lightRed), lists=[allObjects, allImageFrames])
	elif objType == "Label":
		obj = Label(screen, "", rect, (lightBlack, darkWhite, lightRed), "Label", (fontName, fontSize, white), lists=[allObjects, allLabels])
	elif objType == "TextInputBox":
		obj = TextInputBox(screen, "", rect, (lightBlack, darkWhite, lightRed), (fontName, fontSize, white), lists=[allObjects, allTextBoxs])
	elif objType == "Button":
		obj = Button(screen, "", rect, (lightBlack, darkWhite, lightRed), "", (fontName, fontSize, white), lists=[allObjects, allButtons])
	elif objType == "Slider":
		obj = Slider(screen, "", rect, (lightBlack, darkWhite, lightRed), "", (fontName, fontSize, white), lists=[allObjects, allSliders])
	else:
		obj = Box(screen, "", rect, (lightBlack, darkWhite, lightRed), lists=[allObjects, allBoxs])

	return obj


def CreatePropertyMenu(objType, newObj=None):
	global activeProperty
	with open("attributesTypes.json", "r") as typeDataFile:
		objectData = json.load(typeDataFile)
		typeData = {}
		for obj in objectData[objType]["inheritance"]:
			for p in objectData[obj]:
				typeData[p] = objectData[obj][p]

		for prop in objectData[objType]:
			typeData[prop] = objectData[objType][prop]

		typeDataFile.close()

	attributes = []

	for prop in typeData:
		if prop != "inheritance":
			Attribute(typeData[prop].get("name"), typeData[prop].get("text"), typeData[prop].get("type"), typeData[prop].get("textColor"), typeData[prop].get("colors"), typeData[prop].get("textData"), typeData[prop].get("inputData"), lists=[attributes])

	if newObj == None:
		newObj = CreateObject(objType)
	Properties(screen, objType, (width-200, 0, 200, height), (lightBlack, darkWhite, lightRed), f"{objType} - Properties", ("arial", 12, white), textData={"alignText": "center-top"}, inputData={"attributes": attributes, "isScrollable": True, "parentObject": newObj}, drawData={"inactiveY": 11.5})
	activeProperty = newObj

	cam.CreateDifferences()


def ButtonPress(event):
	global objType, activeProperty
	for objMenu in objectMenus:
		if objMenu.name == "objectMenu":
			if objMenu.activeOption != None:
				if objMenu.activeOption.active:
					objType = objMenu.activeOption.text.split(" - ")[1]
					CreatePropertyMenu(objType)
					objMenu.activeOption.active = False

	if event.type == pg.MOUSEBUTTONDOWN:
		if event.button == 3:
			for obj in allObjects:
				if obj.rect.collidepoint(pg.mouse.get_pos()):
					if activeProperty == None:
						activeProperty = obj
					else:
						activeProperty = None
					break
				else:
					activeProperty = None

		if event.button == 1:
			for obj in saveObjs:
				if saveObjs.get(obj).name == "confirmSave":
					if saveObjs.get(obj).active:
						saveName = saveObjs.get("saveFileName").text
						if saveName != "" and saveName != saveObjs.get("saveFileName").splashText:
							Save(saveName)

				if saveObjs.get(obj).name == "confirmLoad":
					if saveObjs.get(obj).active:
						loadName = saveObjs.get("saveFileName").text
						if loadName != "" and loadName != saveObjs.get("saveFileName").splashText:
							Load(loadName)

	if event.type == pg.KEYDOWN:
		if pg.key.get_pressed()[pg.K_SPACE] and (pg.key.get_pressed()[pg.K_LCTRL] or pg.key.get_pressed()[pg.K_RCTRL]):
			cam.SwitchColors()

		if pg.key.get_pressed()[pg.K_DELETE] and (pg.key.get_pressed()[pg.K_LCTRL] or pg.key.get_pressed()[pg.K_RCTRL]):
			if activeProperty != None:
				for menu in propertiesMenus:
					if menu.parentObject == activeProperty:
						DestroyAttribute(menu.attributes[0])

		if event.key in objectShortcuts:
			if activeProperty == None:
				for obj in saveObjs:
					if saveObjs.get(obj).active:
						return
				CreatePropertyMenu(objectShortcuts.get(event.key))


def Inspect():
	inspection = cam

	for obj in allObjects:
		if obj.rect.collidepoint(pg.mouse.get_pos()):
			inspection = obj
			break

	pg.draw.circle(screen, red, pg.mouse.get_pos(), 1*sf)

	texts = []
	try:
		texts.append(f"-------General-------")
		texts.append(f"Name: {inspection.name if inspection.name != '' else str(type(inspection).__name__)}")
		texts.append(f"Pos: x:{inspection.rect.x//sf - cam.rect.x//sf}, y:{inspection.rect.y//sf - cam.rect.y//sf}")
		texts.append(f"Size: w:{inspection.rect.w//sf}, h:{inspection.rect.h//sf}")
		texts.append(f"Foreground color: {inspection.foregroundColor}")
		texts.append(f"Background color: {inspection.backgroundColor}")
	except AttributeError:
		pass
	try:
		if "imageName" in inspection.__dict__:
			texts.append(f"------Image Data------")
		texts.append(f"Image name: {inspection.imageName}")
		texts.append(f"Image size: {inspection.ogSize*sf}")
		texts.append(f"Frame rate: {inspection.frameRate}")
		texts.append(f"Is animation: {inspection.isAnimation}")
		texts.append(f"Number of frames: {inspection.numOfFrames}")
	except AttributeError:
		pass
	try:
		if "fontName" in inspection.__dict__:
			texts.append(f"---------Font---------")
		texts.append(f"Font color: {inspection.fontColor}")
		texts.append(f"Font name: {inspection.fontName}")
		texts.append(f"Text size: {inspection.ogFontSize*sf}")
		texts.append(f"Align text: {inspection.alignText}")
	except AttributeError:
		pass
	try:
		if "charLimit" in inspection.__dict__:
			texts.append(f"----Text Input Data----")
		texts.append(f"Char limit: {inspection.charLimit if inspection.charLimit != -1 else 'Infinite'}")
		texts.append(f"Splash text: {inspection.splashText}")
		texts.append(f"Non allowed keys file path: {inspection.nonAllowedKeysFilePath}")
		texts.append(f"Allowed keys file path: {inspection.allowedKeysFilePath}")
	except AttributeError:
		pass
	try:
		pg.draw.rect(screen, darkGray, (pg.mouse.get_pos()[0], pg.mouse.get_pos()[1], 100*sf, (len(texts)*6)*sf + 4*sf))
		DrawRectOutline(screen, lightGray, (pg.mouse.get_pos()[0], pg.mouse.get_pos()[1], 100*sf, (len(texts)*6)*sf + 4*sf))
		for i, text in enumerate(texts):
			screen.blit(font.render(text, True, white), (pg.mouse.get_pos()[0] + 1*sf, pg.mouse.get_pos()[1] + 2*sf + (i*6)*sf))
	except AttributeError:
		pass


def Save(fileName):
	data = {}
	for obj in allObjects:
		# recursively call object diction checks
		if obj.name != "":
			name = obj.name
		else:
			name = type(obj).__name__

		data[name] = ProcessObject(obj)

	with open(savePath + fileName + ".json", "w") as file:
		json.dump(data, fp=file, indent=2)


def ProcessObject(obj):
	pgObjects = ["surface", "ogRect", "rect", "sliderObj", "textObjs", "font", "textSurface", "textRect", "lists", "image", "scrollObj", "borderWidth"]

	objData = {}
	# name
	objData["name"] = obj.name
	# object type
	objData["type"] = type(obj).__name__
	# position
	objData["position"] = [obj.ogRect.x - cam.rect.x//sf, obj.ogRect.y - cam.rect.y//sf]
	# size
	objData["size"] = [obj.ogRect.w, obj.ogRect.h]

	try:
		# scrollObj
		objData["scrollObj"] = scrollObj.name
	except:
		pass

	# loop through each element
	for item in obj.__dict__:
		# check if item is not a pygame object
		if item not in pgObjects:
			if type(obj.__dict__.get(item)) != set:
				objData[item] = obj.__dict__.get(item)
			# convert sets to lists
			else:
				objData[item] = list(obj.__dict__.get(item))

	return objData


def Load(fileName):
	try:
		with open(savePath + fileName + ".json", "r") as file:
			data = json.load(file)
			file.close()

		with open(savePath + fileName + ".txt", "w") as file:
			for obj in data:
				drawData = {
					"activeSurface": data[obj]["activeSurface"],
					"drawBorder": data[obj]["drawBorder"],
					"borderWidth": data[obj]["ogBorderWidth"],
					"isFilled": data[obj]["isFilled"],
					"roundedEdges": data[obj]["roundedEdges"],
					"roundedCorners": data[obj]["roundedCorners"],
					"roundness": data[obj]["roundness"],
					"activeCorners": data[obj]["activeCorners"],
					"drawBackground": data[obj]["drawBackground"],
					"additive": data[obj]["additive"]
				}
				try:
					imageData = {
						"isAnimation": data[obj]["isAnimation"],
						"numOfFrames": data[obj]["numOfFrames"],
						"frameRate": data[obj]["frameRate"],
						"filePath": data[obj]["imageName"],
						"size": data[obj]["ogSize"]
					}
				except:
					pass

				try:
					textData = {
						"alignText": data[obj]["alignText"],
						"drawText": data[obj]["drawText"],
						"multiline": data[obj]["multiline"],
						"isScrollable": data[obj]["scrollable"],
						"scrollAmount": data[obj]["scrollAmount"]
					}
				except:
					pass

				if data[obj]["type"] == "Box":
					newObj = Box(screen, data[obj]["name"], (data[obj]["position"][0], data[obj]["position"][1], data[obj]["size"][0], data[obj]["size"][1]), (data[obj]["backgroundColor"], data[obj]["foregroundColor"]), drawData, lists=[allObjects, allBoxs])
					file.write(f'Box(screen, "{data[obj]["name"]}", ({data[obj]["position"][0]}, {data[obj]["position"][1]}, {data[obj]["size"][0]}, {data[obj]["size"][1]}), ({data[obj]["backgroundColor"]}, {data[obj]["foregroundColor"]}), {drawData})\n')

				elif data[obj]["type"] == "ImageFrame":
					newObj = ImageFrame(screen, data[obj]["name"], (data[obj]["position"][0], data[obj]["position"][1], data[obj]["size"][0]//sf, data[obj]["size"][1]//sf), (data[obj]["backgroundColor"], data[obj]["foregroundColor"]), imageData=imageData, drawData=drawData, lists=[allObjects, allImageFrames])
					file.write(f'ImageFrame(screen, "{data[obj]["name"]}", ({data[obj]["position"][0]}, {data[obj]["position"][1]}, {data[obj]["size"][0]//sf}, {data[obj]["size"][1]//sf}), ({data[obj]["backgroundColor"]}, {data[obj]["foregroundColor"]}), imageData={imageData}, drawData={drawData})\n')

				elif data[obj]["type"] == "Label":
					textData["alignText"] = data[obj]["alignText"]
					textData["drawText"] = data[obj]["drawText"]
					textData["multiline"] = data[obj]["multiline"]
					textData["isScrollable"] = data[obj]["isScrollable"]
					textData["scrollAmount"] = data[obj]["scrollAmount"]

					newObj = Label(screen, data[obj]["name"], (data[obj]["position"][0], data[obj]["position"][1], data[obj]["size"][0]//sf, data[obj]["size"][1]//sf), (data[obj]["backgroundColor"], data[obj]["foregroundColor"]), data[obj]["text"], (data[obj]["fontName"], data[obj]["ogFontSize"], data[obj]["fontColor"]), textData=textData, imageData=imageData, drawData=drawData, lists=[allObjects, allLabels])
					file.write(f'Label(screen, "{data[obj]["name"]}", ({data[obj]["position"][0]}, {data[obj]["position"][1]}, {data[obj]["size"][0]//sf}, {data[obj]["size"][1]//sf}), ({data[obj]["backgroundColor"]}, {data[obj]["foregroundColor"]}), {data[obj]["text"]}, ({data[obj]["fontName"]}, {data[obj]["ogFontSize"]}, {data[obj]["fontColor"]}), textData={textData}, imageData={imageData}, drawData={drawData})\n')

				elif data[obj]["type"] == "TextInputBox":
					inputData = {
						"charLimit": data[obj]["charLimit"],
						"splashText": data[obj]["splashText"],
						"nonAllowedKeysFile": data[obj]["nonAllowedKeysFilePath"],
						"allowedKeysFile": data[obj]["allowedKeysFilePath"]
					}

					textData["alignText"] = data[obj]["alignText"]
					textData["drawText"] = data[obj]["drawText"]
					textData["multiline"] = data[obj]["multiline"]
					textData["isScrollable"] = data[obj]["isScrollable"]
					textData["scrollAmount"] = data[obj]["scrollAmount"]

					drawData["growRect"] = data[obj]["growRect"]
					drawData["header"] = data[obj]["header"]
					drawData["replaceSplashText"] = data[obj]["replaceSplashText"]

					newObj = TextInputBox(screen, data[obj]["name"], (data[obj]["position"][0], data[obj]["position"][1], data[obj]["size"][0]//sf, data[obj]["size"][1]//sf), (data[obj]["backgroundColor"], data[obj]["inactiveColor"], data[obj]["activeColor"]), (data[obj]["fontName"], data[obj]["ogFontSize"], data[obj]["fontColor"]), inputData=inputData, textData=textData, imageData=imageData, drawData=drawData, lists=[allObjects, allTextBoxs])
					file.write(f'TextInputBox(screen, "{data[obj]["name"]}", ({data[obj]["position"][0]}, {data[obj]["position"][1]}, {data[obj]["size"][0]//sf}, {data[obj]["size"][1]//sf}), ({data[obj]["backgroundColor"]}, {data[obj]["inactiveColor"]}, {data[obj]["activeColor"]}), ({data[obj]["fontName"]}, {data[obj]["ogFontSize"]}, {data[obj]["fontColor"]}), inputData={inputData}, textData={textData}, imageData={imageData}, drawData={drawData})\n')

				elif data[obj]["type"] == "Button":
					inputData = {
						"active": data[obj]["active"]
					}

					textData["alignText"] = data[obj]["alignText"]
					textData["drawText"] = data[obj]["drawText"]
					textData["multiline"] = data[obj]["multiline"]
					textData["isScrollable"] = data[obj]["isScrollable"]
					textData["scrollAmount"] = data[obj]["scrollAmount"]

					newObj = Button(screen, data[obj]["name"], (data[obj]["position"][0], data[obj]["position"][1], data[obj]["size"][0]//sf, data[obj]["size"][1]//sf), (data[obj]["backgroundColor"], data[obj]["inactiveColor"], data[obj]["activeColor"]), data[obj]["text"], (data[obj]["fontName"], data[obj]["ogFontSize"], data[obj]["fontColor"]), data[obj]["isHoldButton"], inputData=inputData, textData=textData, imageData=imageData, drawData=drawData, lists=[allObjects, allButtons])
					file.write(f'Button(screen, "{data[obj]["name"]}", ({data[obj]["position"][0]}, {data[obj]["position"][1]}, {data[obj]["size"][0]//sf}, {data[obj]["size"][1]//sf}), ({data[obj]["backgroundColor"]}, {data[obj]["inactiveColor"]}, {data[obj]["activeColor"]}), "{data[obj]["text"]}", ({data[obj]["fontName"]}, {data[obj]["ogFontSize"]}, {data[obj]["fontColor"]}), {data[obj]["isHoldButton"]}, inputData={inputData}, textData={textData}, imageData={imageData}, drawData={drawData})\n')

				elif data[obj]["type"] == "Slider":
					inputData = {
						"isVertical": data[obj]["isVertical"],
						# "scrollObj": data[obj]["scrollObj"],
						"startValue": data[obj]["startValue"]
					}
					textData["alignText"] = data[obj]["alignText"]
					textData["drawText"] = data[obj]["drawText"]
					textData["multiline"] = data[obj]["multiline"]
					textData["isScrollable"] = data[obj]["isScrollable"]
					textData["scrollAmount"] = data[obj]["scrollAmount"]

					drawData["moveRect"] = data[obj]["moveText"]
					drawData["sliderSize"] = data[obj]["sliderSize"]
					drawData["isFilled"] = data[obj]["isFilled"]

					newObj = Slider(screen, data[obj]["name"], (data[obj]["position"][0], data[obj]["position"][1], data[obj]["size"][0]//sf, data[obj]["size"][1]//sf), (data[obj]["colors"][0], data[obj]["colors"][1], data[obj]["colors"][2]), data[obj]["text"], (data[obj]["fontName"], data[obj]["ogFontSize"], data[obj]["fontColor"]), inputData=inputData, textData=textData, imageData=imageData, drawData=drawData, lists=[allObjects, allSliders])
					file.write(f'Slider(screen, "{data[obj]["name"]}", ({data[obj]["position"][0]}, {data[obj]["position"][1]}, {data[obj]["size"][0]//sf}, {data[obj]["size"][1]//sf}), ({data[obj]["colors"][0]}, {data[obj]["colors"][1]}, {data[obj]["colors"][2]}), "{data[obj]["text"]}", ({data[obj]["fontName"]}, {data[obj]["ogFontSize"]}, {data[obj]["fontColor"]}), inputData={inputData}, textData={textData}, imageData={imageData}, drawData={drawData})\n')

				elif data[obj]["type"] == "Switch":
					inputData = {
						"active": data[obj]["active"]
					}

					textData["optionsText"] = data[obj]["optionsText"]
					textData["optionsFontColor"] = data[obj]["optionsFontColor"]
					textData["optionsAlignText"] = data[obj]["optionsAlignText"]
					textData["optionsFont"] = data[obj]["optionsFont"]
					textData["alignText"] = data[obj]["alignText"]
					textData["drawText"] = data[obj]["drawText"]
					textData["multiline"] = data[obj]["multiline"]
					textData["isScrollable"] = data[obj]["isScrollable"]
					textData["scrollAmount"] = data[obj]["scrollAmount"]

					newObj = Switch(screen, data[obj]["name"], (data[obj]["position"][0], data[obj]["position"][1], data[obj]["size"][0]//sf, data[obj]["size"][1]//sf), (data[obj]["inactiveColor"], data[obj]["activeColor"]), data[obj]["text"], (data[obj]["fontName"], data[obj]["ogFontSize"], data[obj]["fontColor"]), textData=textData, imageData=imageData, drawData=drawData, lists=[allObjects, allSwitchs])
					file.write(f'Switch(screen, "{data[obj]["name"]}", ({data[obj]["position"][0]}, {data[obj]["position"][1]}, {data[obj]["size"][0]//sf}, {data[obj]["size"][1]//sf}), ({data[obj]["inactiveColor"]}, {data[obj]["activeColor"]}), "{data[obj]["text"]}", ({data[obj]["fontName"]}, {data[obj]["ogFontSize"]}, {data[obj]["fontColor"]}), textData={textData}, imageData={imageData}, drawData={drawData})\n')

				elif data[obj]["type"] == "MultiSelctButton":
					inputData = {
						"optionNames": data[obj]["optionNames"],
						"optionAlignText": data[obj]["optionAlignText"],
						"activeOption": data[obj]["activeOption"],
						"optionsSize": data[obj]["optionsSize"],
						"relativePos": data[obj]["relativePos"],
						"isScrollable": data[obj]["isScrollable"],
						"allowNoSelection": data[obj]["allowNoSelection"],
						"active": data[obj]["active"]
					}

					textData["alignText"] = data[obj]["alignText"]
					textData["drawText"] = data[obj]["drawText"]
					textData["multiline"] = data[obj]["multiline"]
					textData["isScrollable"] = data[obj]["isScrollable"]
					textData["scrollAmount"] = data[obj]["scrollAmount"]

					newObj = MultiSelctButton(screen, data[obj]["name"], (data[obj]["position"][0], data[obj]["position"][1], data[obj]["size"][0]//sf, data[obj]["size"][1]//sf), (data[obj]["inactiveColor"], data[obj]["activeColor"]), data[obj]["text"], (data[obj]["fontName"], data[obj]["ogFontSize"], data[obj]["fontColor"]), inputData={inputData}, textData=textData, imageData=imageData, drawData=drawData, lists=[allObjects, allMultiButtons])
					file.write(f'MultiSelctButton(screen, "{data[obj]["name"]}", ({data[obj]["position"][0]}, {data[obj]["position"][1]}, {data[obj]["size"][0]//sf}, {data[obj]["size"][1]//sf}), ({data[obj]["inactiveColor"]}, {data[obj]["activeColor"]}), "{data[obj]["text"]}", ({data[obj]["fontName"]}, {data[obj]["ogFontSize"]}, {data[obj]["fontColor"]}), inputData={inputData}, textData={textData}, imageData={imageData}, drawData={drawData})\n')

				elif data[obj]["type"] == "DropDownMenu":
					inputData = {
						"optionNames": data[obj]["optionNames"],
						"optionAlignText": data[obj]["optionAlignText"],
						"activeOption": data[obj]["activeOption"],
						"optionsSize": data[obj]["optionsSize"],
						"relativePos": data[obj]["relativePos"],
						"isScrollable": data[obj]["isScrollable"],
						"allowNoSelection": data[obj]["allowNoSelection"],
						"inputIsHoldButton": data[obj]["inputIsHoldButton"],
						"active": data[obj]["active"]
					}

					textData["alignText"] = data[obj]["alignText"]
					textData["drawText"] = data[obj]["drawText"]
					textData["multiline"] = data[obj]["multiline"]
					textData["isScrollable"] = data[obj]["isScrollable"]
					textData["scrollAmount"] = data[obj]["scrollAmount"]

					newObj = DropDownMenu(screen, data[obj]["name"], (data[obj]["position"][0], data[obj]["position"][1], data[obj]["size"][0]//sf, data[obj]["size"][1]//sf), (data[obj]["inactiveColor"], data[obj]["activeColor"]), data[obj]["text"], (data[obj]["fontName"], data[obj]["ogFontSize"], data[obj]["fontColor"]), inputData={inputData}, textData=textData, imageData=imageData, drawData=drawData, lists=[allObjects, allMultiButtons])
					file.write(f'DropDownMenu(screen, "{data[obj]["name"]}", ({data[obj]["position"][0]}, {data[obj]["position"][1]}, {data[obj]["size"][0]//sf}, {data[obj]["size"][1]//sf}), ({data[obj]["inactiveColor"]}, {data[obj]["activeColor"]}), "{data[obj]["text"]}", ({data[obj]["fontName"]}, {data[obj]["ogFontSize"]}, {data[obj]["fontColor"]}), inputData={inputData}, textData={textData}, imageData={imageData}, drawData={drawData})\n')

				CreatePropertyMenu(data[obj]["type"], newObj)

			file.close()

	except FileNotFoundError:
		print(f"File '{fileName}' doesn't exist.")


if __name__ == "__main__":
	debugMode = False
	gameState = "Game"

	def DrawLoop():
		screen.fill(darkGray)

		if cam != None:
			cam.Draw()

		DrawGui()

		if activeProperty != None:
			if activeProperty.additive and activeProperty.roundedEdges and not activeProperty.roundedCorners:
				DrawRectOutline(activeProperty.surface, lightRed, (activeProperty.rect.x - 5*sf - (activeProperty.rect.h // 2), activeProperty.rect.y - 5*sf, activeProperty.rect.w + 10*sf + activeProperty.rect.h, activeProperty.rect.h + 10*sf), 2*sf)
			else:
				DrawRectOutline(activeProperty.surface, lightRed, (activeProperty.rect.x - 5*sf, activeProperty.rect.y - 5*sf, activeProperty.rect.w + 10*sf, activeProperty.rect.h + 10*sf), 2*sf)

		for objMenu in objectMenus:
			if gameState in objMenu.activeSurface or objMenu.activeSurface == "all":
				objMenu.Draw()

		for menu in propertiesMenus:
			if gameState in menu.activeSurface or menu.activeSurface == "all":
				if menu.parentObject == activeProperty:
					menu.Draw()

		if inspectMode:
			Inspect()

		pg.display.update()


	def Quit():
		global running
		running = False


	objects = []
	with open("attributesTypes.json", "r") as typeDataFile:
		objectData = json.load(typeDataFile)
		typeDataFile.close()
	for prop in objectData:
		for key in objectShortcutDisplay:
			if key == prop:
				prop = f"{objectShortcutDisplay[key]} - {prop}"
		objects.append(prop)

	# object selection
	DropDownMenu(screen, "objectMenu", (0, 0, 150, height), (lightBlack, darkWhite, lightRed), "Objects", ("arial", 12, white), textData={"alignText": "center-top"}, inputData={"optionNames": objects, "optionAlignText": "center", "optionsSize": [138, 30], "inputIsHoldButton": True, "allowNoSelection": True}, drawData={"inactiveY": 11.5}, lists=[objectMenus])

	# camera
	cam = Camera(screen, "Camera", (0, 0, width, height), ((50, 50, 50), lightGray))

	# save objects
	saveFileName = TextInputBox(screen, "saveFileName", (150, 0, 140, 25), (lightBlack, darkWhite, lightRed), ("arial", 12, white), inputData={"splashText": "Save name: ", "charLimit": 15, "allowedKeysFile": "textAllowedKeys.txt"}, textData={"alignText": "left"}, lists=[saveObjs, allDropDowns])
	confirmSave = Button(screen, "confirmSave", (290, 0, 75, 25), (lightBlack, darkWhite, lightRed), "Save", ("arial", 12, white), isHoldButton=True, lists=[saveObjs, allDropDowns])
	loadSave = Button(screen, "confirmLoad", (365, 0, 75, 25), (lightBlack, darkWhite, lightRed), "Load", ("arial", 12, white), isHoldButton=True, lists=[saveObjs, allDropDowns])

	while running:
		clock.tick_busy_loop(fps)
		if debugMode:
			print(clock.get_fps())

		for event in pg.event.get():
			if event.type == pg.QUIT:
				Quit()
			if event.type == pg.KEYDOWN:
				if event.key == pg.K_ESCAPE:
					Quit()

				if event.key == pg.K_F2:
					inspectMode = not inspectMode
					pg.mouse.set_visible(not inspectMode)

				if event.key == pg.K_F3:
					debugMode = not debugMode


			HandleGUI(event)

			for objMenu in objectMenus:
				if gameState in objMenu.activeSurface or objMenu.activeSurface == "all":
					objMenu.HandleEvent(event)

			for menu in propertiesMenus:
				if gameState in menu.activeSurface or menu.activeSurface == "all":
					if menu.parentObject == activeProperty:
						menu.HandleEvent(event)

			if cam != None:
				cam.HandleEvent(event)

			ButtonPress(event)

		if cam != None:
			cam.Update()

		DrawLoop()
