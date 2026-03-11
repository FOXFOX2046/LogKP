# Excel VBA Version

Files:

- `LogSpiralSolver.bas`: VBA solver and workbook macros
- `WorkbookBuilder.ps1`: builds the macro-enabled workbook
- `LogSpiral_Excel_VBA.xlsm`: generated Excel workbook

To rebuild:

```powershell
powershell -ExecutionPolicy Bypass -File .\WorkbookBuilder.ps1
```

Main macros inside the workbook:

- `RunXiScan`
- `BuildConclusionTables`
- `ResetInputs`
