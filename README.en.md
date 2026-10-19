# Nyquest AI Lab

[简体中文](README.md) | English

A Windows workspace for AI-assisted Nyquest NY8 appliance firmware development. Describe a product in ordinary language, confirm its electrical requirements, qualify the exact MCU, and produce a reproducible engineering handoff.

## Features

- Exact-chip qualification using vendor projects, C headers, linker configuration and cited datasheet evidence.
- A build transaction covering decoded configuration, the Nyquest compiler/assembler/linker, resource checks and project-specific software scenarios.
- Versioned project profiles, named scenario results and SHA256 provenance for source, configuration and firmware.
- Ten reusable C modules: key debounce, sleep/wake, PWM ramp, battery ADC, charge status, motor modes, LED patterns, buzzer, key combinations and software current protection.
- Chinese engineering handoffs, explicit bench records, isolated rebuilds and portable source release exports.

## Requirements

| Component | Supported baseline |
|---|---|
| Host | Windows 10/11, an ASCII workspace path |
| Shell | Windows PowerShell 5.1 with .NET Framework |
| Python | 3.10 or newer |
| Vendor tools | NYC_NY8 2.10, NYASM 2.80; NYIDE supplies make and the original Makefile template |
| Chip onboarding dependency | `python -m pip install -r requirements.txt` |

Obtain the tools through [Nyquest support](https://www.nyquest.com.tw/cn/support/download) or the documented distributor sources in [THIRD_PARTY.md](THIRD_PARTY.md). Vendor files retain their original license terms. The public source release contains the project-authored code and recipes; Setup imports vendor components from your installation.

## Quick start

Clone this repository into an ASCII path such as `C:\work\Nyquest_AI_Lab`. Open PowerShell in that directory. Supply the directories containing the actual vendor files:

```powershell
python -m pip install -r requirements.txt
.\Setup.ps1 `
  -SdkPath 'C:\Nyquest\NYC_NY8' `
  -AssemblerPath 'C:\Nyquest\NYASM' `
  -NyidePath 'C:\Nyquest\NYIDE' `
  -ExamplesPath 'C:\Nyquest\NY8_Example_Code' `
  -DatasheetDirectory 'C:\Nyquest\Datasheets'
```

`SdkPath` contains `bin/sdcc.exe`, `cfg`, `inc`, `include`, and `lib`. `AssemblerPath` contains `nyas.exe`, `nylinker.exe`, and `Nyquest.Core.dll`. `ExamplesPath` contains the `NY8A` and `NY8B` directories. See [setup instructions](docs/SETUP.md) for the two exact datasheet names and hashes.

Setup copies the dependencies into the local workspace, reconstructs each example from its matching official project, writes the profile configuration through the vendor library, and qualifies both reference templates by actually building them. Run Setup in a fresh clone for a fresh qualification run.

```powershell
.\New-Project.ps1 -ListChips
.\New-Project.ps1 -Chip NY8B062D -Name Test_01_LedReference
.\Build.ps1 -Project 02_Projects\Test_01_LedReference_NY8B062D -Isolated
```

The new project initially implements the selected reference. Complete `Product_Requirements.md`, update the application, profile, scenarios and engineering handoff, then build the product revision.

## Build evidence

`Project_Profile.json` defines the chip, clock, explicit decoded configuration fields, pin functions and required scenario names. Each build decodes the current `.cb`, verifies this policy and the timing calculation, compiles current artifacts, and checks the structured behavior report. The report carries a unique run ID and the hashes of that build's inputs and firmware.

| Result | Meaning |
|---|---|
| `ARTIFACTS_PASS` | Compilation artifacts and static resource checks passed |
| Workflow `PASS` | Configuration, compilation and required software scenarios passed |
| `INCOMPLETE` | Required profile or scenario evidence needs completion |
| `FAILED` | A configuration, tool, artifact or scenario check requires correction |
| Bench `UNTESTED` | Hardware measurement remains assigned to the engineer |

The three-mode reference uses a 3.0 V reference board, a PA0 button, three active-low LEDs, 4 MHz IHRC / 4T, a 10 ms timer and a 300 s inactivity timeout. Its expected software coverage has 27 scenarios. NY8A051F supplies an idle qualification probe with 6 scenarios. The supported clock backend currently covers the decoded 4 MHz IRC with 2T/4T; each project profile selects its verified setting.

## Development and handoff

```powershell
python -m unittest discover -s 00_Reference/Scripts -p 'test_*.py' -v
python 00_Reference/Scripts/integration_checks.py
.\Package-Project.ps1 -Project 02_Projects\Test_01_LedReference_NY8B062D
```

Portable unit tests run on a clean source checkout. Integration checks use the imported vendor tools and generated projects. GitHub Actions runs the portable tests; the local integration report records vendor build verification.

Use [the product requirements form](00_Reference/Templates/Product_Requirement_Template.md), [bench checklist](00_Reference/Templates/Bench_Test_Checklist.md) and project `Bench_Results.md` for electrical acceptance. Firmware C sources and comments use ASCII English. Project engineering handoffs use Chinese; repository documentation is available in both languages.

## Public release

```powershell
.\Export-OpenSource.ps1 -Destination C:\work\Nyquest_AI_Lab_Public
```

The exporter writes an explicitly selected source tree, a SHA256 manifest and a verified ZIP into a new destination. Start the public Git history in that exported directory. This preserves the full local development archive and gives the public repository a source-only history. See [publishing instructions](docs/PUBLISH.md).

Project-authored public files use the [MIT License](LICENSE). [Third-party provenance](THIRD_PARTY.md), [contribution instructions](CONTRIBUTING.md), [verification contract](docs/VERIFICATION.md) and [security guidance](SECURITY.md) describe the project boundaries and workflow.
