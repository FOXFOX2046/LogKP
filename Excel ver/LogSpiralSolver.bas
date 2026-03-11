Attribute VB_Name = "LogSpiralSolver"
Option Explicit

Private Const PI As Double = 3.14159265358979

Public Type GeometryResult
    CaseName As String
    Xi As Double
    Alpha1 As Double
    Alpha2 As Double
    Eta As Double
    WallLength As Double
    XOffset As Double
    XA As Double
    YA As Double
    XB As Double
    YB As Double
    XG As Double
    YG As Double
    XF As Double
    YF As Double
    XFPrime As Double
    YFPrime As Double
    R0 As Double
    RG As Double
    ThetaG As Double
    LambdaAngle As Double
    AG As Double
    FG As Double
    HRW As Double
    SpiralCount As Long
    SpiralX() As Double
    SpiralY() As Double
End Type

Public Type PassiveResult
    IsValid As Boolean
    CaseName As String
    Xi As Double
    PassiveForce As Double
    LeverArm As Double
    WeightMoment As Double
    RankineMoment As Double
    SurchargeMoment As Double
    RankineSurchargeMoment As Double
    WedgeArea As Double
    WedgeCentroidX As Double
    Geometry As GeometryResult
End Type

Private Function Rad(ByVal degreesValue As Double) As Double
    Rad = degreesValue * PI / 180#
End Function

Private Function Deg(ByVal radiansValue As Double) As Double
    Deg = radiansValue * 180# / PI
End Function

Private Function SafeAsin(ByVal value As Double) As Double
    If value > 1# Then value = 1#
    If value < -1# Then value = -1#
    SafeAsin = WorksheetFunction.Asin(value)
End Function

Private Function RankineKp(ByVal phi As Double, ByVal beta As Double) As Double
    Dim rootTerm As Double
    rootTerm = Sqr(Application.Max(Cos(beta) ^ 2 - Cos(phi) ^ 2, 0#))
    RankineKp = (Cos(beta) + rootTerm) / Application.Max(Cos(beta) - rootTerm, 0.000000000001)
End Function

Private Function BuildGeometry( _
    ByVal H As Double, _
    ByVal phi As Double, _
    ByVal beta As Double, _
    ByVal omega As Double, _
    ByVal xi As Double, _
    Optional ByVal pointCount As Long = 180) As GeometryResult

    Dim g As GeometryResult
    Dim arcTerm As Double
    Dim thetaValues() As Double
    Dim rValues() As Double
    Dim i As Long
    Dim xiAbs As Double

    If Abs(xi) < 0.000000001 Then Err.Raise vbObjectError + 101, , "xi must be non-zero."

    arcTerm = SafeAsin(Sin(beta) / Sin(phi))
    g.Alpha1 = PI / 4# - phi / 2# + 0.5 * arcTerm - beta / 2#
    g.Alpha2 = PI / 4# - phi / 2# - 0.5 * arcTerm + beta / 2#
    g.Eta = g.Alpha1 - beta
    g.WallLength = H / Cos(omega)
    g.XOffset = g.WallLength * Sin(omega)
    g.Xi = xi

    If xi < 0# Then
        g.CaseName = "A"
        xiAbs = Abs(xi)
        g.XA = xiAbs * Cos(g.Eta)
        g.YA = xiAbs * Sin(g.Eta)
        g.XB = g.XA + Abs(g.XOffset)
        g.YB = g.YA + H
        g.R0 = Sqr((H + g.YA) ^ 2 + (g.XA + g.XOffset) ^ 2)
        g.LambdaAngle = SafeAsin(g.XB / g.R0)
        g.ThetaG = SafeAsin(g.YB / g.R0) - g.Eta
        g.RG = g.R0 * Exp(g.ThetaG * Tan(phi))
        g.XG = g.RG * Cos(g.Eta)
        g.YG = g.RG * Sin(g.Eta)
        g.AG = g.RG - xiAbs
        g.FG = g.AG * Sin(g.Alpha1)
        g.XF = g.XG - g.FG * Sin(beta)
        g.YF = g.YG - g.FG * Cos(beta)
    Else
        g.CaseName = "B"
        g.XA = -(xi * Cos(g.Eta))
        g.YA = -(xi * Sin(g.Eta))
        g.XB = g.XOffset + g.XA
        g.YB = H + g.YA
        g.R0 = Sqr(g.XB ^ 2 + g.YB ^ 2)
        g.LambdaAngle = SafeAsin(g.XB / g.R0)
        g.ThetaG = PI / 2# - g.LambdaAngle - g.Eta
        g.RG = g.R0 * Exp(g.ThetaG * Tan(phi))
        g.XG = g.RG * Cos(g.Eta)
        g.YG = g.RG * Sin(g.Eta)
        g.AG = Abs(xi) + g.RG
        g.FG = g.AG * Sin(g.Alpha1)
        g.XF = g.XG - g.FG * Sin(beta)
        g.YF = g.YG - g.FG * Cos(beta)
    End If

    g.XFPrime = g.XG
    g.YFPrime = g.YA - (g.XG - g.XA) * Tan(beta)
    g.HRW = g.FG / Cos(beta)

    g.SpiralCount = pointCount
    ReDim g.SpiralX(1 To pointCount)
    ReDim g.SpiralY(1 To pointCount)
    For i = 1 To pointCount
        Dim thetaValue As Double
        Dim radiusValue As Double
        thetaValue = (i - 1) / (pointCount - 1) * g.ThetaG
        radiusValue = g.R0 * Exp(thetaValue * Tan(phi))
        g.SpiralX(i) = radiusValue * Sin(thetaValue + g.LambdaAngle)
        g.SpiralY(i) = radiusValue * Cos(thetaValue + g.LambdaAngle)
    Next i

    BuildGeometry = g
End Function

Private Sub PolygonAreaCentroid(ByRef xPoints() As Double, ByRef yPoints() As Double, ByRef area As Double, ByRef centroidX As Double)
    Dim n As Long
    Dim i As Long
    Dim j As Long
    Dim crossValue As Double
    Dim signedArea As Double
    Dim cx As Double

    n = UBound(xPoints)
    signedArea = 0#
    cx = 0#

    For i = 1 To n
        If i = n Then
            j = 1
        Else
            j = i + 1
        End If
        crossValue = xPoints(i) * yPoints(j) - xPoints(j) * yPoints(i)
        signedArea = signedArea + crossValue
        cx = cx + (xPoints(i) + xPoints(j)) * crossValue
    Next i

    signedArea = 0.5 * signedArea
    area = Abs(signedArea)
    If area < 0.000000000001 Then Err.Raise vbObjectError + 102, , "Degenerate polygon."
    centroidX = cx / (6# * signedArea)
End Sub

Public Function EvaluateXiVba( _
    ByVal H As Double, _
    ByVal gammaValue As Double, _
    ByVal phiDeg As Double, _
    ByVal deltaDeg As Double, _
    ByVal betaDeg As Double, _
    ByVal omegaDeg As Double, _
    ByVal q As Double, _
    ByVal xi As Double) As PassiveResult

    Dim result As PassiveResult
    Dim g As GeometryResult
    Dim phi As Double, deltaAngle As Double, beta As Double, omega As Double
    Dim kp As Double, v As Double, l1 As Double, lrw As Double, lq As Double
    Dim af As Double, afPrime As Double
    Dim surchargeForce As Double, surchargeMoment As Double
    Dim rankineForce As Double, rankineMoment As Double
    Dim rankineSurchargeForce As Double, rankineSurchargeMoment As Double
    Dim xPoly() As Double, yPoly() As Double
    Dim area As Double, centroidX As Double
    Dim weightForce As Double, weightMoment As Double
    Dim i As Long, polyCount As Long

    On Error GoTo Handler

    phi = Rad(phiDeg)
    deltaAngle = Rad(deltaDeg)
    beta = Rad(betaDeg)
    omega = Rad(omegaDeg)
    g = BuildGeometry(H, phi, beta, omega, xi, 180)
    kp = RankineKp(phi, beta)
    v = g.Eta - deltaAngle + omega

    If g.CaseName = "A" Then
        l1 = Abs(xi) * Sin(v) + (2# / 3#) * g.WallLength * Cos(deltaAngle)
        lrw = g.RG * Sin(g.Alpha1) - g.FG / 3#
        lq = g.RG * Sin(g.Alpha1) - g.FG / 2#
        af = Abs(g.XF - g.XA) / Application.Max(Cos(beta), 0.000000000001)
        afPrime = af + g.FG * Tan(beta)
        surchargeForce = q * afPrime
        surchargeMoment = surchargeForce * Abs((g.XA + g.XFPrime) / 2#)
    Else
        l1 = (2# / 3#) * g.WallLength * Cos(deltaAngle) - Abs(xi) * Sin(v)
        lrw = (2# / 3#) * g.FG - Abs(xi) * Sin(g.Alpha1)
        lq = 0.5 * g.FG - Abs(xi) * Sin(g.Alpha1)
        af = g.AG * Cos(g.Alpha1)
        afPrime = af + g.FG * Tan(beta)
        surchargeForce = q * afPrime
        surchargeMoment = surchargeForce * Abs((Abs(g.XA) + Abs(g.XFPrime)) / 2# - Abs(g.XA))
    End If

    If l1 <= 0# Then Err.Raise vbObjectError + 103, , "Unstable geometry produced a non-positive lever arm."

    polyCount = g.SpiralCount + 2
    ReDim xPoly(1 To polyCount)
    ReDim yPoly(1 To polyCount)
    xPoly(1) = g.XA: yPoly(1) = g.YA
    xPoly(2) = g.XB: yPoly(2) = g.YB
    For i = 2 To g.SpiralCount
        xPoly(i + 1) = g.SpiralX(i)
        yPoly(i + 1) = g.SpiralY(i)
    Next i
    xPoly(polyCount) = g.XF: yPoly(polyCount) = g.YF
    PolygonAreaCentroid xPoly, yPoly, area, centroidX

    weightForce = area * gammaValue
    weightMoment = weightForce * centroidX
    rankineForce = 0.5 * kp * gammaValue * g.HRW ^ 2 * Cos(beta)
    rankineMoment = rankineForce * lrw
    rankineSurchargeForce = q * Cos(beta) * kp * g.HRW
    rankineSurchargeMoment = rankineSurchargeForce * lq

    result.IsValid = True
    result.CaseName = g.CaseName
    result.Xi = xi
    result.PassiveForce = (weightMoment + rankineMoment + surchargeMoment + rankineSurchargeMoment) / l1
    result.LeverArm = l1
    result.WeightMoment = weightMoment
    result.RankineMoment = rankineMoment
    result.SurchargeMoment = surchargeMoment
    result.RankineSurchargeMoment = rankineSurchargeMoment
    result.WedgeArea = area
    result.WedgeCentroidX = centroidX
    result.Geometry = g
    EvaluateXiVba = result
    Exit Function

Handler:
    result.IsValid = False
    EvaluateXiVba = result
End Function

Public Sub RunXiScan()
    Dim wsIn As Worksheet, wsOut As Worksheet
    Dim H As Double, gammaValue As Double, phiDeg As Double, deltaDeg As Double
    Dim betaDeg As Double, omegaDeg As Double, q As Double
    Dim xiMin As Double, xiMax As Double, nXi As Long
    Dim i As Long, scanIndex As Long
    Dim xi As Double, bestForce As Double
    Dim best As PassiveResult, current As PassiveResult
    Dim stepSize As Double
    Dim rowOut As Long

    Set wsIn = ThisWorkbook.Worksheets("Inputs")
    Set wsOut = ThisWorkbook.Worksheets("Xi Scan")

    H = wsIn.Range("B2").Value
    gammaValue = wsIn.Range("B3").Value
    phiDeg = wsIn.Range("B4").Value
    deltaDeg = wsIn.Range("B5").Value
    betaDeg = wsIn.Range("B6").Value
    omegaDeg = wsIn.Range("B7").Value
    q = wsIn.Range("B8").Value
    If wsIn.Range("B9").Value = "Auto" Then
        xiMin = -3# * H
        xiMax = 2# * H
    Else
        xiMin = wsIn.Range("B10").Value
        xiMax = wsIn.Range("B11").Value
    End If
    nXi = CLng(wsIn.Range("B12").Value)
    If nXi < 2 Then nXi = 2

    wsOut.Cells.Clear
    wsOut.Range("A1:H1").Value = Array("xi", "Case", "Pp", "L1", "Weight moment", "Rankine moment", "Surcharge moment", "Rankine surcharge moment")

    bestForce = 1E+308
    stepSize = (xiMax - xiMin) / (nXi - 1)
    rowOut = 2

    For i = 0 To nXi - 1
        xi = xiMin + stepSize * i
        If Abs(xi) > 0.00000001 Then
            current = EvaluateXiVba(H, gammaValue, phiDeg, deltaDeg, betaDeg, omegaDeg, q, xi)
            If current.IsValid Then
                If current.PassiveForce > 0# Then
                    wsOut.Cells(rowOut, 1).Resize(1, 8).Value = Array( _
                        current.Xi, current.CaseName, current.PassiveForce, current.LeverArm, _
                        current.WeightMoment, current.RankineMoment, current.SurchargeMoment, current.RankineSurchargeMoment)
                    rowOut = rowOut + 1
                    If current.PassiveForce < bestForce Then
                        bestForce = current.PassiveForce
                        best = current
                    End If
                End If
            End If
        End If
    Next i

    If bestForce >= 1E+307 Then
        MsgBox "No valid ξ values were found in the requested range.", vbExclamation
        Exit Sub
    End If

    wsIn.Range("E2").Value = "Critical xi"
    wsIn.Range("F2").Value = best.Xi
    wsIn.Range("E3").Value = "Minimum Pp"
    wsIn.Range("F3").Value = best.PassiveForce
    wsIn.Range("E4").Value = "Case"
    wsIn.Range("F4").Value = best.CaseName
    wsIn.Range("E5").Value = "HRW"
    wsIn.Range("F5").Value = best.Geometry.HRW
    wsIn.Range("E6").Value = "r0"
    wsIn.Range("F6").Value = best.Geometry.R0
    wsIn.Range("E7").Value = "rg"
    wsIn.Range("F7").Value = best.Geometry.RG

    wsOut.Columns.AutoFit
    PlotXiChart wsOut, rowOut - 1
    DrawGeometrySheet best
End Sub

Private Sub PlotXiChart(ByVal ws As Worksheet, ByVal lastRow As Long)
    Dim chartObject As ChartObject
    Dim chartName As String
    chartName = "XiScanChart"

    On Error Resume Next
    ws.ChartObjects(chartName).Delete
    On Error GoTo 0

    Set chartObject = ws.ChartObjects.Add(320, 20, 460, 260)
    chartObject.Name = chartName
    With chartObject.Chart
        .ChartType = xlXYScatterSmooth
        .SetSourceData Source:=ws.Range("A1:C" & lastRow)
        .HasTitle = True
        .ChartTitle.Text = "Passive Force vs xi"
        .SeriesCollection(1).XValues = ws.Range("A2:A" & lastRow)
        .SeriesCollection(1).Values = ws.Range("C2:C" & lastRow)
        .SeriesCollection(1).Name = "Pp"
        .Axes(xlCategory).HasTitle = True
        .Axes(xlCategory).AxisTitle.Text = "xi"
        .Axes(xlValue).HasTitle = True
        .Axes(xlValue).AxisTitle.Text = "Pp"
    End With
End Sub

Private Sub DrawGeometrySheet(ByRef best As PassiveResult)
    Dim ws As Worksheet
    Dim shp As Shape
    Dim scaleFactor As Double
    Dim originX As Double, originY As Double
    Dim i As Long
    Dim minX As Double, maxX As Double, minY As Double, maxY As Double
    Dim currentX As Double, currentY As Double

    Set ws = ThisWorkbook.Worksheets("Geometry")
    ws.Cells.Clear
    For Each shp In ws.Shapes
        shp.Delete
    Next shp

    minX = 0#: maxX = 0#: minY = 0#: maxY = 0#
    minX = WorksheetFunction.Min(best.Geometry.XA, best.Geometry.XB, best.Geometry.XG, best.Geometry.XF, 0#)
    maxX = WorksheetFunction.Max(best.Geometry.XA, best.Geometry.XB, best.Geometry.XG, best.Geometry.XF, 0#)
    minY = WorksheetFunction.Min(best.Geometry.YA, best.Geometry.YB, best.Geometry.YG, best.Geometry.YF, 0#)
    maxY = WorksheetFunction.Max(best.Geometry.YA, best.Geometry.YB, best.Geometry.YG, best.Geometry.YF, 0#)

    scaleFactor = 220# / Application.Max(maxX - minX, maxY - minY, 0.001)
    originX = 240#
    originY = 140#

    ws.Range("A1").Value = "Dynamic Fig. 2"
    ws.Range("A2").Value = "Case"
    ws.Range("B2").Value = best.CaseName
    ws.Range("A3").Value = "Critical xi"
    ws.Range("B3").Value = best.Xi
    ws.Range("A4").Value = "Minimum Pp"
    ws.Range("B4").Value = best.PassiveForce

    AddLine ws, originX, originY, originX + best.Geometry.XA * scaleFactor, originY + best.Geometry.YA * scaleFactor, RGB(148, 163, 184), "Oa"
    AddLine ws, originX, originY, originX + best.Geometry.XB * scaleFactor, originY + best.Geometry.YB * scaleFactor, RGB(203, 213, 225), "Ob"
    AddLine ws, originX, originY, originX + best.Geometry.XG * scaleFactor, originY + best.Geometry.YG * scaleFactor, RGB(100, 116, 139), "Og"
    AddLine ws, originX + best.Geometry.XA * scaleFactor, originY + best.Geometry.YA * scaleFactor, originX + best.Geometry.XB * scaleFactor, originY + best.Geometry.YB * scaleFactor, RGB(15, 23, 42), "ab"
    AddLine ws, originX + best.Geometry.XG * scaleFactor, originY + best.Geometry.YG * scaleFactor, originX + best.Geometry.XF * scaleFactor, originY + best.Geometry.YF * scaleFactor, RGB(234, 88, 12), "gf"
    AddLine ws, originX + best.Geometry.XA * scaleFactor, originY + best.Geometry.YA * scaleFactor, originX + best.Geometry.XFPrime * scaleFactor, originY + best.Geometry.YFPrime * scaleFactor, RGB(22, 163, 74), "af'"

    For i = 1 To best.Geometry.SpiralCount - 1
        AddLine ws, _
            originX + best.Geometry.SpiralX(i) * scaleFactor, originY + best.Geometry.SpiralY(i) * scaleFactor, _
            originX + best.Geometry.SpiralX(i + 1) * scaleFactor, originY + best.Geometry.SpiralY(i + 1) * scaleFactor, _
            RGB(29, 78, 216), ""
    Next i

    AddPoint ws, originX, originY, RGB(220, 38, 38), "O"
    AddPoint ws, originX + best.Geometry.XA * scaleFactor, originY + best.Geometry.YA * scaleFactor, RGB(17, 24, 39), "a"
    AddPoint ws, originX + best.Geometry.XB * scaleFactor, originY + best.Geometry.YB * scaleFactor, RGB(17, 24, 39), "b"
    AddPoint ws, originX + best.Geometry.XG * scaleFactor, originY + best.Geometry.YG * scaleFactor, RGB(17, 24, 39), "g"
    AddPoint ws, originX + best.Geometry.XF * scaleFactor, originY + best.Geometry.YF * scaleFactor, RGB(17, 24, 39), "f"
    AddPoint ws, originX + best.Geometry.XFPrime * scaleFactor, originY + best.Geometry.YFPrime * scaleFactor, RGB(17, 24, 39), "f'"
End Sub

Private Sub AddLine(ByVal ws As Worksheet, ByVal x1 As Double, ByVal y1 As Double, ByVal x2 As Double, ByVal y2 As Double, ByVal rgbColor As Long, ByVal caption As String)
    Dim ln As Shape
    Set ln = ws.Shapes.AddLine(x1, y1, x2, y2)
    ln.Line.ForeColor.RGB = rgbColor
    If caption <> "" Then ln.Name = caption
End Sub

Private Sub AddPoint(ByVal ws As Worksheet, ByVal x As Double, ByVal y As Double, ByVal rgbColor As Long, ByVal caption As String)
    Dim dot As Shape
    Dim label As Shape
    Set dot = ws.Shapes.AddShape(msoShapeOval, x - 4, y - 4, 8, 8)
    dot.Fill.ForeColor.RGB = rgbColor
    dot.Line.Visible = msoFalse
    Set label = ws.Shapes.AddTextbox(msoTextOrientationHorizontal, x + 6, y - 8, 24, 14)
    label.TextFrame.Characters.Text = caption
    label.Line.Visible = msoFalse
    label.Fill.Visible = msoFalse
End Sub

Public Sub BuildConclusionTables()
    Dim ws As Worksheet
    Dim phiValues As Variant, ratioValues As Variant, betaValues As Variant, omegaValues As Variant
    Dim phiItem As Variant, ratioItem As Variant, betaItem As Variant, omegaItem As Variant
    Dim rowPtr As Long, colPtr As Long
    Dim best As PassiveResult, current As PassiveResult
    Dim xi As Double, xiMin As Double, xiMax As Double, stepSize As Double, bestForce As Double
    Dim nXi As Long, i As Long
    Dim H As Double, gammaValue As Double, deltaDeg As Double

    Set ws = ThisWorkbook.Worksheets("Paper Tables")
    ws.Cells.Clear

    phiValues = Array(40#, 35#, 30#, 25#)
    ratioValues = Array(0#, 1# / 3#, 1# / 2#, 2# / 3#, 1#)
    betaValues = Array(0#, 5#, 10#, 15#)
    omegaValues = Array(0#, 5#, 10#, 15#)
    H = 1#
    gammaValue = 1#
    nXi = 800
    rowPtr = 1

    For Each phiItem In phiValues
        ws.Cells(rowPtr, 1).Value = "kp table for phi = " & phiItem & " deg"
        rowPtr = rowPtr + 1
        ws.Cells(rowPtr, 1).Value = "delta/phi"
        ws.Cells(rowPtr, 1).NumberFormat = "@"
        colPtr = 2
        For Each omegaItem In omegaValues
            For Each betaItem In betaValues
                ws.Cells(rowPtr, colPtr).Value = "omega=" & omegaItem & ", beta=" & betaItem
                ws.Cells(rowPtr, colPtr).NumberFormat = "@"
                colPtr = colPtr + 1
            Next betaItem
        Next omegaItem
        rowPtr = rowPtr + 1

        For Each ratioItem In ratioValues
            ws.Cells(rowPtr, 1).NumberFormat = "@"
            ws.Cells(rowPtr, 1).Value = "'" & RatioLabel(CDbl(ratioItem))
            colPtr = 2
            For Each omegaItem In omegaValues
                For Each betaItem In betaValues
                    deltaDeg = phiItem * ratioItem
                    xiMin = -3# * H
                    xiMax = 2# * H
                    stepSize = (xiMax - xiMin) / (nXi - 1)
                    bestForce = 1E+308
                    For i = 0 To nXi - 1
                        xi = xiMin + stepSize * i
                        If Abs(xi) > 0.00000001 Then
                            current = EvaluateXiVba(H, gammaValue, phiItem, deltaDeg, betaItem, omegaItem, 0#, xi)
                            If current.IsValid Then
                                If current.PassiveForce > 0# And current.PassiveForce < bestForce Then
                                    bestForce = current.PassiveForce
                                    best = current
                                End If
                            End If
                        End If
                    Next i
                    ws.Cells(rowPtr, colPtr).Value = Round(2# * best.PassiveForce / (gammaValue * H ^ 2), 2)
                    colPtr = colPtr + 1
                Next betaItem
            Next omegaItem
            rowPtr = rowPtr + 1
        Next ratioItem
        rowPtr = rowPtr + 2
    Next phiItem

    ws.Columns.AutoFit
End Sub

Private Function RatioLabel(ByVal ratioValue As Double) As String
    Select Case Round(ratioValue, 6)
        Case 0#
            RatioLabel = "0"
        Case Round(1# / 3#, 6)
            RatioLabel = "1/3"
        Case Round(1# / 2#, 6)
            RatioLabel = "1/2"
        Case Round(2# / 3#, 6)
            RatioLabel = "2/3"
        Case 1#
            RatioLabel = "1"
        Case Else
            RatioLabel = Format(ratioValue, "0.00")
    End Select
End Function

Public Sub ResetInputs()
    Dim ws As Worksheet
    Set ws = ThisWorkbook.Worksheets("Inputs")
    ws.Range("B2").Value = 0.24
    ws.Range("B3").Value = 15.3
    ws.Range("B4").Value = 35.5
    ws.Range("B5").Value = 24#
    ws.Range("B6").Value = 0#
    ws.Range("B7").Value = 0#
    ws.Range("B8").Value = 0#
    ws.Range("B9").Value = "Auto"
    ws.Range("B10").Value = -0.5
    ws.Range("B11").Value = 0.25
    ws.Range("B12").Value = 250
End Sub
