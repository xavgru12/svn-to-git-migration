import sys
import os
import subprocess
import pdb

references = [
    "refs/remotes/origin/subbranches/work/AMU_Jenkins_Test1:refs/heads/work/AMU_Jenkins_Test1",
    "refs/remotes/origin/subbranches/work/AMU_Jenkins_Test2:refs/heads/work/AMU_Jenkins_Test2",
    "refs/remotes/origin/subbranches/work/AMU_Jenkins_Test3:refs/heads/work/AMU_Jenkins_Test3",
    "refs/remotes/origin/subbranches/work/AMU_Jenkins_Test4:refs/heads/work/AMU_Jenkins_Test4",
    "refs/remotes/origin/subbranches/work/AMU_Jenkins_Test5:refs/heads/work/AMU_Jenkins_Test5",
    "refs/remotes/origin/subbranches/work/Calibrate%20all%20Actuators%20with%20Feedback:refs/heads/work/Calibrate%20all%20Actuators%20with%20Feedback",
    "refs/remotes/origin/subbranches/work/Check%20Power%20Reduction%20by%20Undervoltage:refs/heads/work/Check%20Power%20Reduction%20by%20Undervoltage",
    "refs/remotes/origin/subbranches/work/Deadline:refs/heads/work/Deadline",
    "refs/remotes/origin/subbranches/work/DeviceDescriptorCleanup:refs/heads/work/DeviceDescriptorCleanup",
    "refs/remotes/origin/subbranches/work/FPU1_HCQ:refs/heads/work/FPU1_HCQ",
    "refs/remotes/origin/subbranches/work/FPU2_HCQ:refs/heads/work/FPU2_HCQ",
    "refs/remotes/origin/subbranches/work/GyroImprovements:refs/heads/work/GyroImprovements",
    "refs/remotes/origin/subbranches/work/GyroSupervision:refs/heads/work/GyroSupervision",
    "refs/remotes/origin/subbranches/work/HCS%20pride%20speed%20pot%20style:refs/heads/work/HCS%20pride%20speed%20pot%20style",
    "refs/remotes/origin/subbranches/work/HandleNoLights:refs/heads/work/HandleNoLights",
    "refs/remotes/origin/subbranches/work/KlocworkAMU1:refs/heads/work/KlocworkAMU1",
    "refs/remotes/origin/subbranches/work/LoMa_ex1-25261:refs/heads/work/LoMa_ex1-25261",
    "refs/remotes/origin/subbranches/work/ModuleMountingOrientation:refs/heads/work/ModuleMountingOrientation",
    "refs/remotes/origin/subbranches/work/Revised%20switched%20driving:refs/heads/work/Revised%20switched%20driving",
    "refs/remotes/origin/subbranches/work/amu1:refs/heads/work/amu1",
    "refs/remotes/origin/subbranches/work/amu2:refs/heads/work/amu2",
    "refs/remotes/origin/subbranches/work/amu_ex1_printf:refs/heads/work/amu_ex1_printf",
    "refs/remotes/origin/subbranches/work/emWin:refs/heads/work/emWin",
    "refs/remotes/origin/subbranches/work/ex1-0:refs/heads/work/ex1-0",
    "refs/remotes/origin/subbranches/work/ex1-1:refs/heads/work/ex1-1",
    "refs/remotes/origin/subbranches/work/ex1-19713:refs/heads/work/ex1-19713",
    "refs/remotes/origin/subbranches/work/ex1-20242%20SeatConfiguration%20(TB4):refs/heads/work/ex1-20242%20SeatConfiguration%20(TB4)",
    "refs/remotes/origin/subbranches/work/ex1-20243%20ex1-22596%20ex1-22571%20ex1-22572%20ex1-22573%20Memory%20seating%20basics:refs/heads/work/ex1-20243%20ex1-22596%20ex1-22571%20ex1-22572%20ex1-22573%20Memory%20seating%20basics",
    "refs/remotes/origin/subbranches/work/ex1-21245_190923:refs/heads/work/ex1-21245_190923",
    "refs/remotes/origin/subbranches/work/ex1-21551_190913:refs/heads/work/ex1-21551_190913",
    "refs/remotes/origin/subbranches/work/ex1-21588_191128:refs/heads/work/ex1-21588_191128",
    "refs/remotes/origin/subbranches/work/ex1-21657_191002:refs/heads/work/ex1-21657_191002",
    "refs/remotes/origin/subbranches/work/ex1-21666:refs/heads/work/ex1-21666",
    "refs/remotes/origin/subbranches/work/ex1-21746:refs/heads/work/ex1-21746",
    "refs/remotes/origin/subbranches/work/ex1-21787:refs/heads/work/ex1-21787",
    "refs/remotes/origin/subbranches/work/ex1-21852:refs/heads/work/ex1-21852",
    "refs/remotes/origin/subbranches/work/ex1-21862:refs/heads/work/ex1-21862",
    "refs/remotes/origin/subbranches/work/ex1-21885_FWUpdate:refs/heads/work/ex1-21885_FWUpdate",
    "refs/remotes/origin/subbranches/work/ex1-22223:refs/heads/work/ex1-22223",
    "refs/remotes/origin/subbranches/work/ex1-22262:refs/heads/work/ex1-22262",
    "refs/remotes/origin/subbranches/work/ex1-22292%20Revie%20ANO_DEVICE_APPLICATION:refs/heads/work/ex1-22292%20Revie%20ANO_DEVICE_APPLICATION",
    "refs/remotes/origin/subbranches/work/ex1-22292_AVTS_EnterSwUpdateTimeout:refs/heads/work/ex1-22292_AVTS_EnterSwUpdateTimeout",
    "refs/remotes/origin/subbranches/work/ex1-22301:refs/heads/work/ex1-22301",
    "refs/remotes/origin/subbranches/work/ex1-22307_LogMast_Act_ShortenWhileNotMoving:refs/heads/work/ex1-22307_LogMast_Act_ShortenWhileNotMoving",
    "refs/remotes/origin/subbranches/work/ex1-22326_AVTS-Lite%20AD:refs/heads/work/ex1-22326_AVTS-Lite%20AD",
    "refs/remotes/origin/subbranches/work/ex1-22329_HCS_OnOff_Button:refs/heads/work/ex1-22329_HCS_OnOff_Button",
    "refs/remotes/origin/subbranches/work/ex1-22400_Latch_3-Dir:refs/heads/work/ex1-22400_Latch_3-Dir",
    "refs/remotes/origin/subbranches/work/ex1-22425_SystemBBTimeout:refs/heads/work/ex1-22425_SystemBBTimeout",
    "refs/remotes/origin/subbranches/work/ex1-22510_191128:refs/heads/work/ex1-22510_191128",
    "refs/remotes/origin/subbranches/work/ex1-22531%20ex1-22532%20ex1-22533:refs/heads/work/ex1-22531%20ex1-22532%20ex1-22533",
    "refs/remotes/origin/subbranches/work/ex1-22531,%20ex1-22532,%20ex1-22533:refs/heads/work/ex1-22531,%20ex1-22532,%20ex1-22533",
    "refs/remotes/origin/subbranches/work/ex1-22536_Error204_devMgr_read_failure:refs/heads/work/ex1-22536_Error204_devMgr_read_failure",
    "refs/remotes/origin/subbranches/work/ex1-22536_PowerUpReason_ReadFaild:refs/heads/work/ex1-22536_PowerUpReason_ReadFaild",
    "refs/remotes/origin/subbranches/work/ex1-22536_PowerUpReason_ReadFaild_2nd:refs/heads/work/ex1-22536_PowerUpReason_ReadFaild_2nd",
    "refs/remotes/origin/subbranches/work/ex1-22540:refs/heads/work/ex1-22540",
    "refs/remotes/origin/subbranches/work/ex1-22558%20ex1-22534:refs/heads/work/ex1-22558%20ex1-22534",
    "refs/remotes/origin/subbranches/work/ex1-22565:refs/heads/work/ex1-22565",
    "refs/remotes/origin/subbranches/work/ex1-22583_Extend_actuator_calibration:refs/heads/work/ex1-22583_Extend_actuator_calibration",
    "refs/remotes/origin/subbranches/work/ex1-22601_PowerUpReason_ReadFaild_2nd:refs/heads/work/ex1-22601_PowerUpReason_ReadFaild_2nd",
    "refs/remotes/origin/subbranches/work/ex1-22810:refs/heads/work/ex1-22810",
    "refs/remotes/origin/subbranches/work/ex1-22856:refs/heads/work/ex1-22856",
    "refs/remotes/origin/subbranches/work/ex1-22910:refs/heads/work/ex1-22910",
    "refs/remotes/origin/subbranches/work/ex1-22958:refs/heads/work/ex1-22958",
    "refs/remotes/origin/subbranches/work/ex1-22978:refs/heads/work/ex1-22978",
    "refs/remotes/origin/subbranches/work/ex1-22979%20ex1-22980:refs/heads/work/ex1-22979%20ex1-22980",
    "refs/remotes/origin/subbranches/work/ex1-22981:%20refs/heads/work/ex1-22981",
    "refs/remotes/origin/subbranches/work/ex1-22985:%20refs/heads/work/ex1-22985",
    "refs/remotes/origin/subbranches/work/ex1-22986:refs/heads/work/ex1-22986",
    "refs/remotes/origin/subbranches/work/ex1-22987:refs/heads/work/ex1-22987",
    "refs/remotes/origin/subbranches/work/ex1-22988:refs/heads/work/ex1-22988",
    "refs/remotes/origin/subbranches/work/ex1-22989:refs/heads/work/ex1-22989",
    "refs/remotes/origin/subbranches/work/ex1-22990:refs/heads/work/ex1-22990",
    "refs/remotes/origin/subbranches/work/ex1-22991:refs/heads/work/ex1-22991",
    "refs/remotes/origin/subbranches/work/ex1-22992:refs/heads/work/ex1-22992",
    "refs/remotes/origin/subbranches/work/ex1-22993:refs/heads/work/ex1-22993",
    "refs/remotes/origin/subbranches/work/ex1-22994:refs/heads/work/ex1-22994",
    "refs/remotes/origin/subbranches/work/ex1-22995:refs/heads/work/ex1-22995",
    "refs/remotes/origin/subbranches/work/ex1-22996:refs/heads/work/ex1-22996",
    "refs/remotes/origin/subbranches/work/ex1-22997:refs/heads/work/ex1-22997",
    "refs/remotes/origin/subbranches/work/ex1-22998:refs/heads/work/ex1-22998",
    "refs/remotes/origin/subbranches/work/ex1-22999:refs/heads/work/ex1-22999",
    "refs/remotes/origin/subbranches/work/ex1-23000:refs/heads/work/ex1-23000",
    "refs/remotes/origin/subbranches/work/ex1-23001:refs/heads/work/ex1-23001",
    "refs/remotes/origin/subbranches/work/ex1-23002:refs/heads/work/ex1-23002",
    "refs/remotes/origin/subbranches/work/ex1-23003:refs/heads/work/ex1-23003",
    "refs/remotes/origin/subbranches/work/ex1-23004:refs/heads/work/ex1-23004",
    "refs/remotes/origin/subbranches/work/ex1-23005:refs/heads/work/ex1-23005",
    "refs/remotes/origin/subbranches/work/ex1-23006:refs/heads/work/ex1-23006",
    "refs/remotes/origin/subbranches/work/ex1-23007:refs/heads/work/ex1-23007",
    "refs/remotes/origin/subbranches/work/ex1-23008:refs/heads/work/ex1-23008",
    "refs/remotes/origin/subbranches/work/ex1-23009:refs/heads/work/ex1-23009",
    "refs/remotes/origin/subbranches/work/ex1-23010:refs/heads/work/ex1-23010",
    "refs/remotes/origin/subbranches/work/ex1-23011:refs/heads/work/ex1-23011",
    "refs/remotes/origin/subbranches/work/ex1-23012:refs/heads/work/ex1-23012",
    "refs/remotes/origin/subbranches/work/ex1-23013:refs/heads/work/ex1-23013",
    "refs/remotes/origin/subbranches/work/ex1-23014:refs/heads/work/ex1-23014",
    "refs/remotes/origin/subbranches/work/ex1-23015:refs/heads/work/ex1-23015",
    "refs/remotes/origin/subbranches/work/ex1-23016:refs/heads/work/ex1-23016",
    "refs/remotes/origin/subbranches/work/ex1-23017:refs/heads/work/ex1-23017",
    "refs/remotes/origin/subbranches/work/ex1-23018:refs/heads/work/ex1-23018",
    "refs/remotes/origin/subbranches/work/ex1-23019:refs/heads/work/ex1-23019",
    "refs/remotes/origin/subbranches/work/ex1-23020:refs/heads/work/ex1-23020",
    "refs/remotes/origin/subbranches/work/ex1-23021:refs/heads/work/ex1-23021",
    "refs/remotes/origin/subbranches/work/ex1-23022:refs/heads/work/ex1-23022",
    "refs/remotes/origin/subbranches/work/ex1-23023:refs/heads/work/ex1-23023",
    "refs/remotes/origin/subbranches/work/ex1-23024:refs/heads/work/ex1-23024",
    "refs/remotes/origin/subbranches/work/ex1-23025:refs/heads/work/ex1-23025",
    "refs/remotes/origin/subbranches/work/ex1-23026:refs/heads/work/ex1-23026",
    "refs/remotes/origin/subbranches/work/ex1-23027:refs/heads/work/ex1-23027",
    "refs/remotes/origin/subbranches/work/ex1-23028:refs/heads/work/ex1-23028",
    "refs/remotes/origin/subbranches/work/ex1-23029:refs/heads/work/ex1-23029",
    "refs/remotes/origin/subbranches/work/ex1-23030:refs/heads/work/ex1-23030",
    "refs/remotes/origin/subbranches/work/ex1-23031:refs/heads/work/ex1-23031",
    "refs/remotes/origin/subbranches/work/ex1-23032:refs/heads/work/ex1-23032",
    "refs/remotes/origin/subbranches/work/ex1-23033:refs/heads/work/ex1-23033",
    "refs/remotes/origin/subbranches/work/ex1-23034:refs/heads/work/ex1-23034",
    "refs/remotes/origin/subbranches/work/ex1-23035:refs/heads/work/ex1-23035",
    "refs/remotes/origin/subbranches/work/ex1-23036:refs/heads/work/ex1-23036",
    "refs/remotes/origin/subbranches/work/ex1-23037:refs/heads/work/ex1-23037",
    "refs/remotes/origin/subbranches/work/ex1-23038:refs/heads/work/ex1-23038",
    "refs/remotes/origin/subbranches/work/ex1-23039:refs/heads/work/ex1-23039",
    "refs/remotes/origin/subbranches/work/ex1-23040:refs/heads/work/ex1-23040",
    "refs/remotes/origin/subbranches/work/ex1-23041:refs/heads/work/ex1-23041",
    "refs/remotes/origin/subbranches/work/ex1-23042:refs/heads/work/ex1-23042",
    "refs/remotes/origin/subbranches/work/ex1-23043:refs/heads/work/ex1-23043",
    "refs/remotes/origin/subbranches/work/ex1-23044:refs/heads/work/ex1-23044",
    "refs/remotes/origin/subbranches/work/ex1-23045:refs/heads/work/ex1-23045",
    "refs/remotes/origin/subbranches/work/ex1-23046:refs/heads/work/ex1-23046",
    "refs/remotes/origin/subbranches/work/ex1-23047:refs/heads/work/ex1-23047",
    "refs/remotes/origin/subbranches/work/ex1-23048:refs/heads/work/ex1-23048",
    "refs/remotes/origin/subbranches/work/ex1-23049:refs/heads/work/ex1-23049",
    "refs/remotes/origin/subbranches/work/ex1-23050:refs/heads/work/ex1-23050",
    "refs/remotes/origin/subbranches/work/ex1-23051:refs/heads/work/ex1-23051",
    "refs/remotes/origin/subbranches/work/ex1-23052:refs/heads/work/ex1-23052",
    "refs/remotes/origin/subbranches/work/ex1-23053:refs/heads/work/ex1-23053",
    "refs/remotes/origin/subbranches/work/ex1-23054:refs/heads/work/ex1-23054",
    "refs/remotes/origin/subbranches/work/ex1-23055:refs/heads/work/ex1-23055",
    "refs/remotes/origin/subbranches/work/ex1-23056:refs/heads/work/ex1-23056",
    "refs/remotes/origin/subbranches/work/ex1-23057:refs/heads/work/ex1-23057",
    "refs/remotes/origin/subbranches/work/ex1-23058:refs/heads/work/ex1-23058",
    "refs/remotes/origin/subbranches/work/ex1-23059:refs/heads/work/ex1-23059",
    "refs/remotes/origin/subbranches/work/ex1-23060:refs/heads/work/ex1-23060",
    "refs/remotes/origin/subbranches/work/ex1-23061:refs/heads/work/ex1-23061",
    "refs/remotes/origin/subbranches/work/ex1-23062:refs/heads/work/ex1-23062",
    "refs/remotes/origin/subbranches/work/ex1-23063:refs/heads/work/ex1-23063",
    "refs/remotes/origin/subbranches/work/ex1-23064:refs/heads/work/ex1-23064",
    "refs/remotes/origin/subbranches/work/ex1-23065:refs/heads/work/ex1-23065",
    "refs/remotes/origin/subbranches/work/ex1-23066:refs/heads/work/ex1-23066",
    "refs/remotes/origin/subbranches/work/ex1-23067:refs/heads/work/ex1-23067",
    "refs/remotes/origin/subbranches/work/ex1-23068:refs/heads/work/ex1-23068",
    "refs/remotes/origin/subbranches/work/ex1-23069:refs/heads/work/ex1-23069",
    "refs/remotes/origin/subbranches/work/ex1-23070:refs/heads/work/ex1-23070",
    "refs/remotes/origin/subbranches/work/ex1-23071:refs/heads/work/ex1-23071",
    "refs/remotes/origin/subbranches/work/ex1-23072:refs/heads/work/ex1-23072",
    "refs/remotes/origin/subbranches/work/ex1-23073:refs/heads/work/ex1-23073",
    "refs/remotes/origin/subbranches/work/ex1-23074:refs/heads/work/ex1-23074",
    "refs/remotes/origin/subbranches/work/ex1-23075:refs/heads/work/ex1-23075",
    "refs/remotes/origin/subbranches/work/ex1-23076:refs/heads/work/ex1-23076",
    "refs/remotes/origin/subbranches/work/ex1-23077:refs/heads/work/ex1-23077",
    "refs/remotes/origin/subbranches/work/ex1-23078:refs/heads/work/ex1-23078",
    "refs/remotes/origin/subbranches/work/ex1-23079:refs/heads/work/ex1-23079",
    "refs/remotes/origin/subbranches/work/ex1-23080:refs/heads/work/ex1-23080",
    "refs/remotes/origin/subbranches/work/ex1-23081:refs/heads/work/ex1-23081",
    "refs/remotes/origin/subbranches/work/ex1-23082:refs/heads/work/ex1-23082",
    "refs/remotes/origin/subbranches/work/ex1-23083:refs/heads/work/ex1-23083",
    "refs/remotes/origin/subbranches/work/ex1-23084:refs/heads/work/ex1-23084",
    "refs/remotes/origin/subbranches/work/ex1-23085:refs/heads/work/ex1-23085",
    "refs/remotes/origin/subbranches/work/ex1-23086:refs/heads/work/ex1-23086",
    "refs/remotes/origin/subbranches/work/ex1-23087:refs/heads/work/ex1-23087",
    "refs/remotes/origin/subbranches/work/ex1-23088:refs/heads/work/ex1-23088",
    "refs/remotes/origin/subbranches/work/ex1-23089:refs/heads/work/ex1-23089",
    "refs/remotes/origin/subbranches/work/ex1-23090:refs/heads/work/ex1-23090",
    "refs/remotes/origin/subbranches/work/ex1-23091:refs/heads/work/ex1-23091",
    "refs/remotes/origin/subbranches/work/ex1-23092:refs/heads/work/ex1-23092",
    "refs/remotes/origin/subbranches/work/ex1-23093:refs/heads/work/ex1-23093",
    "refs/remotes/origin/subbranches/work/ex1-23094:refs/heads/work/ex1-23094",
    "refs/remotes/origin/subbranches/work/ex1-23095:refs/heads/work/ex1-23095",
    "refs/remotes/origin/subbranches/work/ex1-23096:refs/heads/work/ex1-23096",
    "refs/remotes/origin/subbranches/work/ex1-23097:refs/heads/work/ex1-23097",
    "refs/remotes/origin/subbranches/work/ex1-23098:refs/heads/work/ex1-23098",
    "refs/remotes/origin/subbranches/work/ex1-23099:refs/heads/work/ex1-23099",
    "refs/remotes/origin/subbranches/work/ex1-23100:refs/heads/work/ex1-23100",
    "refs/remotes/origin/subbranches/work/ex1-23101:refs/heads/work/ex1-23101",
    "refs/remotes/origin/subbranches/work/ex1-23102:refs/heads/work/ex1-23102",
    "refs/remotes/origin/subbranches/work/ex1-23103:refs/heads/work/ex1-23103",
    "refs/remotes/origin/subbranches/work/ex1-23104:refs/heads/work/ex1-23104",
    "refs/remotes/origin/subbranches/work/ex1-23105:refs/heads/work/ex1-23105",
    "refs/remotes/origin/subbranches/work/ex1-23106:refs/heads/work/ex1-23106",
    "refs/remotes/origin/subbranches/work/ex1-23107:refs/heads/work/ex1-23107",
    "refs/remotes/origin/subbranches/work/ex1-23108:refs/heads/work/ex1-23108",
    "refs/remotes/origin/subbranches/work/ex1-23109:refs/heads/work/ex1-23109",
    "refs/remotes/origin/subbranches/work/ex1-23110:refs/heads/work/ex1-23110",
    "refs/remotes/origin/subbranches/work/ex1-23111:refs/heads/work/ex1-23111",
    "refs/remotes/origin/subbranches/work/ex1-23112:refs/heads/work/ex1-23112",
    "refs/remotes/origin/subbranches/work/ex1-23113:refs/heads/work/ex1-23113",
    "refs/remotes/origin/subbranches/work/ex1-23114:refs/heads/work/ex1-23114",
    "refs/remotes/origin/subbranches/work/ex1-23115:refs/heads/work/ex1-23115",
    "refs/remotes/origin/subbranches/work/ex1-23116:refs/heads/work/ex1-23116",
    "refs/remotes/origin/subbranches/work/ex1-23117:refs/heads/work/ex1-23117",
    "refs/remotes/origin/subbranches/work/ex1-23118:refs/heads/work/ex1-23118",
    "refs/remotes/origin/subbranches/work/ex1-23119:refs/heads/work/ex1-23119",
    "refs/remotes/origin/subbranches/work/ex1-23120:refs/heads/work/ex1-23120",
    "refs/remotes/origin/subbranches/work/ex1-23121:refs/heads/work/ex1-23121",
    "refs/remotes/origin/subbranches/work/ex1-23122:refs/heads/work/ex1-23122",
    "refs/remotes/origin/subbranches/work/ex1-23123:refs/heads/work/ex1-23123",
    "refs/remotes/origin/subbranches/work/ex1-23124:refs/heads/work/ex1-23124",
    "refs/remotes/origin/subbranches/work/ex1-23125:refs/heads/work/ex1-23125",
    "refs/remotes/origin/subbranches/work/ex1-23126:refs/heads/work/ex1-23126",
    "refs/remotes/origin/subbranches/work/ex1-23127:refs/heads/work/ex1-23127",
    "refs/remotes/origin/subbranches/work/ex1-23128:refs/heads/work/ex1-23128",
    "refs/remotes/origin/subbranches/work/ex1-23129:refs/heads/work/ex1-23129",
    "refs/remotes/origin/subbranches/work/ex1-23130:refs/heads/work/ex1-23130",
    "refs/remotes/origin/subbranches/work/ex1-23131:refs/heads/work/ex1-23131",
    "refs/remotes/origin/subbranches/work/ex1-23132:refs/heads/work/ex1-23132",
    "refs/remotes/origin/subbranches/work/ex1-23133:refs/heads/work/ex1-23133",
    "refs/remotes/origin/subbranches/work/ex1-23134:refs/heads/work/ex1-23134",
    "refs/remotes/origin/subbranches/work/ex1-23135:refs/heads/work/ex1-23135",
]


# The string was incomplete. I'll complete the given git command to count the characters.
command = """git push test refs/remotes/origin/subbranches/release/v01.141:refs/heads/release/v01.141 \
refs/remotes/origin/subbranches/release/v01.142:refs/heads/release/v01.142 \
refs/remotes/origin/subbranches/release/v01.143:refs/heads/release/v01.143 \
refs/remotes/origin/subbranches/release/v01.144:refs/heads/release/v01.144 \
refs/remotes/origin/subbranches/release/v01.145:refs/heads/release/v01.145 \
refs/remotes/origin/subbranches/release/v01.146:refs/heads/release/v01.146 \
refs/remotes/origin/subbranches/release/v01.147:refs/heads/release/v01.147 \
refs/remotes/origin/subbranches/release/v01.148:refs/heads/release/v01.148 \
refs/remotes/origin/subbranches/release/v01.149:refs/heads/release/v01.149 \
refs/remotes/origin/subbranches/release/v01.150:refs/heads/release/v01.150 \
refs/remotes/origin/subbranches/release/v01.151:refs/heads/release/v01.151"""

working_directory = r"C:\bitbucketWorkspace\gitNoExternals\ag-nor-image-creator"
# Counting the number of characters in the command
# character_count = len(git_command)
# character_count
branches = []
with open("hcq.txt", "r") as file:
    for line in file:
        branch_as_command = line.replace("\n", "")
        branches.append(branch_as_command)

# breakpoint()


def check_output(command, working_directory):
    if not isinstance(command, list):
        command = command.split()
    output = subprocess.check_output(command, cwd=f"{working_directory}").decode(
        sys.stdout.encoding
    )


def generate_commands(branches, max_length, base_command):
    commands = []
    current_command = base_command
    for branch in branches:
        potential_command = f"{current_command} {branch}"
        if len(potential_command) > max_length:
            # If the current command would exceed max length, finalize it and start a new one
            commands.append(current_command.split())
            current_command = f"{base_command} {branch}"
        else:
            current_command = potential_command

    # Append the last command if it has content
    if current_command != base_command:
        commands.append(current_command.split())

    return commands


# Generate commands
max_command_length = 32768
base_command = "git push origin --force"
commands = generate_commands(branches, max_command_length, base_command)

# breakpoint()

for command in commands:
    # if "refs/remotes/origin/subbranches/work/ex1-23359_Gyro%20while%20driving%20with%20proportional%20input:refs/heads/work/ex1-23359_Gyro%20while%20driving%20with%20proportional%20input" in command:
    #     breakpoint()
    breakpoint()
    check_output(command, working_directory)
