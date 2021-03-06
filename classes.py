# -*- encoding: utf-8 -*-
import math

Figures = []
Tools = []
Paint = None

PenStyles = [
	["Стандартный", SOLID, "sLine"],
	["Точечный", DOT, "sPPoint"],
	["Длинный Пунктир", LONG_DASH, "sLDash"],
	["Короткий Пунктир", SHORT_DASH, "sSDash"],
	["Пунктир-Точка", DOT_DASH, "sPDash"],
	["Без Границ", TRANSPARENT, "none"]
]
BrushStyles = [
	["Без Заливки", TRANSPARENT, "bTrans"],
	["Заливка", SOLID, "bSolid"],
	["Прямая Диагональ", FDIAGONAL_HATCH, "bFDiag"],
	["Обратная Диагональ", BDIAGONAL_HATCH, "bBDiag"],
	["Крестовое Пересечение", CROSSDIAG_HATCH, "bCross"],
	["Клетки", CROSS_HATCH, "bQuad"],
	["Вертикаль", VERTICAL_HATCH, "bVert"],
	["Горизонталь", HORIZONTAL_HATCH, "bHorz"]
]

class PaintZone(PaintDC):

	def __init__(self, parent, *args, **kwar):
		PaintDC.__init__(self, parent, *args, **kwar)
		self.Name = "Pen"
		self.Parent = parent
		self.MinW, self.MinH = parent.GetSize()
		self.SavedOld = [0, 0]

	def DrawFigure(self, figure):
		if hasattr(figure, "BrushStyle"): 
			self.SetBrush(Brush(figure.BrushColor, figure.BrushStyle))

		self.SetPen(Pen(figure.PenColor, int(figure.BrushSize), figure.PenStyle))
		#self.SetTool(figure.Tool.Name)

		if figure.Continious == True:

			for i, v in enumerate(figure.Points):
			
				if i+1 < len(figure.Points):

					figure.Draw(self, v[0], v[1], figure.Points[i+1][0], figure.Points[i+1][1])

		else:
			figure.Draw(self, figure.Points[0][0], figure.Points[0][1], figure.Points[1][0], figure.Points[1][1])


		if figure.Selected:

				self.SetBrush(Brush(Colors["Selection"], TRANSPARENT))
				self.SetPen(Pen(Colors["Selection"], 1, SHORT_DASH))

				minp, maxp = figure.GetRect() 

				self.DrawRect(minp[0]-2, minp[1]-2, maxp[0]+2, maxp[1]+2)

	def DrawRect(self, ax, ay, bx, by):

		x, y = min(ax, bx), min(ay, by)
		w, h = abs(ax-bx), abs(ay-by)

		self.DrawRectangle(x, y, w, h)	

	def DrawEll(self, ax, ay, bx, by):

		x, y = min(ax, bx), min(ay, by)
		w, h = abs(ax-bx), abs(ay-by)

		self.DrawEllipse(x, y, w, h)

	def DrawRoundRect(self, ax, ay, bx, by, rad=20):

		x, y = min(ax, bx), min(ay, by)
		w, h = abs(ax-bx), abs(ay-by)

		self.DrawRoundedRectangle(x, y, w, h, rad)

	def DrawPoly(self, ax, ay, bx, by, numOfAngles = 4, ang=0):

		x, y = min(ax, bx), min(ay, by)
		w, h = abs(ax-bx), abs(ay-by)

		if numOfAngles < 3:
			numOfAngles = 3

		radiusW = w/2
		radiusH = h/2
		
		angle = (2*math.pi/numOfAngles)
		x, y = x+radiusW, y+radiusH

		points = []
		for i in xrange(numOfAngles):
			
			fx = radiusW*math.cos(angle*i+math.radians(ang))
			fy = radiusH*math.sin(angle*i+math.radians(ang))
			
			points.append([x+fx, y+fy])

		self.DrawPolygon(list(points))
		

	def SetTool(self, name):
		self.Name = name

	def CalcSizes(self):

		w, h = self.Parent.GetSize()
		wa, ha = self.Parent.GetParent().GetSize()

		MinCoordX, MinCoordY = 0, 0
		MaxCoordX, MaxCoordY = 0, 0

		for i in Figures:
			for j in i.Points:
				MinCoordX, MinCoordY = min(MinCoordX, j[0]-int(i.BrushSize/2)), min(MinCoordY, j[1]-int(i.BrushSize/2))
				MaxCoordX, MaxCoordY = max(MaxCoordX, j[0]+int(i.BrushSize/2)), max(MaxCoordY, j[1]+int(i.BrushSize/2))

		MinCoordX = 0 if MinCoordX >= 0 else MinCoordX-8
		MinCoordY = 0 if MinCoordY >= 0 else MinCoordY-8

		for i in Figures:
			for j in i.Points:
				j[0] = j[0]-MinCoordX
				j[1] = j[1]-MinCoordY


		MaxCoordX = wa+MinCoordX if wa+MinCoordX > MaxCoordX else MaxCoordX
		MaxCoordY = ha+MinCoordY if ha+MinCoordY > MaxCoordY else MaxCoordY

		self.MinW = wa if MaxCoordX < wa else MaxCoordX+8
		self.MinH = ha if MaxCoordY < ha else MaxCoordY+8

		self.Parent.Move(Point(0, 0))
		x, y = self.Parent.GetParent().GetViewStart()

		self.Parent.SetSize(Size(self.MinW, self.MinH))
		self.Parent.GetParent().SetScrollbars(1, 1, self.MinW, self.MinH)
		self.Parent.GetParent().Scroll(x+abs(MinCoordX)+self.SavedOld[0], y+abs(MinCoordY)+self.SavedOld[1])

		self.SavedOld = [abs(MinCoordX), abs(MinCoordY)]

SavingColours = [
	"#FF0000", "#00FF00", "#0000FF", "#4444FF", 
	"#6600FF", "#143F72", "#FF9900", "#18C018", 
	"#C01818", "#1818C0", "#D73030", "#30D730", 
	"#FFFFFF", "#000000", "#333333", "#444444"
]

class ColorBox(ColourDialog):

	def __init__(self, parent, colourD):
		global SavingColours 

		data = ColourData()
		data.SetColour(colourD)

		for i in xrange(16):
			data.SetCustomColour(i, SavingColours[i])


		ColourDialog.__init__(self, parent, data)

	def GetColor(self):
		r, g, b = self.GetColourData().GetColour()
		return "#"+ToHEX(r, g, b)

class Figure:

	def __init__(self):

		self.Points = []
		self.PenStyle = SOLID
		self.PenColor = "#000000"
		self.BrushSize = 1
		self.Selected = False
		self.Continious = False

		Figures.append(self)

	def GetRect(self):
		
		minP, maxP = self.Points[0], self.Points[1]
		x0, y0, x1, y1 = minP[0], minP[1], maxP[0], maxP[1]

		for i in self.Points:
			x0 = i[0] if x0 > i[0] else x0
			y0 = i[1] if y0 > i[1] else y0
			x1 = i[0] if x1 < i[0] else x1
			y1 = i[1] if y1 < i[1] else y1

		minP, maxP = (x0, y0), (x1, y1)
		return minP, maxP

#########################################################################

class RectFigure(Figure):

	def __init__(self, *args):
		Figure.__init__(self, *args)
		self.BrushStyle = TRANSPARENT
		self.BrushColor = "#FFFFFF"

	def Draw(self, paint, x0, y0, x1, y1):
		paint.DrawRect(x0, y0, x1, y1)

	def IsRectIn(self, x0, y0, x1, y1):

		x0, x1 = min(x0, x1), max(x0, x1)
		y0, y1 = min(y0, y1), max(y0, y1)
		ax, ay, bx, by = self.Points[0][0], self.Points[0][1], self.Points[1][0], self.Points[1][1]

		s1 = sympy.Polygon((x0, y0), (x1, y0), (x1, y1), (x0, y1))
		s2 = sympy.Polygon((ax, ay), (bx, ay), (bx, by), (ax, by))

		nc = x0 <= ax and y0 <= ay and x1 >= bx and y1 >= by

		result = nc or sympy.intersection(s1, s2)

		return True if result else False

class RoundRectFigure(Figure):

	def __init__(self, *args):
		Figure.__init__(self, *args)
		self.Radius = 5
		self.BrushStyle = TRANSPARENT
		self.BrushColor = "#FFFFFF"

	def Draw(self, paint, x0, y0, x1, y1):
		paint.DrawRoundRect(x0, y0, x1, y1, self.Radius)

	def IsRectIn(self, x0, y0, x1, y1):

		x0, x1 = min(x0, x1), max(x0, x1)
		y0, y1 = min(y0, y1), max(y0, y1)
		ax, ay, bx, by = self.Points[0][0], self.Points[0][1], self.Points[1][0], self.Points[1][1]
		
		s1 = sympy.Polygon((x0, y0), (x1, y0), (x1, y1), (x0, y1))
		s2 = sympy.Polygon((ax, ay), (bx, ay), (bx, by), (ax, by))

		nc = x0 <= ax and y0 <= ay and x1 >= bx and y1 >= by

		result = nc or sympy.intersection(s1, s2)

		return True if result else False

class EllipseFigure(Figure):

	def __init__(self, *args):
		Figure.__init__(self, *args)
		self.BrushStyle = TRANSPARENT
		self.BrushColor = "#FFFFFF"

	def Draw(self, paint, x0, y0, x1, y1):
		paint.DrawEll(x0, y0, x1, y1)

	def IsRectIn(self, x0, y0, x1, y1):

		x0, x1 = min(x0, x1), max(x0, x1)
		y0, y1 = min(y0, y1), max(y0, y1)
		ax, ay, bx, by = self.Points[0][0], self.Points[0][1], self.Points[1][0], self.Points[1][1]
		Pols = polygon(x0, y0, x1, y1, 30, 0)

		s1 = sympy.Polygon((x0, y0), (x1, y0), (x1, y1), (x0, y1))
		s2 = sympy.Polygon(*Pols)

		nc = x0 <= ax and y0 <= ay and x1 >= bx and y1 >= by

		result = nc or sympy.intersection(s1, s2)

		return True if result else False

class LineFigure(Figure):

	def __init__(self, *args):
		Figure.__init__(self, *args)
		self.BrushStyle = TRANSPARENT
		self.BrushColor = "#FFFFFF"

	def Draw(self, paint, x0, y0, x1, y1):
		paint.DrawLine(x0, y0, x1, y1)

	def IsRectIn(self, x0, y0, x1, y1):

		x0, x1 = min(x0, x1), max(x0, x1)
		y0, y1 = min(y0, y1), max(y0, y1)
		ax, ay, bx, by = self.Points[0][0], self.Points[0][1], self.Points[1][0], self.Points[1][1]
		
		s1 = sympy.Polygon((x0, y0), (x1, y0), (x1, y1), (x0, y1))
		s2 = sympy.Segment((ax, ay), (bx, by))
		
		nc = x0 <= ax and y0 <= ay and x1 >= bx and y1 >= by

		result = nc or sympy.intersection(s1, s2)

		return True if result else False

class PolygonFigure(Figure):

	def __init__(self, *args):
		Figure.__init__(self, *args)
		self.Angle = 0
		self.EdgeCount = 3
		self.BrushStyle = TRANSPARENT
		self.BrushColor = "#FFFFFF"

	def Draw(self, paint, x0, y0, x1, y1):
		paint.DrawPoly(x0, y0, x1, y1, self.EdgeCount, self.Angle)

	def IsRectIn(self, x0, y0, x1, y1):

		x0, x1 = min(x0, x1), max(x0, x1)
		y0, y1 = min(y0, y1), max(y0, y1)
		ax, ay, bx, by = self.Points[0][0], self.Points[0][1], self.Points[1][0], self.Points[1][1]
		Pols = polygon(x0, y0, x1, y1, self.EdgeCount, self.Angle)
		
		s1 = sympy.Polygon((x0, y0), (x1, y0), (x1, y1), (x0, y1))
		s2 = sympy.Polygon(*Pols)

		nc = x0 <= ax and y0 <= ay and x1 >= bx and y1 >= by

		result = nc or sympy.intersection(s1, s2)

		return True if result else False

#########################################################################

PropList = {}

class Tool:

	def __init__(self, name, rname):
		self.Name = name
		self.Rus = rname
		self.Continious = False 
		self.IsDrawTool = True
		self.Figure = None
		self.Icon = APPDIR+"icons/def.png"
		self.Properties = {}
		self.GUI = None

		Tools.append({"name":name, "tool":self})

	def AddProperty(self, name, rus, tabOfProps, tableOfImages = []):
		self.Properties[name] = [tabOfProps, rus, tableOfImages]
		PropList[name] = [tabOfProps, rus, tableOfImages]

#########################################################################

def GetToolsMergeProps(*toolsname):
	global PropList

	props = PropList

	for i in Tools:
		if i["name"] in toolsname:
			for j, _ in PropList.items():
				if not i.Properties.get(j) and props.get(j):
					del props[j]

	return props

#########################################################################

ContLine 			= Tool("Pen", "Кисть")
ContLine.Continious = True
ContLine.Icon 		= APPDIR+"icons/brush.png"
ContLine.Figure 	= LineFigure

Selector			= Tool("Selection", "Выделение")
Selector.Icon 		= APPDIR+"icons/selector.png"
Selector.IsDrawTool = False

Line 				= Tool("Line", "Линия")
Line.Icon 			= APPDIR+"icons/line.png"
Line.Figure 		= LineFigure

Rectangle			= Tool("Rectangle", "Прямоугольник")
Rectangle.Icon		= APPDIR+"icons/rectangle.png"
Rectangle.Figure 	= RectFigure

RoundRect 			= Tool("RoundRect", "Закруглённый прямоугольник")
RoundRect.Icon 		= APPDIR+"icons/rround.png"
RoundRect.Figure 	= RoundRectFigure

Ellipse				= Tool("Ellipse", "Эллипс")
Ellipse.Icon		= APPDIR+"icons/ellipse.png"
Ellipse.Figure 		= EllipseFigure

Polygon				= Tool("Polygon", "Многоугольник")
Polygon.Icon 		= APPDIR+"icons/polygon.png"
Polygon.Figure 		= PolygonFigure

Move 				= Tool("Move", "Перемещение")
Move.Icon 			= APPDIR+"icons/move.png"
Move.IsDrawTool 	= False

Loop				= Tool("Scale", "Лупа")
Loop.Icon 			= APPDIR+"icons/zoom.png"
Loop.IsDrawTool 	= False

CurrentTool = ContLine

DrawingToolsTable = [ContLine, Line, Rectangle, Ellipse, Polygon, RoundRect]

#Example:
#Line.AddProperty("Scales", "Nothink")				#For BUTTON
#Line.AddProperty("Scaled", ["12", "123", "1234"]) 	#For COMBOBOX
#Line.AddProperty("Scalen", [1, 5])	 				#For SPINBOX

for i in DrawingToolsTable:
	i.AddProperty("BS", "Размер Кисти", [1, 60])
	i.AddProperty("SP", "Стиль Кисти", [j[0] for j in PenStyles], [j[2] for j in PenStyles])
	if i != ContLine and i != Line:
		i.AddProperty("SB", "Стиль Фигуры", [j[0] for j in BrushStyles], [j[2] for j in BrushStyles])
	

Polygon.AddProperty("AN", "Многоугольник", [3, 12])
Polygon.AddProperty("UG", "Угол поворота", [0, 359])

RoundRect.AddProperty("AN", "Радиус", [0, 128])

Move.AddProperty("ST", "Перемещение", "В начало")

Loop.AddProperty("LP", "Масштаб", [20, 500])

