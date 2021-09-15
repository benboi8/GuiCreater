# auto-py-to-exe

# TODO:
# 1. fix slider button - 99% - needs testing
# 2. fix slider attributes - 0%
# 3. add mouse keybinding - 0%
# 4. fix text-input cursor - 0%

# import GUI objects
import sys
sys.path.insert(1, "/Python Projects/GuiObjects")

from GUIObjects import *
import json

# create screen
width, height = 870, 440
sf = 2
screen = pg.display.set_mode((width * sf, height * sf))

# save path for data
savePath = "saves/"
autoSavePath = "autoSaves/"
lastSave = dt.datetime.now()
autoSaveCounter = 0

# attribute types
attributeTypesFilePath = "attributesTypes.json"

# all placed objects
allObjects = []

# save objects
saveObjs = {}

# key binding objs
keyBindingObjs = []
rebindingKeys = False

# settings
userSettings = "deafultSettings.json"
customUserSettings = "userSettings.json"

# object being edited
activeProperty = None

# all property menus
propertiesMenus = []
objectMenus = []

# extra colors
backGroundColor = darkGray

# is inspection enabled
inspectMode = False
pinnedInspections = []
createdInspection = False

# is debug mode enabled
debugMode = False

# keyboard shortcuts
objectShortcuts = {
	pg.K_1: "Box",
	pg.K_2: "ImageFrame",
	pg.K_3: "Label",
	pg.K_4: "TextInputBox",
	pg.K_5: "Button",
	pg.K_6: "Slider",
	pg.K_7: "Switch",
	pg.K_8: "MultiSelectButton",
	pg.K_9: "DropDownMenu",

	pg.K_KP1: "Box",
	pg.K_KP2: "ImageFrame",
	pg.K_KP3: "Label",
	pg.K_KP4: "TextInputBox",
	pg.K_KP5: "Button",
	pg.K_KP6: "Slider",
	pg.K_KP7: "Switch",
	pg.K_KP8: "MultiSelectButton",
	pg.K_KP9: "DropDownMenu",
}

objectShortcutDisplay = {
	"1": "Box",
	"2": "Image frame",
	"3": "Label",
	"4": "Text input box",
	"5": "Button",
	"6": "Slider",
	"7": "Switch",
	"8": "Multi-select button",
	"9": "Drop-down menu"
}

objTypeDisplay = {
	"Box": "Box",
	"Image frame": "ImageFrame",
	"Label": "Label",
	"Text input box": "TextInputBox",
	"Button": "Button",
	"Slider": "Slider",
	"Switch": "Switch",
	"Multi-select button": "MultiSelectButton",
	"Drop-down menu": "DropDownMenu"
}

shorcuts = {}

# camera
class Camera(Box):
	def __init__(self, name, rect, colors, drawData={}, lists=[]):
		# is camera being moved
		self.moving = False
		# does camera have original pos
		self.gotStartPos = False
		# can the camera be moved
		self.canMove = False

		# the start foreground color
		self.ogForegroundColor = colors[1]
		# foreground, background and active colors
		self.colors = colors
		# initialise the inherited object
		super().__init__(screen, name, rect, colors, drawData, lists)

		self.CreateDifferences()

	def CreateDifferences(self):
		# all the object position differences
		self.differences = []
		for obj in allObjects:
			# add the difference in position and the object
			self.differences.append((obj.rect.x - self.rect.x, obj.rect.y - self.rect.y, obj))

	def ResetPosition(self):
		self.CreateDifferences()
		self.Move((0, 0))

	def HanldeEvent(self, event):
		# if left ctrl is pressed set can move to true
		if event.type == pg.KEYDOWN:
			self.canMove = event.mod and event.key == pg.K_LCTRL

		# check if camera should be moving
		if self.canMove:
			if event.type == pg.MOUSEBUTTONDOWN:
				if event.button == 1:
					if self.rect.collidepoint(pg.mouse.get_pos()):
						self.moving = True
						self.CreateDifferences()
					else:
						self.moving = False

		# check for mouse button released
		if event.type == pg.MOUSEBUTTONUP:
			if event.button == 1:
				self.moving = False

		# check for left ctrl released
		if event.type == pg.KEYUP:
			if event.mod and pg.K_LCTRL:
				self.canMove = False
				self.moving = False

	def Update(self):
		if self.moving:
			# move camera
			self.Move()
		else:
			self.gotStartPos = False

	def Move(self, pos=None):
		if pos == None:
			if not self.gotStartPos:
				self.startPos = pg.mouse.get_pos()
				self.startRect = self.rect
				self.gotStartPos = True

			if self.gotStartPos:
				self.rect = MoveRectWithoutCenter(self.startPos, self.startRect)
		else:
			self.rect = pg.Rect(pos[0], pos[1], self.rect.w, self.rect.h)

		# update the position of all placed objects
		for diff in self.differences:
			if diff[2] in allObjects:
				allObjects[allObjects.index(diff[2])].rect = pg.Rect(diff[0] + self.rect.x, diff[1] + self.rect.y, diff[2].rect.w, diff[2].rect.h)
				if type(diff[2]) == Slider:
					diff[2].sliderObj.rect = pg.Rect(diff[2].rect.x + 2 * sf, diff[2].rect.y + 2 * sf, diff[2].sliderObj.rect.w, diff[2].sliderObj.rect.h)
				try:
					diff[2].UpdateTextRect()
				except AttributeError:
					pass

	def SwitchColors(self):
		if self.backgroundColor == self.colors[0]:
			self.backgroundColor = self.colors[1]
			self.foregroundColor = self.colors[0]
		else:
			self.backgroundColor = self.colors[0]
			self.foregroundColor = self.colors[1]

# attribute fields for objects
class Attribute:
	def __init__(self, name, text, inputType, textColor, colors, textData={}, inputData={}, lists=[]):
		self.name = name
		self.text = text
		# the type of input the attribute will use
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

		self.numOfOptionsList = []

		self.font = pg.font.SysFont(self.fontName, self.fontSize)
		self.textSurface = self.font.render(self.text, True, self.textColor)

		for l in lists:
			l.append(self)

	# create attribute inputs
	def CreateObject(self):
		# rect for attribute
		self.objectRect = pg.Rect(self.rect.x, self.rect.y + 2 * sf, self.rect.w, self.rect.h - 4 * sf)

		# change rect to make room for text box
		if self.inputType == "TextBox":
			self.objectRect.x += self.textSurface.get_width() + 10 * sf
			self.objectRect.w += self.textSurface.get_width() + 12 * sf

			self.textBox = TextInputBox(self.surface, self.name, pg.Rect(self.objectRect.x // sf, self.objectRect.y // sf, self.objectRect.w // sf, self.objectRect.h // sf), (self.backgroundColor, self.foregroundColor, self.inputColor), (self.fontName, self.fontSize // sf, self.textColor), self.inputData, self.textData, lists=[])

			# change the text box text to the input data
			if "pos" in self.name:
				if self.name.split("-")[1] == "X":
					self.textBox.text = str(self.parentObject.rect.x // sf)
				if self.name.split("-")[1] == "Y":
					self.textBox.text = str(self.parentObject.rect.y // sf)
				if self.name.split("-")[1] == "W":
					self.textBox.text = str(self.parentObject.rect.w // sf)
				if self.name.split("-")[1] == "H":
					self.textBox.text = str(self.parentObject.rect.h // sf)

			elif "options" in self.name:
				if "FontColor" in self.name:
					if self.name.split("-")[0] in self.parentObject.__dict__:
						if self.name.split("-")[1] == "R":
							if self.name.split("-")[-1] == "1":
								self.textBox.text = str(getattr(self.parentObject, self.name.split("-")[0])[0][0])

							if self.name.split("-")[-1] == "2":
								self.textBox.text = str(getattr(self.parentObject, self.name.split("-")[0])[1][1])

						if self.name.split("-")[1] == "G":
							if self.name.split("-")[-1] == "1":
								self.textBox.text = str(getattr(self.parentObject, self.name.split("-")[0])[0][1])

							if self.name.split("-")[-1] == "2":
								self.textBox.text = str(getattr(self.parentObject, self.name.split("-")[0])[1][1])

						if self.name.split("-")[1] == "B":
							if self.name.split("-")[-1] == "1":
								self.textBox.text = str(getattr(self.parentObject, self.name.split("-")[0])[0][2])
							if self.name.split("-")[-1] == "2":
								self.textBox.text = str(getattr(self.parentObject, self.name.split("-")[0])[1][2])

				elif "FontName" in self.name:
					self.textBox.text = str(getattr(self.parentObject, self.name))

				elif "Size" in self.name:
					if self.name.split("-")[1] == "W":
						self.textBox.text = str(getattr(self.parentObject, self.name.split("-")[0])[0])
					if self.name.split("-")[1] == "H":
						self.textBox.text = str(getattr(self.parentObject, self.name.split("-")[0])[1])

				elif self.name.split("-")[0] in self.parentObject.__dict__:
					if self.name.split("-")[-1] == "1":
						self.textBox.text = str(getattr(self.parentObject, self.name.split("-")[0])[0])
					if self.name.split("-")[-1] == "2":
						self.textBox.text = str(getattr(self.parentObject, self.name.split("-")[0])[1])

			elif "Color" in self.name:
				if self.name.split("-")[0] in self.parentObject.__dict__:
					if self.name.split("-")[1] == "R":
						self.textBox.text = str(getattr(self.parentObject, self.name.split("-")[0])[0])
					if self.name.split("-")[1] == "G":
						self.textBox.text = str(getattr(self.parentObject, self.name.split("-")[0])[1])
					if self.name.split("-")[1] == "B":
						self.textBox.text = str(getattr(self.parentObject, self.name.split("-")[0])[2])

			elif self.name == "numOfOptions":
				self.textBox.text = str(getattr(self.parentObject, self.name))

			elif "Option-" in self.name:
				self.textBox.text = str((getattr(self.parentObject, "optionNames")[int(self.name.split("-")[1].strip(":"))]))

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

		# add a button to check
		elif self.inputType == "CheckBox":
			self.checkBox = Button(self.surface, self.name, pg.Rect(self.objectRect.x//sf, self.objectRect.y//sf, self.objectRect.w//sf, self.objectRect.h//sf), (self.backgroundColor, self.foregroundColor, self.inputColor), self.text, (self.fontName, self.fontSize//sf, self.textColor), False, self.textData, {}, inputData=self.inputData, lists=[])

	def UpdateRects(self):
		# original rect
		self.objectRect = pg.Rect(self.rect.x, self.rect.y + 2*sf, self.rect.w, self.rect.h - 4*sf)

		# change rects
		if self.inputType == "TextBox":
			self.objectRect.x += self.textSurface.get_width() + 10 * sf
			self.objectRect.w -= self.textSurface.get_width() + 12 * sf
			self.textBox.rect = self.objectRect

		elif self.inputType == "CheckBox":
			self.objectRect.x += 2 * sf
			self.objectRect.w -= 4 * sf
			self.checkBox.rect = self.objectRect

	def Draw(self):
		# if attribute rect is in the bounds of the properties menu
		if pg.Rect(self.parent.rect.x, self.parent.rect.y + self.parent.textSurface.get_height() + self.parent.borderWidth, self.parent.rect.w, self.parent.rect.h - self.parent.textSurface.get_height() + self.parent.borderWidth).contains(self.rect):
			pg.draw.rect(screen, self.backgroundColor, self.rect)
			DrawRectOutline(screen, self.foregroundColor, self.rect, 1 * sf)

			# draw input types
			if self.inputType == "TextBox":
				self.textBox.Draw()
			elif self.inputType == "CheckBox":
				self.checkBox.Draw()

			self.surface.blit(self.textSurface, AlignText(self.rect, self.textSurface, self.alignText))

	def HandleEvent(self, event):
		global activeProperty
		# is input a number
		isNum = False

		if self.inputType == "TextBox":
			self.textBox.HandleEvent(event)
			try:
				value = int(self.textBox.text)
				isNum = True
			except ValueError:
				value = self.textBox.text

			# if input is a number check all inputs with a number input
			if isNum:
				# check position inputs
				if "pos" in self.name:
					for diff in mainCamera.differences:
						index = mainCamera.differences.index(diff)

					if self.name.split("-")[1] == "X":
						rect = getattr(self.parentObject, "ogRect")
						rect = pg.Rect((mainCamera.rect.x // sf) + value, rect.y, rect.w, rect.h)
						setattr(self.parentObject, "ogRect", rect)

					if self.name.split("-")[1] == "Y":
						rect = getattr(self.parentObject, "ogRect")
						rect = pg.Rect(rect.x, (mainCamera.rect.y // sf) + value, rect.w, rect.h)
						setattr(self.parentObject, "ogRect", rect)

					if self.name.split("-")[1] == "W":
						rect = getattr(self.parentObject, "ogRect")
						rect = pg.Rect(rect.x, rect.y, value, rect.h)
						setattr(self.parentObject, "ogRect", rect)

					if self.name.split("-")[1] == "H":
						rect = getattr(self.parentObject, "ogRect")
						rect = pg.Rect(rect.x, rect.y, rect.w, value)
						setattr(self.parentObject, "ogRect", rect)

					if type(self.parentObject) == MultiSelectButton or type(self.parentObject) == DropDownMenu:
						self.parentObject.CreateOptions()

					if type(self.parentObject) == Slider:
						self.parentObject.CreateSliderButton()

			# if text box is active check all attributes with text inputs
			if self.textBox.active:
				if isNum:
					# check each combination of attributes
					if self.name in self.parentObject.__dict__:
						if self.name == "numOfOptions":
							# add text input boxs for each option
							setattr(self.parentObject, self.name, int(value))

							options = getattr(self.parentObject, "optionNames")
							if len(options) != self.parentObject.numOfOptions:

								for obj in self.parentObject.optionNames:
									if obj in allGUIObjects:
										allGUIObjects.remove(obj)

								self.parentObject.optionNames = []

								for i in range(self.parentObject.numOfOptions):
									self.parentObject.optionNames.append(str(i + 1))
								self.parentObject.CreateOptions()

								self.AddAttribute(self.name, value)

						elif "options" in self.name:
							if "FontColor" in self.name:
								if self.name.split("-")[0] in self.parentObject.__dict__:
									if self.name.split("-")[1] == "R":
										if self.name.split("-")[2] == "1":
											color = getattr(self.parentObject, self.name.split("-")[0])[0]
											color = (max(min(value, 255), 0), color[1], color[2])
											setattr(self.parentObject, self.name.split("-")[0], [color, getattr(self.parentObject, self.name.split("-")[0])[1]])

										if self.name.split("-")[2] == "2":
											color = getattr(self.parentObject, self.name.split("-")[0])[1]
											color = (max(min(value, 255), 0), color[1], color[2])
											setattr(self.parentObject, self.name.split("-")[0], [getattr(self.parentObject, self.name.split("-")[0])[0], color])

									if self.name.split("-")[1] == "G":
										if self.name.split("-")[2] == "1":
											color = getattr(self.parentObject, self.name.split("-")[0])[0]
											color = (color[0], max(min(value, 255), 0), color[2])
											setattr(self.parentObject, self.name.split("-")[0], [color, getattr(self.parentObject, self.name.split("-")[0])[1]])

										if self.name.split("-")[2] == "2":
											color = getattr(self.parentObject, self.name.split("-")[0])[1]
											color = (color[0], max(min(value, 255), 0), color[2])
											setattr(self.parentObject, self.name.split("-")[0], [getattr(self.parentObject, self.name.split("-")[0])[0], color])

									if self.name.split("-")[1] == "B":
										if self.name.split("-")[2] == "1":
											color = getattr(self.parentObject, self.name.split("-")[0])[0]
											color = (color[0], color[1], max(min(value, 255), 0))
											setattr(self.parentObject, self.name.split("-")[0], [color, getattr(self.parentObject, self.name.split("-")[0])[1]])

										if self.name.split("-")[2] == "2":
											color = getattr(self.parentObject, self.name.split("-")[0])[1]
											color = (color[0], color[1], max(min(value, 255), 0))
											setattr(self.parentObject, self.name.split("-")[0], [getattr(self.parentObject, self.name.split("-")[0])[0], color])

							elif "Size" in self.name:
								if self.name.split("-")[1] == "W":
									size = getattr(self.parentObject, self.name.split("-")[0])
									size = (value, size[1])
									setattr(self.parentObject, self.name.split("-")[0], size)
									self.parentObject.CreateOptions()

								if self.name.split("-")[1] == "H":
									size = getattr(self.parentObject, self.name.split("-")[0])
									size = (size[0], value)
									setattr(self.parentObject, self.name.split("-")[0], size)
									self.parentObject.CreateOptions()

						elif "inactiveSize" in self.name:
							setattr(self.parentObject, self.name, (int(value)))

						elif "Color" in self.name:
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

					# if attribute is in parent object set the value to the input
					else:
						if value != "":
							setattr(self.parentObject, self.name, int(value))
							try:
								if self.name == "text":
									self.parentObject.Rescale()
									self.parentObject.GetTextObjects()
							except TypeError:
								pass

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
					if self.name == "numOfOptions":
						setattr(self.parentObject, self.name, 0)

					elif "options" in self.name:
						if "FontName" in self.name:
							setattr(self.parentObject, self.name, str(value))

						elif self.name.split("-")[0] in self.parentObject.__dict__:
							if self.name.split("-")[1] == "1":
								setattr(self.parentObject, self.name.split("-")[0], [str(value), getattr(self.parentObject, self.name.split("-")[0])[1]])
							if self.name.split("-")[1] == "2":
								setattr(self.parentObject, self.name.split("-")[0], [getattr(self.parentObject, self.name.split("-")[0])[0], str(value)])

					elif "inactiveSize" == self.name:
						if value == "":
							value = 0
						setattr(self.parentObject, self.name, int(value))

					elif "Option-" in self.name:
						options = getattr(self.parentObject, "optionNames")
						options[int(self.name.split("-")[1].strip(":"))] = str(value)

						setattr(self.parentObject, "optionNames", options)
						self.parentObject.CreateOptions()

					elif self.name in self.parentObject.__dict__:
						setattr(self.parentObject, self.name, str(value))

						try:
							self.parentObject.Rescale()
							self.parentObject.GetTextObjects()
						except:
							pass
						if self.name == "text":
							if ".txt" in value:
								try:
									with open(value, "r") as file:
										contents = file.read()
										setattr(self.parentObject, self.name, str(contents))
										file.close()
								except IOError:
									pass
							self.parentObject.Rescale()
							self.parentObject.GetTextObjects()

						if self.name == "name":
							setattr(self.parentObject, self.name, str(value))
							self.parentObject.Rescale()
							try:
								self.parentObject.GetTextObjects()
							except AttributeError:
								pass

		# if input is a check box
		elif self.inputType == "CheckBox":
			self.checkBox.HandleEvent(event)
			value = self.checkBox.active

			if self.name == "delObject":
				if value:
					DestroyAttribute(self)

			# check every attribute which uses true/false
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


	def AddAttribute(self, name, value):
		for obj in self.numOfOptionsList:
			if obj in self.parent.attributes:
				self.parent.attributes.remove(obj)

		self.numOfOptionsList = []
		attribute = Attribute("optionNames:", "Option Names", "Label", (45, 45, 45), ((215, 215, 215), (45, 45, 45), (184, 39, 39)), textData = {"alignText": "center", "fontSize": 10}, inputData={}, lists=[self.parent.attributes, self.numOfOptionsList])

		height = self.parent.textSurface.get_height()
		if not self.parent.expandUpwards:
			attributeRect = pg.Rect(self.parent.rect.x + 3 * sf, (self.parent.attributes[-2].rect.y + 2 * sf) + ((height * sf) + 1 * sf) , self.parent.rect.w - 6 * sf, height * sf)
		else:
			attributeRect = pg.Rect(self.parent.rect.x + 3 * sf, self.parent.attributes[-2].rect.y - ((height * sf) + 1 * sf), self.parent.rect.w - 6 * sf, height * sf)
		attribute.surface = self.parent.surface
		attribute.rect = attributeRect
		attribute.parentObject = self.parent.parentObject
		attribute.parent = self.parent
		attribute.CreateObject()
		attribute.UpdateRects()

		for i in range(int(getattr(self.parentObject, self.name))):
			attribute = Attribute(f"Option-{i}:", f"Option {i + 1}", "TextBox", (215, 215, 215), ((45, 45, 45), (215, 215, 215), (184, 39, 39)), textData = {"alignText": "left", "fontSize": 10}, inputData={"allowedKeysFile": "displayTextAllowedKeys.txt", "charLimit": 15, "splashText": ""}, lists=[self.parent.attributes, self.numOfOptionsList])

			height = self.parent.textSurface.get_height()
			if not self.parent.expandUpwards:
				attributeRect = pg.Rect(self.parent.rect.x + 3 * sf, (self.parent.attributes[-2].rect.y + 2 * sf) + (((height * sf) + 1 * sf)) , self.parent.rect.w - 6 * sf, height * sf)
			else:
				attributeRect = pg.Rect(self.parent.rect.x + 3 * sf, self.parent.attributes[-2].rect.y - (((height * sf) + 1 * sf)), self.parent.rect.w - 6 * sf, height * sf)
			attribute.surface = self.parent.surface
			attribute.rect = attributeRect
			attribute.parentObject = self.parent.parentObject
			attribute.parent = self.parent
			attribute.CreateObject()
			attribute.UpdateRects()

# properties menu
class Properties(DropDownMenu):
	def __init__(self, surface, name, rect, colors, text, font, inputData={}, textData={}, drawData={}, imageData={}, lists=[propertiesMenus]):
		super().__init__(surface, name, rect, colors, text, font, inputData, textData, drawData, imageData, lists)
		# all attributes of the property menu
		self.attributes = []

		# the object the properties belong to
		self.parentObject = inputData.get("parentObject")

		self.objType = name

		# get all the attributes and add them the list
		for i, attribute in enumerate(inputData.get("attributes", [])):
			height = self.textSurface.get_height()
			if not self.expandUpwards:
				attributeRect = pg.Rect(self.rect.x + 3 * sf, (self.rect.y + 2 * sf) + (((height * sf) + 1 * sf) * (i + 1)) , self.rect.w - 6 * sf, height * sf)
			else:
				attributeRect = pg.Rect(self.rect.x + 3 * sf, self.rect.y - (((height * sf) + 1 * sf) * (i + 1)), self.rect.w - 6 * sf, height * sf)
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
		# check if attribute is within the bounds of the property menu and handle an event
		for attribute in self.attributes:
			if attribute.rect.y > self.textSurface.get_height():
				if self.active:
					attribute.HandleEvent(event)

		# scroll through the menu
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

		# get active options
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

				# release active option
				if self.isHoldButton:
					if event.type == pg.MOUSEBUTTONUP:
						if event.button == 1:
							self.active = False
							self.OnRelease()

		# update texts
		self.name = self.parentObject.name

		for key in objTypeDisplay:
			if objTypeDisplay[key] == self.objType:
				self.objTypeName = key

		self.text = f"{self.objTypeName} - Properties"
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

# inspection
class Inspector(Label):
	def __init__(self, surface, name, rect, colors, child, text, font, textData={}, drawData={}, imageData={}, lists=[]):
		super().__init__(surface, name, rect, colors, text, font, textData, drawData, imageData, lists)
		self.child = child
		self.difference = []
		self.CalculateDifference()

	def CalculateDifference(self):
		if self.child != None:
			self.difference = [self.rect.x - self.child.rect.x, self.rect.y - self.child.rect.y]

	def Update(self):
		self.rect = pg.Rect(self.difference[0] + self.child.rect.x, self.difference[1] + self.child.rect.y, self.rect.w, self.rect.h)

# draw everything
def DrawLoop():
	# fill screen
	screen.fill(backGroundColor)

	mainCamera.Draw()

	if activeProperty != None:
		if activeProperty.additive and activeProperty.roundedEdges and not activeProperty.roundedCorners:
			DrawRectOutline(activeProperty.surface, lightRed, (activeProperty.rect.x - 5 * sf - (activeProperty.rect.h // 2), activeProperty.rect.y - 5 * sf, activeProperty.rect.w + 10 * sf + activeProperty.rect.h, activeProperty.rect.h + 10 * sf), 2 * sf)
		else:
			DrawRectOutline(activeProperty.surface, lightRed, (activeProperty.rect.x - 5 * sf, activeProperty.rect.y - 5 * sf, activeProperty.rect.w + 10 * sf, activeProperty.rect.h + 10 * sf), 2 * sf)

	# draw gui objects
	DrawGui()

	for inspection in pinnedInspections:
		inspection.Draw()

	for obj in keyBindingObjs:
		obj.Draw()

	if inspectMode:
		Inspect()

	for objMenu in objectMenus:
		if gameState in objMenu.activeSurface or objMenu.activeSurface == "all":
			objMenu.Draw()

	for menu in propertiesMenus:
		if gameState in menu.activeSurface or menu.activeSurface == "all":
			if menu.parentObject == activeProperty:
				menu.Draw()

	pg.display.update()

# quit program
def Quit(bypassSaveSuccess=False):
	global running
	CreateKeyBindingsInfo(True)
	saveName = saveObjs.get("saveFileName").text
	saveSuccess = False # change to false
	if saveName != "" and saveName != saveObjs.get("saveFileName").splashText:
		saveSuccess = Save(saveName)

	if saveSuccess or bypassSaveSuccess or len(allObjects) == 0:
		running = False
	else:
		CreateMessageBox("Confirm exit!", "\nYou are about to exit without saving!\n\nAre you sure you want to continue?", {"name": "confirmExit", "rect": (width // 2 - 200, height // 2 - 90, 400, 180), "fontSize": 20, "textData": {"alignText": "center-top"}, "drawData": {"borderWidth": 2, "roundedCorners": True, "roundness": 15}, "input": {"messageDraw": {"borderWidth": 1.5, "roundness": 10, "roundedCorners": True}, "messageText": {"alignText": "center-top", "multiline": True, "fontSize": 18}, "confirmDraw": {"borderWidth": 1.5, "roundness": 5, "roundedCorners": True}, "confirmText": {"alignText": "center", "fontSize": 14}, "cancelDraw": {"borderWidth": 1.5, "roundness": 5, "roundedCorners": True}, "cancelText": {"alignText": "center", "fontSize": 14}}})
		SwapInspection(False)

# destroy an attribute
def DestroyAttribute(attribute):
	global activeProperty
	if type(attribute.parentObject).__name__ == "Slider":
		attribute.parentObject.RemoveFromList()
	for l in attribute.parentObject.lists:
		if attribute.parentObject in l:
			l.remove(attribute.parentObject)
	propertiesMenus.remove(attribute.parent)
	activeProperty = None

# create a gui object to edit
def CreateObject(objType):
	rect = pg.Rect((mainCamera.rect.x//sf + (mainCamera.rect.w//sf)//2) - 60, (mainCamera.rect.y//sf + (mainCamera.rect.h//sf)//2) - 15, 120, 30)
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

	elif objType == "Switch":
		obj = Switch(screen, "", rect, (lightBlack, darkWhite, lightRed), "", (fontName, fontSize, white), lists=[allObjects, allSliders])

	elif objType == "MultiSelectButton":
		obj = MultiSelectButton(screen, "", rect, (lightBlack, darkWhite, lightRed), "", (fontName, fontSize, white), lists=[allObjects, allSliders])

	elif objType == "DropDownMenu":
		obj = DropDownMenu(screen, "", rect, (lightBlack, darkWhite, lightRed), "", (fontName, fontSize, white), lists=[allObjects, allSliders])

	return obj

# create a property menu for a new object
def CreatePropertyMenu(objType, newObj=None):
	global activeProperty
	with open(attributeTypesFilePath, "r") as typeDataFile:
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

	for name in objTypeDisplay:
		if objTypeDisplay[name] == objType:
			objTypeName = name
			break

	Properties(screen, objType, (width - 160, 0, 160, height), (lightBlack, darkWhite, lightRed), f"{objTypeName} - Properties", ("arial", 12, white), textData={"alignText": "center-top"}, inputData={"attributes": attributes, "isScrollable": True, "parentObject": newObj}, drawData={"inactiveY": 11.5})
	activeProperty = newObj

	mainCamera.CreateDifferences()

# inspect an object
def Inspect():
	global createdInspection, inspectionLabel
	inspection = mainCamera

	for obj in allObjects:
		if obj.rect.collidepoint(pg.mouse.get_pos()):
			inspection = obj
			break

	pg.draw.circle(screen, red, pg.mouse.get_pos(), 1 * sf)

	texts = ""
	numberOfLines = 0
	try:
		texts += f"-------General-------\\n"
		texts += f"Name: {inspection.name if inspection.name != '' else str(type(inspection).__name__)}\\n"
		if inspection == mainCamera:
			texts += f"Pos: x:{inspection.rect.x // sf}, y:{inspection.rect.y // sf}\\n"
		else:
			texts += f"Pos: x:{inspection.rect.x // sf - mainCamera.rect.x // sf}, y:{inspection.rect.y // sf - mainCamera.rect.y // sf}\\n"
		texts += f"Size: w:{inspection.rect.w // sf}, h:{inspection.rect.h // sf}\\n"
		texts += f"Foreground color: {inspection.foregroundColor}\\n"
		texts += f"Background color: {inspection.backgroundColor}\\n"
		numberOfLines += 6
	except AttributeError:
		pass
	try:
		if "imageName" in inspection.__dict__:
			texts += f"------Image Data------\\n"
			numberOfLines += 1
		texts += f"Image name: {inspection.imageName}\\n"
		texts += f"Image size: {inspection.ogSize * sf}\\n"
		texts += f"Frame rate: {inspection.frameRate}\\n"
		texts += f"Is animation: {inspection.isAnimation}\\n"
		texts += f"Number of frames: {inspection.numOfFrames}\\n"
		numberOfLines += 5
	except AttributeError:
		pass
	try:
		if "fontName" in inspection.__dict__:
			texts += f"---------Font---------\\n"
			numberOfLines += 1
		texts += f"Font color: {inspection.fontColor}\\n"
		texts += f"Font name: {inspection.fontName}\\n"
		texts += f"Text size: {inspection.ogFontSize * sf}\\n"
		texts += f"Align text: {inspection.alignText}\\n"
		numberOfLines += 4
	except AttributeError:
		pass
	try:
		if "charLimit" in inspection.__dict__:
			texts += f"----Text Input Data----\\n"
			numberOfLines += 1
		texts += f"Char limit: {inspection.charLimit if inspection.charLimit != -1 else 'Infinite'}\\n"
		texts += f"Splash text: {inspection.splashText}\\n"
		texts += f"Non allowed keys file path: {inspection.nonAllowedKeysFilePath}\\n"
		texts += f"Allowed keys file path: {inspection.allowedKeysFilePath}\\n"
		numberOfLines += 4
	except AttributeError:
		pass

	if not createdInspection:
		inspectionLabel = Inspector(screen, type(inspection).__name__, (pg.mouse.get_pos()[0] // sf, pg.mouse.get_pos()[1] // sf, 100, (numberOfLines * 6) + 4), (darkGray, lightGray), inspection, texts, ("arial", 6, white), textData = {"multiline": True, "isScrollable": False, "alignText": "center-top"}, lists=[])
		createdInspection = True

	inspectionLabel.Draw()

# pin an inspected object
def PinInspection():
	if inspectionLabel not in pinnedInspections:
		pinnedInspections.append(inspectionLabel)

# remove pinned inspections
def RemoveInspections():
	global pinnedInspections
	pinnedInspections = []

# handle events
def HandleEvents(event):
	global objType, activeProperty, rebindingKeys, debugMode
	for obj in keyBindingObjs:
		if "resetToDefault" == obj.name:
			if obj.active:
				ResetUserSettings()

		elif "rebindKey" in obj.name:
			if obj.active:
				rebindingKeys = True

	# handle gui events
	HandleGUI(event)

	# handle object menus
	for objMenu in objectMenus:
		if gameState in objMenu.activeSurface or objMenu.activeSurface == "all":
			objMenu.HandleEvent(event)

	# handle property menus
	for menu in propertiesMenus:
		if gameState in menu.activeSurface or menu.activeSurface == "all":
			if menu.parentObject == activeProperty:
				menu.HandleEvent(event)

	mainCamera.HanldeEvent(event)

	# create a new object to edit
	if event.type == pg.MOUSEBUTTONDOWN:
		# left click
		if event.button == 1:
			# save data
			for obj in saveObjs:
				if saveObjs.get(obj).name == "confirmSave":
					if saveObjs.get(obj).active:
						Save()

				# load data
				if saveObjs.get(obj).name == "confirmLoad":
					if saveObjs.get(obj).active:
						loadName = saveObjs.get("saveFileName").text
						if loadName != "" and loadName != saveObjs.get("saveFileName").splashText:
							Load(loadName)

			for obj in keyBindingObjs:
				if obj.name == "keyBindings":
					if obj.active:
						CreateKeyBindingsInfo()

		for objMenu in objectMenus:
			if objMenu.name == "objectMenu":
				if objMenu.activeOption != None:
					if objMenu.activeOption.active:
						objType = objMenu.activeOption.text.split(" - ")[1]
						CreatePropertyMenu(objTypeDisplay[objType])
						objMenu.activeOption.active = False
						return

		# change the active property to the clicked object
		# right click
		if event.button == 3:
			for obj in allObjects:
				if obj.rect.collidepoint(pg.mouse.get_pos()):
					if activeProperty == None:
						activeProperty = obj
						break
					else:
						activeProperty = None
						break
				else:
					activeProperty = None
					break

		for message in allMessageBoxs:
			if message.name == "confirmExit":
				message.HandleEvent(event)
				message.cancelButton.HandleEvent(event)
				message.confirmButton.HandleEvent(event)
				if message.cancelButton.active:
					allMessageBoxs.remove(message)
					break
				if message.confirmButton.active:
					Quit(True)
					break

	if event.type == pg.KEYDOWN:
		# toggle debug mode
		if event.key == pg.K_F3:
			debugMode = not debugMode


		for obj in allGUIObjects:
			if gameState in obj.activeSurface or obj.activeSurface == "all":
				if type(obj) == TextInputBox:
					if obj.active:
						return

		keyBind = GetKeyName(event)
		if keyBind != None:
			if keyBind in shorcuts:
				name = shorcutFunctions[shorcuts[keyBind]["name"]]["name"]
				args = shorcutFunctions[shorcuts[keyBind]["name"]]["args"]

				print(f'{name}({args})')

				if "." in name:
					getattr(globals()[name.split(".")[0]], name.split(".")[1])()
				else:
					if args != "":
						if args == "inspectMode":
							args = not inspectMode
						globals()[name](args)
					else:
						globals()[name]()

# delete gui object
def DeleteObject():
	if activeProperty != None:
		for menu in propertiesMenus:
			if menu.parentObject == activeProperty:
				DestroyAttribute(menu.attributes[0])

# get key pressed name
def GetKeyName(event):
	keyName = str(pg.key.name(event.key))
	with open("nonAllowedRebindKeys.txt", "r") as nonAllowedKeysFile:
		nonAllowedKeys = nonAllowedKeysFile.read()
		nonAllowedKeysFile.close()

	for key in nonAllowedKeys.split("\n"):
		if key == keyName:
			return

	keyBind = ""
	if pg.key.get_pressed()[pg.K_LCTRL] or pg.key.get_pressed()[pg.K_RCTRL]:
		keyBind += "ctrl + "
	if pg.key.get_pressed()[pg.K_LSHIFT] or pg.key.get_pressed()[pg.K_RSHIFT]:
		keyBind += "shift + "
	if pg.key.get_pressed()[pg.K_LALT] or pg.key.get_pressed()[pg.K_RALT]:
		keyBind += "alt + "

	if len(keyName) >= 3:
		print(keyName[0], keyName[2])
		if keyName[0] == "[" and keyName[2] == "]":
			keyBind += keyName.strip("[]")
		else:
			keyBind += keyName
	else:
		keyBind += keyName

	return keyBind

# reset custom settings
def ResetUserSettings():
	with open(userSettings, "r") as settingsFile:
		settings = json.load(settingsFile)
		settingsFile.close()

	with open(customUserSettings, "w") as settingsFile:
		json.dump(settings, fp=settingsFile, indent=2)
		settingsFile.close()

	CreateKeyBindingsInfo()
	CreateKeyBindingsInfo()

# create keybindings info
def CreateKeyBindingsInfo(destroy=False):
	global keyBindingObjs
	remove = []
	if len(keyBindingObjs) > 1 or destroy:
		for obj in keyBindingObjs[1:]:
			remove.append(obj)

		for obj in remove:
			if obj in allLabels:
				allLabels.remove(obj)

			if obj in allButtons:
				allButtons.remove(obj)

		keyBindingObjs = keyBindingObjs[:1]
	else:
		Label(screen, "boundingBox", (50, 50, width - 100, height - 100), (lightBlack, darkWhite), "Key bindings", ("arial", 14, white), textData={"alignText": "center-top"}, drawData={"roundedCorners": True, "roundness": 20}, lists=[keyBindingObjs, allLabels])
		Button(screen, "resetToDefault", (710, 50, 100, 25), (lightBlack, darkWhite, lightRed), "Reset to default", ("arial", 12, white), isHoldButton=True, drawData={"roundedCorners": True, "roundness": 5}, lists=[keyBindingObjs, allButtons])

		with open(customUserSettings, "r") as settingsFile:
			settings = json.load(settingsFile)
			settingsFile.close()

		x = 0
		h = 13
		for i, name in enumerate(settings):
			if settings[name]["rank"] >= h:
				x = 415
			else:
				x = 0
			Label(screen, settings[name]["name"], (x + 60, 80 + ((settings[name]["rank"] % h) * 23), 150, 20), (lightBlack, darkWhite), settings[name]["name"], ("arial", 11, white), drawData={"roundedCorners": True, "roundness": 5}, lists=[keyBindingObjs, allLabels])
			Label(screen, f"keyBind-{name}", (x + 215, 80 + ((settings[name]["rank"] % h) * 23), 135, 20), (lightBlack, darkWhite), name, ("arial", 11, white), drawData={"roundedCorners": True, "roundness": 5}, lists=[keyBindingObjs, allLabels])
			Button(screen, f"rebindKey+{settings[name]['name']}", (x + 355, 80 + ((settings[name]["rank"] % h) * 23), 40, 20), (lightBlack, darkWhite, lightRed), "Rebind", ("arial", 11, white), isHoldButton=False, drawData={"roundedCorners": True, "roundness": 5}, lists=[keyBindingObjs, allButtons])

	SetKeyBinds()

# rebind shortcut keys
def RebindKeys(event):
	global rebindingKeys
	if event.type == pg.KEYDOWN:
		if event.key == pg.K_ESCAPE:
			rebindingKeys = False
			for obj in keyBindingObjs:
				if "rebindKey" in obj.name:
					obj.active = False
			return

		keyName = str(pg.key.name(event.key))
		keyBind = GetKeyName(event)

		with open(customUserSettings, "r") as settingsFile:
			settings = json.load(settingsFile)
			settingsFile.close()

		for key in settings:
			if key == keyBind:
				return

		for obj in keyBindingObjs:
			if "rebindKey" in obj.name:
				if obj.active:

					for key in settings:
						if settings[key]["name"] == obj.name.split("+")[1]:
							oldKey = key

					if keyBind not in settings:
						settings[keyBind] = settings[oldKey]
						del settings[oldKey]

					with open(customUserSettings, "w") as settingsFile:
						json.dump(settings, fp=settingsFile, indent=2)
						settingsFile.close()

				obj.active = False

		rebindingKeys = False

		for obj in keyBindingObjs:
			if "keyBind-" in obj.name:
				if obj.name.split("-")[1] == oldKey:
					obj.name = f"keyBind-{keyBind}"
					obj.UpdateText(keyBind, obj.ogFontObj)

# save
def Save(saveName=None, saveFolder=savePath):
	# get name for saved obj
	CheckSaveFolder(saveFolder)

	if saveName == None:
		saveName = saveObjs.get("saveFileName").text

	if saveName != "" and saveName != saveObjs.get("saveFileName").splashText:
		codeLines = ""
		for obj in allObjects:
			if obj.name != "":
				name = obj.name
			else:
				name = type(obj).__name__

			codeLines += f"{ProcessObject(obj, name)}\n"

		with open(saveFolder + saveName + ".py", "w") as file:
			file.write(codeLines)

	return True

# auto save every minute
def AutoSave():
	global lastSave, autoSaveCounter
	date = dt.datetime.now()
	if lastSave.minute != date.minute and lastSave.second == date.second and len(allObjects) > 0:
		saveName = f"{date.year}-{date.month}-{date.day}-{date.hour}-{date.minute}-{autoSaveCounter}"
		Save(saveName, autoSavePath)
		lastSave = date
		autoSaveCounter += 1

# check if save folders exist
def CheckSaveFolder(saveFolder):
	if not os.path.isdir(f'./{saveFolder}'):
		os.mkdir(f"./{saveFolder}")

# Show messages to user
def CreateMessageBox(messageTitle, message, messageBoxData):
	remove = []
	for obj in allMessageBoxs:
		remove.append(obj)
	for obj in remove:
		allMessageBoxs.remove(obj)
	MessageBox(screen, messageBoxData["name"], messageBoxData["rect"], (lightBlack, darkWhite, lightRed), messageTitle, message, ("arial", messageBoxData["fontSize"], white), drawData=messageBoxData["drawData"], textData=messageBoxData["textData"], inputData=messageBoxData["input"], lists=[allMessageBoxs])

# process objects into lines of code
def ProcessObject(obj, name):
	objList = {
		Box: allBoxs,
		ImageFrame: allImageFrames,
		Label: allLabels,
		TextInputBox: allTextBoxs,
		Button: allButtons,
		Slider: allSliders,
		Switch: allSwitchs,
		MultiSelectButton: allMultiButtons,
		DropDownMenu: allDropDowns
	}

	rect = ((obj.rect.x - mainCamera.rect.x) // sf, (obj.rect.y - mainCamera.rect.y) // sf, obj.rect.w // sf, obj.rect.h // sf)

	if type(obj) == Box or type(obj) == ImageFrame or type(obj) == Label or type(obj) == Switch:
		colors = (obj.backgroundColor, obj.foregroundColor)
	elif type(obj) == Slider:
		colors = (obj.backgroundColor, obj.foregroundColor, obj.sliderObj.activeColor)
	else:
		colors = (obj.backgroundColor, obj.inactiveColor, obj.activeColor)

	drawData = {
		"drawBorder": obj.drawBorder,
		"borderWidth": obj.ogBorderWidth,
		"isFilled": obj.isFilled,
		"roundedEdges": obj.roundedEdges,
		"roundedCorners": obj.roundedCorners,
		"roundness": obj.roundness,
		"activeCorners": obj.activeCorners
	}
	if type(obj) == TextInputBox:
		drawData["growRect"] = obj.growRect
		drawData["header"] = obj.header
		drawData["replaceSplashText"] = obj.replaceSplashText

	if type(obj) == Slider:
		drawData["moveText"] = obj.moveText
		drawData["sliderSize"] = obj.sliderSize
		drawData["isFilled"] = obj.isFilled

	args = f'surface = screen, name = "{name}", rect = {rect}, colors = {colors}, drawData = {drawData}'

	if type(obj) != Box:
		imageData = {
			"isAnimation": obj.isAnimation,
			"numOfFrames": obj.numOfFrames,
			"frameRate": obj.frameRate,
			"filePath": obj.imageName,
			"size": obj.ogSize
		}

		args += f', imageData = {imageData}'

		if type(obj) != ImageFrame:
			if type(obj) != TextInputBox:
				args += f', text = "{obj.text}"'

			textData = {
				"alignText": obj.alignText,
				"drawText": obj.drawText,
				"multiline": obj.multiline,
				"isScrollable": obj.scrollable,
				"scrollAmount": obj.scrollAmount
			}
			if type(obj) == Switch:
				textData["optionsText"] = obj.optionsText
				textData["optionsFontColor"] = obj.optionsFontColor
				textData["optionsAlignText"] = obj.optionsAlignText
				textData["optionsFont"] = (obj.fontName, obj.ogFontSize, obj.fontColor)

			args += f', font = ("{obj.fontName}", {obj.ogFontSize}, {obj.fontColor}), textData = {textData}'

		if type(obj) == TextInputBox:
			inputData = {
				"charLimit": obj.charLimit,
				"splashText": obj.splashText,
				"nonAllowedKeysFile": obj.nonAllowedKeysFilePath,
				"allowedKeysFile": obj.allowedKeysFilePath,
				"nonAllowedKeysList": obj.nonAllowedKeysList,
				"allowedKeysList": obj.allowedKeysList
			}

		if type(obj) == Button:
			inputData = {
				"active": obj.active
			}

		if type(obj) == Slider:
			inputData = {
				"isVertical": obj.isVertical,
				"scrollObj": obj.scrollObj,
				"startValue": obj.startValue
			}

		if type(obj) == MultiSelectButton:
			inputData = {
				"optionNames": obj.optionNames,
				"optionAlignText": obj.optionAlignText,
				"activeOption": obj.startActiveOption,
				"optionsSize": obj.optionsSize,
				"relativePos": obj.relativePos,
				"isScrollable": obj.isScrollable,
				"allowNoSelection": obj.allowNoSelection
			}

			if type(obj) == DropDownMenu:
				inputData["inputIsHoldButton"] = obj.inputIsHoldButton

		if type(obj) in [TextInputBox, Button, Slider, MultiSelectButton, DropDownMenu]:
			args += f', inputData = {inputData}'

	codeLine = f'{type(obj).__name__}({args})'
	return codeLine

# swap inspection mode
def SwapInspection(inspect):
	global inspectMode
	inspectMode = inspect
	pg.mouse.set_visible(not inspect)

# set key binds
def SetKeyBinds():
	global shorcuts
	with open(customUserSettings, "r") as settingsFile:
		settings = json.load(settingsFile)
		settingsFile.close()

	shorcuts = settings


Rescale(sf, rescaleScreen=False)


# get object data
objects = []
with open(attributeTypesFilePath, "r") as typeDataFile:
	objectData = json.load(typeDataFile)
	typeDataFile.close()

for i, prop in enumerate(objectData):
	for key in objectShortcutDisplay:
		if int(key) == i + 1:
			obj = f"{key} - {objectShortcutDisplay[key]}"
			objects.append(obj)

# object selection
DropDownMenu(screen, "objectMenu", (0, 0, 150, height), (lightBlack, darkWhite, lightRed), "Objects", ("arial", 12, white), textData={"alignText": "center-top"}, inputData={"optionNames": objects, "optionAlignText": "center", "optionsSize": [138, 35], "inputIsHoldButton": True, "allowNoSelection": True}, drawData={"inactiveY": 11.5}, lists=[objectMenus])

# camera
mainCamera = Camera("Camera", (40, 40, 640, 360), ((50, 50, 50), lightGray))

confirmSave = Button(screen, "confirmSave", (460, 0, 75, 25), (lightBlack, darkWhite, lightRed), "Save", ("arial", 12, white), isHoldButton=True, lists=[saveObjs, allDropDowns])
saveFileName = TextInputBox(screen, "saveFileName", (150, 0, 310, 25), (lightBlack, darkWhite, lightRed), ("arial", 12, white), inputData={"splashText": "Save name: ", "charLimit": 23, "allowedKeysFile": "textAllowedKeys.txt"}, textData={"alignText": "left"}, drawData={"replaceSplashText": False}, lists=[saveObjs, allDropDowns])
# confirmLoad = Button(screen, "confirmLoad", (635, 0, 75, 25), (lightBlack, darkWhite, lightRed), "Load", ("arial", 12, white), isHoldButton=True, lists=[saveObjs, allDropDowns])

keyBindingsButton = Button(screen, "keyBindings", (535, 0, 100, 25), (lightBlack, darkWhite, lightRed), "Key bindings", ("arial", 12, white), isHoldButton=True, lists=[keyBindingObjs, allButtons])

SetKeyBinds()

shorcutFunctions = {
	"Box": {
		"name": "CreatePropertyMenu",
		"args": "Box"
	},
	"Image frame": {
		"name": "CreatePropertyMenu",
		"args": "ImageFrame"
	},
	"Label": {
		"name": "CreatePropertyMenu",
		"args": "Label"
	},
	"Text input box": {
		"name": "CreatePropertyMenu",
		"args": "TextInputBox"
	},
	"Button": {
		"name": "CreatePropertyMenu",
		"args": "Button"
	},
	"Slider": {
		"name": "CreatePropertyMenu",
		"args": "Slider"
	},
	"Switch": {
		"name": "CreatePropertyMenu",
		"args": "Switch"
	},
	"Multi-select button": {
		"name": "CreatePropertyMenu",
		"args": "MultiSelectButton"
	},
	"Drop-down menu": {
		"name": "CreatePropertyMenu",
		"args": "DropDownMenu"
	},
	"Save": {
		"name": "Save",
		"args": ""
	},
	"Swap camera colors": {
		"name": "mainCamera.SwitchColors",
		"args": ""
	},
	"Reset camera position": {
		"name": "mainCamera.ResetPosition",
		"args": ""
	},
	"Move camera": {
		"name": "Move",
		"args": ""
	},
	"Inspection mode": {
		"name": "SwapInspection",
		"args": "inspectMode"
	},
	"Pin inspection": {
		"name": "PinInspection",
		"args": ""
	},
	"ctrl + Middle mouse click": {
		"name": "RemoveInspections",
		"args": ""
	},
	"Delete object": {
		"name": "DeleteObject",
		"args": ""
	}
}

while running:
	# tick clock at fps
	clock.tick_busy_loop(fps)
	AutoSave()
	if debugMode:
		print(clock.get_fps(), len(allObjects), len(allGUIObjects))

	# get all events
	for event in pg.event.get():
		# check for quit events
		if event.type == pg.QUIT:
			Quit()

		if not rebindingKeys:
			if event.type == pg.KEYDOWN:
				if event.key == pg.K_ESCAPE:
					Quit()

			if event.type == pg.MOUSEBUTTONDOWN:
				# pin inspection
				if event.button == 2:
					if inspectMode:
						PinInspection()

						if pg.key.get_pressed()[pg.K_LCTRL] or pg.key.get_pressed()[pg.K_RCTRL]:
							RemoveInspections()

			if inspectMode:
				createdInspection = False

			for inspector in pinnedInspections:
				inspector.Update()

			HandleEvents(event)
		else:
			RebindKeys(event)

	mainCamera.Update()

	DrawLoop()
