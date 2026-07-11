# FMOFP — Flight Management Operating Flight Program

> **Development build (B20SS).** This is an in-development avionics simulation used as a training and software-test-readiness (SSTR) platform. It is not flight software and is not intended for operational use.

The FMOFP is a Python/PyQt6 simulation of an integrated military aircraft avionics suite. It models radar systems, cockpit displays, a flight management system, and a range of supporting aircraft subsystems, all communicating over a simulated **MIL-STD-1553B** data bus. The codebase is primarily used as an intern/training environment and as a fixture for verifying known software defects (the SSTR catalog).

The project is large — roughly 470 Python modules under `B20SS/FMOFP/` — and depth of implementation varies by subsystem. The radar suite and cockpit displays are the most developed; many other aircraft systems are present as lighter-weight models or scaffolding.

---

## Repository layout

The application source lives under `B20SS/FMOFP/`. The top level (`B20SS/`) also bundles vendored dependencies (`PyQt6/`, a `.venv/`), documentation, diagrams, and tooling.

| Path | Purpose |
|------|---------|
| `B20SS/FMOFP/Main.py` | Main application entry point; constructs the program, event bus, and handlers. |
| `B20SS/FMOFP/SystemStart.py` | Async startup wrapper that initializes the system and launches `Main`. |
| `B20SS/FMOFP/core/` | Startup and lifecycle core: `initializer.py` (creates the `QApplication`), `system_manager.py` (component registration and async startup orchestration), `event_driven_communication.py` (the event bus), and the startup sequencers. |
| `B20SS/FMOFP/Systems/` | Aircraft subsystem models (see the subsystem table below). |
| `B20SS/FMOFP/Interfaces/` | User-facing layer: `userInterface/displays/` (PFD, MFD, radar, HUD, holographic), `userInterface/managers/`, `userInterface/messaging/`, plus `predefinedMessages/` and `scenarios/`. |
| `B20SS/FMOFP/MIL_STD_1553B/` | Simulated 1553B bus: `Bus_Controller/` and `Remote_Terminal/`, each with `*_connect/` (TCP sockets) and `*_messaging/` (queueing, extraction). |
| `B20SS/FMOFP/local_messaging/` | In-process message routing, handlers, response services, and message configurations. |
| `B20SS/FMOFP/storage/` | Database-backed state persistence (`DBM.py`, `databases/`). |
| `B20SS/FMOFP/Utils/` | Logging, threading/partitions, message-loop prevention, the debug console, and shared helpers. |
| `B20SS/FMOFP/Tests/` | Subsystem and integration tests, including `radar_tests/`. |
| `B20SS/FMOFP/*.xml` | Runtime configuration (see Configuration below). |
| `B20SS/FMOFP_User_Manual/` | Multi-file user manual (overview, per-radar docs, display docs, procedures). |
| `B20SS/PLANNING.md` | Architecture notes and the radar capability roadmap. |
| `B20SS/__TOOLS__/` | Developer utilities (`Cleanup.py`, `programStructure.py`, `nameAddXML.py`). |
| `B20SS/__ABOUT__/`, `B20SS/__Diagrams__/` | UML, entity-relationship, sequence, and state diagrams. |

---

## Architecture overview

The system is event-driven and multi-threaded. Subsystems do not call each other directly; they exchange messages, either through the in-process routing layer (`local_messaging/`) or across the simulated 1553B bus. Startup is orchestrated by a singleton `Initializer` (which owns the Qt `QApplication` and event loop) and a `SystemManager` that registers components, starts them asynchronously, and drives a periodic display-refresh timer.

### Simulated MIL-STD-1553B bus

The bus is modeled with **real TCP sockets** rather than abstract calls. The Bus Controller (BC) runs a listener (by default on `localhost:5000`) and Remote Terminals (RTs) connect to it. Messages are encoded into 1553-style words:

- **Command word:** sync(3) + RT address(5) + T/R bit(1) + subaddress(5) + word count(5) + parity(1)
- **Status word:** sync(3) + RT address(5) + flags(11) + parity(1)
- **Data word:** sync(3) + data(16) + parity(1)

### RT address map

Subsystems are assigned 1553B remote-terminal addresses (from `rtAddressConfig.xml`):

| RT address | System |
|-----------|--------|
| 1 | Avionics |
| 2 | Communications |
| 3 | Engine Management |
| 4 | Environmental Control System |
| 5 | Flight Control System |
| 6 | Mission Planning |
| 7 | Navigation |
| 8 | Power Management |
| 9 | Radar |
| 10 | Sensor Management |
| 11 | Display System |
| 12 | Flight Management System |

### Radar subaddresses (RT 9)

| Radar | Subaddress | Manual status |
|-------|-----------|---------------|
| Weather Radar (WR) | 1 | Operational |
| TFR Radar (terrain following) | 2 | Basic simulation |
| SAR Radar (synthetic aperture) | 3 | Basic simulation |
| Targeting Radar (TR) | 4 | Operational |
| AEWC Radar (early warning) | 5 | Basic simulation |

### Display subaddresses (RT 11)

The display system renders a Primary Flight Display (PFD) and a Multi-Function Display (MFD), with a radar display embedded in the MFD. Several display variants exist in the code — standard, "futuristic," holographic, HUD, and a node-based PFD.

### Local messaging

In-process request handling uses a `RadarMessageHandler` for request initiation and tracking, and an `AsyncMessageHandler` with multiple worker threads. The layer includes UUID-based request tracking, rate limiting, and routing/response services. See `B20SS/FMOFP/local_messaging/README.md` and `.../routing/README.md` for detail.

For the full architectural picture, see `B20SS/PLANNING.md` and the diagrams under `B20SS/__ABOUT__/` and `B20SS/__Diagrams__/`.

---

## Subsystems

`B20SS/FMOFP/Systems/` contains the aircraft subsystem models. Implementation depth varies considerably — the figures below are module counts as a rough proxy for maturity, not a guarantee of completeness.

| Subsystem | Modules | Notes |
|-----------|--------:|-------|
| `radarManagement/` | ~44 | The most developed area: per-radar implementations (weather, targeting, SAR, TFR, AEWC), radar control, and radar messaging. |
| `flightManagementSys/` | ~16 | FMS, flight dynamics, and FMS messaging. |
| `powerManagement/` | ~14 | Electrical, batteries, thermal management. |
| `missionPlanning/` | ~10 | Route management, order of battle, targeting, mission data. |
| `nav/` | ~9 | GPS, INS, TACAN, data fusion. |
| `engineManagement/` | ~9 | ECU, thrust, fuel management. |
| `comms/` | ~8 | SATCOM, radios, data link. |
| `flightControlSys/` | ~7 | Flight control computer, ground collision avoidance, performance monitoring. |
| `sensorManagement/` | ~6 | Active and passive sensors. |
| `enviornmentalControlSystem/` | ~6 | Climate, oxygen generation *(directory name is spelled this way in the repo)*. |
| `avionics/` | ~4 | Hardware health. |
| `hydraulics/`, `fuelSystems/`, `fmFitness/`, `flightDataMonitoring/`, `electricalPower/`, `configurationManagement/`, `builtInTestSystems/`, `airframeSystemManagement/` | ~2 each | Lightweight models or scaffolding. |
| `flightSurfaces/`, `defensiveSys/` | 0 | Present as placeholders; no Python modules yet. |


---

## Configuration

Runtime configuration is XML-driven, with files at `B20SS/FMOFP/`:

| File | Purpose |
|------|---------|
| `rtAddressConfig.xml` | 1553B RT addresses and subaddresses for every system. |
| `startupConfiguration.xml` | Startup sequencing/options. |
| `dbConfig.xml` | Database/storage config, including the list of system names and worker limits. |
| `messageRateConfig.xml` | Message rate settings. |
| `queryRateConfig.xml` | Query rate settings. |

Additional component-level XML (address books, command registries, message templates, log filters) lives alongside the relevant modules under `local_messaging/` and `Utils/logger/`.

---

## Running the application

The application is launched as a module so the `FMOFP.` package prefix resolves. Run it from the `B20SS/` directory:

```bash
cd B20SS
python -m FMOFP.Main
```

Because the simulated 1553B bus uses TCP sockets (BC listener on `localhost:5000` by default), the port must be free. On startup you should see console output for component loading, database initialization, and component status, with radar systems reaching STANDBY and displays becoming responsive. See `B20SS/FMOFP_User_Manual/00a_Getting_Started.md` for a guided walkthrough.

---

## Interactive debug console (userCLI)

The project includes an interactive command-line console for exercising the system at runtime: `B20SS/FMOFP/Utils/debug/userCLI.py`. It is a singleton (`UserCLI`) built on `click` with an `input()`-driven prompt loop, and it talks to the running system through the same radar-management and 1553B messaging layers the application uses. It is intended for development and testing, not operational use.

Once the system is running and the CLI prompt is shown, type a command. The commands actually wired into the console's dispatcher (`_process_command`) are:

| Command | Description |
|---------|-------------|
| `test` | Shows a menu of test suites and runs the selected one: combined precipitation/VIL flow, FMS system, flight control system, predefined messages, and the all-modes test for each radar (weather, TFR, SAR, targeting, AEWC). |
| `help` | Prints the help menu. (Any input beginning with `help` triggers it.) |
| `list_tables` | Lists the persisted state tables. |
| `get_table` | Prompts for a table name, then prints that table's contents. |
| `get_import_statement` | Prompts for a function name and file path. Currently a stub (no-op). |

Any unrecognized input returns "Unknown command."

**Note on the help menu.** The built-in `help` output advertises `send`, `msg`, and `test_1553b`, but these are not implemented in the dispatcher — typing them returns "Unknown command." Conversely, `list_tables`, `get_table`, and `get_import_statement` are functional but are not listed by `help`. The table above reflects what the code actually does, not the help text.

---

## Tests

Tests live under `B20SS/FMOFP/Tests/`, with per-radar tests in `B20SS/FMOFP/Tests/radar_tests/`. `setup_env.py` prepares the environment used by the suites. Many of the same suites are also reachable interactively through the `test` command in the debug console. Run individual test modules from the `B20SS` directory so the `FMOFP` package resolves, for example:

```bash
cd B20SS
python -m FMOFP.Tests.radar_tests.weather_radar_test
```

Test-specific requirements are documented in `B20SS/FMOFP/Tests/REQUIREMENTS.md`.

---

## Documentation

- **User manual:** `B20SS/FMOFP_User_Manual/` — start at `00_Title_and_TOC.md`. The manual marks each feature with a status indicator (operational, in development, not implemented, known issue).
- **Requirements:** `B20SS/FMOFP/REQUIREMENTS.md` and `B20SS/FMOFP/Tests/REQUIREMENTS.md`.
- **Planning & architecture:** `B20SS/PLANNING.md`.
- **Subsystem READMEs:** `B20SS/FMOFP/local_messaging/README.md`, `.../local_messaging/routing/README.md`, `.../Utils/message_loop_prevention/README.md`.
- **Diagrams:** `B20SS/__ABOUT__/` and `B20SS/__Diagrams__/`.

---

## Project status

This is an active development build. Per the user manual, the Weather and Targeting radars and the core displays are the most complete; SAR, TFR, and AEWC are basic simulations, and several supporting aircraft subsystems are partial or placeholder. A number of subsystems carry documented known issues that are tracked separately as SSTR items. Verify the current status of any feature against the user manual and the code before relying on it.
