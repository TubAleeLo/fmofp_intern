# FMOFP System Requirements

---

## AEWC RADAR SYSTEM REQUIREMENTS

When the AEWC radar display initializes, the system shall[1] set a default range scale of 200 nautical miles. 
When the AEWC displays targets, the system shall[2] convert world coordinates to screen coordinates within the specified range scale.  
When the AEWC renders the display, the system shall[3] draw: 
 
    Range rings 
 
    Cardinal direction indicators 
 
    Range scale labels 
 
    Mode indicators 
 
    Status information 
When the AEWC tracks targets, the system shall[4] display the targets current position 
When the AEWC tracks targets, the system shall[4.1] show track history up to 10 points 
When the AEWC tracks targets, the system shall[4.2] differentiate between standard and stealth targets 
When the AEWC tracks targets, the system shall[4.3] update target positions in real-time 
When the AEWC detects stealth targets, the system shall[5] use purple (RGB: 128, 0, 128) to indicate the targets. 
When the AEWC detects stealth targets, the system shall[5.1] draw diamond shape with internal cross to indicate the targets.  
When the AEWC tracks stealth targets, the system shall[6] maintain separate track history from standard targets.  
When the AEWC is in SEARCH mode, the system shall[7] display wide area surveillance 
When the AEWC is in SEARCH mode, the system shall[7.1] show all detected targets 
When the AEWC is in SEARCH mode, the system shall[7.2] display sector scan indicators 
When the AEWC is in SEARCH mode, the system shall[7.3] maintain track histories  
When the AEWC is in TRACK mode, the system shall[8] display focused target tracking 
When the AEWC is in TRACK mode, the system shall[8.1] highlight priority tracks 
When the AEWC is in TRACK mode, the system shall[8.2] show track histories 
When the AEWC is in TRACK mode, the system shall[8.3] display tracking indicators 
When the AEWC is in GROUND_MAPPING mode, the system shall[9] display ground mapping specific elements.  
When the AEWC is in STANDBY mode, the system shall[10] display "AEWC RADAR STANDBY" message. 
When the AEWC displays range rings, the system shall[11] label each ring with the distance in nautical miles 
When the AEWC displays range rings, the system shall[11.1] use dotted lines for ring visualization  
When the AEWC is operational, the system shall[12] display: 
 
   Current operational mode 
 
   Total number of tracks 
 
   Number of stealth tracks 
 
   System status information 
When the AEWC maintains track histories, the system shall[13] store up to 10 previous positions per target 
When the AEWC maintains track histories, the system shall[13.1] display history using faded green color (RGBA: 0, 255, 0, 50) 
When the AEWC maintains track histories, the system shall[13.2] remove oldest position when maximum history length is reached 
When the AEWC encounters errors, the system shall[14] log error details 
When the AEWC encounters errors, the system shall[14.1] include stack trace information 
When the AEWC encounters errors, the system shall[14.2] maintain system stability 
When the AEWC encounters errors, the system shall[14.3] continue operation when possible 
When the AEWC draws display elements, the system shall[15] support: 
 
   Multiple styles (solid, dotted, dashed) 
 
   Color-coded information 
 
   Transparent overlays 
 
   Text annotations 
When the AEWC displays sector scans, the system shall[16] show current scan sector 
When the AEWC displays sector scans, the system shall[16.1] display start and end angles 
When the AEWC displays sector scans, the system shall[16.2] indicate scan coverage area 
When the AEWC displays sector scans, the system shall[16.3] update scan position in real-time 

### **AEWC MEMORY MANAGEMENT REQUIREMENTS** *(Bug 20.1 Prevention)*
When the AEWC removes a target from tracking, the system shall[17] release all associated memory resources within 1 second.
When the AEWC removes a target from tracking, the system shall[17.1] delete track history data for both regular and stealth targets.
When the AEWC removes a target from tracking, the system shall[17.2] deallocate memory used for target-specific data structures.
When the AEWC operates continuously for more than 8 hours, the system shall[17.3] maintain memory usage growth below 5% per hour.
When the AEWC processes stealth targets, the system shall[17.4] use identical memory cleanup procedures as for regular targets.

---

## MULTI-FUNCTION DISPLAY (MFD) REQUIREMENTS

When the Multi-Function Display (MFD) is initialized, the system shall[1] provide multiple display page options: 
 
Navigation 
 
Radar 
 
Systems 
 
Weapons 
 
Communications 
 
 Settings 
When a user selects a page from the MFD menu, the system shall[2] switch to the selected page display. 
When switching between pages, the system shall[3] preserve page-specific settings and state information. 
When displaying information, the system shall[4] organize content using a consistent layout structure with defined areas for title, menu, and content.
When in the Settings page, the system shall[5] allow configuration of display parameters including theme selection: 
When the "Classic" theme is selected, the system shall[5.1.1] change the display to the "Classic" theme.
When the "Modern" theme is selected, the system shall[5.1.2] change the display to the "Modern" theme.
When the "Night" theme is selected, the system shall[5.1.3] change the display to the "Night" theme.
When in the Settings page, the system shall[6] allow configuration of display parameters including display type: 
 
Standard 
 
Holographic
The system shall[6.1.1] allow configuration of the display type to Standard
 The system shall[6.1.2] allow configuration of the display type to Holographic
 

When user preferences are changed, the system shall[7] apply them across sessions. 
When displaying data, the system shall[8] support different visual styles (standard, holographic, futuristic) that can be selected by the user. 
When in Radar mode, the system shall[9] provide a sub-menu for selecting different radar types: 
 
Weather Radar 
 
Targeting Radar 
 
Terrain Following 
 
Synthetic Aperture 
 
AEWC Radar 
When in Radar mode the system shall[10] display radar information appropriate to the selected radar type. 
When receiving radar data, the system shall[11] visualize this data using appropriate graphical representations based on the radar type. 
When a radar type is selected, the system shall[12] initialize the appropriate radar display  
When a radar type is selected, the system shall[13] connect to the corresponding data source. 
When displaying radar data, the system shall[14] show a scan line animation that corresponds to the simulated radar sweep. (this use to happen but I need to ask Doanh because i cant get it to work anymore) 
When in Navigation mode, the system shall[15] display navigational information including: 
 
waypoints  
 
routing information. 
When displaying navigation data, the system shall[16] provide a visual representation of the aircraft's position relative to waypoints. 
When navigation data is updated, the system shall[17] refresh the display to show the current information.
When in Navigation mode, the system shall[18] display a compass rose with cardinal directions.

---

## PRIMARY FLIGHT DISPLAY (PFD) REQUIREMENTS

When the Primary Flight Display (PFD) receives flight data from the FMS, the system shall[1] display the current: 
 
Altitude  
 
Airspeed 
 
Mach number 
 
Vertical speed in feet per minute 
When the PFD is updated, the system shall[2] render the airspeed with as scrolling tape displays tick marks. 
When the PFD is updated, the system shall[3] render altitude values as scrolling tape displays with tick marks 
When the target altitude differs from the current attitude by more than 100 feet, the system shall[4] display a visual indicator of the target altitude on the altitude tape. 
When the target airspeed differs from the current airspeed by more than 5 knots, the system shall[5] display a visual indicator of the target airspeed. 
When the PFD receives attitude data from the FMS, the system shall[6] display the current pitch. 
When the PFD receives attitude data from the FMS, the system shall[6.1] display the current roll. 
When the PFD is rendering the attitude indicator, the system shall[7] display pitch lines at 5-degree intervals from -20 to +20 degrees. 
When the PFD is rendering the attitude indicator, the system shall[8] rotate the artificial horizon to match the aircraft's roll angle. 
When the PFD is rendering the attitude indicator, the system shall[8.1] display an aircraft reference symbol at the center of the altitude indicator. 
When the PFD receives navigation data from the FMS, the system shall[9] display the current heading with a precision of 1 degree. 
When the PFD is rendering the heading indicator, the system shall[10] display heading tick marks at 10-degree intervals. 
When the PFD is rendering the heading indicator, the system shall[11] display numerical heading values at 20-degree intervals
When the PFD receives a flight mode of "COMBAT", the system shall[12] display the flight mode in red. 
When the PFD receives a flight mode of "STEALTH", the system shall[13] display the flight mode in blue. 
When the PFD receives a flight mode of "EMERGENCY", the system shall[14] display the flight mode in orange/red with a blinking effect.

---

## SYNTHETIC APERTURE RADAR (SAR) REQUIREMENTS

When Synthetic Aperture Radar (SAR) is operating, the system shall[1] support the following radar modes: 
 
STANDBY 
 
NORMAL 
 
STRIPMAP  
 
SPOTLIGHT  
 
SCANSAR  
 
INTERFEROMETRIC 
 
DOPPLER_BEAM 
When the SAR initializes, the system's mode shall[2] be set as STANDBY. 
When the SAR changes modes, the system shall[3] validate mode transition requests. 
When the SAR changes modes, the system shall[3.1] update operational parameters. 
When the SAR changes modes, the system shall[3.2] log mode transition events. 
When the SAR changes modes, the system shall[3.3] maintain system stability during transition. 
When generating SAR imagery, the system shall[4] create 1024x1024 pixel resolution images. 
When generating SAR imagery, the system shall[4.1] maintain 1.0 meter per pixel ground. resolution 
When generating SAR imagery, the system shall[4.2] generate mode-specific terrain features. 
When the SAR is in STRIPMAP mode, the system shall[5] generate linear terrain features. 
When the SAR is in STRIPMAP mode, the system shall[5.1] support variable swath widths 
 When the SAR is in SPOTLIGHT mode, the system shall[6] focus on circular target areas 
When the SAR is in SPOTLIGHT mode, the system shall[6.1] provide enhanced resolution in target area 
When the SAR is in SPOTLIGHT mode, the system shall[6.3] generate circular scan patterns 
When the SAR is in SPOTLIGHT mode, the system shall[6.4] support variable spotlight radius 
When the SAR is operating, the system shall[7] track corner points for mapped area. 
When the SAR is operating, the system shall[8] support 10km x 10km coverage area (-5000m to +5000m).  
When the SAR handles messages, the system shall[9] process MIL-STD-1553B messages. 
When the SAR handles messages, the system shall[9.1] handle mode change commands. 
When the SAR handles messages, the system shall[9.2] respond to imagery requests. 
When the SAR handles messages, the system shall[9.3] validate message integrity. 
When the SAR sends imagery data, the system shall[10] package binary image data 
When the SAR sends imagery data, the system shall[10.1] include corner point coordinates 
When the SAR sends imagery data, the system shall[10.2] specify resolution parameters 
When the SAR sends imagery data, the system shall[10.3] ensure data integrity 
When operational the SAR shall[11] monitor and report: 
 
Operational status 
 
Current mode 
 
System health 
 
Image dimensions

---

## TARGETING RADAR SYSTEM REQUIREMENTS

When the Target Radar System (TR) is operating, the system shall[1] support the following targeting modes: 
 
STANDBY  
 
NORMAL  
 
SEARCH 
 
TRACK  
 
LOCK 
 
GROUND_MAPPING 
 
TERRAIN_AVOIDANCE 
When the TR is initialized, the system shall[2] have a maximum detection range of 100,000 meters. 
When the TR system is initialized, the system shall[3] initialize to STANDBY state. 
When the TR system is in SEARCH mode, the system shall[4] track up to a maximum of 5 targets simultaneously. 
When the TR system updates target information, the system shall[5] calculate new target positions based on their: 
 
Current velocity 
 
Current acceleration 
 
Current position 
 
Elapsed time 
When the calculated range of a target exceeds the system's maximum detection range, the TR system shall[5] remove the target from the list of tracked targets. 
When the TR system initializes, the system shall[6] assign sequential integer track IDs starting from 1 for each new target. 
When the TR processes a target, the system shall[7] classify the target as a one of the following modes: 
 
FIGHTER 
 
HIGH_ALT 
 
UNKNOWN 
When the TR system initializes, the target classification shall[8] be set as UNKNOWN. 
When the TR system processes a target with a velocity magnitude greater that 250 m/s, the system shall[9] classify the target as a FIGHTER. 
When the TR system processes a target with an absolute altitude greater that 10,000 meters, the system shall[10] classify the target as a HIGH_ALT 
When the TR system is operational, the system shall [11] process these MIL-STD-1553B message types with the following actions: 
 
MODE_CHANGE: Change operational mode 
 
TRACK_DATA_REQUEST: Transmit current target data 
 
LOCK_REQUEST: Attempt target lock on specified track ID 
When the TR receives a "TRACK_DATA_REQUEST" message, the system shall[12] include the following information in the track data report for each target:  
 
position (x, y, z coordinates) 
 
velocity (vx, vy, vz components) 
 
Timestamp 
 
Target ID 
 
Confidence level 
When the TR receives a " LOCK_DATA_REQUEST" message, the system shall[13] include the following information in the report for each target: 
 
Lock uuid 
 
Locked target position 
 
Target ID 
 
Lock status: "LOCKED" when lock quality > 0.5, "ACQUIRING" otherwise 
 
Lock time stamp 
When the TR system is tracking a target, the system shall[14] calculate the parameters: 
 
Target range 
 
Range rate (m/s) 
 
Azimuth angle (-π to π) 
 
Elevation angle (-π/2 to π/2)  
When the TR system receives a "MODE_CHANGE" message, the system shall[15] transition to the specified mode based on the binary value associated with the targeting enum. 
When the system transitions to STANDBY mode, the system shall[16] clear all tracked targets and release any active target lock. 
When the TR is in TRACK mode and receives a "LOCK_REQUEST" message, the system shall[17] attempt to lock onto the target identified. 
When the TR system receive requests, the system shall[18] only process lock requests when in TRACK mode. 
When the TR system locks onto a target, the system shall[20] set the jamming detection status to TRUE. 
When the TR system locks onto a target, the system shall[20.1] have a 5% chance of jamming during each update cycle.  
When the TR locks onto a target, the system shall[21] calculate the lock quality derived from the target's SNR. 
When the TR locks onto a target, the system shall[22] report the calculated lock quality. 
When the TR is operational, the system shall[23] continuously report its status. 
When TR reports its status, the system shall[23.1] include  
 
Radar's name 
 
Current mode 
 
Operational status 
 
Health status 
 
Maximum range  
 
Number of active tracks  
When the TR reports its target locked status, the system shall[23.2] also include  
 
Track ID 
 
Lock quality 
 
Jamming status

### **TARGETING RADAR CLASSIFICATION REQUIREMENTS** *(Bug 23.1 Prevention)*
When the TR system processes a target with a velocity magnitude greater than 250 m/s, the system shall[24] classify the target as a FIGHTER.
When the TR system processes a target with an absolute altitude greater than 10,000 meters, the system shall[24.1] classify the target as a HIGH_ALT.
When the TR system classification thresholds are updated, the system shall[24.2] validate threshold values against operational requirements.
When the TR system validates classification parameters, the system shall[24.3] ensure FIGHTER threshold is set to 250 m/s (±5 m/s tolerance).
When the TR system validates classification parameters, the system shall[24.4] ensure HIGH_ALT threshold is set to 10,000 meters (±100 meter tolerance).

---

## TERRAIN FOLLOWING RADAR (TFR) REQUIREMENTS

When the Terrain Following Radar (TFR) is operating, the system shall[1] support the following modes: 
 
   STANDBY 
 
   SEARCH  
 
   TRACK  
 
   TERRAIN_FOLLOWING 
 
   OBSTACLE_AVOIDANCE 
 
   GROUND_MAPPING 
When the TFR system initializes, the system shall[2] enter a STANDBY mode. 
When the TFR system initializes, the system shall[3]  generate simulated terrain data. 
When the TFR system is operational, the system shall[4] support the incoming messages: 
 
MODE_CHANGE 
 
DATA 
When the TFR system processes a MODE_CHANGE message, the system shall[5] set new mode based on the incoming message. 
When the TFR system changes mode, the system shall[6] log the previous mode and the new mode. 
While the TFR system is operational, the system will support data requests in these modes: 
 
SEARCH 
 
TRACK 
 
TERRAIN_FOLLOWING 
When the TFR system processes a DATA message, the system shall[7]  send an elevation profile. 
When the TFR system transmits elevation profile data, the system shall[8] analyze the elevation profile for potential terrain warnings. 
When the TFR system enters SEARCH  mode, the system shall[9] regenerate the simulated terrain data. 
When the TFR system enters TRACK mode, the system shall[10] regenerate the simulated terrain data. 
When the TFR system is operational, the system shall [11] check for these terrain warnings: 
 
HIGH TERRAIN 
 
STEEP TERRAIN 
When the TFR system processes terrain with elevation greater than 1500 meters, the system shall[12] classify the terrain as HIGH TERRAIN.  
When the TFR system processes terrain with absolute elevation greater than 300 meters, the system shall[13] classify the terrain as STEEP TERRAIN.  
When the TFR system issues a terrain warning, warning shall[14] include the system's current:  
 
Warning type 
 
Distance 
 
Elevation 
When the TFR system is operational, the system shall[15] report its status periodically. 
When the TFR system is reporting its status, the system shall[16] include: 
 
TFR radar name 
 
Current mode 
 
Operational status 
 
Health 
 
Scan range 
 
Scan 
When the TFR system stops operating, the system shall[17] enter the STANDBY mode.

---

## WEATHER RADAR DISPLAY REQUIREMENTS

When the Weather Radar Display (WRD) initializes, the system shall[0] load configuration from the display tree manager.
When the WRD initializes, the system shall[1] initialize visual settings for all radar modes 
When the WRD initializes, the system shall[2] set up data storage for weather information 
 When the WRD initializes, the system shall[3] establish event-driven communication channels 
When the WRD is operating, the system shall[4] support the following radar modes: 
STANDBY 
SURVEILLANCE 
MAPPING 
TURBULENCE 
WINDSHEAR   
NORMAL 
When the WRD displays weather data, the system shall[5] visualize: 
    a) Vertically Integrated Liquid (VIL) data 
    b) Precipitation data 
    c) Storm cell information 
    d) Weather intensity levels 
When the WRD is rendering VIL data, the system shall[6] display data points as diamond shapes. 
When the WRD is rendering VIL data, the system shall[7] color-code based on intensity levels 
When the WRD is rendering VIL data, the system shall[8] show numerical values when enabled 
When the WRD is rendering VIL data, the system shall[9] maintain data persistence for 5 seconds 
When the WRD is in SURVEILLANCE mode, the system shall[11] show rotating scan line 
When the WRD is in SURVEILLANCE mode, the system shall[12] display weather cell information 
When the WRD is in SURVEILLANCE mode, the system shall[13] show VIL data overlay 
When the WRD is in SURVEILLANCE mode, the system shall[14] present intensity scale 
When the WRD changes to a different mode, the system shall[15] show the mode previously transitioned from.

### **WEATHER RADAR RESOURCE MONITORING REQUIREMENTS** *(Bug 22.1 Prevention)*
When the WRD monitors system resources, the system shall[16] report CPU usage with accuracy within ±2% of actual system load.
When the WRD monitors system resources, the system shall[16.1] report memory usage with accuracy within ±2% of actual system utilization.
When the WRD monitors system resources, the system shall[16.2] report disk usage with accuracy within ±2% of actual disk utilization.
When the WRD updates resource monitoring data, the system shall[16.3] refresh values at least every 5 seconds during active operations.
When the WRD operates in different modes, the system shall[16.4] reflect varying resource utilization based on operational load.

### **WEATHER RADAR VIL CALCULATION REQUIREMENTS** *(Bug 24.1 Prevention)*
When the WRD calculates VIL data from reflectivity inputs, the system shall[17] maintain double-precision floating point accuracy (64-bit).
When the WRD processes reflectivity data for VIL calculations, the system shall[17.1] preserve numerical precision to at least 15 significant digits.
When the WRD converts data types during VIL processing, the system shall[17.2] validate that no precision loss occurs beyond acceptable meteorological tolerances.
When the WRD performs VIL calculations, the system shall[17.3] use IEEE 754 double precision format (float64) for all intermediate calculations.
When the WRD validates VIL calculation accuracy, the system shall[17.4] ensure results are within 0.1% of reference double-precision calculations.

---

## MESSAGE PROCESSING SYSTEM REQUIREMENTS

### **MESSAGE PRIORITY PROCESSING REQUIREMENTS** *(Bug 21.1 Prevention)*
When the message processing system receives messages with different priority levels, the system shall[1] process messages in order of priority (0=highest, 1=normal, 2=lowest).
When the message processing system sorts the message queue, the system shall[1.1] place lower-numbered priority messages before higher-numbered priority messages.
When the message processing system processes high-priority messages (priority 0), the system shall[1.2] complete processing within 100 milliseconds of receipt.
When the message processing system processes normal-priority messages (priority 1), the system shall[1.3] complete processing within 500 milliseconds of receipt.
When the message processing system processes low-priority messages (priority 2), the system shall[1.4] complete processing within 2000 milliseconds of receipt.
When the message processing system validates priority queue implementation, the system shall[1.5] ensure priority sorting algorithm places urgent messages first in processing order.

---

## SYSTEM VERIFICATION AND VALIDATION

### **Bug Prevention Validation Requirements**
When the system undergoes acceptance testing, the system shall[1] demonstrate compliance with all memory management requirements during 24-hour continuous operation.
When the system undergoes acceptance testing, the system shall[1.1] demonstrate correct message priority processing under mixed-load conditions.
When the system undergoes acceptance testing, the system shall[1.2] demonstrate accurate resource monitoring during varying operational loads.
When the system undergoes acceptance testing, the system shall[1.3] demonstrate correct target classification across all specified threshold ranges.
When the system undergoes acceptance testing, the system shall[1.4] demonstrate VIL calculation precision within specified meteorological tolerances.

### **Compliance Monitoring Requirements**
When the system operates in production, the system shall[2] continuously monitor compliance with memory management requirements.
When the system operates in production, the system shall[2.1] continuously monitor compliance with message priority processing requirements.
When the system operates in production, the system shall[2.2] continuously monitor compliance with resource monitoring accuracy requirements.
When the system operates in production, the system shall[2.3] continuously monitor compliance with target classification threshold requirements.
When the system operates in production, the system shall[2.4] continuously monitor compliance with VIL calculation precision requirements.

---
