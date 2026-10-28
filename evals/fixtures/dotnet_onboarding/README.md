# Desktop and text utilities

`Legacy.sln` contains the .NET Framework 4.8 desktop component and its executable
checks. On Windows with the .NET Framework 4.8 targeting pack and MSBuild, run
from the repository root:

```powershell
msbuild Legacy.sln /t:Build /p:Configuration=Debug
.\Legacy.Checks\bin\Debug\net48\Legacy.Checks.exe
```

`Modern.sln` contains an independent .NET 8 class library. Build it with a matching
SDK using `dotnet build Modern.sln`. It has no test project in this snapshot.
The desktop checks do not verify the text library. Opening this directory in an
IDE does not establish that both solutions have been loaded or built.
